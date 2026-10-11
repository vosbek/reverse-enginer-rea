"""Windows PE decoding from bytes: headers, sections, imports, version resource, Authenticode signers, overlay.

Everything here walks structures with `struct` and bounds checks. Malformed
input raises struct.error or returns partial results; it is never loaded.
"""

from __future__ import annotations

import struct
from datetime import datetime, timezone

MACHINES = {0x14C: "x86", 0x8664: "x86-64", 0xAA64: "ARM64", 0x1C0: "ARM", 0x1C4: "ARMv7"}
SUBSYSTEMS = {2: "Windows GUI", 3: "Windows console", 10: "EFI application", 16: "Windows boot application"}
DLL_CHARS = {0x0020: "high-entropy ASLR", 0x0040: "ASLR", 0x0100: "DEP/NX", 0x0400: "no SEH",
             0x4000: "Control Flow Guard"}
VERSION_KEYS = ("CompanyName", "FileDescription", "FileVersion", "InternalName", "LegalCopyright",
                "OriginalFilename", "ProductName", "ProductVersion")

# Imported Windows APIs grouped by what they let a program do. Matching is by exact name or prefix.
CAPABILITIES = [
    ("Network (WinINet/WinHTTP)", "network", ("InternetOpen", "InternetConnect", "InternetReadFile", "HttpOpenRequest",
                                              "HttpSendRequest", "InternetOpenUrl", "WinHttp", "URLDownloadTo")),
    ("Sockets", "network", ("WSAStartup", "socket", "connect", "getaddrinfo", "WSASocket")),
    ("Start other programs", "process", ("CreateProcess", "ShellExecute", "WinExec", "CreateProcessAsUser")),
    ("Inspect or modify other processes", "process", ("OpenProcess", "WriteProcessMemory", "ReadProcessMemory",
                                                      "CreateRemoteThread", "VirtualAllocEx")),
    ("Load code at runtime", "dynamic-code", ("LoadLibrary", "GetProcAddress", "LdrLoadDll")),
    ("Registry", "host", ("RegCreateKey", "RegSetValue", "RegOpenKey", "RegQueryValue", "RegDeleteKey",
                          "RegDeleteValue", "RegEnumKey")),
    ("Files and folders", "filesystem", ("CreateFile", "WriteFile", "DeleteFile", "MoveFile", "CopyFile",
                                         "CreateDirectory", "RemoveDirectory", "SHFileOperation",
                                         "SHGetKnownFolderPath", "SHGetFolderPath")),
    ("Shortcuts and shell integration", "host", ("SHChangeNotify", "IShellLink", "CoCreateInstance",
                                                 "SHCreateItemFromParsingName")),
    ("Privileges and security", "privilege", ("AdjustTokenPrivileges", "OpenProcessToken", "LookupPrivilegeValue",
                                              "CheckTokenMembership", "GetTokenInformation")),
    ("Cryptography and signatures", "crypto", ("Crypt", "BCrypt", "NCrypt", "WinVerifyTrust", "CertGetCertificate")),
    ("User interface", "ui", ("CreateWindow", "DialogBox", "MessageBox", "ShowWindow", "InitCommonControls",
                              "TaskDialog")),
    ("Version checks", "host", ("GetFileVersionInfo", "VerQueryValue", "RtlGetVersion", "VerifyVersionInfo")),
    ("Services", "host", ("OpenSCManager", "CreateService", "StartService")),
    ("Scheduled tasks / COM automation", "host", ("CoInitialize", "CLSIDFromProgID")),
]


def _sections(b: bytes, sec_off: int, nsec: int) -> list[dict]:
    out = []
    for i in range(min(nsec, 96)):
        base = sec_off + i * 40
        name = b[base: base + 8].rstrip(b"\x00").decode("ascii", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", b, base + 8)
        chars, = struct.unpack_from("<I", b, base + 36)
        out.append({"name": name, "va": va, "vsize": vsize, "rawptr": rawptr, "rawsize": rawsize,
                    "exec": bool(chars & 0x20000000), "write": bool(chars & 0x80000000)})
    return out


def _rva(sections: list[dict], rva: int) -> int | None:
    for s in sections:
        if s["va"] <= rva < s["va"] + max(s["vsize"], s["rawsize"]):
            return rva - s["va"] + s["rawptr"]
    return None


def _cstr(b: bytes, off: int | None, limit: int = 256) -> str:
    if off is None or off >= len(b):
        return ""
    end = b.find(b"\x00", off, off + limit)
    return b[off: end if end != -1 else off + limit].decode("ascii", "replace")


def _imports(b: bytes, sections, rva: int, is64: bool) -> list[dict]:
    off = _rva(sections, rva)
    out = []
    if off is None:
        return out
    for _ in range(512):
        if off + 20 > len(b):
            break
        oft, _ts, _fwd, name_rva, ft = struct.unpack_from("<IIIII", b, off)
        if not (oft or name_rva or ft):
            break
        dll = _cstr(b, _rva(sections, name_rva))
        funcs = []
        thunk = _rva(sections, oft or ft)
        size, fmt, flag = (8, "<Q", 1 << 63) if is64 else (4, "<I", 1 << 31)
        while thunk is not None and thunk + size <= len(b) and len(funcs) < 4096:
            val, = struct.unpack_from(fmt, b, thunk)
            if not val:
                break
            if val & flag:
                funcs.append(f"#{val & 0xFFFF}")
            else:
                funcs.append(_cstr(b, (_rva(sections, val & 0x7FFFFFFF) or 0) + 2))
            thunk += size
        out.append({"dll": dll, "functions": funcs})
        off += 20
    return out


def _version(rsrc: bytes) -> dict[str, str]:
    """Read StringFileInfo values. Each String is: u16 length, u16 value-length (words), u16 type, key, pad, value."""
    out = {}
    for key in VERSION_KEYS:
        needle = key.encode("utf-16-le") + b"\x00\x00"
        idx = rsrc.find(needle)
        if idx < 6:
            continue
        start = idx - 6
        _length, vlen, _type = struct.unpack_from("<HHH", rsrc, start)
        key_end = idx + len(needle)
        val = start + ((key_end - start + 3) & ~3)
        raw = rsrc[val: val + vlen * 2]
        text = raw.decode("utf-16-le", "replace").rstrip("\x00").strip()
        if text:
            out[key] = text
    return out


def _der_names(blob: bytes) -> list[str]:
    """Pull CN and O attribute values out of DER certificates (OID 2.5.4.3 / 2.5.4.10)."""
    names = []
    for oid, label in ((b"\x06\x03\x55\x04\x03", "CN"), (b"\x06\x03\x55\x04\x0a", "O")):
        pos = 0
        while True:
            pos = blob.find(oid, pos)
            if pos == -1 or pos + 7 > len(blob):
                break
            tag, ln = blob[pos + 5], blob[pos + 6]
            if tag in (0x0C, 0x13, 0x14, 0x16, 0x1E) and ln < 0x80:
                raw = blob[pos + 7: pos + 7 + ln]
                value = raw.decode("utf-16-be" if tag == 0x1E else "utf-8", "replace")
                item = f"{label}={value}"
                if item not in names:
                    names.append(item)
            pos += 5
    return names


def parse(b: bytes) -> dict:
    if len(b) < 0x40 or b[:2] != b"MZ":
        return {"format": "unknown"}
    pe_off, = struct.unpack_from("<I", b, 0x3C)
    if pe_off + 24 > len(b) or b[pe_off:pe_off + 4] != b"PE\x00\x00":
        return {"format": "DOS MZ executable", "notes": []}
    machine, nsec, timestamp = struct.unpack_from("<HHI", b, pe_off + 4)
    opt_size, chars = struct.unpack_from("<HH", b, pe_off + 20)
    opt = pe_off + 24
    magic, = struct.unpack_from("<H", b, opt)
    is64 = magic == 0x20B
    entry, = struct.unpack_from("<I", b, opt + 16)
    subsystem, dllchars = struct.unpack_from("<HH", b, opt + (68 if is64 else 68))
    ndirs_at = opt + (108 if is64 else 92)
    ndirs, = struct.unpack_from("<I", b, ndirs_at)
    dirs_at = ndirs_at + 4
    dirs = [struct.unpack_from("<II", b, dirs_at + i * 8) for i in range(min(ndirs, 16))]
    sections = _sections(b, opt + opt_size, nsec)

    notes = []
    ts = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    if timestamp == 0 or ts.year < 2010 or ts > datetime.now(timezone.utc):
        notes.append(f"link timestamp {timestamp:#010x} is not a plausible date (deterministic /Brepro build)")
    else:
        notes.append(f"linked {ts:%Y-%m-%d}")
    hardening = [label for bit, label in DLL_CHARS.items() if dllchars & bit]
    if b"Rich" in b[0x80:pe_off]:
        notes.append("MSVC Rich header present")
    if any(s["exec"] and s["write"] for s in sections):
        notes.append("writable+executable section")

    imports = _imports(b, sections, dirs[1][0], is64) if len(dirs) > 1 and dirs[1][0] else []
    version = {}
    rsrc = next((s for s in sections if s["name"] == ".rsrc"), None)
    if rsrc:
        version = _version(b[rsrc["rawptr"]: rsrc["rawptr"] + rsrc["rawsize"]])
    signers, sig_size = [], 0
    if len(dirs) > 4 and dirs[4][0] and dirs[4][1]:
        sig_off, sig_size = dirs[4]  # file offset, not an RVA
        signers = _der_names(b[sig_off: sig_off + sig_size])
    if len(dirs) > 14 and dirs[14][0]:
        notes.append(".NET assembly")
    if any(s["name"].startswith("UPX") for s in sections):
        notes.append("UPX-packed")
    raw_end = max((s["rawptr"] + s["rawsize"] for s in sections), default=0)
    overlay = len(b) - raw_end - sig_size
    if overlay > 512:
        notes.append(f"{overlay:,} bytes appended after the image (overlay)")

    return {
        "format": "PE", "arch": MACHINES.get(machine, hex(machine)), "bits": "64-bit" if is64 else "32-bit",
        "kind": "DLL" if chars & 0x2000 else "executable", "subsystem": SUBSYSTEMS.get(subsystem, str(subsystem)),
        "entry_rva": f"{entry:#x}", "hardening": hardening, "notes": notes,
        "sections": [s["name"] for s in sections], "section_table": sections,
        "imports": imports, "version": version, "signed": bool(sig_size), "signers": signers,
        "overlay": max(overlay, 0),
    }


def capabilities(imports: list[dict]) -> list[dict]:
    rows = []
    for label, category, prefixes in CAPABILITIES:
        hits = []
        for imp in imports:
            for fn in imp["functions"]:
                base = fn.rstrip("AW") if fn.endswith(("A", "W")) else fn
                if any(fn.startswith(p) or base == p for p in prefixes):
                    hits.append(f"{imp['dll']}!{fn}")
        if hits:
            rows.append({"capability": label, "category": category, "apis": hits})
    return rows

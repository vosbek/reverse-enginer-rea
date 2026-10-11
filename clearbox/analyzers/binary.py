"""Binary triage: identify formats, parse headers, measure entropy, and pull meaningful strings.

Headers are decoded with `struct` from bytes already read through the
Workspace. Nothing is loaded, mapped, or executed.
"""

from __future__ import annotations

import math
import re
import struct
from collections import Counter

from clearbox.analyzers import pe
from clearbox.core import PARSED, PATTERN, Analyzer, Result, evidence, register, table

ELF_MACHINES = {3: "x86", 8: "MIPS", 20: "PowerPC", 21: "PowerPC64", 40: "ARM", 62: "x86-64", 183: "AArch64",
                243: "RISC-V", 247: "BPF"}
PE_MACHINES = {0x14C: "x86", 0x8664: "x86-64", 0xAA64: "ARM64", 0x1C0: "ARM", 0x1C4: "ARMv7"}
MACHO_CPUS = {7: "x86", 0x01000007: "x86-64", 12: "ARM", 0x0100000C: "ARM64"}
MEDIA = [(b"\x89PNG", "PNG image"), (b"\xff\xd8\xff", "JPEG image"), (b"GIF8", "GIF image"), (b"%PDF", "PDF"),
         (b"wOFF", "WOFF font"), (b"wOF2", "WOFF2 font"), (b"\x00\x01\x00\x00", "TrueType font"),
         (b"RIFF", "RIFF media"), (b"OggS", "Ogg media"), (b"ID3", "MP3 audio")]
UTF16 = re.compile(rb"(?:[\x20-\x7e]\x00){5,}")
INTERESTING = re.compile(
    rb"https?://[\x21-\x7e]{4,200}"                                   # URLs
    rb"|(?:/(?:usr|etc|var|tmp|Library|System|opt)/[\x21-\x7e]{2,120})"  # Unix paths
    rb"|[A-Za-z]:\\\\[\x20-\x7e]{3,120}"                                # Windows paths
    rb"|%[A-Za-z_]{3,30}%[\x20-\x7e]{0,120}"                            # %APPDATA%\...
    rb"|\b(?:HKEY_[A-Z_]+|Software|SOFTWARE)\\\\[\x20-\x7e]{3,160}"           # registry keys
    rb"|(?<![\w-])--?[a-z][a-z0-9]+(?:-[a-z0-9]+)+(?:=[\x21-\x7e]{0,40})?"  # --command-line-flags
    rb"|\b[\w.-]+\.(?:dll|so|dylib|exe|sys)\b"                             # libraries and programs
    rb"|\b(?:[A-Z][a-z]+){2,}(?:Error|Exception|Manager|Service|Controller)\b")


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def parse_elf(b: bytes) -> dict:
    cls = {1: "32-bit", 2: "64-bit"}.get(b[4], "?")
    endian = "<" if b[5] == 1 else ">"
    etype, machine = struct.unpack_from(endian + "HH", b, 16)
    out = {"format": "ELF", "arch": ELF_MACHINES.get(machine, f"machine {machine}"), "bits": cls,
           "kind": {1: "relocatable", 2: "executable", 3: "shared object / PIE", 4: "core dump"}.get(etype, "?")}
    try:
        if b[4] == 2:
            shoff, = struct.unpack_from(endian + "Q", b, 0x28)
            shentsize, shnum, shstrndx = struct.unpack_from(endian + "HHH", b, 0x3A)
            off_fmt, name_at, off_at, size_at = "Q", 0, 0x18, 0x20
        else:
            shoff, = struct.unpack_from(endian + "I", b, 0x20)
            shentsize, shnum, shstrndx = struct.unpack_from(endian + "HHH", b, 0x2E)
            off_fmt, name_at, off_at, size_at = "I", 0, 0x10, 0x14
        if 0 < shnum < 4096 and shoff + shnum * shentsize <= len(b):
            def sh(i):
                base = shoff + i * shentsize
                name, = struct.unpack_from(endian + "I", b, base + name_at)
                off, = struct.unpack_from(endian + off_fmt, b, base + off_at)
                size, = struct.unpack_from(endian + off_fmt, b, base + size_at)
                return name, off, size
            _, stroff, strsize = sh(shstrndx)
            strtab = b[stroff: stroff + strsize]
            names = []
            for i in range(shnum):
                n, _, _ = sh(i)
                end = strtab.find(b"\x00", n)
                if n and end > n:
                    names.append(strtab[n:end].decode("ascii", "replace"))
            out["sections"] = names
            out["notes"] = []
            if ".symtab" not in names:
                out["notes"].append("stripped")
            if ".gnu_debuglink" in names or any(n.startswith(".debug") for n in names):
                out["notes"].append("debug info")
            if "UPX0" in names or "UPX1" in names:
                out["notes"].append("UPX-packed")
    except struct.error:
        out["notes"] = ["truncated headers"]
    return out


def parse_macho(b: bytes) -> dict:
    magic = b[:4]
    if magic in (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"):
        n, = struct.unpack_from(">I", b, 4)
        archs = []
        for i in range(min(n, 8)):
            cpu, = struct.unpack_from(">I", b, 8 + i * 20)
            archs.append(MACHO_CPUS.get(cpu, hex(cpu)))
        return {"format": "Mach-O universal", "arch": " + ".join(archs), "bits": "", "kind": "fat binary"}
    endian = "<" if magic in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe") else ">"
    cpu, _, ftype, ncmds = struct.unpack_from(endian + "IIII", b, 4)
    return {"format": "Mach-O", "arch": MACHO_CPUS.get(cpu, hex(cpu)),
            "bits": "64-bit" if magic in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf") else "32-bit",
            "kind": {1: "object", 2: "executable", 6: "dylib", 8: "bundle"}.get(ftype, f"type {ftype}"),
            "notes": [f"{ncmds} load commands"]}


def identify(head: bytes) -> dict | None:
    if head.startswith(b"\x7fELF") and len(head) >= 64:
        return {"format": "ELF"}
    if head.startswith(b"MZ"):
        return {"format": "PE"}
    if head[:4] in (b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"):
        return {"format": "Mach-O"}
    if head[:4] == b"\xca\xfe\xba\xbe" and len(head) >= 8:
        major, = struct.unpack_from(">H", head, 6)
        return {"format": "Java class" if major >= 45 else "Mach-O"}
    if head.startswith(b"\x00asm"):
        return {"format": "WebAssembly", "notes": [f"version {head[4]}"]}
    if head.startswith(b"PK\x03\x04"):
        return {"format": "ZIP archive (jar/apk/docx/…)"}
    if head.startswith(b"\x1f\x8b"):
        return {"format": "gzip"}
    if head.startswith(b"SQLite format 3"):
        return {"format": "SQLite database"}
    if head.startswith(b"dex\n"):
        return {"format": "Android DEX"}
    for magic, label in MEDIA:
        if head.startswith(magic):
            return {"format": label, "media": True}
    return None


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    rows, strings_rows, pe_rows, import_rows, cap_rows, wide_rows = [], [], [], [], [], []
    formats = Counter()
    for f in ws.files:
        if f.lang is not None and f.lang != "Docker" and not ws.is_binary(f.path):
            continue
        head = ws.sniff(f.path, 4096)
        ident = identify(head)
        if ident is None:
            if not ws.is_binary(f.path):
                continue
            ident = {"format": "unknown binary"}
        formats[ident["format"]] += 1
        if ident.get("media"):
            continue
        data = ws.read_bytes(f.path, ws.limits.max_binary_bytes)
        info = dict(ident)
        if data is not None:
            try:
                if ident["format"] == "ELF":
                    info = parse_elf(data)
                elif ident["format"] == "PE":
                    info = pe.parse(data)
                    if info.get("format") == "PE":
                        ev = [evidence(ws, f.path, None, f"PE {info['arch']} {info['subsystem']}")]
                        v = info["version"]
                        pe_rows.append({"path": f.path, "product": f"{v.get('ProductName', '')} {v.get('ProductVersion', '')}".strip(),
                                        "company": v.get("CompanyName", ""), "description": v.get("FileDescription", ""),
                                        "original": v.get("OriginalFilename", ""), "subsystem": info["subsystem"],
                                        "signed": "yes: " + "; ".join(info["signers"][:4]) if info["signed"] else "no",
                                        "hardening": ", ".join(info["hardening"]) or "none", "_ev": ev})
                        for imp in info["imports"]:
                            import_rows.append({"path": f.path, "dll": imp["dll"], "count": len(imp["functions"]),
                                                "functions": ", ".join(imp["functions"][:14])
                                                + (f" … +{len(imp['functions']) - 14}" if len(imp["functions"]) > 14 else ""),
                                                "_ev": [evidence(ws, f.path, None, f"{imp['dll']}: " + ", ".join(imp["functions"][:40]))]})
                        for cap in pe.capabilities(info["imports"]):
                            cap_rows.append({"path": f.path, "capability": cap["capability"], "count": len(cap["apis"]),
                                             "apis": ", ".join(a.split("!")[1] for a in cap["apis"][:10]),
                                             "_ev": [evidence(ws, f.path, None, a) for a in cap["apis"][:12]]})
                elif ident["format"] == "Mach-O":
                    info = parse_macho(data)
            except struct.error:
                info.setdefault("notes", []).append("malformed headers")
            ent = entropy(data[: 8 * 1024 * 1024])
            if ent > 7.2 and info["format"] not in ("ZIP archive (jar/apk/docx/…)", "gzip"):
                info.setdefault("notes", []).append("high entropy: compressed, encrypted, or packed")
            window = data[: 16 * 1024 * 1024]
            hits = Counter(m.group(0).decode("ascii", "replace") for m in INTERESTING.finditer(window))
            seen_wide = set()
            for m in UTF16.finditer(window):  # Windows binaries keep most text as UTF-16LE
                text_w = m.group(0).decode("utf-16-le", "replace").strip()
                if (text_w not in seen_wide and len(seen_wide) < 300
                        and sum(c.isalpha() for c in text_w) >= 0.6 * len(text_w) and re.search(r"[A-Za-z]{3}", text_w)):
                    seen_wide.add(text_w)
                    wide_rows.append({"file": f.path, "string": text_w, "offset": f"{m.start():#x}",
                                      "_ev": [evidence(ws, f.path, None, f"offset {m.start():#x}: {text_w}")]})
                wide = m.group(0).decode("utf-16-le", "replace").encode("ascii", "replace")
                for w in INTERESTING.finditer(wide):
                    hits[w.group(0).decode("ascii") + "  (UTF-16)"] += 1
            for s, n in hits.most_common(120):
                strings_rows.append({"file": f.path, "string": s, "count": n, "_ev": [evidence(ws, f.path, None, s)]})
        else:
            ent = None
        rows.append({"path": f.path, "format": info.get("format", "?"), "arch": info.get("arch", ""),
                     "kind": info.get("kind", ""), "size": f.size,
                     "entropy": f"{ent:.2f}" if ent is not None else "n/a",
                     "notes": ", ".join(info.get("notes", [])),
                     "sections": ", ".join(info.get("sections", [])[:12]),
                     "_ev": [evidence(ws, f.path, None, f"{info.get('format')} {info.get('arch', '')}".strip())]})
    res.data["binaries"] = rows
    res.views["binary.pe"] = table(
        "Windows executables: identity and signature",
        [("path", "File"), ("product", "Product"), ("company", "Company"), ("description", "Description"),
         ("subsystem", "Subsystem"), ("signed", "Authenticode"), ("hardening", "Hardening")], pe_rows, confidence=PARSED,
        note="From the version resource, the certificate table, and DllCharacteristics. Signer names are read from "
             "the certificates; Clearbox does not validate the signature chain.")
    res.views["binary.imports"] = table(
        "Imported DLLs and functions", [("path", "File"), ("dll", "DLL"), ("count", "Functions"),
                                        ("functions", "Imports")], import_rows, confidence=PARSED, limit=300)
    res.views["binary.capabilities"] = table(
        "What the imports let it do", [("path", "File"), ("capability", "Capability"), ("count", "APIs"),
                                       ("apis", "Imported functions")], cap_rows, confidence=PARSED,
        note="Derived from the import table. Functions resolved at runtime with GetProcAddress do not appear here.")
    res.views["binary.files"] = table(
        "Binaries and opaque files",
        [("path", "File"), ("format", "Format"), ("arch", "Arch"), ("kind", "Kind"), ("size", "Bytes"),
         ("entropy", "Entropy"), ("notes", "Notes")], rows, confidence=PARSED,
        note="Entropy is bits per byte (0 to 8). Above 7.2 usually means compressed or encrypted content.")
    res.views["binary.sections"] = table("Section tables", [("path", "File"), ("sections", "Sections")],
                                         [r for r in rows if r["sections"]], confidence=PARSED)
    res.views["binary.strings"] = table(
        "Meaningful strings inside binaries", [("file", "File"), ("string", "String"), ("count", "Count")],
        strings_rows, confidence=PATTERN, limit=200,
        note="URLs, absolute paths, library names, and type-like identifiers. Strings are data from the target.")
    res.views["binary.wide_strings"] = table(
        "Readable UTF-16 strings", [("file", "File"), ("offset", "Offset"), ("string", "String")], wide_rows,
        confidence=PARSED, limit=300,
        note="Windows programs store user-facing text, object names, and identifiers as UTF-16. Mostly-letter "
             "strings only; offsets are file offsets.")
    res.views["binary.formats"] = table("Opaque file formats", [("format", "Format"), ("count", "Files")],
                                        [{"format": k, "count": v} for k, v in formats.most_common()])
    if rows:
        res.blind_spots.append("Binary triage reads headers and strings only. Control flow, decompilation, and runtime "
                               "behavior need a disassembler (Ghidra, IDA, Hopper) in an isolated environment.")
    return res


register(Analyzer("binary", "Format identification, headers, entropy, and strings for binaries.", run,
                  requires=("inventory",),
                  views=("binary.files", "binary.sections", "binary.strings", "binary.formats", "binary.pe",
                         "binary.imports", "binary.capabilities", "binary.wide_strings")))

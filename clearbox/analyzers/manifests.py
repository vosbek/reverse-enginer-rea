"""Declared dependencies, entry points, and install-time hooks from package manifests."""

from __future__ import annotations

import json
import re
import tomllib

from clearbox.core import PARSED, Analyzer, Finding, Result, evidence, register, stats, table

INSTALL_HOOKS = ("preinstall", "install", "postinstall", "prepare")
MANIFEST_NAMES = {"package.json", "pyproject.toml", "go.mod", "Cargo.toml", "composer.json", "Gemfile",
                  "pom.xml", "build.gradle", "build.gradle.kts"}
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock", "go.sum",
             "uv.lock", "Gemfile.lock", "composer.lock"}


def _line_of_key(ws, path: str, text: str, key: str) -> int | None:
    m = re.search(r'["\']?' + re.escape(key) + r'["\']?\s*[:=]', text)
    if m is None:
        idx = text.find(key)
        return ws.line_of(path, idx) if idx >= 0 else None
    return ws.line_of(path, m.start())


def _req_name(spec: str) -> tuple[str, str]:
    m = re.match(r"\s*([A-Za-z0-9_.\-\[\]]+)\s*(.*)", spec)
    if not m:
        return spec.strip(), ""
    return re.sub(r"\[.*\]", "", m.group(1)), m.group(2).split(";")[0].strip()


def parse_package_json(ws, path, text, deps, entries, hooks, notes):
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        notes.append(f"{path}: invalid JSON ({exc.msg}).")
        return
    if not isinstance(doc, dict):
        return
    for field, kind in (("dependencies", "runtime"), ("devDependencies", "dev"),
                        ("peerDependencies", "peer"), ("optionalDependencies", "optional")):
        for name, spec in (doc.get(field) or {}).items():
            deps.append({"eco": "npm", "name": name, "spec": str(spec), "kind": kind, "manifest": path,
                         "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})
    bins = doc.get("bin")
    if isinstance(bins, str):
        bins = {doc.get("name", "bin"): bins}
    for name, target in (bins or {}).items():
        entries.append({"kind": "bin", "name": name, "target": target, "manifest": path,
                        "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})
    for field in ("main", "module", "browser"):
        if isinstance(doc.get(field), str):
            entries.append({"kind": field, "name": doc.get("name", ""), "target": doc[field], "manifest": path,
                            "_ev": [evidence(ws, path, _line_of_key(ws, path, text, field))]})
    for name, cmd in (doc.get("scripts") or {}).items():
        if name in INSTALL_HOOKS:
            hooks.append({"name": name, "command": str(cmd), "manifest": path,
                          "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})


def parse_pyproject(ws, path, text, deps, entries, notes):
    try:
        doc = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        notes.append(f"{path}: invalid TOML ({exc}).")
        return
    project = doc.get("project", {})
    for spec in project.get("dependencies", []):
        name, version = _req_name(spec)
        deps.append({"eco": "pypi", "name": name, "spec": version, "kind": "runtime", "manifest": path,
                     "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})
    for group, specs in (project.get("optional-dependencies") or {}).items():
        for spec in specs:
            name, version = _req_name(spec)
            deps.append({"eco": "pypi", "name": name, "spec": version, "kind": f"extra:{group}",
                         "manifest": path, "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})
    poetry = doc.get("tool", {}).get("poetry", {})
    for name, spec in (poetry.get("dependencies") or {}).items():
        if name != "python":
            deps.append({"eco": "pypi", "name": name, "spec": str(spec), "kind": "runtime", "manifest": path,
                         "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})
    for name, target in (project.get("scripts") or {}).items():
        entries.append({"kind": "script", "name": name, "target": target, "manifest": path,
                        "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})


def parse_cargo(ws, path, text, deps, entries, notes):
    try:
        doc = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        notes.append(f"{path}: invalid TOML ({exc}).")
        return
    for field, kind in (("dependencies", "runtime"), ("dev-dependencies", "dev"), ("build-dependencies", "build")):
        for name, spec in (doc.get(field) or {}).items():
            version = spec if isinstance(spec, str) else (spec.get("version", "") if isinstance(spec, dict) else "")
            deps.append({"eco": "crates", "name": name, "spec": version, "kind": kind, "manifest": path,
                         "_ev": [evidence(ws, path, _line_of_key(ws, path, text, name))]})
    for b in doc.get("bin", []) or []:
        entries.append({"kind": "bin", "name": b.get("name", ""), "target": b.get("path", ""), "manifest": path,
                        "_ev": [evidence(ws, path, _line_of_key(ws, path, text, "[[bin]]"))]})


def parse_requirements(ws, path, text, deps):
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name, version = _req_name(line)
        deps.append({"eco": "pypi", "name": name, "spec": version, "kind": "runtime", "manifest": path,
                     "_ev": [evidence(ws, path, i)]})


def parse_go_mod(ws, path, text, deps):
    block = False
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.split("//", 1)[0].strip()
        if line.startswith("require ("):
            block = True
            continue
        if block and line == ")":
            block = False
            continue
        m = re.match(r"(?:require\s+)?([\w./\-~]+)\s+(v[\w.\-+]+)", line) if (block or line.startswith("require ")) else None
        if m:
            kind = "indirect" if "// indirect" in raw else "runtime"
            deps.append({"eco": "go", "name": m.group(1), "spec": m.group(2), "kind": kind, "manifest": path,
                         "_ev": [evidence(ws, path, i)]})


def count_lock_entries(name: str, text: str) -> int:
    if name == "package-lock.json":
        try:
            doc = json.loads(text)
        except json.JSONDecodeError:
            return 0
        pkgs = doc.get("packages") or doc.get("dependencies") or {}
        return len([k for k in pkgs if k])
    if name == "yarn.lock":
        return len(re.findall(r"^\"?[^\s#][^\n]*:\s*$", text, re.M))
    if name in ("Cargo.lock", "poetry.lock", "uv.lock"):
        return text.count("[[package]]")
    if name == "go.sum":
        return len({line.split()[0] for line in text.splitlines() if line.strip()})
    if name == "pnpm-lock.yaml":
        return len(re.findall(r"^  /?['\"]?[@\w][^\n]*:\s*$", text, re.M))
    return len(re.findall(r"^\s{4}\S", text, re.M))


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    deps, entries, hooks, notes, locks = [], [], [], [], []
    for f in ws.files:
        name = f.path.rsplit("/", 1)[-1]
        in_fixture = f.is_test
        if name in LOCKFILES:
            text = ws.read_text(f.path)
            if text is not None:
                locks.append({"path": f.path, "packages": count_lock_entries(name, text),
                              "_ev": [evidence(ws, f.path, 1)]})
            continue
        is_req = name.startswith("requirements") and name.endswith(".txt")
        if (name not in MANIFEST_NAMES and not is_req) or in_fixture:
            continue
        text = ws.read_text(f.path)
        if text is None:
            continue
        if name == "package.json":
            parse_package_json(ws, f.path, text, deps, entries, hooks, notes)
        elif name == "pyproject.toml":
            parse_pyproject(ws, f.path, text, deps, entries, notes)
        elif name == "Cargo.toml":
            parse_cargo(ws, f.path, text, deps, entries, notes)
        elif name == "go.mod":
            parse_go_mod(ws, f.path, text, deps)
        elif is_req:
            parse_requirements(ws, f.path, text, deps)
        else:
            notes.append(f"{f.path}: {name} is recognized but its dependencies are not parsed yet.")

    for h in hooks:
        res.findings.append(Finding(
            "install-hook", f"`{h['name']}` script runs code at install time", "medium", PARSED, "supply-chain",
            f"Installing this package runs: {h['command']}", h["_ev"]))

    runtime = [d for d in deps if d["kind"] == "runtime"]
    dev = [d for d in deps if d["kind"] == "dev"]
    res.data.update(deps=deps, entries=entries, hooks=hooks, locks=locks)
    lock_total = sum(lk["packages"] for lk in locks)
    res.views["manifests.stats"] = stats("Declared dependencies", [
        ("Runtime", len(runtime), "declared direct dependencies"),
        ("Development", len(dev), "build, lint, and test tooling"),
        ("Locked packages", lock_total, f"in {len(locks)} lockfile(s)" if locks else "no lockfile found"),
        ("Install hooks", len(hooks), ", ".join(h["name"] for h in hooks) or "none"),
    ])
    res.views["manifests.dependencies"] = table(
        "Declared dependencies",
        [("name", "Package"), ("spec", "Version"), ("kind", "Kind"), ("eco", "Ecosystem"), ("manifest", "Manifest")],
        sorted(deps, key=lambda d: (d["kind"] != "runtime", d["kind"], d["name"])), limit=300)
    res.views["manifests.entrypoints"] = table(
        "Declared entry points", [("kind", "Kind"), ("name", "Name"), ("target", "Target"), ("manifest", "Manifest")],
        entries)
    res.views["manifests.install_hooks"] = table(
        "Install-time scripts", [("name", "Hook"), ("command", "Command"), ("manifest", "Manifest")], hooks,
        note="These run automatically during `npm install` (or `npm install` of a git checkout for `prepare`).")
    res.views["manifests.locks"] = table("Lockfiles", [("path", "Lockfile"), ("packages", "Packages")], locks)
    res.blind_spots.extend(notes)
    return res


register(Analyzer("manifests", "Declared dependencies, entry points, install hooks.", run,
                  requires=("inventory",),
                  views=("manifests.stats", "manifests.dependencies", "manifests.entrypoints",
                         "manifests.install_hooks", "manifests.locks")))


"""The module graph: who imports whom, which packages are really used, and where the cycles are."""

from __future__ import annotations

import ast
import posixpath
import re
import sys
from collections import Counter, defaultdict

from clearbox.core import HEURISTIC, PATTERN, Analyzer, Result, evidence, matrix, register, stats, table

JS_LANGS = {"JavaScript", "TypeScript", "Vue", "Svelte"}
JS_STATIC = re.compile(r"""(?:^|[;\s}])(?:import|export)\s+(?:[^;"'()=`]{0,1500}?\bfrom\s*)?["']([^"'\n]+)["']""")
JS_CALL = re.compile(r"""\b(?:require|import)\(\s*["']([^"'\n]+)["']\s*\)""")
JS_DYNAMIC = re.compile(r"""\b(?:require|import)\(\s*(?!["'\s)])[^)]""")
GO_IMPORT = re.compile(r"""^\s*(?:import\s+)?(?:[\w.]+\s+)?"([^"]+)"\s*$""", re.M)
JS_EXTS = (".ts", ".tsx", ".mts", ".cts", ".js", ".mjs", ".cjs", ".jsx", ".vue", ".svelte", ".json")
BUILD_DIRS = {"dist", "build", "out", "lib", "esm", "cjs"}
NODE_BUILTINS = {
    "assert", "async_hooks", "buffer", "child_process", "cluster", "console", "crypto", "dgram", "dns",
    "events", "fs", "http", "http2", "https", "inspector", "module", "net", "os", "path", "perf_hooks",
    "process", "querystring", "readline", "repl", "stream", "string_decoder", "timers", "tls", "tty",
    "url", "util", "v8", "vm", "worker_threads", "zlib", "test", "sqlite",
}
PY_STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}


def _js_package(spec: str) -> str:
    if spec.startswith("node:"):
        return spec
    parts = spec.split("/")
    name = "/".join(parts[:2]) if spec.startswith("@") else parts[0]
    return f"node:{name}" if name in NODE_BUILTINS else name


class Resolver:
    def __init__(self, ws) -> None:
        self.paths = set(ws.by_path)
        self.py_modules: dict[str, str] = {}
        for p in self.paths:
            if p.endswith(".py"):
                mod = p[:-3].replace("/", ".")
                if mod.endswith(".__init__"):
                    mod = mod[: -len(".__init__")]
                self.py_modules.setdefault(mod, p)
                head, _, rest = mod.partition(".")
                if head in ("src", "lib", "python") and rest:
                    self.py_modules.setdefault(rest, p)
        self.via_build = 0
        self.go_module: str | None = None
        self.go_dirs: dict[str, list[str]] = defaultdict(list)
        for p in self.paths:
            if p.endswith(".go") and not p.endswith("_test.go"):
                self.go_dirs[posixpath.dirname(p)].append(p)

    def js(self, src: str, spec: str) -> str | None:
        if not spec.startswith("."):
            return None
        base = posixpath.normpath(posixpath.join(posixpath.dirname(src), spec))
        hit = self._js_candidates(base)
        if hit is None:
            # Compiled-output imports (../dist/x.js) usually mirror a source tree (src/x.ts).
            parts = base.split("/")
            for i, part in enumerate(parts):
                if part in BUILD_DIRS:
                    hit = self._js_candidates("/".join(parts[:i] + ["src"] + parts[i + 1:]))
                    if hit:
                        self.via_build += 1
                    break
        return hit

    def _js_candidates(self, base: str) -> str | None:
        stem, ext = posixpath.splitext(base)
        candidates = [base]
        if ext in (".js", ".mjs", ".cjs", ".jsx"):
            candidates += [stem + e for e in (".ts", ".tsx", ".mts", ".cts")]
        candidates += [base + e for e in JS_EXTS]
        candidates += [base + "/index" + e for e in JS_EXTS]
        for c in candidates:
            if c in self.paths:
                return c
        return None

    def py(self, src: str, module: str | None, level: int, names: list[str]) -> list[str]:
        if level:
            pkg = posixpath.dirname(src).split("/") if posixpath.dirname(src) else []
            if level > 1:
                pkg = pkg[: len(pkg) - (level - 1)] if level - 1 <= len(pkg) else []
            base = ".".join(pkg)
            full = ".".join(x for x in (base, module) if x)
            targets = []
            for n in names:
                hit = self.py_modules.get(f"{full}.{n}" if full else n)
                if hit:
                    targets.append(hit)
            if not targets:
                hit = self._py_lookup(full)
                if hit:
                    targets.append(hit)
            return targets
        hit = self._py_lookup(module or "")
        if hit is None and module:
            # Script-style import of a sibling module (python tools/report.py with tools/helpers.py).
            here = posixpath.dirname(src)
            rel = module.replace(".", "/")
            for cand in (f"{here}/{rel}.py", f"{here}/{rel}/__init__.py"):
                cand = cand.lstrip("/")
                if cand in self.paths:
                    hit = cand
                    break
        return [hit] if hit else []

    def _py_lookup(self, module: str) -> str | None:
        parts = module.split(".")
        for i in range(len(parts), 0, -1):
            hit = self.py_modules.get(".".join(parts[:i]))
            if hit:
                return hit
        return None


def tarjan(nodes, graph) -> list[list[str]]:
    index, low, on_stack, stack, out = {}, {}, set(), [], []
    counter = 0
    for start in nodes:
        if start in index:
            continue
        work = [(start, iter(sorted(graph.get(start, ()))))]
        index[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        while work:
            node, it = work[-1]
            advanced = False
            for nxt in it:
                if nxt not in index:
                    index[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack.add(nxt)
                    work.append((nxt, iter(sorted(graph.get(nxt, ())))))
                    advanced = True
                    break
                if nxt in on_stack:
                    low[node] = min(low[node], index[nxt])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == node:
                        break
                if len(comp) > 1:
                    out.append(sorted(comp))
    return out


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    resolver = Resolver(ws)
    for f in ws.files:
        if f.path.endswith("go.mod"):
            text = ws.read_text(f.path) or ""
            m = re.search(r"^module\s+(\S+)", text, re.M)
            if m and resolver.go_module is None:
                resolver.go_module = m.group(1)

    graph: dict[str, set[str]] = defaultdict(set)
    edge_ev: dict[tuple[str, str], int] = {}
    external: dict[str, dict[str, int]] = defaultdict(dict)  # package -> {file: line}
    unresolved: list[tuple[str, int, str]] = []
    dynamic: list[tuple[str, int]] = []
    parse_errors: list[str] = []

    def add_internal(src: str, dst: str, line: int) -> None:
        if dst != src:
            graph[src].add(dst)
            edge_ev.setdefault((src, dst), line)

    for f in ws.files:
        if f.lang not in JS_LANGS and f.lang not in ("Python", "Go"):
            continue
        text = ws.read_text(f.path)
        if text is None:
            continue
        if f.lang in JS_LANGS:
            for rx in (JS_STATIC, JS_CALL):
                for m in rx.finditer(text):
                    spec = m.group(1)
                    line = ws.line_of(f.path, m.start(1))
                    if spec.startswith("."):
                        target = resolver.js(f.path, spec)
                        if target:
                            add_internal(f.path, target, line)
                        else:
                            unresolved.append((f.path, line, spec))
                    elif spec.startswith("#") or spec.startswith("/") or spec.startswith("~"):
                        unresolved.append((f.path, line, spec))
                    elif re.match(r"^[@\w]", spec):
                        external[_js_package(spec)].setdefault(f.path, line)
            for m in JS_DYNAMIC.finditer(text):
                dynamic.append((f.path, ws.line_of(f.path, m.start())))
        elif f.lang == "Python":
            try:
                tree = ast.parse(text, filename=f.path)
            except (SyntaxError, ValueError):
                parse_errors.append(f.path)
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        targets = resolver.py(f.path, alias.name, 0, [])
                        for t in targets:
                            add_internal(f.path, t, node.lineno)
                        if not targets:
                            top = alias.name.split(".")[0]
                            pkg = f"stdlib:{top}" if top in PY_STDLIB else top
                            external[pkg].setdefault(f.path, node.lineno)
                elif isinstance(node, ast.ImportFrom):
                    names = [a.name for a in node.names]
                    targets = resolver.py(f.path, node.module, node.level, names)
                    for t in targets:
                        add_internal(f.path, t, node.lineno)
                    if not targets:
                        if node.level:
                            unresolved.append((f.path, node.lineno, "." * node.level + (node.module or "")))
                        else:
                            top = (node.module or "").split(".")[0]
                            pkg = f"stdlib:{top}" if top in PY_STDLIB else top
                            external[pkg].setdefault(f.path, node.lineno)
                elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                      and node.func.id == "__import__") or (
                        isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "import_module"):
                    dynamic.append((f.path, node.lineno))
        else:  # Go
            blocks = re.findall(r"import\s*\(([^)]*)\)", text) + re.findall(r'import\s+((?:\w+\s+)?"[^"]+")', text)
            for block in blocks:
                for m in GO_IMPORT.finditer(block):
                    spec = m.group(1)
                    idx = text.find(f'"{spec}"')
                    line = ws.line_of(f.path, idx) if idx >= 0 else None
                    mod = resolver.go_module
                    if mod and spec.startswith(mod):
                        rel = spec[len(mod):].lstrip("/")
                        for target in resolver.go_dirs.get(rel, []):
                            add_internal(f.path, target, line or 1)
                    elif "." not in spec.split("/")[0]:
                        external[f"go:{spec}"].setdefault(f.path, line or 1)
                    else:
                        external[spec].setdefault(f.path, line or 1)

    rgraph: dict[str, set[str]] = defaultdict(set)
    for src, dsts in graph.items():
        for d in dsts:
            rgraph[d].add(src)
    res.data.update(graph=graph, rgraph=rgraph, external=external, edge_line=edge_ev)

    nodes = sorted(set(graph) | set(rgraph))
    cycles = sorted(tarjan(nodes, graph), key=len, reverse=True)
    edges = sum(len(v) for v in graph.values())

    # -- views ---------------------------------------------------------------
    third_party = {k: v for k, v in external.items() if not k.startswith(("node:", "stdlib:", "go:"))}
    res.views["imports.stats"] = stats("Module graph", [
        ("Import edges", edges, f"between {len(nodes):,} source files"),
        ("Third-party packages", len(third_party), "actually imported somewhere"),
        ("Platform modules", len(external) - len(third_party), "Node builtins, Python stdlib, Go std"),
        ("Import cycles", len(cycles), f"largest spans {len(cycles[0])} files" if cycles else "none found"),
        ("Unresolved", len(unresolved), "relative or aliased imports with no file"),
    ])

    area_of = ctx.data("inventory")["area_of"]
    is_test = {f.path: f.is_test for f in ws.files}
    test_heavy = {a for a in ctx.data("inventory")["areas"]
                  if all(is_test.get(p) for p, ar in area_of.items() if ar == a and p in graph)}
    areas = [a for a in ctx.data("inventory")["areas"] if a not in test_heavy][:14]
    pos = {a: i for i, a in enumerate(areas)}
    cells = [[0] * len(areas) for _ in areas]
    for src, dsts in graph.items():
        a = pos.get(area_of.get(src))
        if a is None or is_test.get(src):
            continue
        for d in dsts:
            b = pos.get(area_of.get(d))
            if b is not None:
                cells[a][b] += 1
    res.views["imports.matrix"] = matrix(
        "Who imports whom (by area)", areas, cells,
        note="Row imports column. Counts are file-to-file import edges from non-test code. The diagonal is internal cohesion.")

    hubs = sorted(rgraph.items(), key=lambda kv: -len([s for s in kv[1] if not is_test.get(s)]))[:25]
    res.views["imports.hubs"] = table(
        "Load-bearing files (most imported)",
        [("path", "File"), ("fan_in", "Imported by"), ("fan_out", "Imports"), ("area", "Area")],
        [{"path": p, "fan_in": len([s for s in srcs if not is_test.get(s)]), "fan_out": len(graph.get(p, ())),
          "area": area_of.get(p, ""), "_ev": [evidence(ws, p, 1, "")]} for p, srcs in hubs if srcs],
        note="Fan-in counts non-test importers. Changing a hub ripples widely; rebuilding one first unblocks the most.")

    ext_rows = []
    for pkg, users in sorted(external.items(), key=lambda kv: -len(kv[1])):
        prod = [p for p in users if not is_test.get(p)]
        first = sorted(users.items())[0]
        ext_rows.append({"package": pkg, "files": len(prod), "test_files": len(users) - len(prod),
                         "_ev": [evidence(ws, first[0], first[1])]})
    res.views["imports.external"] = table(
        "External packages by reach", [("package", "Package"), ("files", "Files importing"),
                                       ("test_files", "Test files")], ext_rows, limit=60, confidence=PATTERN,
        note="Reach is how many non-test files import the package. node:, stdlib:, and go: are platform modules.")

    res.views["imports.cycles"] = table(
        "Import cycles", [("size", "Files"), ("members", "Members")],
        [{"size": len(c), "members": ", ".join(c[:6]) + (f" … +{len(c) - 6}" if len(c) > 6 else ""),
          "_ev": [evidence(ws, c[0], edge_ev.get((c[0], min(graph[c[0]] & set(c))), 1))]}
         for c in cycles], limit=30,
        note="Strongly connected components of the import graph. Cycles make pieces hard to lift out on their own.")

    # Cross-check declared vs. used
    declared = {}
    for d in ctx.data("manifests")["deps"]:
        declared[_norm(d["name"])] = d
    imported_norm = {_norm(k): k for k in third_party}
    undeclared = []
    for norm, pkg in sorted(imported_norm.items()):
        if norm in declared or pkg.startswith("@types/"):
            continue
        users = external[pkg]
        prod = [p for p in users if not is_test.get(p)]
        if not prod:
            continue
        first = sorted((p, ln) for p, ln in users.items() if p in prod)[0]
        undeclared.append({"package": pkg, "files": len(prod), "_ev": [evidence(ws, first[0], first[1])]})
    unused = []
    for norm, d in sorted(declared.items()):
        if d["kind"] != "runtime" or norm in imported_norm or d["name"].startswith("@types/"):
            continue
        unused.append({"package": d["name"], "spec": d["spec"], "manifest": d["manifest"], "_ev": d["_ev"]})
    res.views["imports.undeclared"] = table(
        "Imported but not declared", [("package", "Package"), ("files", "Files")], undeclared, confidence=HEURISTIC,
        note="May be workspace packages, path aliases, or Python import names that differ from their distribution name.")
    res.views["imports.unused_declared"] = table(
        "Declared but never imported", [("package", "Package"), ("spec", "Version"), ("manifest", "Manifest")],
        unused, confidence=HEURISTIC,
        note="Runtime dependencies no source file imports. They may still be used by CLIs, config files, or types.")

    if dynamic:
        ex = ", ".join(f"{p}:{ln}" for p, ln in dynamic[:3])
        res.blind_spots.append(f"{len(dynamic)} dynamic imports use computed module names and could not be followed (e.g. {ex}).")
    if unresolved:
        aliases = sum(1 for _, _, s in unresolved if s[:1] in "#~/")
        res.blind_spots.append(
            f"{len(unresolved)} imports did not resolve to a file ({aliases} use path aliases or package import maps).")
    if resolver.via_build:
        res.blind_spots.append(f"{resolver.via_build} imports point at build output (dist/, build/); they were mapped "
                               "to the matching file under src/ by path, which assumes the usual one-to-one layout.")
    if parse_errors:
        res.blind_spots.append(f"{len(parse_errors)} Python files failed to parse (e.g. {parse_errors[0]}).")
    return res


def _norm(name: str) -> str:
    return name.lower().replace("_", "-")


register(Analyzer("imports", "Module graph, external package reach, cycles, declared-vs-used.", run,
                  requires=("inventory", "manifests"),
                  views=("imports.stats", "imports.matrix", "imports.hubs", "imports.external", "imports.cycles",
                         "imports.undeclared", "imports.unused_declared")))

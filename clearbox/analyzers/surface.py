"""How you get into the target: entry points, HTTP routes, CLI commands, agent tools, and configuration."""

from __future__ import annotations

import posixpath
import re
from collections import defaultdict

from clearbox.core import PATTERN, Analyzer, Result, evidence, register, table

ROUTE_PATTERNS = [
    ("express/koa/fastify", re.compile(
        r"""\b(?:app|router|server|api|fastify|r)\.(get|post|put|patch|delete|all|route)\(\s*["'`](/[^"'`]*)["'`]""")),
    ("flask/fastapi", re.compile(
        r"""@\w+\.(get|post|put|patch|delete|route|api_route)\(\s*["'](/[^"']*)["']""")),
    ("go net/http", re.compile(r"""\b(?:http|mux|r|router)\.(HandleFunc|Handle|Get|Post|Put|Delete)\(\s*"(/[^"]*)""")),
    ("django", re.compile(r"""\b(re_)?path\(\s*r?["']([^"']*)["']\s*,""")),
]
CLI_PATTERNS = [
    ("commander/yargs", re.compile(r"""\.command\(\s*["'`]([\w:-]+)""")),
    ("argparse", re.compile(r"""\.add_parser\(\s*["']([\w-]+)["']""")),
    ("click/typer", re.compile(r"""@\w+\.command\(\s*(?:name\s*=\s*)?["']([\w-]+)["']""")),
    ("cobra", re.compile(r"""\bUse:\s*"([\w-]+)""")),
]
TOOL_PATTERNS = [
    ("MCP registerTool", re.compile(r"""\.registerTool\(\s*["'`]([\w.-]+)["'`]""")),
    ("MCP server.tool", re.compile(r"""\b(?:server|mcp)\.tool\(\s*["'`]([\w.-]+)["'`]""")),
    ("MCP tool contract", re.compile(r"""\btoolContract\(\s*["'`]([\w.-]+)["'`]""")),
    ("MCP decorator", re.compile(r"""@\w+\.tool\((?:[^)]*name\s*=\s*["']([\w.-]+)["'])?""")),
    ("tool definition", re.compile(r"""\{\s*name:\s*["'`]([a-z][\w-]*)["'`],\s*description:""")),
]
ENV_PATTERNS = [
    re.compile(r"""process\.env\.([A-Z][A-Z0-9_]{2,})"""),
    re.compile(r"""process\.env\[\s*["'`]([A-Z][A-Z0-9_]{2,})["'`]\s*\]"""),
    re.compile(r"""\benv(?:ironment)?\s*\[\s*["'`]([A-Z][A-Z0-9_]{2,})["'`]\s*\]"""),
    re.compile(r"""\benv(?:ironment)?\.([A-Z][A-Z0-9_]{3,})\b"""),
    re.compile(r"""os\.environ(?:\.get)?[\[(]\s*["']([A-Z][A-Z0-9_]{2,})["']"""),
    re.compile(r"""os\.getenv\(\s*["']([A-Z][A-Z0-9_]{2,})["']"""),
    re.compile(r"""os\.(?:Getenv|LookupEnv)\(\s*"([A-Z][A-Z0-9_]{2,})"""),
    re.compile(r"""env::var\(\s*"([A-Z][A-Z0-9_]{2,})"""),
]
ENTRY_NAMES = {"main", "cli", "index", "server", "app", "__main__", "manage", "wsgi", "asgi"}


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    routes, commands, tools = [], [], {}
    env: dict[str, dict] = {}
    entries = []

    for e in ctx.data("manifests")["entries"]:
        entries.append({"kind": f"manifest {e['kind']}", "name": e["name"], "target": e["target"], "_ev": e["_ev"]})

    for f in ws.files:
        if not f.is_code or f.is_test:
            continue
        text = ws.read_text(f.path)
        if text is None:
            continue
        stem = posixpath.splitext(posixpath.basename(f.path))[0]
        depth = f.path.count("/")
        if 'if __name__ == "__main__"' in text or "if __name__ == '__main__'" in text:
            idx = text.find("__name__ ==")
            entries.append({"kind": "python __main__", "name": stem, "target": f.path,
                            "_ev": [evidence(ws, f.path, ws.line_of(f.path, idx))]})
        elif f.lang == "Go" and "func main()" in text:
            idx = text.find("func main()")
            entries.append({"kind": "go main", "name": stem, "target": f.path,
                            "_ev": [evidence(ws, f.path, ws.line_of(f.path, idx))]})
        elif stem in ENTRY_NAMES and depth <= 2:
            entries.append({"kind": "conventional name", "name": stem, "target": f.path,
                            "_ev": [evidence(ws, f.path, 1, "")]})
        for label, rx in ROUTE_PATTERNS:
            if label == "django" and f.lang != "Python":
                continue
            for m in rx.finditer(text):
                method = (m.group(1) or "path").upper()
                routes.append({"method": method, "route": m.group(2), "framework": label, "file": f.path,
                               "_ev": [evidence(ws, f.path, ws.line_of(f.path, m.start()))]})
        for label, rx in CLI_PATTERNS:
            for m in rx.finditer(text):
                commands.append({"command": m.group(1), "via": label, "file": f.path,
                                 "_ev": [evidence(ws, f.path, ws.line_of(f.path, m.start()))]})
        for label, rx in TOOL_PATTERNS:
            for m in rx.finditer(text):
                name = m.group(1)
                if not name and label == "MCP decorator":
                    after = re.search(r"def\s+(\w+)", text[m.end(): m.end() + 400])
                    name = after.group(1) if after else None
                if not name or name in tools:
                    continue
                tools[name] = {"tool": name, "via": label, "file": f.path,
                               "_ev": [evidence(ws, f.path, ws.line_of(f.path, m.start(1) if m.group(1) else m.start()))]}
        for rx in ENV_PATTERNS:
            for m in rx.finditer(text):
                name = m.group(1)
                rec = env.setdefault(name, {"var": name, "files": set(), "_ev": []})
                rec["files"].add(f.path)
                line = ws.line_of(f.path, m.start())
                if len(rec["_ev"]) < 3 and not any(e["path"] == f.path and e["line"] == line for e in rec["_ev"]):
                    rec["_ev"].append(evidence(ws, f.path, ws.line_of(f.path, m.start())))

    env_rows = []
    for rec in sorted(env.values(), key=lambda r: (-len(r["files"]), r["var"])):
        env_rows.append({"var": rec["var"], "files": len(rec["files"]), "_ev": rec["_ev"]})

    tool_rows = sorted(tools.values(), key=lambda r: r["tool"])
    res.data.update(entries=entries, routes=routes, commands=commands, tools=tool_rows, env=env,
                    entry_files=sorted({e["target"] for e in entries if e["target"] in ws.by_path}))
    res.views["surface.entrypoints"] = table(
        "Entry points", [("kind", "Kind"), ("name", "Name"), ("target", "Target")], entries, confidence=PATTERN)
    res.views["surface.routes"] = table(
        "HTTP routes", [("method", "Method"), ("route", "Route"), ("framework", "Framework"), ("file", "File")],
        routes, confidence=PATTERN)
    res.views["surface.cli"] = table(
        "CLI commands", [("command", "Command"), ("via", "Declared via"), ("file", "File")],
        _dedupe(commands, "command"), confidence=PATTERN,
        note="Only commands declared with a literal name are found; names held in constants are not.")
    res.views["surface.tools"] = table(
        "Agent / MCP tools", [("tool", "Tool"), ("via", "Declared via"), ("file", "File")], tool_rows,
        confidence=PATTERN, limit=300)
    res.views["surface.env"] = table(
        "Environment variables read", [("var", "Variable"), ("files", "Files")], env_rows, confidence=PATTERN,
        limit=150, note="Configuration that changes behavior without changing code.")
    return res


def _dedupe(rows: list[dict], key: str) -> list[dict]:
    seen = defaultdict(int)
    out = []
    for r in rows:
        seen[r[key]] += 1
        if seen[r[key]] == 1:
            out.append(r)
    return out


register(Analyzer("surface", "Entry points, routes, CLI commands, agent tools, environment variables.", run,
                  requires=("inventory", "manifests"),
                  views=("surface.entrypoints", "surface.routes", "surface.cli", "surface.tools", "surface.env")))

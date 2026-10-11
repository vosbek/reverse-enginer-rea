"""Named things each file defines: functions, classes, types, exported constants."""

from __future__ import annotations

import ast
import re
from collections import Counter

from clearbox.core import Analyzer, Result, register, stats

JS_DECL = re.compile(
    r"^[ \t]*(export\s+)?(?:default\s+)?(?:declare\s+)?(?:abstract\s+)?(?:async\s+)?"
    r"(function\*?|class|interface|type|enum|const|let|var)\s+([A-Za-z_$][\w$]*)", re.M)
GO_DECL = re.compile(r"^(?:func\s+(?:\([^)]*\)\s*)?|type\s+)([A-Za-z_]\w*)", re.M)
KIND = {"function": "function", "function*": "function", "class": "class", "interface": "type", "type": "type",
        "enum": "type", "const": "value", "let": "value", "var": "value"}


def python_symbols(text: str, path: str) -> list[dict]:
    try:
        tree = ast.parse(text, filename=path)
    except (SyntaxError, ValueError):
        return []
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            doc = (ast.get_docstring(node) or "").strip().split("\n")[0]
            out.append({"name": node.name, "kind": kind, "line": node.lineno,
                        "exported": not node.name.startswith("_"), "doc": doc[:140]})
            if isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and not sub.name.startswith("_"):
                        out.append({"name": f"{node.name}.{sub.name}", "kind": "method", "line": sub.lineno,
                                    "exported": False, "doc": ""})
    return out


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    by_file: dict[str, list[dict]] = {}
    kinds: Counter = Counter()
    for f in ws.files:
        if not f.is_code:
            continue
        text = ws.read_text(f.path)
        if text is None:
            continue
        if f.lang == "Python":
            syms = python_symbols(text, f.path)
        elif f.lang in ("JavaScript", "TypeScript"):
            syms = [{"name": m.group(3), "kind": KIND[m.group(2)], "line": ws.line_of(f.path, m.start(3)),
                     "exported": bool(m.group(1)), "doc": ""} for m in JS_DECL.finditer(text)]
        elif f.lang == "Go":
            syms = [{"name": m.group(1), "kind": "function" if m.group(0).startswith("func") else "type",
                     "line": ws.line_of(f.path, m.start(1)), "exported": m.group(1)[:1].isupper(), "doc": ""}
                    for m in GO_DECL.finditer(text)]
        else:
            continue
        by_file[f.path] = syms
        for s in syms:
            if s["exported"]:
                kinds[s["kind"]] += 1
    res.data["symbols"] = by_file
    res.views["symbols.stats"] = stats("Public surface of the code", [
        ("Exported functions", kinds["function"], "top-level, public"),
        ("Exported classes", kinds["class"], ""),
        ("Exported types", kinds["type"], "interfaces, type aliases, enums"),
        ("Exported values", kinds["value"], "constants and singletons"),
    ])
    return res


register(Analyzer("symbols", "Functions, classes, and types each file defines.", run,
                  requires=("inventory",), views=("symbols.stats",)))

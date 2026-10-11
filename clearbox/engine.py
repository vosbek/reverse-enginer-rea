"""Load a template, run the analyzers it needs, and assemble a report."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
import tomllib
from datetime import datetime, timezone
from importlib import resources

import clearbox.analyzers  # noqa: F401  (registers analyzers)
from clearbox import __version__
from clearbox.core import REGISTRY, Context
from clearbox.workspace import Limits, Workspace

SAFETY_CONTRACT = [
    "Read-only: target files are opened O_RDONLY and never modified.",
    "No execution: nothing from the target is run, imported, or evaluated. Python is parsed with ast.parse.",
    "No network: Clearbox has no networking code; it analyzes a local directory only.",
    "Jailed: paths that resolve outside the target are refused; symlinks are not followed.",
    "Bounded: file count, per-file size, and total bytes read are capped.",
    "Redacted: secret values are masked and fingerprinted before they reach a report.",
    "Accountable: every file read is listed in the ledger with its SHA-256.",
]


class TemplateError(Exception):
    pass


def all_views() -> dict[str, str]:
    return {v: a.id for a in REGISTRY.values() for v in a.views}


def builtin_templates() -> list[str]:
    root = resources.files("clearbox") / "templates"
    return sorted(p.name[:-5] for p in root.iterdir() if p.name.endswith(".toml"))


def load_template(name_or_path: str) -> tuple[dict, str]:
    if name_or_path.endswith(".toml") and os.path.isfile(name_or_path):
        with open(name_or_path, encoding="utf-8") as fh:
            raw = fh.read()
    else:
        res = resources.files("clearbox") / "templates" / f"{name_or_path}.toml"
        if not res.is_file():
            raise TemplateError(f"Unknown template '{name_or_path}'. Built-in templates: {', '.join(builtin_templates())}")
        raw = res.read_text(encoding="utf-8")
    try:
        tpl = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        raise TemplateError(f"Template is not valid TOML: {exc}") from exc
    validate_template(tpl)
    return tpl, raw


def validate_template(tpl: dict) -> None:
    for key in ("id", "name", "sections"):
        if key not in tpl:
            raise TemplateError(f"Template is missing '{key}'.")
    views = all_views()
    for i, sec in enumerate(tpl["sections"], 1):
        if "title" not in sec or not sec.get("views"):
            raise TemplateError(f"Section {i} needs a 'title' and at least one entry in 'views'.")
        for v in sec["views"]:
            if v not in views:
                raise TemplateError(f"Section '{sec['title']}' uses unknown view '{v}'. Run `clearbox views` to list them.")


def required_analyzers(tpl: dict) -> list[str]:
    views = all_views()
    out = []
    for sec in tpl["sections"]:
        for v in sec["views"]:
            if views[v] not in out:
                out.append(views[v])
    return out


def scan(target: str, template: str = "overview", params: dict[str, str] | None = None,
         limits: Limits | None = None, include_vendored: bool = False, label: str | None = None, exclude: tuple[str, ...] = ()) -> dict:
    tpl, raw = load_template(template)
    params = dict(params or {})
    for p in tpl.get("params", []):
        if p.get("required") and not params.get(p["name"]):
            raise TemplateError(f"Template '{tpl['id']}' needs --param {p['name']}=...  ({p.get('help', '')})")
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    ws = Workspace(target, limits=limits, include_vendored=include_vendored, extra_ignores=exclude)
    ctx = Context(ws, params)
    timings = {}
    for analyzer_id in required_analyzers(tpl):
        t = time.perf_counter()
        ctx.need(analyzer_id)
        timings[analyzer_id] = round(time.perf_counter() - t, 3)

    sections = []
    for sec in tpl["sections"]:
        views = []
        for vid in sec["views"]:
            analyzer_id = all_views()[vid]
            view = ctx.results[analyzer_id].views.get(vid)
            if view is None:
                continue
            views.append({"id": vid, **view})
        sections.append({"title": sec["title"], "question": sec.get("question", ""), "views": views})

    blind = []
    for aid in ctx.order:
        for b in ctx.results[aid].blind_spots:
            if b not in blind:
                blind.append(b)
    findings, seen = [], set()
    for aid in ctx.order:
        for f in ctx.results[aid].findings:
            d = f.to_dict()
            key = json.dumps(d, sort_keys=True)
            if key not in seen:
                seen.add(key)
                findings.append(d)
    ledger = [{"path": e.path, "size": e.size, "mode": e.mode, "sha256": e.sha256, "readers": sorted(e.readers)}
              for e in sorted(ws.ledger.values(), key=lambda e: e.path)]
    ledger_digest = hashlib.sha256(json.dumps(ledger, sort_keys=True).encode()).hexdigest()
    sev = {}
    for f in findings:
        if "test" not in f["tags"] and "docs" not in f["tags"]:
            sev[f["severity"]] = sev.get(f["severity"], 0) + 1

    report = {
        "clearbox": __version__,
        "manifest": {
            "target": label or os.path.basename(ws.root.rstrip("/")) or ws.root,
            "template": {"id": tpl["id"], "name": tpl["name"], "summary": tpl.get("summary", ""),
                         "sha256": hashlib.sha256(raw.encode()).hexdigest()},
            "params": params,
            "started": started.isoformat(timespec="seconds"),
            "duration_s": round(time.perf_counter() - t0, 2),
            "analyzers": timings,
            "python": platform.python_version(),
            "limits": vars(ws.limits),
            "files_seen": len(ws.files),
            "files_read": sum(1 for e in ledger if e["mode"] == "read"),
            "bytes_read": ws.bytes_read,
            "ledger_sha256": ledger_digest,
            "safety": SAFETY_CONTRACT,
            "severity_counts": sev,
        },
        "sections": sections,
        "blind_spots": blind,
        "findings": findings,
        "skipped": ws.skipped,
        "ledger": ledger,
    }
    body = {k: v for k, v in report.items() if k != "manifest"}
    report["manifest"]["content_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
    return report

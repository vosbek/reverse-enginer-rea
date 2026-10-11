"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import os
import sys

from clearbox import __version__
from clearbox.core import REGISTRY
from clearbox.engine import TemplateError, all_views, builtin_templates, load_template, scan
from clearbox.render import FORMATS, write_report
from clearbox.workspace import Limits, ScopeError


def _params(items: list[str]) -> dict[str, str]:
    out = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--param expects name=value, got: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _run(args, template: str, params: dict[str, str]) -> int:
    limits = Limits(max_files=args.max_files, max_file_bytes=args.max_file_mb * 1024 * 1024)
    try:
        report = scan(args.target, template, params, limits=limits, include_vendored=args.include_vendored,
                      label=args.label, exclude=tuple(args.exclude))
    except (TemplateError, ScopeError) as exc:
        print(f"clearbox: {exc}", file=sys.stderr)
        return 2
    if args.link_template:
        if not args.link_template.startswith("https://"):
            print("clearbox: --link-template must start with https://", file=sys.stderr)
            return 2
        report["manifest"]["link_template"] = args.link_template
    out = args.out or os.path.join("clearbox-reports", f"{report['manifest']['target']}-{report['manifest']['template']['id']}")
    out_real = os.path.realpath(out)
    target_real = os.path.realpath(args.target)
    if os.path.commonpath([out_real, target_real]) == target_real:
        print("clearbox: refusing to write the report inside the target; choose another --out.", file=sys.stderr)
        return 2
    formats = tuple(f.strip() for f in args.format.split(",") if f.strip())
    written = write_report(report, out, formats)
    m = report["manifest"]
    sev = m["severity_counts"]
    print(f"{m['template']['name']} of {m['target']}: {m['files_read']:,} files read in {m['duration_s']}s, "
          f"{sev.get('high', 0)} high / {sev.get('medium', 0)} medium capability sites, "
          f"{len(report['blind_spots'])} blind spots.")
    for path in written:
        print(f"  wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="clearbox",
        description="Static, evidence-first reverse engineering. Reads files; never runs, installs, or connects.")
    p.add_argument("--version", action="version", version=f"clearbox {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("target", help="Directory to analyze (clone or extract it first).")
        sp.add_argument("-o", "--out", help="Output directory (default: clearbox-reports/<target>-<template>).")
        sp.add_argument("--format", default=",".join(FORMATS), help="Comma list of html,md,json (default: all).")
        sp.add_argument("--label", help="Name to show for the target instead of its directory name.")
        sp.add_argument("--link-template", help="Make evidence clickable, e.g. "
                        "https://github.com/OWNER/REPO/blob/COMMIT/{path}#L{line}")
        sp.add_argument("--include-vendored", action="store_true", help="Also analyze node_modules, vendor, etc.")
        sp.add_argument("--exclude", action="append", default=[], help="Directory name to skip (repeatable).")
        sp.add_argument("--max-files", type=int, default=100_000)
        sp.add_argument("--max-file-mb", type=int, default=4)

    s = sub.add_parser("scan", help="Run a template against a directory.")
    common(s)
    s.add_argument("-t", "--template", default="overview", help="Built-in name or path to a .toml template.")
    s.add_argument("-p", "--param", action="append", help="Template parameter, name=value (repeatable).")

    t = sub.add_parser("trace", help="Shortcut for the feature-trace template.")
    common(t)
    t.add_argument("feature", help="Words describing the feature to find and explain.")

    sub.add_parser("templates", help="List built-in templates.")
    sub.add_parser("views", help="List every view a template can use.")
    sub.add_parser("analyzers", help="List analyzers.")

    mcp = sub.add_parser("mcp", help="Serve Clearbox to an AI agent over MCP (stdio).")
    mcp.add_argument("--allow-root", action="append", required=True,
                     help="Directory the agent may analyze (repeatable). Everything else is refused.")
    mcp.add_argument("--reports", default=None, help="Where to write reports (default: a temp directory).")

    args = p.parse_args(argv)
    if args.cmd == "scan":
        return _run(args, args.template, _params(args.param))
    if args.cmd == "trace":
        return _run(args, "feature-trace", {"feature": args.feature})
    if args.cmd == "templates":
        for name in builtin_templates():
            tpl, _ = load_template(name)
            needs = ", ".join(f"--param {x['name']}=…" for x in tpl.get("params", []))
            print(f"{name:20} {tpl['summary']}" + (f"\n{'':20} needs {needs}" if needs else ""))
        return 0
    if args.cmd == "views":
        for vid, aid in sorted(all_views().items()):
            print(f"{vid:28} ({aid})")
        return 0
    if args.cmd == "analyzers":
        print(json.dumps({a.id: {"summary": a.summary, "requires": a.requires, "views": a.views}
                          for a in REGISTRY.values()}, indent=1))
        return 0
    if args.cmd == "mcp":
        from clearbox.mcp import serve
        return serve(args.allow_root, args.reports)
    return 1

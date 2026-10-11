"""Report writers: JSON (canonical), Markdown (for diffs and agents), HTML (for people)."""

from __future__ import annotations

import json
import os

from clearbox.render.html import render_html
from clearbox.render.markdown import render_markdown

FORMATS = ("html", "md", "json")


def write_report(report: dict, out_dir: str, formats: tuple[str, ...] = FORMATS) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    written = []
    if "json" in formats:
        path = os.path.join(out_dir, "report.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1, default=str)
        written.append(path)
    if "md" in formats:
        path = os.path.join(out_dir, "report.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_markdown(report))
        written.append(path)
    if "html" in formats:
        path = os.path.join(out_dir, "index.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_html(report))
        written.append(path)
    return written

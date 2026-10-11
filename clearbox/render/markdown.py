"""Markdown report: readable in a terminal, a pull request, or an agent's context window."""

from __future__ import annotations


def _cell(v) -> str:
    return str(v if v is not None else "").replace("|", "\\|").replace("\n", " ")


def _ev(ev: list[dict]) -> str:
    if not ev:
        return ""
    e = ev[0]
    return f"`{e['path']}:{e['line']}`" if e.get("line") else f"`{e['path']}`"


def render_view(v: dict, max_rows: int = 25) -> list[str]:
    out = [f"#### {v.get('title', '')}" + (f"  _({v['confidence']})_" if v.get("confidence") else ""), ""]
    kind = v["kind"]
    if kind == "stats":
        for it in v["items"]:
            hint = f" — {it['hint']}" if it.get("hint") else ""
            out.append(f"- **{it['label']}:** {it['value']:,}{hint}" if isinstance(it["value"], int)
                       else f"- **{it['label']}:** {it['value']}{hint}")
    elif kind == "bars":
        for it in v["items"]:
            out.append(f"- {it['label']}: {it['value']:,} {v.get('unit', '')}")
    elif kind == "table":
        rows = v["rows"][:max_rows]
        if not rows:
            out.append("_Nothing found._")
        else:
            cols = v["columns"]
            out.append("| " + " | ".join(c["label"] for c in cols) + " | Evidence |")
            out.append("|" + "---|" * (len(cols) + 1))
            for r in rows:
                out.append("| " + " | ".join(_cell(r.get(c["key"])) for c in cols) + f" | {_ev(r.get('_ev', []))} |")
            if v["total"] > len(rows):
                out.append(f"\n_{v['total'] - len(rows)} more rows in report.json._")
    elif kind == "matrix":
        labels = v["labels"]
        out.append("| imports → | " + " | ".join(labels) + " |")
        out.append("|" + "---|" * (len(labels) + 1))
        for label, row in zip(labels, v["cells"]):
            out.append(f"| **{label}** | " + " | ".join(str(c or "") for c in row) + " |")
    elif kind == "steps":
        for i, it in enumerate(v["items"], 1):
            out.append(f"{i}. **{it['title']}**")
            if it.get("body"):
                out.append("")
                out.append("   ```")
                out.extend("   " + line for line in it["body"].splitlines())
                out.append("   ```")
        if not v["items"]:
            out.append("_Nothing to show._")
    elif kind == "text":
        out.append(v["body"])
    if v.get("note"):
        out += ["", f"> {v['note']}"]
    out.append("")
    return out


def render_markdown(report: dict) -> str:
    m = report["manifest"]
    lines = [
        f"# {m['template']['name']}: {m['target']}",
        "",
        m["template"]["summary"],
        "",
        f"Clearbox {report['clearbox']} · {m['files_read']:,} files read · {m['duration_s']}s · "
        f"ledger `{m['ledger_sha256'][:16]}` · content `{m['content_sha256'][:16]}`",
        "",
    ]
    if m["params"]:
        lines += ["Parameters: " + ", ".join(f"`{k}={v}`" for k, v in m["params"].items()), ""]
    for sec in report["sections"]:
        lines += [f"## {sec['title']}", ""]
        if sec.get("question"):
            lines += [f"_{sec['question']}_", ""]
        for v in sec["views"]:
            lines += render_view(v)
    lines += ["## Blind spots", ""]
    lines += [f"- {b}" for b in report["blind_spots"]] or ["- None recorded."]
    lines += ["", "## Safety contract", ""] + [f"- {s}" for s in m["safety"]] + [""]
    return "\n".join(lines)

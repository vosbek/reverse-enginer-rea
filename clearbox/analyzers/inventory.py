"""What is the target made of: files, languages, sizes, and areas."""

from __future__ import annotations

from collections import Counter, defaultdict

from clearbox.core import Analyzer, Result, bars, register, stats, table
from clearbox.workspace import CODE_LANGUAGES, DOC_LANGUAGES

TEXT_LANGS = CODE_LANGUAGES | DOC_LANGUAGES | {"JSON", "YAML", "TOML", "XML", "Config", "HTML", "CSS",
                                               "SQL", "Protobuf", "GraphQL", "Docker"}


def human_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def compute_areas(files) -> dict[str, str]:
    """Group files into 'areas': top-level directories, with any directory that
    holds more than 35% of the code split one level further (up to 3 levels).
    Areas are the unit for architecture views, so they need to be few and meaningful."""
    code = [f for f in files if f.is_code]
    total = sum(f.loc for f in code) or 1
    dir_loc: Counter = Counter()
    for f in code:
        dirs = f.path.split("/")[:-1]
        for i in range(1, len(dirs) + 1):
            dir_loc["/".join(dirs[:i])] += f.loc

    def area(path: str) -> str:
        dirs = path.split("/")[:-1]
        if not dirs:
            return "(root)"
        i = 1
        while i < len(dirs) and i < 3 and dir_loc["/".join(dirs[:i])] / total > 0.35:
            i += 1
        return "/".join(dirs[:i])

    return {f.path: area(f.path) for f in files}


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    loc_by_lang: Counter = Counter()
    files_by_lang: Counter = Counter()
    for f in ws.files:
        if f.lang in TEXT_LANGS:
            text = ws.read_text(f.path)
            if text is not None:
                f.loc = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        elif f.lang is None:
            ws.is_binary(f.path)
        label = f.lang or ("binary" if f.binary else "other")
        files_by_lang[label] += 1
        loc_by_lang[label] += f.loc

    areas = compute_areas(ws.files)
    res.data["area_of"] = areas
    code_files = [f for f in ws.files if f.is_code]
    code_loc = sum(f.loc for f in code_files)
    test_loc = sum(f.loc for f in code_files if f.is_test)
    total_bytes = sum(f.size for f in ws.files)

    res.data.update(code_loc=code_loc, test_loc=test_loc, total_files=len(ws.files),
                    total_bytes=total_bytes, code_files=len(code_files))

    langs = sorted(((k, v) for k, v in loc_by_lang.items() if k in CODE_LANGUAGES and v), key=lambda kv: -kv[1])
    res.data["languages"] = langs
    res.views["inventory.stats"] = stats("Shape of the target", [
        ("Files", len(ws.files), f"{human_bytes(total_bytes)} on disk"),
        ("Lines of code", code_loc, f"across {len(code_files):,} source files"),
        ("Test code", f"{(100 * test_loc / code_loc) if code_loc else 0:.0f}%", f"{test_loc:,} lines in test files"),
        ("Languages", len(langs), ", ".join(k for k, _ in langs[:3]) or "none detected"),
        ("Skipped", len(ws.skipped), "symlinks, oversized, or special files"),
    ])
    res.views["inventory.languages"] = bars("Lines of code by language", langs[:12], "lines")

    by_area = defaultdict(lambda: {"files": 0, "loc": 0, "tests": 0, "langs": Counter()})
    for f in ws.files:
        a = by_area[areas[f.path]]
        a["files"] += 1
        if f.is_code:
            a["loc"] += f.loc
            a["langs"][f.lang] += f.loc
            if f.is_test:
                a["tests"] += f.loc
    rows = []
    for name, a in sorted(by_area.items(), key=lambda kv: (-kv[1]["loc"], kv[0])):
        lang = a["langs"].most_common(1)[0][0] if a["langs"] else "-"
        rows.append({"area": name, "files": a["files"], "loc": a["loc"], "lang": lang,
                     "tests": f"{(100 * a['tests'] / a['loc']) if a['loc'] else 0:.0f}%"})
    res.data["areas"] = [r["area"] for r in rows if r["loc"]]
    res.views["inventory.areas"] = table(
        "Areas", [("area", "Area"), ("files", "Files"), ("loc", "Code lines"), ("lang", "Main language"),
                  ("tests", "Test share")], rows, limit=40,
        note="Areas are top-level directories; any directory holding over 35% of the code is split one level deeper.")

    largest = sorted((f for f in code_files if not f.is_test), key=lambda f: -f.loc)[:25]
    res.views["inventory.largest"] = table(
        "Largest source files", [("path", "File"), ("loc", "Lines"), ("lang", "Language")],
        [{"path": f.path, "loc": f.loc, "lang": f.lang, "_ev": [{"path": f.path, "line": 1, "snippet": "",
                                                                  "sha256": ws.sha(f.path)}]} for f in largest])
    if ws.truncated:
        res.blind_spots.append(f"Stopped after {ws.limits.max_files:,} files; the rest of the target was not examined.")
    oversized = [s for s in ws.skipped if "limit" in s["reason"]]
    if oversized:
        res.blind_spots.append(f"{len(oversized)} files were over the read limit and were not parsed.")
    links = [s for s in ws.skipped if "symlink" in s["reason"]]
    if links:
        res.blind_spots.append(f"{len(links)} symlinks were not followed (by design).")
    return res


register(Analyzer("inventory", "Files, languages, sizes, and areas.", run,
                  views=("inventory.stats", "inventory.languages", "inventory.areas", "inventory.largest")))

"""Feature trace: find where a feature lives, how you reach it, what it needs, and how to rebuild it.

Input is a plain-language feature description (`--param feature="..."`).
Files are scored by keyword hits in paths, symbol names, and content; the best
matches become seeds; the import graph supplies callers, dependencies, the
entry-point chain, and a leaves-first build order.
"""

from __future__ import annotations

import posixpath
import re
from collections import Counter, deque

from clearbox.core import HEURISTIC, PARSED, Analyzer, Result, evidence, register, steps, table, text

STOPWORDS = {"the", "and", "for", "how", "does", "what", "with", "this", "that", "from", "into", "when", "work",
             "works", "feature", "app", "application", "code", "show", "find", "where", "its", "are", "use"}


def keywords(feature: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9_\-]+", feature.lower())
    out = []
    for w in words:
        for part in w.replace("-", "_").split("_"):
            if len(part) >= 3 and part not in STOPWORDS and part not in out:
                out.append(part)
    return out


def _split_camel(s: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s).lower()


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    feature = (ctx.params.get("feature") or "").strip()
    kws = keywords(feature)
    if not kws:
        res.views["trace.seeds"] = text("No feature given", "Pass --param feature=\"words describing the feature\".")
        res.blind_spots.append("No feature keywords were supplied, so nothing was traced.")
        return res

    imp = ctx.data("imports")
    graph, rgraph = imp["graph"], imp["rgraph"]
    symbols = ctx.data("symbols")["symbols"]
    surface = ctx.data("surface")
    area_of = ctx.data("inventory")["area_of"]
    risk_findings = ctx.data("risk")["findings"]
    patterns = {k: re.compile(re.escape(k), re.I) for k in kws}

    scored = []
    for f in ws.files:
        if not f.is_code or f.is_test:
            continue
        body = ws.read_text(f.path)
        if body is None:
            continue
        path_l = _split_camel(f.path)
        score, matched, why = 0, set(), []
        for k in kws:
            if k in path_l:
                score += 6
                matched.add(k)
                why.append(f"path has '{k}'")
        sym_hits = Counter()
        for s in symbols.get(f.path, []):
            name = _split_camel(s["name"])
            for k in kws:
                if k in name:
                    sym_hits[k] += 1
                    matched.add(k)
        for k, n in sym_hits.items():
            score += min(3 * n, 15)
            why.append(f"{n} symbol(s) named '{k}'")
        line_hits = []
        for i, line in enumerate(body.splitlines(), 1):
            hit = [k for k, rx in patterns.items() if rx.search(line)]
            if hit:
                line_hits.append((len(hit), i, line))
                matched.update(hit)
        content = Counter()
        for _, _, line in line_hits:
            for k, rx in patterns.items():
                if rx.search(line):
                    content[k] += 1
        for k, n in content.items():
            score += min(n, 15)
        score += 4 * len(matched)
        if len(kws) > 1 and len(matched) == 1:
            score //= 2
        if score:
            best = sorted(line_hits, key=lambda t: (-t[0], t[1]))[:4]
            scored.append((score, f.path, sorted(matched), why, best))
    scored.sort(key=lambda t: (-t[0], t[1]))
    if not scored:
        res.views["trace.seeds"] = text("Nothing matched", f"No source file mentions: {', '.join(kws)}.")
        res.blind_spots.append(f"No file matched the keywords {kws}. Try synonyms or identifiers from the UI.")
        return res

    top = scored[0][0]
    seeds = [s for s in scored if s[0] >= max(8, top * 0.3)][:10]
    seed_paths = [s[1] for s in seeds]
    seed_set = set(seed_paths)

    res.views["trace.seeds"] = table(
        f"Where '{feature}' lives",
        [("path", "File"), ("score", "Score"), ("matched", "Keywords"), ("why", "Why")],
        [{"path": p, "score": sc, "matched": ", ".join(m), "why": "; ".join(w[:3]) or "content mentions",
          "_ev": [evidence(ws, p, ln, line) for _, ln, line in best]} for sc, p, m, w, best in seeds],
        confidence=HEURISTIC,
        note=f"Keywords: {', '.join(kws)}. Score = path hits ×6 + symbol hits ×3 + content lines + 4 per distinct keyword.")

    # -- neighborhood ---------------------------------------------------------
    is_test = {f.path: f.is_test for f in ws.files}
    callers, deps = Counter(), Counter()
    for s in seed_paths:
        for c in rgraph.get(s, ()):
            if c not in seed_set and not is_test.get(c):
                callers[c] += 1
        for d in graph.get(s, ()):
            if d not in seed_set:
                deps[d] += 1
    neighborhood = [{"path": p, "role": "seed", "links": len(graph.get(p, ())) + len(rgraph.get(p, ())),
                     "area": area_of.get(p, "")} for p in seed_paths]
    for p, n in callers.most_common(15):
        neighborhood.append({"path": p, "role": "caller", "links": n, "area": area_of.get(p, "")})
    for p, n in deps.most_common(15):
        neighborhood.append({"path": p, "role": "dependency", "links": n, "area": area_of.get(p, "")})
    for row in neighborhood:
        row["_ev"] = [evidence(ws, row["path"], 1, "")]
    res.views["trace.neighborhood"] = table(
        "Neighborhood", [("path", "File"), ("role", "Role"), ("links", "Links to seeds"), ("area", "Area")],
        neighborhood, confidence=PARSED,
        note="Callers import a seed; dependencies are imported by one. Links count seed connections.")

    # -- how you reach it -----------------------------------------------------
    parent: dict[str, str | None] = {s: None for s in seed_paths}
    q = deque(seed_paths)
    while q:
        node = q.popleft()
        for c in sorted(rgraph.get(node, ())):
            if c not in parent and not is_test.get(c):
                parent[c] = node
                q.append(c)
    entry_files = set(surface["entry_files"])
    roots = [p for p in parent if p in entry_files] or \
            [p for p in parent if not [c for c in rgraph.get(p, ()) if not is_test.get(c)] and p not in seed_set]

    def chain(p: str) -> list[str]:
        out = [p]
        while parent.get(out[-1]) is not None:
            out.append(parent[out[-1]])
        return out

    chains = sorted((chain(r) for r in roots), key=lambda c: (-len(c), c[0]))
    seen_ends, flow_items = set(), []
    for c in chains:
        if c[-1] in seen_ends and len(flow_items) >= 3:
            continue
        seen_ends.add(c[-1])
        flow_items.append({
            "title": f"{c[0]} → … → {c[-1]}" if len(c) > 3 else " → ".join(c),
            "body": "\n".join(f"{'  ' * i}{'└ ' if i else ''}{p}" for i, p in enumerate(c)),
            "ev": [evidence(ws, a, imp["edge_line"].get((a, b), 1)) for a, b in zip(c, c[1:])] or
                  [evidence(ws, c[0], 1, "")]})
        if len(flow_items) >= 6:
            break
    res.views["trace.flow"] = steps(
        "How execution reaches it", flow_items, confidence=PARSED,
        note="Import chains from top-level files (entry points, or files nothing else imports) down to a seed. "
             "Each step's evidence is the import line.")

    # -- blueprint ------------------------------------------------------------
    sub = list(seed_paths)
    frontier = list(seed_paths)
    for _ in range(2):
        nxt = []
        for p in frontier:
            for d in sorted(graph.get(p, ())):
                if d not in sub and len(sub) < 40 and not is_test.get(d):
                    sub.append(d)
                    nxt.append(d)
        frontier = nxt
    sub_set = set(sub)
    depth: dict[str, int] = {}

    def layer(p: str, stack: frozenset = frozenset()) -> int:
        if p in depth:
            return depth[p]
        if p in stack:
            return 0
        kids = [d for d in graph.get(p, ()) if d in sub_set]
        depth[p] = 0 if not kids else 1 + max(layer(d, stack | {p}) for d in kids)
        return depth[p]

    for p in sub:
        layer(p)
    ext = imp["external"]
    caps_by_file = {}
    for fnd in risk_findings:
        path = fnd.evidence[0]["path"]
        if path in sub_set and fnd.severity != "info":
            caps_by_file.setdefault(path, Counter())[fnd.title] += 1
    layers = sorted(set(depth.values()))
    names = {0: "foundations", }
    bp_items = []
    for li, d in enumerate(layers):
        files = sorted(p for p in sub if depth[p] == d)
        lines = []
        for p in files:
            pub = [s["name"] for s in symbols.get(p, []) if s["exported"]][:6]
            pkgs = sorted(k for k, users in ext.items() if p in users and not k.startswith(("node:", "stdlib:")))[:5]
            caps = list(caps_by_file.get(p, {}))[:3]
            role = "seed" if p in seed_set else "support"
            bits = [f"{p} ({role})"]
            if pub:
                bits.append(f"   exposes: {', '.join(pub)}")
            if pkgs:
                bits.append(f"   needs packages: {', '.join(pkgs)}")
            if caps:
                bits.append(f"   capabilities: {'; '.join(caps)}")
            lines.append("\n".join(bits))
        label = names.get(d, "composition" if d == layers[-1] else f"layer {li + 1}")
        bp_items.append({"title": f"Step {li + 1}: {label} — {len(files)} file(s)", "body": "\n".join(lines),
                         "ev": [evidence(ws, p, 1, "") for p in files[:8]]})
    res.views["trace.blueprint"] = steps(
        "Rebuild blueprint (leaves first)", bp_items,
        note="Seeds plus two levels of their internal dependencies, ordered so each step only needs earlier steps. "
             "Build and test each step before the next.")

    pkg_rows = Counter()
    for k, users in ext.items():
        n = sum(1 for p in sub if p in users)
        if n:
            pkg_rows[k] = n
    res.views["trace.packages"] = table(
        "Packages this feature needs", [("package", "Package"), ("files", "Files in feature")],
        [{"package": k, "files": n} for k, n in pkg_rows.most_common()], confidence=PARSED)
    cap_rows = []
    for fnd in risk_findings:
        if fnd.evidence[0]["path"] in sub_set and fnd.severity != "info":
            cap_rows.append({"severity": fnd.severity, "title": fnd.title, "path": fnd.evidence[0]["path"],
                             "line": fnd.evidence[0]["line"], "_ev": fnd.evidence})
    res.views["trace.capabilities"] = table(
        "What this feature does to the host",
        [("severity", "Severity"), ("title", "Capability"), ("path", "File"), ("line", "Line")], cap_rows,
        confidence=HEURISTIC)
    env_rows = []
    for name, rec in surface["env"].items():
        hit = sorted(rec["files"] & sub_set)
        if hit:
            env_rows.append({"var": name, "files": len(hit), "_ev": [e for e in rec["_ev"] if e["path"] in sub_set][:3]
                             or [evidence(ws, hit[0], 1, "")]})
    res.views["trace.config"] = table("Configuration it reads", [("var", "Variable"), ("files", "Files")],
                                      sorted(env_rows, key=lambda r: -r["files"]))
    # Tests of widely shared helpers say little about this feature; keep files with modest fan-in.
    specific = {p for p in sub_set if p in seed_set or len(rgraph.get(p, ())) <= 25}
    stems = {posixpath.splitext(posixpath.basename(p))[0].lower() for p in seed_paths}
    test_rows = []
    for f in ws.files:
        if not f.is_test or not f.is_code:
            continue
        direct = sorted(set(graph.get(f.path, ())) & specific)
        named = posixpath.basename(f.path).lower().split(".")[0] in stems
        if direct or named:
            test_rows.append({"path": f.path, "covers": ", ".join(direct[:3]) or "(by name)",
                              "_ev": [evidence(ws, f.path, 1, "")]})
    res.views["trace.tests"] = table(
        "Existing tests that exercise it", [("path", "Test file"), ("covers", "Covers")], test_rows,
        note="Port these alongside the code: they are the executable spec of the original behavior.")

    questions = []
    caps_titles = Counter(r["title"] for r in cap_rows)
    for title, n in caps_titles.most_common():
        questions.append({"title": f"{title} ({n} site(s))",
                          "body": "Static reading shows the call, not what it does at runtime. Confirm the exact "
                                  "programs, hosts, or paths involved before reproducing it.", "ev": []})
    if env_rows:
        questions.append({"title": f"{len(env_rows)} environment variable(s) change behavior",
                          "body": "Defaults and accepted values are worth confirming: " +
                                  ", ".join(r["var"] for r in env_rows[:8]), "ev": []})
    if not test_rows:
        questions.append({"title": "No tests found for this feature",
                          "body": "Write characterization tests against the original before rebuilding.", "ev": []})
    res.views["trace.questions"] = steps("Open questions before you rebuild", questions,
                                         note="What static analysis cannot settle on its own.")
    res.data.update(seeds=seed_paths, subgraph=sub, keywords=kws)
    return res


register(Analyzer("trace", "Locate a feature, its call chain, dependencies, and a rebuild blueprint.", run,
                  requires=("inventory", "imports", "symbols", "surface", "risk"), params=("feature",),
                  views=("trace.seeds", "trace.neighborhood", "trace.flow", "trace.blueprint", "trace.packages",
                         "trace.capabilities", "trace.config", "trace.tests", "trace.questions")))

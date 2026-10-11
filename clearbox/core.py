"""Shared types: evidence, findings, views, and the analyzer registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from clearbox.workspace import Workspace

# How a claim was established. Reports show this next to every finding.
PARSED = "parsed"        # read from a real parser (Python ast, JSON, TOML, binary headers)
PATTERN = "pattern"      # matched a documented regular expression
HEURISTIC = "heuristic"  # inferred from scores, names, or graph shape

SEVERITIES = ("info", "low", "medium", "high")
SNIPPET_MAX = 180


def evidence(ws: Workspace, path: str, line: int | None = None, snippet: str | None = None) -> dict:
    if snippet is None and line:
        snippet = ws.line_text(path, line)
    snippet = (snippet or "").strip()
    if len(snippet) > SNIPPET_MAX:
        snippet = snippet[: SNIPPET_MAX - 1] + "…"
    ev = {"path": path, "line": line, "snippet": snippet}
    sha = ws.sha(path)
    if sha:
        ev["sha256"] = sha
    return ev


@dataclass
class Finding:
    rule: str
    title: str
    severity: str
    confidence: str
    category: str
    detail: str
    evidence: list[dict]
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": self.rule, "title": self.title, "severity": self.severity,
            "confidence": self.confidence, "category": self.category,
            "detail": self.detail, "evidence": self.evidence, "tags": self.tags,
        }


def table(title: str, columns: list[tuple[str, str]], rows: list[dict], *,
          note: str = "", limit: int = 200, confidence: str = PARSED) -> dict:
    """A tabular view. Rows may carry an `_ev` list of evidence dicts."""
    return {
        "kind": "table", "title": title,
        "columns": [{"key": k, "label": label} for k, label in columns],
        "rows": rows[:limit], "total": len(rows), "note": note, "confidence": confidence,
    }


def stats(title: str, items: list[tuple[str, Any, str]], note: str = "") -> dict:
    return {"kind": "stats", "title": title, "note": note,
            "items": [{"label": label, "value": value, "hint": hint} for label, value, hint in items]}


def bars(title: str, items: list[tuple[str, float]], unit: str, note: str = "",
         confidence: str = PARSED) -> dict:
    return {"kind": "bars", "title": title, "unit": unit, "note": note, "confidence": confidence,
            "items": [{"label": label, "value": value} for label, value in items]}


def matrix(title: str, labels: list[str], cells: list[list[int]], note: str = "") -> dict:
    return {"kind": "matrix", "title": title, "labels": labels, "cells": cells, "note": note,
            "confidence": PARSED}


def steps(title: str, items: list[dict], note: str = "", confidence: str = HEURISTIC) -> dict:
    """Ordered items: [{title, body, ev: [...]}]."""
    return {"kind": "steps", "title": title, "items": items, "note": note, "confidence": confidence}


def text(title: str, body: str) -> dict:
    return {"kind": "text", "title": title, "body": body}


@dataclass
class Result:
    views: dict[str, dict] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    blind_spots: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Analyzer:
    id: str
    summary: str
    run: Callable[["Context"], Result]
    requires: tuple[str, ...] = ()
    views: tuple[str, ...] = ()
    params: tuple[str, ...] = ()


REGISTRY: dict[str, Analyzer] = {}


def register(analyzer: Analyzer) -> Analyzer:
    REGISTRY[analyzer.id] = analyzer
    return analyzer


class Context:
    def __init__(self, ws: Workspace, params: dict[str, str] | None = None) -> None:
        self.ws = ws
        self.params = params or {}
        self.results: dict[str, Result] = {}
        self.order: list[str] = []

    def need(self, analyzer_id: str) -> Result:
        if analyzer_id in self.results:
            return self.results[analyzer_id]
        analyzer = REGISTRY[analyzer_id]
        for dep in analyzer.requires:
            self.need(dep)
        previous, self.ws.reader = self.ws.reader, analyzer_id
        try:
            result = analyzer.run(self)
        finally:
            self.ws.reader = previous
        self.results[analyzer_id] = result
        self.order.append(analyzer_id)
        return result

    def data(self, analyzer_id: str) -> dict[str, Any]:
        return self.need(analyzer_id).data

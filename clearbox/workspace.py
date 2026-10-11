"""The only door between Clearbox and the target.

Every byte an analyzer sees comes through a Workspace. It enforces the safety
contract:

* read-only: files are opened with O_RDONLY, never written
* jailed: paths that resolve outside the target root are refused
* no symlinks: symlinked files and directories are skipped, and the final open
  uses O_NOFOLLOW so a swapped-in link cannot redirect a read
* bounded: file count, per-file size, and total bytes read are capped
* accountable: every read is recorded in a ledger with its SHA-256 and the
  analyzers that used it, so a report can prove what it looked at
"""

from __future__ import annotations

import hashlib
import os
import stat
from bisect import bisect_right
from dataclasses import dataclass, field

VCS_AND_CACHE_DIRS = frozenset(
    {
        ".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache",
        ".ruff_cache", ".tox", ".venv", "venv", ".turbo", ".next", ".cache",
        ".idea", ".vscode",
    }
)
VENDORED_DIRS = frozenset({"node_modules", "bower_components", "vendor", "Pods"})

LANGUAGES = {
    ".py": "Python", ".pyi": "Python",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".mts": "TypeScript", ".cts": "TypeScript",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin",
    ".swift": "Swift", ".m": "Objective-C", ".mm": "Objective-C",
    ".c": "C", ".h": "C/C++ header", ".cc": "C++", ".cpp": "C++", ".cxx": "C++", ".hpp": "C++",
    ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".scala": "Scala", ".lua": "Lua",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".ps1": "PowerShell",
    ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".scss": "CSS", ".vue": "Vue", ".svelte": "Svelte",
    ".sql": "SQL", ".proto": "Protobuf", ".graphql": "GraphQL",
    ".json": "JSON", ".jsonc": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
    ".xml": "XML", ".ini": "Config", ".cfg": "Config", ".env": "Config",
    ".md": "Markdown", ".mdx": "Markdown", ".rst": "Docs", ".txt": "Text",
}
CODE_LANGUAGES = frozenset(
    {
        "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "Kotlin", "Swift",
        "Objective-C", "C", "C/C++ header", "C++", "C#", "Ruby", "PHP", "Scala", "Lua",
        "Shell", "PowerShell", "Vue", "Svelte",
    }
)
DOC_LANGUAGES = frozenset({"Markdown", "Docs", "Text"})
TEST_MARKERS = ("/test/", "/tests/", "/__tests__/", "/spec/", "/testdata/", "/fixtures/")


class ScopeError(Exception):
    """Raised when a path would escape the target root."""


@dataclass(frozen=True)
class Limits:
    max_files: int = 100_000
    max_file_bytes: int = 4 * 1024 * 1024
    max_binary_bytes: int = 64 * 1024 * 1024
    max_total_bytes: int = 2 * 1024 * 1024 * 1024


@dataclass
class FileInfo:
    path: str
    size: int
    lang: str | None
    is_test: bool
    loc: int = 0
    binary: bool | None = None

    @property
    def is_code(self) -> bool:
        return self.lang in CODE_LANGUAGES


@dataclass
class LedgerEntry:
    path: str
    size: int
    mode: str
    sha256: str | None = None
    readers: set[str] = field(default_factory=set)


def classify(path: str) -> tuple[str | None, bool]:
    name = path.rsplit("/", 1)[-1]
    ext = os.path.splitext(name)[1].lower()
    lang = LANGUAGES.get(ext)
    if name == "Dockerfile":
        lang = "Docker"
    p = "/" + path.lower()
    is_test = any(m in p for m in TEST_MARKERS) or any(
        tag in name.lower() for tag in (".test.", ".spec.", "_test.", "test_")
    )
    return lang, is_test


class Workspace:
    def __init__(
        self,
        root: str,
        limits: Limits | None = None,
        include_vendored: bool = False,
        extra_ignores: tuple[str, ...] = (),
    ) -> None:
        real = os.path.realpath(root)
        if not os.path.isdir(real):
            raise ScopeError(f"Target is not a directory: {root}")
        self.root = real
        self.limits = limits or Limits()
        self.ignored = set(VCS_AND_CACHE_DIRS) | set(extra_ignores)
        if not include_vendored:
            self.ignored |= VENDORED_DIRS
        self.ledger: dict[str, LedgerEntry] = {}
        self.skipped: list[dict[str, str]] = []
        self.truncated = False
        self.bytes_read = 0
        self.reader = "core"
        self._cache: dict[str, bytes] = {}
        self._line_index: dict[str, list[int]] = {}
        self.files: list[FileInfo] = self._walk()
        self.by_path = {f.path: f for f in self.files}

    # -- discovery -----------------------------------------------------------

    def _walk(self) -> list[FileInfo]:
        out: list[FileInfo] = []
        for dirpath, dirnames, filenames in os.walk(self.root, followlinks=False):
            keep = []
            for d in sorted(dirnames):
                full = os.path.join(dirpath, d)
                if d in self.ignored:
                    continue
                if os.path.islink(full):
                    self._skip(self._rel(full), "symlinked directory (not followed)")
                    continue
                keep.append(d)
            dirnames[:] = keep
            for name in sorted(filenames):
                full = os.path.join(dirpath, name)
                rel = self._rel(full)
                try:
                    st = os.lstat(full)
                except OSError as exc:
                    self._skip(rel, f"unreadable: {exc.strerror}")
                    continue
                if stat.S_ISLNK(st.st_mode):
                    self._skip(rel, "symlink (not followed)")
                    continue
                if not stat.S_ISREG(st.st_mode):
                    self._skip(rel, "not a regular file")
                    continue
                if len(out) >= self.limits.max_files:
                    self.truncated = True
                    self._skip(rel, f"file limit {self.limits.max_files} reached")
                    return out
                lang, is_test = classify(rel)
                out.append(FileInfo(rel, st.st_size, lang, is_test))
        return out

    def _rel(self, full: str) -> str:
        return os.path.relpath(full, self.root).replace(os.sep, "/")

    def _skip(self, rel: str, reason: str) -> None:
        self.skipped.append({"path": rel, "reason": reason})

    # -- reading -------------------------------------------------------------

    def _resolve(self, rel: str) -> str:
        if os.path.isabs(rel) or ".." in rel.replace("\\", "/").split("/") or "\x00" in rel:
            raise ScopeError(f"Path is outside the target: {rel}")
        joined = os.path.join(self.root, rel)
        real = os.path.realpath(joined)
        if os.path.commonpath([real, self.root]) != self.root:
            raise ScopeError(f"Path is outside the target: {rel}")
        if os.path.islink(joined):
            raise ScopeError(f"Refusing to follow symlink: {rel}")
        return real

    def read_bytes(self, rel: str, limit: int | None = None) -> bytes | None:
        """Read a whole file, or return None if it is over the size limit."""
        limit = limit or self.limits.max_file_bytes
        if rel in self._cache:
            self._touch(rel)
            return self._cache[rel]
        full = self._resolve(rel)
        size = os.lstat(full).st_size
        if size > limit:
            self._skip(rel, f"over the {limit:,}-byte read limit")
            return None
        if self.bytes_read + size > self.limits.max_total_bytes:
            self._skip(rel, "total read budget exhausted")
            return None
        fd = os.open(full, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0))
        with os.fdopen(fd, "rb") as fh:
            data = fh.read(limit + 1)
        if len(data) > limit:
            self._skip(rel, f"grew past the {limit:,}-byte read limit")
            return None
        self.bytes_read += len(data)
        self._cache[rel] = data
        entry = self.ledger.get(rel)
        if entry is None or entry.mode != "read":
            readers = entry.readers if entry else set()
            entry = LedgerEntry(rel, len(data), "read", hashlib.sha256(data).hexdigest(), readers)
            self.ledger[rel] = entry
        self._touch(rel)
        return data

    def sniff(self, rel: str, n: int = 8192) -> bytes:
        """Read only the first n bytes (for format detection)."""
        if rel in self._cache:
            self._touch(rel)
            return self._cache[rel][:n]
        full = self._resolve(rel)
        fd = os.open(full, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0))
        with os.fdopen(fd, "rb") as fh:
            data = fh.read(n)
        self.bytes_read += len(data)
        if rel not in self.ledger:
            self.ledger[rel] = LedgerEntry(rel, self.by_path[rel].size if rel in self.by_path else len(data), "sniff")
        self._touch(rel)
        return data

    def read_text(self, rel: str) -> str | None:
        """Decoded text, or None for binary or oversized files."""
        info = self.by_path.get(rel)
        if info is not None and info.binary:
            return None
        data = self.read_bytes(rel)
        if data is None:
            return None
        if b"\x00" in data[:8192]:
            if info is not None:
                info.binary = True
            return None
        if info is not None:
            info.binary = False
        return data.decode("utf-8", errors="replace")

    def is_binary(self, rel: str) -> bool:
        info = self.by_path[rel]
        if info.binary is None:
            info.binary = b"\x00" in self.sniff(rel)
        return info.binary

    def _touch(self, rel: str) -> None:
        entry = self.ledger.get(rel)
        if entry is not None:
            entry.readers.add(self.reader)

    # -- helpers for evidence ------------------------------------------------

    def line_of(self, rel: str, offset: int) -> int:
        """1-based line number for a character offset in a file's text."""
        index = self._line_index.get(rel)
        if index is None:
            text = self.read_text(rel) or ""
            index = [0]
            pos = text.find("\n")
            while pos != -1:
                index.append(pos + 1)
                pos = text.find("\n", pos + 1)
            self._line_index[rel] = index
        return bisect_right(index, offset)

    def line_text(self, rel: str, line: int) -> str:
        text = self.read_text(rel) or ""
        lines = text.splitlines()
        if 1 <= line <= len(lines):
            return lines[line - 1]
        return ""

    def sha(self, rel: str) -> str | None:
        entry = self.ledger.get(rel)
        return entry.sha256 if entry else None

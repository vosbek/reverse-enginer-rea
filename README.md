# Clearbox

**Reverse engineer anything. Run nothing.**

Clearbox reads a codebase or a folder of binaries and explains it: architecture, how a feature is wired,
what it can do to your machine, and how to rebuild it. Every claim points to a file, a line, and the
SHA-256 of the bytes it read.

It is a static, zero-dependency alternative to [REA](https://github.com/morluto/rea) for the first,
and often the only, pass over unfamiliar code. Case studies: REA itself, and Spotify's Windows
installer rebuilt as [mySpotify](https://github.com/vosbek/my-spotify). Live site with demo reports:
https://vosbek.github.io/reverse-enginer-rea/ (case studies: [Spotify for Windows](https://vosbek.github.io/reverse-enginer-rea/case-studies/spotify/), [REA](https://vosbek.github.io/reverse-enginer-rea/case-studies/rea/))

## Install

Requires Python 3.11 or newer. There are no dependencies.

```bash
pip install git+https://github.com/vosbek/reverse-enginer-rea
# or run from a checkout without installing:
python3 -m clearbox --help
```

## Use

```bash
clearbox scan ./some-app                        # architecture overview
clearbox scan ./some-app -t security-surface    # what it can do to the host
clearbox scan ./some-app -t dependency-audit    # declared vs. imported
clearbox scan ./some-app -t binary-triage       # ELF / PE / Mach-O / WASM / DEX headers and strings
clearbox trace ./some-app "search notes"        # where a feature lives and how to rebuild it
clearbox templates                              # list templates
clearbox views                                  # list views a custom template can use
```

Each run writes `index.html` (self-contained, opens offline), `report.md`, and `report.json` to
`clearbox-reports/<target>-<template>/`. Useful flags:

| Flag | Purpose |
| --- | --- |
| `-t path/to/custom.toml` | Use your own template |
| `-p name=value` | Template parameter (e.g. `-p feature="checkout"`) |
| `--link-template URL` | Make evidence clickable, e.g. `https://github.com/O/R/blob/SHA/{path}#L{line}` |
| `--exclude DIR` | Skip a directory name (repeatable) |
| `--include-vendored` | Also read `node_modules`, `vendor`, … |
| `--max-files`, `--max-file-mb` | Change read limits |

## Use from an AI agent (MCP)

```json
{
  "mcpServers": {
    "clearbox": { "command": "clearbox", "args": ["mcp", "--allow-root", "/path/to/targets"] }
  }
}
```

The agent gets four read-only tools (`clearbox_templates`, `clearbox_scan`, `clearbox_trace`,
`clearbox_read`) and can only reach directories under `--allow-root`. Text derived from the target is
wrapped in a fence with a random nonce and labeled as data, so a target cannot pose as instructions.

## Safety contract

* **Read-only.** Target files are opened `O_RDONLY | O_NOFOLLOW` and never modified. Reports are refused
  if the output directory is inside the target.
* **No execution.** Python is parsed with `ast.parse`; binaries are decoded with `struct`. Nothing from
  the target is imported, evaluated, or run.
* **No network.** Clearbox contains no networking code. It analyzes a local directory only.
* **Jailed.** Paths that resolve outside the target are refused. Symlinks are skipped, not followed.
* **Bounded.** File count, per-file size, and total bytes read are capped.
* **Redacted.** Secret values are masked and fingerprinted before they reach any report.
* **Accountable.** Every file read is listed in a ledger with its SHA-256. Reports carry a ledger digest
  and a content digest that is identical across re-runs of the same input.

`tests/test_clearbox.py` enforces the first three claims against Clearbox's own source: the build fails
if the package imports `subprocess`, `socket`, `urllib`, `http`, `ctypes` and friends, or calls `eval`,
`exec`, `os.system`, file deletion, and similar.

## Templates

A template is a TOML file: questions, each answered by one or more views.

```toml
id = "handoff"
name = "New-engineer handoff"
summary = "What a new teammate needs on day one."

[[sections]]
title = "Where do I start reading?"
views = ["surface.entrypoints", "imports.hubs"]

[[sections]]
title = "What can break production?"
views = ["risk.summary", "surface.env"]
```

Built in: `overview`, `feature-trace`, `security-surface`, `dependency-audit`, `binary-triage`
(see `clearbox/templates/`).

## How each claim is established

| Label | Meaning |
| --- | --- |
| `parsed` | From a real parser: Python `ast`, JSON, TOML, binary headers. |
| `pattern` | A documented regular expression matched. The row shows the line. |
| `heuristic` | Inferred from scores or graph shape, like which files make up a feature. |

Every report also lists its **blind spots**: dynamic imports, path aliases, oversized files, and other
things the run could not see.

## Layout

```
clearbox/
  workspace.py     the read-only, jailed, ledgered file access layer
  core.py          evidence, findings, views, analyzer registry
  engine.py        templates → analyzers → report
  analyzers/       inventory, manifests, imports, symbols, surface, risk, binary, trace
  templates/       built-in TOML templates
  render/          html (self-contained, strict CSP), markdown, json
  mcp.py           read-only MCP server
site/              the GitHub Pages site; site/demo is rebuilt by CI
scripts/build-demo.sh   regenerates the demo reports from a pinned REA commit
```

## Development

```bash
python3 -m unittest discover -s tests -v
scripts/build-demo.sh            # needs git and network access to fetch REA
```

## License

MIT

# Dependency audit: morluto/rea

What the target declares, what it actually imports, the gaps between the two, and what runs at install.

Clearbox 0.2.0 · 2,757 files read · 1.69s · ledger `0aa8ee16dff3063e` · content `8c131124afe2c91f`

## Declared

_What do the manifests and lockfiles say?_

#### Declared dependencies

- **Runtime:** 38 — declared direct dependencies
- **Development:** 19 — build, lint, and test tooling
- **Locked packages:** 561 — in 1 lockfile(s)
- **Install hooks:** 1 — prepare

#### Declared dependencies  _(parsed)_

| Package | Version | Kind | Ecosystem | Manifest | Evidence |
|---|---|---|---|---|---|
| @babel/parser | 8.0.4 | runtime | npm | package.json | `package.json:273` |
| @babel/types | 8.0.4 | runtime | npm | package.json | `package.json:274` |
| @clack/prompts | 1.7.0 | runtime | npm | package.json | `package.json:275` |
| @electron/asar | 4.2.0 | runtime | npm | package.json | `package.json:276` |
| @jridgewell/trace-mapping | 0.3.31 | runtime | npm | package.json | `package.json:277` |
| @lydell/node-pty | 1.1.0 | runtime | npm | package.json | `package.json:278` |
| @modelcontextprotocol/client | 2.3.1 | runtime | npm | package.json | `package.json:279` |
| @modelcontextprotocol/server | 2.3.1 | runtime | npm | package.json | `package.json:280` |
| @xmldom/xmldom | 0.9.12 | runtime | npm | package.json | `package.json:281` |
| @xterm/addon-serialize | 0.14.0 | runtime | npm | package.json | `package.json:282` |
| @xterm/headless | 6.0.0 | runtime | npm | package.json | `package.json:283` |
| @zip.js/zip.js | 2.15.0 | runtime | npm | package.json | `package.json:284` |
| CairoSVG | ==2.9.1 | runtime | pypi | website/requirements.txt | `website/requirements.txt:2` |
| ajv | 8.20.0 | runtime | npm | package.json | `package.json:285` |
| ajv-formats | 3.0.1 | runtime | npm | package.json | `package.json:286` |
| canonicalize | 3.0.0 | runtime | npm | package.json | `package.json:287` |
| cross-spawn | 7.0.6 | runtime | npm | package.json | `package.json:288` |
| diff | 9.0.0 | runtime | npm | package.json | `package.json:289` |
| evmole | 0.9.3 | runtime | npm | package.json | `package.json:290` |
| har-schema | 2.0.0 | runtime | npm | package.json | `package.json:291` |
| ignore | 7.0.6 | runtime | npm | package.json | `package.json:292` |
| incur | 0.6.1 | runtime | npm | package.json | `package.json:293` |
| isomorphic-git | 1.38.7 | runtime | npm | package.json | `package.json:294` |
| jsonc-parser | 3.3.1 | runtime | npm | package.json | `package.json:295` |
| lossless-json | 4.3.1 | runtime | npm | package.json | `package.json:296` |

_32 more rows in report.json._

#### Lockfiles  _(parsed)_

| Lockfile | Packages | Evidence |
|---|---|---|
| package-lock.json | 561 | `package-lock.json:1` |

## Actually used

_Which packages are imported, and by how many files?_

#### External packages by reach  _(pattern)_

| Package | Files importing | Test files | Evidence |
|---|---|---|---|
| vitest | 3 | 887 | `src/adb/AdbConfiguration.test.ts:1` |
| node:path | 291 | 393 | `scripts/build-conformance-fixtures.mjs:4` |
| node:fs/promises | 252 | 414 | `scripts/build-conformance-fixtures.mjs:2` |
| zod | 295 | 101 | `scripts/lib/catalog-cli.mjs:2` |
| node:crypto | 185 | 110 | `scripts/build-ghidra-nativeaot.mjs:3` |
| node:child_process | 101 | 109 | `scripts/build-conformance-fixtures.mjs:1` |
| node:url | 120 | 71 | `scripts/build-ghidra-nativeaot.mjs:13` |
| @modelcontextprotocol/client | 51 | 106 | `scripts/generate-mcp-tool-catalog.mjs:4` |
| node:util | 83 | 73 | `scripts/build-conformance-fixtures.mjs:5` |
| node:assert/strict | 114 | 7 | `scripts/lib/artifact-e2e.mjs:1` |
| node:fs | 83 | 37 | `scripts/ci/plan.mjs:2` |
| node:os | 92 | 27 | `scripts/build-conformance-fixtures.mjs:3` |
| pino | 82 | 6 | `src/application/DirectAnalysis.ts:9` |
| @modelcontextprotocol/server | 21 | 35 | `scripts/generate-mcp-tool-catalog.mjs:6` |
| @babel/types | 48 | 5 | `scripts/lib/module-boundaries.mjs:2` |
| ajv | 15 | 37 | `scripts/generate-mcp-tool-catalog.mjs:5` |
| incur | 39 | 5 | `scripts/lib/catalog-cli.mjs:1` |
| canonicalize | 32 | 2 | `scripts/lib/catalog-core.mjs:5` |
| node:stream | 21 | 13 | `src/android/AndroidTargetSnapshot.ts:5` |
| node:events | 10 | 23 | `scripts/fixtures/browser-network-site.mjs:1` |
| electron | 7 | 24 | `scripts/electron-active-hook.cjs:597` |
| node:http | 9 | 21 | `scripts/fixtures/browser-module-site.mjs:1` |
| node:timers/promises | 13 | 12 | `scripts/lib/browser-scenario-environment-e2e.mjs:2` |
| @electron/asar | 2 | 22 | `src/artifacts/AsarArtifactReader.ts:22` |
| stdlib:sys | 12 | 10 | `bridge/native/test_rea_lldb_tracer.py:7` |

_128 more rows in report.json._

> Reach is how many non-test files import the package. node:, stdlib:, and go: are platform modules.

## Gaps

_What is imported but undeclared, or declared but never imported?_

#### Imported but not declared  _(heuristic)_

| Package | Files | Evidence |
|---|---|---|
| electron | 7 | `scripts/electron-active-hook.cjs:597` |
| elftools | 3 | `bridge/pwntools/layout_impl.py:129` |
| gdb | 1 | `bridge/pwndbg/core_context.py:6` |
| lldb | 1 | `bridge/native/rea_lldb_tracer.py:20` |
| m | 1 | `src/browser/WebSourceMapFetcher.ts:1024` |
| mitmproxy | 1 | `bridge/mitmproxy/capture.py:15` |
| pwndbg | 1 | `bridge/pwndbg/core_context.py:29` |
| pwnlib | 3 | `bridge/pwntools/layout_impl.py:127` |
| z3 | 1 | `website/public/showcase/ctf/solve.py:10` |

> May be workspace packages, path aliases, or Python import names that differ from their distribution name.

#### Declared but never imported  _(heuristic)_

_Nothing found._

> Runtime dependencies no source file imports. They may still be used by CLIs, config files, or types.

## Install time

_Which scripts run automatically when the package is installed?_

#### Install-time scripts  _(parsed)_

| Hook | Command | Manifest | Evidence |
|---|---|---|---|
| prepare | node scripts/prepare.mjs | package.json | `package.json:227` |

> These run automatically during `npm install` (or `npm install` of a git checkout for `prepare`).

## Blind spots

- 107 dynamic imports use computed module names and could not be followed (e.g. scripts/generate-completion-ledger.mjs:45, scripts/generate-skill-metadata.mjs:20, scripts/generate-skill-metadata.mjs:23).
- 154 imports did not resolve to a file (14 use path aliases or package import maps).
- 284 imports point at build output (dist/, build/); they were mapped to the matching file under src/ by path, which assumes the usual one-to-one layout.

## Safety contract

- Read-only: target files are opened O_RDONLY and never modified.
- No execution: nothing from the target is run, imported, or evaluated. Python is parsed with ast.parse.
- No network: Clearbox has no networking code; it analyzes a local directory only.
- Jailed: paths that resolve outside the target are refused; symlinks are not followed.
- Bounded: file count, per-file size, and total bytes read are capped.
- Redacted: secret values are masked and fingerprinted before they reach a report.
- Accountable: every file read is listed in the ledger with its SHA-256.

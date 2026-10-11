# Security surface: morluto/rea

Everything the target can do to the host it runs on, with the exact line for each claim. Use before you install, run, or connect an agent to it.

Clearbox 0.2.0 · 2,757 files read · 12.48s · ledger `31030c50c75106af` · content `58cbc90d569f7489`

## Summary

_Which host-touching capabilities appear in production code, and how often?_

#### Capabilities that touch the host  _(pattern)_

| Severity | Category | Capability | Files | Sites | In tests/docs | Evidence |
|---|---|---|---|---|---|---|
| high | Process execution | Spawns OS processes (Node child_process) | 106 | 159 | 200 | `scripts/build-conformance-fixtures.mjs:1` |
| high | Dynamic code | Evaluates code built at runtime (Python) | 7 | 8 | 3 | `bridge/pwndbg/core_context.py:28` |
| high | Process execution | Drives an interactive terminal (PTY) | 5 | 7 | 3 | `scripts/verify-package-setup.mjs:12` |
| high | Process execution | Spawns OS processes (Python) | 4 | 10 | 5 | `bridge/pwndbg/launch_impl.py:26` |
| high | Privilege and host changes | Requests elevated privileges | 1 | 1 | 2 | `src/application/LinuxHopper.ts:337` |
| high | Dynamic code | Evaluates code built at runtime | 0 | 0 | 4 | `src/application/javascript/JavaScriptSemanticGraphScope.test.ts:14` |
| medium | Filesystem | Deletes files or directories | 78 | 96 | 135 | `bridge/hopper_bridge.py:1135` |
| medium | Network | Makes network requests | 20 | 26 | 44 | `scripts/audit-website-links.py:14` |
| medium | Network | Drives a web browser | 19 | 23 | 15 | `vitest.config.ts:18` |
| medium | Network | Opens raw sockets or servers | 10 | 11 | 35 | `bridge/hopper_bridge.py:1136` |
| medium | Privilege and host changes | Installs system software | 3 | 6 | 3 | `scripts/verify-package-environment.mjs:31` |
| medium | Filesystem | Touches user-level config directories | 1 | 1 | 0 | `scripts/verify-agent-experience.mjs:81` |
| medium | Supply chain | Runs code at install time | 1 | 1 | 0 | `package.json:227` |
| medium | Secrets | Hard-coded credential | 0 | 0 | 2 | `scripts/fixtures/browser-network-site.mjs:13` |
| medium | Agent safety | Text that addresses an AI agent | 0 | 0 | 2 | `tests/boundary/mcp/promptMcp.test.ts:73` |
| low | Filesystem | Writes files | 14 | 43 | 38 | `bridge/mitmproxy/capture.py:203` |

> Counts exclude tests and docs; those are listed separately. A capability is not a vulnerability; it is something a reviewer should know the code can do.

#### Capability sites by category (production code)  _(parsed)_

- Process execution: 176 sites
- Filesystem: 140 sites
- Network: 60 sites
- Dynamic code: 8 sites
- Privilege and host changes: 7 sites
- Supply chain: 1 sites

#### Where host-touching code lives  _(parsed)_

| Area | Sites | Mostly | Evidence |
|---|---|---|---|
| scripts | 279 | Process execution 149, Filesystem 96, Network 33 |  |
| src/application | 29 | Filesystem 15, Privilege and host changes 6, Process execution 5 |  |
| bridge | 20 | Filesystem 9, Dynamic code 8, Network 2 |  |
| src/browser | 20 | Network 17, Filesystem 2, Process execution 1 |  |
| src/process | 19 | Process execution 13, Filesystem 6 |  |
| src/ghidra | 4 | Process execution 2, Filesystem 2 |  |
| src/hopper | 4 | Process execution 2, Filesystem 2 |  |
| src/adb | 3 | Process execution 2, Filesystem 1 |  |
| src/javascript | 3 | Filesystem 3 |  |
| website | 3 | Network 3 |  |
| src/domain | 2 | Network 1, Process execution 1 |  |
| src/native | 2 | Filesystem 2 |  |
| (root) | 1 | Network 1 |  |
| src/apktool | 1 | Filesystem 1 |  |
| src/artifacts | 1 | Filesystem 1 |  |

## Install time

_Does installing it run code?_

#### Install-time scripts  _(parsed)_

| Hook | Command | Manifest | Evidence |
|---|---|---|---|
| prepare | node scripts/prepare.mjs | package.json | `package.json:227` |

> These run automatically during `npm install` (or `npm install` of a git checkout for `prepare`).

#### Declared dependencies

- **Runtime:** 38 — declared direct dependencies
- **Development:** 19 — build, lint, and test tooling
- **Locked packages:** 561 — in 1 lockfile(s)
- **Install hooks:** 1 — prepare

## Processes and privileges

_Does it launch other programs, drive terminals, or ask for root?_

#### Process execution  _(pattern)_

| Severity | Finding | File | Line | Evidence |
|---|---|---|---|---|
| high | Spawns OS processes (Python) | bridge/pwndbg/launch_impl.py | 26 | `bridge/pwndbg/launch_impl.py:26` |
| high | Spawns OS processes (Python) | scripts/audit-website-links.py | 22 | `scripts/audit-website-links.py:22` |
| high | Spawns OS processes (Node child_process) | scripts/build-conformance-fixtures.mjs | 1 | `scripts/build-conformance-fixtures.mjs:1` |
| high | Spawns OS processes (Node child_process) | scripts/build-ghidra-nativeaot.mjs | 2 | `scripts/build-ghidra-nativeaot.mjs:2` |
| high | Spawns OS processes (Node child_process) | scripts/build-ghidra-nativeaot.mjs | 40 | `scripts/build-ghidra-nativeaot.mjs:40` |
| high | Spawns OS processes (Node child_process) | scripts/build-ghidra-nativeaot.mjs | 167 | `scripts/build-ghidra-nativeaot.mjs:167` |
| high | Spawns OS processes (Node child_process) | scripts/build-windows-native.mjs | 4 | `scripts/build-windows-native.mjs:4` |
| high | Spawns OS processes (Node child_process) | scripts/build-windows-native.mjs | 21 | `scripts/build-windows-native.mjs:21` |
| high | Spawns OS processes (Node child_process) | scripts/ci/plan.mjs | 1 | `scripts/ci/plan.mjs:1` |
| high | Spawns OS processes (Node child_process) | scripts/ci/plan.mjs | 42 | `scripts/ci/plan.mjs:42` |
| high | Spawns OS processes (Node child_process) | scripts/electron-active-hook-boundaries.cjs | 354 | `scripts/electron-active-hook-boundaries.cjs:354` |
| high | Spawns OS processes (Node child_process) | scripts/generate-completion-ledger.mjs | 2 | `scripts/generate-completion-ledger.mjs:2` |
| high | Spawns OS processes (Node child_process) | scripts/generate-nativeaot-fixtures.mjs | 2 | `scripts/generate-nativeaot-fixtures.mjs:2` |
| high | Spawns OS processes (Node child_process) | scripts/generate-nativeaot-fixtures.mjs | 35 | `scripts/generate-nativeaot-fixtures.mjs:35` |
| high | Spawns OS processes (Python) | scripts/hopper-demo-x11.py | 385 | `scripts/hopper-demo-x11.py:385` |
| high | Spawns OS processes (Python) | scripts/hopper-demo-x11.py | 427 | `scripts/hopper-demo-x11.py:427` |
| high | Spawns OS processes (Python) | scripts/hopper-demo-x11.py | 444 | `scripts/hopper-demo-x11.py:444` |
| high | Spawns OS processes (Python) | scripts/hopper-demo-x11.py | 544 | `scripts/hopper-demo-x11.py:544` |
| high | Spawns OS processes (Python) | scripts/hopper-demo-x11.py | 563 | `scripts/hopper-demo-x11.py:563` |
| high | Spawns OS processes (Python) | scripts/hopper-demo-x11.py | 654 | `scripts/hopper-demo-x11.py:654` |
| high | Spawns OS processes (Python) | scripts/hopper-demo-x11.py | 669 | `scripts/hopper-demo-x11.py:669` |
| high | Spawns OS processes (Node child_process) | scripts/lib/artifact-e2e.mjs | 2 | `scripts/lib/artifact-e2e.mjs:2` |
| high | Spawns OS processes (Node child_process) | scripts/lib/browser-dom-destinations-e2e.mjs | 2 | `scripts/lib/browser-dom-destinations-e2e.mjs:2` |
| high | Spawns OS processes (Node child_process) | scripts/lib/browser-module-e2e.mjs | 2 | `scripts/lib/browser-module-e2e.mjs:2` |
| high | Spawns OS processes (Node child_process) | scripts/lib/browser-nested-source-map-e2e.mjs | 2 | `scripts/lib/browser-nested-source-map-e2e.mjs:2` |

_359 more rows in report.json._

#### Privilege and host changes  _(pattern)_

| Severity | Finding | File | Line | Evidence |
|---|---|---|---|---|
| high | Requests elevated privileges | src/application/LinuxHopper.ts | 337 | `src/application/LinuxHopper.ts:337` |
| medium | Installs system software | scripts/verify-package-environment.mjs | 31 | `scripts/verify-package-environment.mjs:31` |
| medium | Installs system software | src/application/LinuxHopper.ts | 329 | `src/application/LinuxHopper.ts:329` |
| medium | Installs system software | src/application/LinuxHopper.ts | 331 | `src/application/LinuxHopper.ts:331` |
| medium | Installs system software | src/application/LinuxHopper.ts | 333 | `src/application/LinuxHopper.ts:333` |
| medium | Installs system software | src/application/LinuxHopper.ts | 334 | `src/application/LinuxHopper.ts:334` |
| medium | Installs system software | src/application/homebrew.ts | 8 | `src/application/homebrew.ts:8` |
| info | Requests elevated privileges | SECURITY.md | 47 | `SECURITY.md:47` |
| info | Requests elevated privileges | src/application/LinuxHopper.test.ts | 155 | `src/application/LinuxHopper.test.ts:155` |
| info | Installs system software | src/application/LinuxHopper.test.ts | 123 | `src/application/LinuxHopper.test.ts:123` |
| info | Installs system software | src/application/LinuxHopper.test.ts | 126 | `src/application/LinuxHopper.test.ts:126` |
| info | Installs system software | src/application/LinuxHopper.test.ts | 137 | `src/application/LinuxHopper.test.ts:137` |

#### Dynamic code  _(pattern)_

| Severity | Finding | File | Line | Evidence |
|---|---|---|---|---|
| high | Evaluates code built at runtime (Python) | bridge/pwndbg/core_context.py | 28 | `bridge/pwndbg/core_context.py:28` |
| high | Evaluates code built at runtime (Python) | bridge/pwndbg/launch.py | 25 | `bridge/pwndbg/launch.py:25` |
| high | Evaluates code built at runtime (Python) | bridge/pwndbg/launch_impl.py | 9 | `bridge/pwndbg/launch_impl.py:9` |
| high | Evaluates code built at runtime (Python) | bridge/pwndbg/launch_impl.py | 24 | `bridge/pwndbg/launch_impl.py:24` |
| high | Evaluates code built at runtime (Python) | bridge/pwntools/layout.py | 25 | `bridge/pwntools/layout.py:25` |
| high | Evaluates code built at runtime (Python) | bridge/pwntools/layout_impl.py | 308 | `bridge/pwntools/layout_impl.py:308` |
| high | Evaluates code built at runtime (Python) | bridge/pwntools/recorded_crash.py | 25 | `bridge/pwntools/recorded_crash.py:25` |
| high | Evaluates code built at runtime (Python) | bridge/pwntools/recorded_crash_impl.py | 146 | `bridge/pwntools/recorded_crash_impl.py:146` |
| info | Evaluates code built at runtime | src/application/javascript/JavaScriptSemanticGraphScope.test.ts | 14 | `src/application/javascript/JavaScriptSemanticGraphScope.test.ts:14` |
| info | Evaluates code built at runtime | src/application/javascript/JavaScriptSemanticGraphScope.test.ts | 28 | `src/application/javascript/JavaScriptSemanticGraphScope.test.ts:28` |
| info | Evaluates code built at runtime | src/domain/javascript/javascriptSemanticAnalysis.structure.test.ts | 403 | `src/domain/javascript/javascriptSemanticAnalysis.structure.test.ts:403` |
| info | Evaluates code built at runtime | tests/evaluation/model-evals/agentEvaluationReport.test.ts | 65 | `tests/evaluation/model-evals/agentEvaluationReport.test.ts:65` |
| info | Evaluates code built at runtime (Python) | tests/fixtures/hopperBridgeFacadeProbe.py | 117 | `tests/fixtures/hopperBridgeFacadeProbe.py:117` |
| info | Evaluates code built at runtime (Python) | tests/fixtures/hopperInstructionProbe.py | 113 | `tests/fixtures/hopperInstructionProbe.py:113` |
| info | Evaluates code built at runtime (Python) | tests/fixtures/hopperStringSearchProbe.py | 56 | `tests/fixtures/hopperStringSearchProbe.py:56` |

## Network

_Does it talk to the network or automate a browser?_

#### Network  _(pattern)_

| Severity | Finding | File | Line | Evidence |
|---|---|---|---|---|
| medium | Opens raw sockets or servers | bridge/hopper_bridge.py | 1136 | `bridge/hopper_bridge.py:1136` |
| medium | Opens raw sockets or servers | bridge/hopper_bridge.py | 1139 | `bridge/hopper_bridge.py:1139` |
| medium | Makes network requests | scripts/audit-website-links.py | 14 | `scripts/audit-website-links.py:14` |
| medium | Makes network requests | scripts/build-windows-native.mjs | 50 | `scripts/build-windows-native.mjs:50` |
| medium | Makes network requests | scripts/lib/browser-capture-metadata-budget-e2e.mjs | 62 | `scripts/lib/browser-capture-metadata-budget-e2e.mjs:62` |
| medium | Makes network requests | scripts/lib/browser-capture-metadata-budget-e2e.mjs | 64 | `scripts/lib/browser-capture-metadata-budget-e2e.mjs:64` |
| medium | Makes network requests | scripts/lib/browser-capture-metadata-budget-e2e.mjs | 141 | `scripts/lib/browser-capture-metadata-budget-e2e.mjs:141` |
| medium | Opens raw sockets or servers | scripts/lib/browser-capture-metadata-budget-e2e.mjs | 49 | `scripts/lib/browser-capture-metadata-budget-e2e.mjs:49` |
| medium | Drives a web browser | scripts/lib/browser-module-e2e.mjs | 9 | `scripts/lib/browser-module-e2e.mjs:9` |
| medium | Makes network requests | scripts/lib/browser-nested-source-map-e2e.mjs | 112 | `scripts/lib/browser-nested-source-map-e2e.mjs:112` |
| medium | Makes network requests | scripts/lib/browser-network-e2e.mjs | 142 | `scripts/lib/browser-network-e2e.mjs:142` |
| medium | Opens raw sockets or servers | scripts/lib/browser-popup-e2e.mjs | 191 | `scripts/lib/browser-popup-e2e.mjs:191` |
| medium | Drives a web browser | scripts/lib/browser-popup-e2e.mjs | 7 | `scripts/lib/browser-popup-e2e.mjs:7` |
| medium | Makes network requests | scripts/lib/browser-runtime-e2e.mjs | 69 | `scripts/lib/browser-runtime-e2e.mjs:69` |
| medium | Makes network requests | scripts/lib/browser-runtime-termination-e2e.mjs | 9 | `scripts/lib/browser-runtime-termination-e2e.mjs:9` |
| medium | Makes network requests | scripts/lib/browser-runtime-termination-e2e.mjs | 94 | `scripts/lib/browser-runtime-termination-e2e.mjs:94` |
| medium | Makes network requests | scripts/lib/browser-scenario-environment-e2e.mjs | 87 | `scripts/lib/browser-scenario-environment-e2e.mjs:87` |
| medium | Makes network requests | scripts/lib/browser-scenario-environment-e2e.mjs | 111 | `scripts/lib/browser-scenario-environment-e2e.mjs:111` |
| medium | Makes network requests | scripts/lib/browser-scenario-storage-e2e.mjs | 294 | `scripts/lib/browser-scenario-storage-e2e.mjs:294` |
| medium | Makes network requests | scripts/lib/browser-scenario-storage-e2e.mjs | 645 | `scripts/lib/browser-scenario-storage-e2e.mjs:645` |
| medium | Opens raw sockets or servers | scripts/lib/browser-scenario-storage-e2e.mjs | 172 | `scripts/lib/browser-scenario-storage-e2e.mjs:172` |
| medium | Makes network requests | scripts/lib/browser-screenshot-e2e.mjs | 35 | `scripts/lib/browser-screenshot-e2e.mjs:35` |
| medium | Drives a web browser | scripts/lib/browser-screenshot-e2e.mjs | 9 | `scripts/lib/browser-screenshot-e2e.mjs:9` |
| medium | Drives a web browser | scripts/rea.mjs | 30 | `scripts/rea.mjs:30` |
| medium | Makes network requests | scripts/test-website.py | 14 | `scripts/test-website.py:14` |

_129 more rows in report.json._

#### Transport security  _(pattern)_

_Nothing found._

## Files

_Does it delete files, write files, or touch other applications' settings?_

#### Filesystem  _(pattern)_

| Severity | Finding | File | Line | Evidence |
|---|---|---|---|---|
| medium | Deletes files or directories | bridge/hopper_bridge.py | 1135 | `bridge/hopper_bridge.py:1135` |
| medium | Deletes files or directories | bridge/hopper_bridge.py | 1155 | `bridge/hopper_bridge.py:1155` |
| medium | Deletes files or directories | bridge/native/rea_lldb_tracer.py | 151 | `bridge/native/rea_lldb_tracer.py:151` |
| medium | Deletes files or directories | bridge/native/rea_lldb_tracer.py | 157 | `bridge/native/rea_lldb_tracer.py:157` |
| medium | Deletes files or directories | scripts/build-conformance-fixtures.mjs | 25 | `scripts/build-conformance-fixtures.mjs:25` |
| medium | Deletes files or directories | scripts/build-ghidra-nativeaot.mjs | 146 | `scripts/build-ghidra-nativeaot.mjs:146` |
| medium | Deletes files or directories | scripts/generate-skill-metadata.mjs | 44 | `scripts/generate-skill-metadata.mjs:44` |
| medium | Deletes files or directories | scripts/lib/browser-module-e2e.mjs | 305 | `scripts/lib/browser-module-e2e.mjs:305` |
| medium | Deletes files or directories | scripts/lib/browser-screenshot-e2e.mjs | 197 | `scripts/lib/browser-screenshot-e2e.mjs:197` |
| medium | Deletes files or directories | scripts/lib/browser-script-export-e2e.mjs | 110 | `scripts/lib/browser-script-export-e2e.mjs:110` |
| medium | Deletes files or directories | scripts/lib/browser-source-map-e2e.mjs | 133 | `scripts/lib/browser-source-map-e2e.mjs:133` |
| medium | Deletes files or directories | scripts/lib/native-value-e2e.mjs | 108 | `scripts/lib/native-value-e2e.mjs:108` |
| medium | Deletes files or directories | scripts/lib/real-ghidra-entry-aliases.mjs | 206 | `scripts/lib/real-ghidra-entry-aliases.mjs:206` |
| medium | Deletes files or directories | scripts/lib/real-ghidra-large-results.mjs | 210 | `scripts/lib/real-ghidra-large-results.mjs:210` |
| medium | Deletes files or directories | scripts/lib/real-ghidra-namespace-annotations.mjs | 178 | `scripts/lib/real-ghidra-namespace-annotations.mjs:178` |
| medium | Deletes files or directories | scripts/lib/real-ghidra-snapshot-lifecycle.mjs | 149 | `scripts/lib/real-ghidra-snapshot-lifecycle.mjs:149` |
| medium | Deletes files or directories | scripts/lib/real-ghidra-target-admission.mjs | 129 | `scripts/lib/real-ghidra-target-admission.mjs:129` |
| medium | Deletes files or directories | scripts/lib/real-ghidra-target-admission.mjs | 186 | `scripts/lib/real-ghidra-target-admission.mjs:186` |
| medium | Deletes files or directories | scripts/lib/real-hopper-boundaries.mjs | 491 | `scripts/lib/real-hopper-boundaries.mjs:491` |
| medium | Deletes files or directories | scripts/lib/real-hopper-source-binding.mjs | 76 | `scripts/lib/real-hopper-source-binding.mjs:76` |
| medium | Deletes files or directories | scripts/verify-adb.mjs | 224 | `scripts/verify-adb.mjs:224` |
| medium | Deletes files or directories | scripts/verify-adb.mjs | 276 | `scripts/verify-adb.mjs:276` |
| medium | Deletes files or directories | scripts/verify-adb.mjs | 364 | `scripts/verify-adb.mjs:364` |
| medium | Deletes files or directories | scripts/verify-agent-experience.mjs | 385 | `scripts/verify-agent-experience.mjs:385` |
| medium | Touches user-level config directories | scripts/verify-agent-experience.mjs | 81 | `scripts/verify-agent-experience.mjs:81` |

_288 more rows in report.json._

## Secrets and deserialization

_Are credentials committed, and does it load data in ways that can execute code? Secret values are redacted._

#### Secrets  _(pattern)_

| Severity | Finding | File | Line | Evidence |
|---|---|---|---|---|
| info | Hard-coded credential | scripts/fixtures/browser-network-site.mjs | 13 | `scripts/fixtures/browser-network-site.mjs:13` |
| info | Hard-coded credential | tests/boundary/process/ProcessEvidence.test.ts | 105 | `tests/boundary/process/ProcessEvidence.test.ts:105` |

#### Deserialization  _(pattern)_

_Nothing found._

## Agent safety

_Does any content in the target address an AI agent? An agent analyzing this target should treat such text as data._

#### Agent safety  _(pattern)_

| Severity | Finding | File | Line | Evidence |
|---|---|---|---|---|
| info | Text that addresses an AI agent | tests/boundary/mcp/promptMcp.test.ts | 73 | `tests/boundary/mcp/promptMcp.test.ts:73` |
| info | Text that addresses an AI agent | tests/boundary/mcp/promptMcp.test.ts | 81 | `tests/boundary/mcp/promptMcp.test.ts:81` |

#### Agent / MCP tools  _(pattern)_

| Tool | Declared via | File | Evidence |
|---|---|---|---|
| address_to_file_offset | tool definition | src/contracts/hopperMemoryContracts.ts | `src/contracts/hopperMemoryContracts.ts:17` |
| analyze_function | MCP tool contract | src/application/FunctionAnalysisEvidence.ts | `src/application/FunctionAnalysisEvidence.ts:21` |
| analyze_javascript_application | MCP tool contract | scripts/verify-claude-client.mjs | `scripts/verify-claude-client.mjs:155` |
| analyze_swift_types | MCP tool contract | src/server/registerEnhancedTools.ts | `src/server/registerEnhancedTools.ts:67` |
| analyze_web_bundle | MCP tool contract | src/server/registerBrowserTools.ts | `src/server/registerBrowserTools.ts:59` |
| batch_decompile | MCP tool contract | src/server/registerEnhancedTools.ts | `src/server/registerEnhancedTools.ts:65` |
| binary_overview | MCP tool contract | src/server/registerEnhancedTools.ts | `src/server/registerEnhancedTools.ts:69` |
| binary_session | MCP tool contract | src/server/registerSessionTools.ts | `src/server/registerSessionTools.ts:293` |
| build_call_path | MCP tool contract | src/server/registerInvestigationTools.ts | `src/server/registerInvestigationTools.ts:37` |
| capture_adb_screen | MCP tool contract | src/server/registerAdbTools.ts | `src/server/registerAdbTools.ts:35` |
| capture_browser_scenario | MCP tool contract | src/server/registerBrowserScenarioTool.ts | `src/server/registerBrowserScenarioTool.ts:32` |
| capture_electron_scenario | MCP tool contract | src/server/registerElectronTools.ts | `src/server/registerElectronTools.ts:65` |
| capture_process_scenario | MCP tool contract | src/server/registerSessionTools.ts | `src/server/registerSessionTools.ts:296` |
| capture_web_screenshot | MCP tool contract | src/server/registerBrowserTools.ts | `src/server/registerBrowserTools.ts:63` |
| close_binary | MCP tool contract | src/server/registerSessionTools.ts | `src/server/registerSessionTools.ts:292` |
| collect_adb_bugreport | MCP tool contract | src/server/registerAdbTools.ts | `src/server/registerAdbTools.ts:43` |
| compare_artifacts | MCP tool contract | src/server/registerSessionTools.ts | `src/server/registerSessionTools.ts:298` |
| compare_bundles | MCP tool contract | src/server/registerSessionTools.ts | `src/server/registerSessionTools.ts:300` |
| compare_functions | MCP tool contract | src/server/registerSessionTools.ts | `src/server/registerSessionTools.ts:299` |
| compare_process_captures | MCP tool contract | src/server/registerSessionTools.ts | `src/server/registerSessionTools.ts:297` |
| compare_web_captures | MCP tool contract | src/server/registerBrowserTools.ts | `src/server/registerBrowserTools.ts:62` |
| compare_web_screenshots | MCP tool contract | src/server/registerBrowserTools.ts | `src/server/registerBrowserTools.ts:64` |
| correlate_static_and_runtime | MCP tool contract | src/server/registerInvestigationTools.ts | `src/server/registerInvestigationTools.ts:41` |
| decode_android_resources | MCP tool contract | src/server/registerApktoolTools.ts | `src/server/registerApktoolTools.ts:27` |
| decompile_jeb_item | MCP tool contract | src/server/registerJebTools.ts | `src/server/registerJebTools.ts:43` |

_78 more rows in report.json._

## Configuration

_Which environment variables change behavior?_

#### Environment variables read  _(pattern)_

| Variable | Files | Evidence |
|---|---|---|
| PATH | 27 | `scripts/verify-agent-experience.mjs:67` |
| JAVA_HOME | 17 | `scripts/build-ghidra-nativeaot.mjs:38` |
| GHIDRA_INSTALL_DIR | 16 | `scripts/build-ghidra-nativeaot.mjs:20` |
| REA_VERIFY_RUNTIME_ROOT | 10 | `scripts/verify-claude-client.mjs:21` |
| REA_BROWSER_EXECUTABLE | 9 | `scripts/verify-browser-dom-destinations.mjs:10` |
| NODE_OPTIONS | 8 | `scripts/verify-commandcode-client.mjs:61` |
| REA_PWNTOOLS_PYTHON | 6 | `scripts/verify-binary-layout.mjs:29` |
| HOPPER_LAUNCHER_PATH | 5 | `scripts/verify-real-hopper-deadlines.mjs:36` |
| REA_CC | 5 | `scripts/verify-real-ghidra-noreturn.mjs:68` |
| REA_BROWSER_NO_SANDBOX | 4 | `scripts/verify-real-browser.mjs:69` |
| REA_PROCESS_RUN_ID | 4 | `scripts/verify-recorded-crash.mjs:35` |
| REA_PWNDBG_GDB | 4 | `scripts/verify-recorded-crash.mjs:20` |
| REA_VERIFY_STRACE_COMMAND | 4 | `scripts/verify-binary-layout.mjs:30` |
| TMPDIR | 4 | `scripts/verify-commandcode-client.mjs:192` |
| GHIDRA_HEADLESS_MAXMEM | 3 | `scripts/verify-real-ghidra-nativeaot.mjs:101` |
| HOME | 3 | `vitest.config.ts:17` |
| PLAYWRIGHT_BROWSERS_PATH | 3 | `vitest.config.ts:14` |
| REA_IDA_MCP_CONFIG | 3 | `scripts/verify-real-ida.mjs:23` |
| REA_ILSPY_CMD_PATH | 3 | `scripts/verify/managed/oracles.mjs:118` |
| REA_PWNDBG_GDBINIT | 3 | `scripts/verify-recorded-crash.mjs:241` |
| REA_WABT_BIN_DIRECTORY | 3 | `scripts/verify-wasm-artifact.mjs:20` |
| REA_WAKARU_COMMAND | 3 | `scripts/verify/javascript/recovery.mjs:19` |
| XDG_CACHE_HOME | 3 | `vitest.config.ts:17` |
| CODEX_HOME | 2 | `scripts/verify-agent-experience.mjs:81` |
| GHIDRA_MAXMEM | 2 | `scripts/lib/native-value-e2e.mjs:34` |

_146 more rows in report.json._

> Configuration that changes behavior without changing code.

## Blind spots

- Pattern rules see literal call sites only; wrappers that hide a capability behind another name are counted where the wrapper calls the real API.

## Safety contract

- Read-only: target files are opened O_RDONLY and never modified.
- No execution: nothing from the target is run, imported, or evaluated. Python is parsed with ast.parse.
- No network: Clearbox has no networking code; it analyzes a local directory only.
- Jailed: paths that resolve outside the target are refused; symlinks are not followed.
- Bounded: file count, per-file size, and total bytes read are capped.
- Redacted: secret values are masked and fingerprinted before they reach a report.
- Accountable: every file read is listed in the ledger with its SHA-256.

# Architecture overview: morluto/rea

Map an unfamiliar codebase: what it is made of, how it is organized, what it depends on, how you get in, and what it can do to the machine.

Clearbox 0.1.0 · 2,757 files read · 14.39s · ledger `5fed102b0b2f1991` · content `b10aecf811565ac6`

## What is it made of?

_How big is it, in which languages, and how much of it is tests?_

#### Shape of the target

- **Files:** 2,816 — 30.0 MB on disk
- **Lines of code:** 504,490 — across 2,530 source files
- **Test code:** 43% — 217,557 lines in test files
- **Languages:** 10 — TypeScript, JavaScript, Python
- **Skipped:** 0 — symlinks, oversized, or special files

#### Lines of code by language  _(parsed)_

- TypeScript: 434,176 lines
- JavaScript: 53,633 lines
- Python: 7,229 lines
- Java: 5,574 lines
- C++: 1,556 lines
- Swift: 1,332 lines
- C: 624 lines
- Shell: 224 lines
- Objective-C: 103 lines
- C#: 39 lines

## How is it organized?

_What are the major areas, and which areas depend on which?_

#### Areas  _(parsed)_

| Area | Files | Code lines | Main language | Test share | Evidence |
|---|---|---|---|---|---|
| tests | 753 | 135491 | TypeScript | 100% |  |
| src/domain | 466 | 101965 | TypeScript | 29% |  |
| src/application | 280 | 53967 | TypeScript | 28% |  |
| scripts | 284 | 53611 | JavaScript | 4% |  |
| src/browser | 113 | 24327 | TypeScript | 28% |  |
| src/ghidra | 57 | 14697 | TypeScript | 40% |  |
| src/process | 57 | 13894 | TypeScript | 42% |  |
| src/artifacts | 59 | 13190 | TypeScript | 17% |  |
| src/native | 54 | 11929 | TypeScript | 18% |  |
| src/dotnet | 31 | 9936 | TypeScript | 29% |  |
| src/contracts | 70 | 9907 | TypeScript | 13% |  |
| bridge | 27 | 8705 | Java | 3% |  |
| src/server | 76 | 7132 | TypeScript | 3% |  |
| src/hopper | 28 | 5889 | TypeScript | 16% |  |
| src/cli | 39 | 5365 | TypeScript | 0% |  |
| src/javascript | 23 | 5313 | TypeScript | 9% |  |
| src/adb | 7 | 4154 | TypeScript | 30% |  |
| src/ida | 20 | 3761 | TypeScript | 47% |  |
| src | 24 | 2658 | TypeScript | 25% |  |
| src/firmware | 10 | 2228 | TypeScript | 18% |  |
| src/android | 8 | 2156 | TypeScript | 0% |  |
| src/inspector | 8 | 1701 | TypeScript | 37% |  |
| src/apktool | 6 | 1675 | TypeScript | 36% |  |
| native | 5 | 1326 | C++ | 0% |  |
| src/reference | 8 | 1179 | TypeScript | 6% |  |

_17 more rows in report.json._

> Areas are top-level directories; any directory holding over 35% of the code is split one level deeper.

#### Module graph

- **Import edges:** 10,692 — between 2,357 source files
- **Third-party packages:** 82 — actually imported somewhere
- **Platform modules:** 71 — Node builtins, Python stdlib, Go std
- **Import cycles:** 27 — largest spans 6 files
- **Unresolved:** 154 — relative or aliased imports with no file

#### Who imports whom (by area)  _(parsed)_

| imports → | src/domain | src/application | scripts | src/browser | src/ghidra | src/process | src/artifacts | src/native | src/dotnet | src/contracts | src/server | src/hopper | src/cli | src/javascript |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **src/domain** | 1111 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **src/application** | 889 | 467 |  | 2 |  | 8 | 20 |  | 1 | 28 |  |  |  |  |
| **scripts** | 82 | 35 | 311 | 17 | 31 | 24 | 1 | 3 | 7 | 23 | 1 | 9 | 2 | 1 |
| **src/browser** | 257 | 30 |  | 215 |  | 8 | 16 |  |  |  |  |  |  | 2 |
| **src/ghidra** | 108 | 9 |  |  | 93 | 25 |  |  |  | 1 |  |  |  |  |
| **src/process** | 33 |  |  |  |  | 62 |  |  |  |  |  |  |  |  |
| **src/artifacts** | 75 | 4 |  |  |  | 3 | 118 | 2 |  | 2 |  |  |  | 1 |
| **src/native** | 103 | 9 |  |  |  | 22 | 8 | 71 |  | 3 |  |  |  |  |
| **src/dotnet** | 24 | 4 |  |  |  | 1 |  |  | 77 | 2 |  |  |  |  |
| **src/contracts** | 178 |  |  |  |  |  |  |  |  | 157 |  |  |  |  |
| **src/server** | 127 | 168 |  |  |  | 4 | 3 |  |  | 60 | 327 |  |  |  |
| **src/hopper** | 67 | 7 |  |  |  | 18 |  |  |  | 2 |  | 32 |  |  |
| **src/cli** | 83 | 51 |  | 1 |  |  | 6 |  |  | 3 |  |  | 52 |  |
| **src/javascript** | 70 | 6 |  |  |  | 16 | 7 |  |  |  |  |  |  | 38 |

> Row imports column. Counts are file-to-file import edges from non-test code. The diagonal is internal cohesion.

## Where is the weight?

_Which files would break the most if they changed, and which are largest?_

#### Load-bearing files (most imported)  _(parsed)_

| File | Imported by | Imports | Area | Evidence |
|---|---|---|---|---|
| src/domain/result.ts | 231 | 0 | src/domain | `src/domain/result.ts:1` |
| src/domain/jsonValue.ts | 215 | 1 | src/domain | `src/domain/jsonValue.ts:1` |
| src/domain/analysisErrorCore.ts | 202 | 2 | src/domain | `src/domain/analysisErrorCore.ts:1` |
| src/domain/analysisErrorBase.ts | 199 | 14 | src/domain | `src/domain/analysisErrorBase.ts:1` |
| src/domain/evidence.ts | 186 | 8 | src/domain | `src/domain/evidence.ts:1` |
| src/application/AnalysisProvider.ts | 143 | 15 | src/application | `src/application/AnalysisProvider.ts:1` |
| src/domain/unicodeCodePointOrder.ts | 115 | 0 | src/domain | `src/domain/unicodeCodePointOrder.ts:1` |
| src/domain/binaryTargetTypes.ts | 68 | 0 | src/domain | `src/domain/binaryTargetTypes.ts:1` |
| src/domain/digests.ts | 65 | 0 | src/domain | `src/domain/digests.ts:1` |
| src/contracts/toolContracts.ts | 55 | 24 | src/contracts | `src/contracts/toolContracts.ts:1` |
| src/artifacts/ArtifactReader.ts | 54 | 3 | src/artifacts | `src/artifacts/ArtifactReader.ts:1` |
| src/domain/analysisErrorProjection.ts | 52 | 14 | src/domain | `src/domain/analysisErrorProjection.ts:1` |
| src/server/EvidenceMcpServer.ts | 52 | 10 | src/server | `src/server/EvidenceMcpServer.ts:1` |
| src/domain/providerAdapterError.ts | 49 | 2 | src/domain | `src/domain/providerAdapterError.ts:1` |
| src/server/toolRegistrationOptions.ts | 46 | 2 | src/server | `src/server/toolRegistrationOptions.ts:1` |
| scripts/lib/verifier-run.mjs | 43 | 0 | scripts | `scripts/lib/verifier-run.mjs:1` |
| src/domain/browserObservation.ts | 42 | 0 | src/domain | `src/domain/browserObservation.ts:1` |
| scripts/lib/mcp-verifier-results.mjs | 40 | 2 | scripts | `scripts/lib/mcp-verifier-results.mjs:1` |
| src/contracts/toolContractTypes.ts | 38 | 2 | src/contracts | `src/contracts/toolContractTypes.ts:1` |
| src/application/investigation/InvestigationRecordPort.ts | 37 | 7 | src/application | `src/application/investigation/InvestigationRecordPort.ts:1` |
| src/server/analysisAdmission.ts | 36 | 5 | src/server | `src/server/analysisAdmission.ts:1` |
| src/domain/javascript/javascriptSemanticIr.ts | 35 | 3 | src/domain | `src/domain/javascript/javascriptSemanticIr.ts:1` |
| src/domain/javascript/javascriptAstValues.ts | 34 | 1 | src/domain | `src/domain/javascript/javascriptAstValues.ts:1` |
| src/domain/canonicalDigest.ts | 33 | 0 | src/domain | `src/domain/canonicalDigest.ts:1` |
| src/contracts/toolOutputSchemaPrimitives.ts | 33 | 7 | src/contracts | `src/contracts/toolOutputSchemaPrimitives.ts:1` |

> Fan-in counts non-test importers. Changing a hub ripples widely; rebuilding one first unblocks the most.

#### Largest source files  _(parsed)_

| File | Lines | Language | Evidence |
|---|---|---|---|
| bridge/ghidra/ReaGhidraBridge.java | 3840 | Java | `bridge/ghidra/ReaGhidraBridge.java:1` |
| src/adb/AdbProvider.ts | 2069 | TypeScript | `src/adb/AdbProvider.ts:1` |
| src/domain/native/nativeAotPe.ts | 1797 | TypeScript | `src/domain/native/nativeAotPe.ts:1` |
| src/process/capture/ProcessCaptureLifecycle.ts | 1530 | TypeScript | `src/process/capture/ProcessCaptureLifecycle.ts:1` |
| src/application/ClientConfigurationDocument.ts | 1459 | TypeScript | `src/application/ClientConfigurationDocument.ts:1` |
| scripts/verify-binary-layout.mjs | 1333 | JavaScript | `scripts/verify-binary-layout.mjs:1` |
| src/domain/javascript/javascriptSemanticAnalysis.ts | 1172 | TypeScript | `src/domain/javascript/javascriptSemanticAnalysis.ts:1` |
| bridge/hopper_bridge.py | 1162 | Python | `bridge/hopper_bridge.py:1` |
| src/dotnet/ManagedPe.fixture.ts | 1129 | TypeScript | `src/dotnet/ManagedPe.fixture.ts:1` |
| src/native/NativeMacOSProvider.ts | 1123 | TypeScript | `src/native/NativeMacOSProvider.ts:1` |
| src/domain/javascript/javascriptSemanticMemberMutations.ts | 1119 | TypeScript | `src/domain/javascript/javascriptSemanticMemberMutations.ts:1` |
| src/application/javascript/JavaScriptArtifactPathResolution.ts | 1087 | TypeScript | `src/application/javascript/JavaScriptArtifactPathResolution.ts:1` |
| src/process/ProcessOwnership.ts | 1038 | TypeScript | `src/process/ProcessOwnership.ts:1` |
| src/browser/WebSourceMapFetcher.ts | 1037 | TypeScript | `src/browser/WebSourceMapFetcher.ts:1` |
| src/hopper/HopperClient.ts | 1025 | TypeScript | `src/hopper/HopperClient.ts:1` |
| src/native/LldbCallTracer.ts | 1016 | TypeScript | `src/native/LldbCallTracer.ts:1` |
| scripts/verify-web-network-captures.mjs | 996 | JavaScript | `scripts/verify-web-network-captures.mjs:1` |
| scripts/lib/real-ghidra-boundaries.mjs | 930 | JavaScript | `scripts/lib/real-ghidra-boundaries.mjs:1` |
| src/ghidra/GhidraProviderClient.ts | 917 | TypeScript | `src/ghidra/GhidraProviderClient.ts:1` |
| src/ghidra/GhidraClient.ts | 913 | TypeScript | `src/ghidra/GhidraClient.ts:1` |
| src/process/capture/ProcessHarness.ts | 899 | TypeScript | `src/process/capture/ProcessHarness.ts:1` |
| src/domain/javascript/javascriptSemanticGraph.ts | 890 | TypeScript | `src/domain/javascript/javascriptSemanticGraph.ts:1` |
| src/domain/analysisSnapshot.ts | 853 | TypeScript | `src/domain/analysisSnapshot.ts:1` |
| bridge/native/rea_lldb_tracer.py | 839 | Python | `bridge/native/rea_lldb_tracer.py:1` |
| src/domain/javascript/javascriptSemanticValues.ts | 828 | TypeScript | `src/domain/javascript/javascriptSemanticValues.ts:1` |

#### Import cycles  _(parsed)_

| Files | Members | Evidence |
|---|---|---|
| 6 | src/process/DarwinProcessRunTokenReader.ts, src/process/ProcessOwnership.ts, src/process/ProcessOwnershipIdentity.ts, src/process/ProcessOwnershipObservation.ts, src/process/ProcessOwnershipProcessTree.ts, src/process/ProcessRunTokenObservations.ts | `src/process/DarwinProcessRunTokenReader.ts:14` |
| 5 | src/domain/analysisView/analysisView.ts, src/domain/analysisView/analysisViewCoverage.ts, src/domain/analysisView/binaryLayoutView.ts, src/domain/analysisView/javascriptApplicationView.ts, src/domain/analysisView/nativeFunctionView.ts | `src/domain/analysisView/analysisView.ts:21` |
| 4 | src/domain/process/processCapture.ts, src/domain/process/processCaptureCoverage.ts, src/domain/process/processCaptureValidation.ts, src/domain/process/processObservation.ts | `src/domain/process/processCapture.ts:16` |
| 4 | src/domain/managed/managedMemberComparison.ts, src/domain/managed/managedMemberComparisonCoverage.ts, src/domain/managed/managedMemberComparisonItems.ts, src/domain/managed/managedMemberComparisonMatch.ts | `src/domain/managed/managedMemberComparison.ts:15` |
| 3 | src/domain/apple/dyldPaths.ts, src/domain/apple/dylibResolution.ts, src/domain/apple/dylibResolutionFindings.ts | `src/domain/apple/dyldPaths.ts:5` |
| 3 | src/browser/CdpPageCapture.ts, src/browser/CdpPageCaptureScripts.ts, src/browser/CdpPageCaptureWorkers.ts | `src/browser/CdpPageCapture.ts:26` |
| 3 | src/dotnet/ManagedDecodeBudget.ts, src/dotnet/ManagedMetadataLayout.ts, src/dotnet/ManagedMetadataRowSizes.ts | `src/dotnet/ManagedDecodeBudget.ts:3` |
| 3 | src/ghidra/extensions/GhidraExtensions.ts, src/ghidra/extensions/nativeaot/NativeAotAdapter.ts, src/ghidra/extensions/nativeaot/NativeAotReport.ts | `src/ghidra/extensions/GhidraExtensions.ts:17` |
| 3 | src/application/Doctor.ts, src/application/DoctorDiagnostics.ts, src/application/DoctorScope.ts | `src/application/Doctor.ts:36` |
| 2 | scripts/website.py, scripts/website_i18n.py | `scripts/website.py:115` |
| 2 | src/domain/immutableJson.ts, src/domain/jsonValue.ts | `src/domain/immutableJson.ts:1` |
| 2 | src/domain/managed/managedApplicationGraph.ts, src/domain/managed/managedApplicationGraphNodes.ts | `src/domain/managed/managedApplicationGraph.ts:34` |
| 2 | src/domain/javascript/javascriptRuntimeReconciliationActive.ts, src/domain/javascript/javascriptRuntimeReconciliationCaptureParsing.ts | `src/domain/javascript/javascriptRuntimeReconciliationActive.ts:20` |
| 2 | src/domain/javascript/electronStaticAnalysisTypes.ts, src/domain/javascript/javascriptStaticAnalysisTypes.ts | `src/domain/javascript/electronStaticAnalysisTypes.ts:4` |
| 2 | src/domain/reconstructionCoverage.ts, src/domain/reconstructionCoverageEvaluation.ts | `src/domain/reconstructionCoverage.ts:19` |
| 2 | src/domain/analysisErrorPresentation.ts, src/domain/analysisErrorProjection.ts | `src/domain/analysisErrorPresentation.ts:31` |
| 2 | src/domain/javascript/javascriptStaticAnalysisFindings.ts, src/domain/javascript/javascriptStaticAnalysisState.ts | `src/domain/javascript/javascriptStaticAnalysisFindings.ts:7` |
| 2 | src/artifacts/SafeOutputTree.ts, src/artifacts/SafeOutputTreeCreationFailure.ts | `src/artifacts/SafeOutputTree.ts:21` |
| 2 | src/application/binary/AnalysisProviderEvaluation.ts, src/application/binary/AnalysisProviderRegistry.ts | `src/application/binary/AnalysisProviderEvaluation.ts:14` |
| 2 | src/dotnet/ManagedMetadataInventory.ts, src/dotnet/ManagedMetadataInventoryRows.ts | `src/dotnet/ManagedMetadataInventory.ts:16` |
| 2 | src/native/AppleMachoFixups.ts, src/native/AppleMachoSelection.ts | `src/native/AppleMachoFixups.ts:1` |
| 2 | src/native/AppleObjcCategories.ts, src/native/AppleObjcDispatchFacets.ts | `src/native/AppleObjcCategories.ts:3` |
| 2 | src/native/NativeUiHelperRuntime.ts, src/native/NativeUiObservation.ts | `src/native/NativeUiHelperRuntime.ts:9` |
| 2 | src/application/Uninstall.ts, src/application/UninstallFailure.ts | `src/application/Uninstall.ts:32` |
| 2 | src/application/Update.ts, src/application/UpdateFailure.ts | `src/application/Update.ts:6` |

_2 more rows in report.json._

> Strongly connected components of the import graph. Cycles make pieces hard to lift out on their own.

## What does it stand on?

_Which third-party packages does it declare, and which does it actually use?_

#### Declared dependencies

- **Runtime:** 38 — declared direct dependencies
- **Development:** 19 — build, lint, and test tooling
- **Locked packages:** 561 — in 1 lockfile(s)
- **Install hooks:** 1 — prepare

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

#### Lockfiles  _(parsed)_

| Lockfile | Packages | Evidence |
|---|---|---|
| package-lock.json | 561 | `package-lock.json:1` |

## How do you get in?

_Entry points, commands, agent tools, and HTTP routes a user or another program can call._

#### Entry points  _(pattern)_

| Kind | Name | Target | Evidence |
|---|---|---|---|
| manifest bin | rea | scripts/rea.mjs | `package.json:37` |
| manifest bin | rea-agents | scripts/rea.mjs | `package.json:38` |
| manifest main | rea-notes-example | main.js | `website/public/examples/notes-electron/package.json:5` |
| python __main__ | hopper_bridge | bridge/hopper_bridge.py | `bridge/hopper_bridge.py:1160` |
| python __main__ | launch_impl | bridge/pwndbg/launch_impl.py | `bridge/pwndbg/launch_impl.py:33` |
| python __main__ | layout_impl | bridge/pwntools/layout_impl.py | `bridge/pwntools/layout_impl.py:305` |
| python __main__ | recorded_crash_impl | bridge/pwntools/recorded_crash_impl.py | `bridge/pwntools/recorded_crash_impl.py:143` |
| python __main__ | audit-website-links | scripts/audit-website-links.py | `scripts/audit-website-links.py:134` |
| python __main__ | hopper-demo-x11 | scripts/hopper-demo-x11.py | `scripts/hopper-demo-x11.py:786` |
| python __main__ | prepare-website | scripts/prepare-website.py | `scripts/prepare-website.py:86` |
| python __main__ | test-website | scripts/test-website.py | `scripts/test-website.py:405` |
| python __main__ | verify-website | scripts/verify-website.py | `scripts/verify-website.py:460` |
| python __main__ | website | scripts/website.py | `scripts/website.py:266` |
| conventional name | cli | src/cli.ts | `src/cli.ts:1` |
| conventional name | main | src/main.ts | `src/main.ts:1` |

#### CLI commands  _(pattern)_

| Command | Declared via | File | Evidence |
|---|---|---|---|
| sync | argparse | scripts/website.py | `scripts/website.py:206` |
| check | argparse | scripts/website.py | `scripts/website.py:208` |
| links | argparse | scripts/website.py | `scripts/website.py:209` |
| new-page | argparse | scripts/website.py | `scripts/website.py:211` |
| translations | argparse | scripts/website.py | `scripts/website.py:215` |
| serve | argparse | scripts/website.py | `scripts/website.py:219` |
| DOM | commander/yargs | src/browser/execution/CdpEventListeners.ts | `src/browser/execution/CdpEventListeners.ts:28` |
| DOMDebugger | commander/yargs | src/browser/execution/CdpEventListeners.ts | `src/browser/execution/CdpEventListeners.ts:58` |
| Profiler | commander/yargs | src/browser/execution/CdpExecutionCapture.ts | `src/browser/execution/CdpExecutionCapture.ts:31` |
| Page | commander/yargs | src/browser/execution/CdpRuntimeSession.ts | `src/browser/execution/CdpRuntimeSession.ts:153` |
| Debugger | commander/yargs | src/browser/execution/CdpRuntimeSources.ts | `src/browser/execution/CdpRuntimeSources.ts:244` |

> Only commands declared with a literal name are found; names held in constants are not.

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

#### HTTP routes  _(pattern)_

_Nothing found._

## What can it do to your machine?

_Process, network, filesystem, and privilege capabilities found in production code._

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

## What changes its behavior?

_Environment variables the code reads._

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

- 107 dynamic imports use computed module names and could not be followed (e.g. scripts/generate-completion-ledger.mjs:45, scripts/generate-skill-metadata.mjs:20, scripts/generate-skill-metadata.mjs:23).
- 154 imports did not resolve to a file (14 use path aliases or package import maps).
- 284 imports point at build output (dist/, build/); they were mapped to the matching file under src/ by path, which assumes the usual one-to-one layout.
- Pattern rules see literal call sites only; wrappers that hide a capability behind another name are counted where the wrapper calls the real API.

## Safety contract

- Read-only: target files are opened O_RDONLY and never modified.
- No execution: nothing from the target is run, imported, or evaluated. Python is parsed with ast.parse.
- No network: Clearbox has no networking code; it analyzes a local directory only.
- Jailed: paths that resolve outside the target are refused; symlinks are not followed.
- Bounded: file count, per-file size, and total bytes read are capped.
- Redacted: secret values are masked and fingerprinted before they reach a report.
- Accountable: every file read is listed in the ledger with its SHA-256.

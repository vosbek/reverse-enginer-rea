# Feature trace: morluto/rea

Find where a feature lives, how execution reaches it, what it depends on, and a leaves-first plan to rebuild it.

Clearbox 0.1.0 · 2,757 files read · 14.47s · ledger `f0fb3cfabd819a21` · content `6b51f527c8620063`

Parameters: `feature=setup agent client configuration`

## Where it lives

_Which files implement the feature, and what is the evidence?_

#### Where 'setup agent client configuration' lives  _(heuristic)_

| File | Score | Keywords | Why | Evidence |
|---|---|---|---|---|
| src/application/SetupClientConfiguration.ts | 105 | client, configuration, setup | path has 'setup'; path has 'client'; path has 'configuration' | `src/application/SetupClientConfiguration.ts:266` |
| src/application/SetupHost.ts | 105 | agent, client, configuration, setup | path has 'setup'; 4 symbol(s) named 'setup'; 6 symbol(s) named 'client' | `src/application/SetupHost.ts:38` |
| src/application/SupportedClients.ts | 97 | agent, client, configuration, setup | path has 'client'; 1 symbol(s) named 'setup'; 10 symbol(s) named 'client' | `src/application/SupportedClients.ts:11` |
| src/cli/interactiveSetup.ts | 94 | agent, client, configuration, setup | path has 'setup'; 11 symbol(s) named 'client'; 4 symbol(s) named 'setup' | `src/cli/interactiveSetup.ts:14` |
| src/cli/setupCommands.ts | 94 | agent, client, configuration, setup | path has 'setup'; 8 symbol(s) named 'setup'; 4 symbol(s) named 'client' | `src/cli/setupCommands.ts:142` |
| src/application/ClientConfigurationDocument.ts | 88 | client, configuration, setup | path has 'client'; path has 'configuration'; 16 symbol(s) named 'client' | `src/application/ClientConfigurationDocument.ts:23` |
| src/application/ClientConfigurationFiles.ts | 87 | client, configuration, setup | path has 'client'; path has 'configuration'; 4 symbol(s) named 'client' | `src/application/ClientConfigurationFiles.ts:8` |
| src/application/SetupTypes.ts | 85 | client, configuration, setup | path has 'setup'; 13 symbol(s) named 'setup'; 3 symbol(s) named 'client' | `src/application/SetupTypes.ts:4` |
| src/application/SetupPlan.ts | 84 | client, configuration, setup | path has 'setup'; 4 symbol(s) named 'setup'; 8 symbol(s) named 'client' | `src/application/SetupPlan.ts:12` |
| src/application/Setup.ts | 83 | client, configuration, setup | path has 'setup'; 7 symbol(s) named 'setup'; 10 symbol(s) named 'client' | `src/application/Setup.ts:2` |

> Keywords: setup, agent, client, configuration. Score = path hits ×6 + symbol hits ×3 + content lines + 4 per distinct keyword.

#### Neighborhood  _(parsed)_

| File | Role | Links to seeds | Area | Evidence |
|---|---|---|---|---|
| src/application/SetupClientConfiguration.ts | seed | 23 | src/application | `src/application/SetupClientConfiguration.ts:1` |
| src/application/SetupHost.ts | seed | 27 | src/application | `src/application/SetupHost.ts:1` |
| src/application/SupportedClients.ts | seed | 32 | src/application | `src/application/SupportedClients.ts:1` |
| src/cli/interactiveSetup.ts | seed | 4 | src/cli | `src/cli/interactiveSetup.ts:1` |
| src/cli/setupCommands.ts | seed | 19 | src/cli | `src/cli/setupCommands.ts:1` |
| src/application/ClientConfigurationDocument.ts | seed | 13 | src/application | `src/application/ClientConfigurationDocument.ts:1` |
| src/application/ClientConfigurationFiles.ts | seed | 8 | src/application | `src/application/ClientConfigurationFiles.ts:1` |
| src/application/SetupTypes.ts | seed | 17 | src/application | `src/application/SetupTypes.ts:1` |
| src/application/SetupPlan.ts | seed | 9 | src/application | `src/application/SetupPlan.ts:1` |
| src/application/Setup.ts | seed | 18 | src/application | `src/application/Setup.ts:1` |
| src/application/Setup.fixture.ts | caller | 3 | src/application | `src/application/Setup.fixture.ts:1` |
| src/application/GeminiClientSettings.ts | caller | 3 | src/application | `src/application/GeminiClientSettings.ts:1` |
| src/application/UpdateMaintenance.ts | caller | 3 | src/application | `src/application/UpdateMaintenance.ts:1` |
| src/application/ClientRegistrationStatus.ts | caller | 3 | src/application | `src/application/ClientRegistrationStatus.ts:1` |
| src/application/Uninstall.ts | caller | 2 | src/application | `src/application/Uninstall.ts:1` |
| src/application/SetupClients.ts | caller | 2 | src/application | `src/application/SetupClients.ts:1` |
| src/application/DoctorScope.ts | caller | 1 | src/application | `src/application/DoctorScope.ts:1` |
| src/application/SetupSkill.ts | caller | 1 | src/application | `src/application/SetupSkill.ts:1` |
| scripts/verify-windows-package.mjs | caller | 1 | scripts | `scripts/verify-windows-package.mjs:1` |
| scripts/verify-package-environment.mjs | caller | 1 | scripts | `scripts/verify-package-environment.mjs:1` |
| src/cli.ts | caller | 1 | src | `src/cli.ts:1` |
| src/application/ClientRegistrationEnvironment.ts | caller | 1 | src/application | `src/application/ClientRegistrationEnvironment.ts:1` |
| src/application/Doctor.ts | dependency | 5 | src/application | `src/application/Doctor.ts:1` |
| src/application/ClientRegistrationIdentity.ts | dependency | 4 | src/application | `src/application/ClientRegistrationIdentity.ts:1` |
| src/identity.ts | dependency | 4 | src | `src/identity.ts:1` |

_12 more rows in report.json._

> Callers import a seed; dependencies are imported by one. Links count seed connections.

## How you reach it

_Which import chains lead from top-level files to the feature?_

#### How execution reaches it  _(parsed)_

1. **scripts/rea.mjs → src/cli.ts → src/cli/setupCommands.ts**

   ```
   scripts/rea.mjs
     └ src/cli.ts
       └ src/cli/setupCommands.ts
   ```
2. **src/cli.ts → src/cli/setupCommands.ts**

   ```
   src/cli.ts
     └ src/cli/setupCommands.ts
   ```

> Import chains from top-level files (entry points, or files nothing else imports) down to a seed. Each step's evidence is the import line.

## What it needs

_Packages, configuration, and host capabilities the feature depends on._

#### Packages this feature needs  _(parsed)_

| Package | Files in feature | Evidence |
|---|---|---|
| node:path | 13 |  |
| node:fs/promises | 11 |  |
| node:fs | 8 |  |
| zod | 5 |  |
| semver | 4 |  |
| node:os | 3 |  |
| node:util | 3 |  |
| write-file-atomic | 3 |  |
| node:child_process | 2 |  |
| node:crypto | 2 |  |
| node:url | 2 |  |
| jsonc-parser | 2 |  |
| incur | 2 |  |
| pino | 2 |  |
| node:stream | 1 |  |
| smol-toml | 1 |  |
| yaml | 1 |  |
| cross-spawn | 1 |  |
| @clack/prompts | 1 |  |

#### Configuration it reads  _(parsed)_

| Variable | Files | Evidence |
|---|---|---|
| HOPPER_LAUNCHER_PATH | 2 | `src/application/Doctor.ts:1` |
| XDG_CACHE_HOME | 1 | `src/application/UpdateRuntime.ts:156` |
| HOME | 1 | `src/config/homeDirectory.ts:14` |
| CODEX_HOME | 1 | `src/application/SupportedClients.ts:108` |
| XDG_CONFIG_HOME | 1 | `src/application/SupportedClients.ts:86` |
| REA_ILSPY_CMD_PATH | 1 | `src/application/Doctor.ts:324` |
| HERMES_DATA_DIR_SUFFIX | 1 | `src/application/HermesClientHome.ts:28` |
| LOCALAPPDATA | 1 | `src/application/HermesClientHome.ts:31` |
| HERMES_HOME | 1 | `src/application/HermesClientHome.ts:41` |
| APPDATA | 1 | `src/application/SupportedClients.ts:80` |
| CLAUDE_CONFIG_DIR | 1 | `src/application/SupportedClients.ts:102` |
| QWEN_HOME | 1 | `src/application/SupportedClients.ts:112` |
| GROK_HOME | 1 | `src/application/SupportedClients.ts:130` |
| SAND_DATA_ROOT | 1 | `src/application/SupportedClients.ts:137` |
| PI_CONFIG_DIR | 1 | `src/application/SupportedClients.ts:168` |
| OMP_PROFILE | 1 | `src/application/SupportedClients.ts:170` |
| PI_PROFILE | 1 | `src/application/SupportedClients.ts:170` |
| PI_CODING_AGENT_DIR | 1 | `src/application/SupportedClients.ts:183` |
| COPILOT_HOME | 1 | `src/application/SupportedClients.ts:223` |
| OPENCODE_CONFIG_DIR | 1 | `src/application/SupportedClients.ts:235` |
| OPENCODE_CONFIG | 1 | `src/application/SupportedClients.ts:259` |
| GEMINI_CLI_SYSTEM_SETTINGS_PATH | 1 | `src/application/SupportedClients.ts:314` |
| GEMINI_RESTRICTED_MODE | 1 | `src/application/SupportedClients.ts:321` |
| GEMINI_CLI_TRUST_WORKSPACE | 1 | `src/application/SupportedClients.ts:322` |
| GEMINI_CLI_SYSTEM_DEFAULTS_PATH | 1 | `src/application/SupportedClients.ts:330` |

_7 more rows in report.json._

#### What this feature does to the host  _(heuristic)_

| Severity | Capability | File | Line | Evidence |
|---|---|---|---|---|
| high | Spawns OS processes (Node child_process) | src/application/LinuxHopper.ts | 2 | `src/application/LinuxHopper.ts:2` |
| high | Spawns OS processes (Node child_process) | src/application/MacHopper.ts | 2 | `src/application/MacHopper.ts:2` |
| high | Spawns OS processes (Node child_process) | src/application/UpdateRuntime.ts | 5 | `src/application/UpdateRuntime.ts:5` |
| high | Spawns OS processes (Node child_process) | src/application/UpdateRuntime.ts | 51 | `src/application/UpdateRuntime.ts:51` |
| high | Requests elevated privileges | src/application/LinuxHopper.ts | 337 | `src/application/LinuxHopper.ts:337` |
| medium | Installs system software | src/application/LinuxHopper.ts | 329 | `src/application/LinuxHopper.ts:329` |
| medium | Installs system software | src/application/LinuxHopper.ts | 331 | `src/application/LinuxHopper.ts:331` |
| medium | Installs system software | src/application/LinuxHopper.ts | 333 | `src/application/LinuxHopper.ts:333` |
| medium | Installs system software | src/application/LinuxHopper.ts | 334 | `src/application/LinuxHopper.ts:334` |
| medium | Deletes files or directories | src/application/LinuxHopper.ts | 258 | `src/application/LinuxHopper.ts:258` |
| medium | Deletes files or directories | src/application/MacHopper.ts | 259 | `src/application/MacHopper.ts:259` |
| medium | Deletes files or directories | src/application/MacHopper.ts | 260 | `src/application/MacHopper.ts:260` |
| medium | Deletes files or directories | src/application/MacHopper.ts | 266 | `src/application/MacHopper.ts:266` |
| medium | Deletes files or directories | src/application/MacHopper.ts | 271 | `src/application/MacHopper.ts:271` |
| medium | Deletes files or directories | src/application/MacHopper.ts | 296 | `src/application/MacHopper.ts:296` |
| medium | Deletes files or directories | src/application/Uninstall.ts | 62 | `src/application/Uninstall.ts:62` |
| low | Writes files | src/application/SetupClientConfiguration.ts | 18 | `src/application/SetupClientConfiguration.ts:18` |
| low | Writes files | src/application/SetupClientConfiguration.ts | 183 | `src/application/SetupClientConfiguration.ts:183` |
| low | Writes files | src/application/SetupSkill.ts | 4 | `src/application/SetupSkill.ts:4` |
| low | Writes files | src/application/SetupSkill.ts | 145 | `src/application/SetupSkill.ts:145` |
| low | Writes files | src/application/Uninstall.ts | 14 | `src/application/Uninstall.ts:14` |
| low | Writes files | src/application/Uninstall.ts | 59 | `src/application/Uninstall.ts:59` |

## How to rebuild it

_In what order should the pieces be rebuilt, and which tests describe the original behavior?_

#### Rebuild blueprint (leaves first)  _(heuristic)_

1. **Step 1: foundations — 16 file(s)**

   ```
   src/application/ClientConfigPath.ts (support)
      exposes: resolveClientConfigTransactionPath
   src/application/DoctorProviderIds.ts (support)
      exposes: DOCTOR_PROVIDER_IDS
   src/application/HermesClientHome.ts (support)
      exposes: HermesClientPathError, resolveHermesClientHome
   src/application/LinuxHopper.ts (support)
      exposes: LinuxPackageFamily, LinuxHopperInstallDisclosure, linuxHopperInstallDisclosure, LinuxDistribution, LinuxHopperDownload, LinuxHopperInstallHost
      capabilities: Spawns OS processes (Node child_process); Requests elevated privileges; Installs system software
   src/application/SetupInstallFailure.ts (support)
      exposes: SetupFailureCode, SetupHopperInstallResult, HopperInstallFailureReason, setupInstallFailure
   src/artifacts/ArtifactReader.ts (support)
      exposes: ArtifactReaderFailureOptions, ArtifactEntry, copyArtifactEntry, sameArtifactEntry, ArtifactReader, ArtifactReaderFailure
   src/cli/types.ts (support)
      exposes: CliInstance
      needs packages: incur
   src/cliCommandNames.ts (support)
      exposes: CLI_COMMANDS, CLI_COMMAND_NAMES, CLI_COMMAND_ALIASES, CLI_COMMAND_TOOL_ALIASES, MCP_TOOLS_WITHOUT_DEDICATED_CLI
   src/cliLogging.ts (support)
      exposes: isCliOperationFailure, logCliCommand
      needs packages: pino
   src/config/homeDirectory.ts (support)
      exposes: homeDirectoryFromEnvironment
   src/domain/configurationErrors.ts (support)
      exposes: ConfigurationSettingIssue, ConfigurationErrorOptions, ConfigurationError, NoBinaryOpenError, BinaryTargetErrorOptions, BinaryTargetError
   src/domain/result.ts (support)
      exposes: Result, ok, err
   src/domain/runtimeVersion.ts (support)
      exposes: SUPPORTED_NODE_VERSION_RANGE, SUPPORTED_NODE_VERSION_PROSE, supportsNodeVersion, JavaScriptRuntime, javaScriptRuntime
      needs packages: semver
   src/domain/unicodeCodePointOrder.ts (support)
      exposes: compareUnicodeCodePoints, compositeKey
   src/identity.ts (support)
      exposes: PRODUCT_IDENTITY, SDK_IDENTITY
   src/mcpStartupPolicy.ts (support)
      exposes: MCP_STARTUP_POLICY
   ```
2. **Step 2: layer 2 — 6 file(s)**

   ```
   src/application/ClientRegistrationIdentity.ts (support)
      exposes: PackageRunner, invokingPackageRunner, withoutPackageRunnerIdentity, packageRunnerRegistrationCommand, npxRegistrationCommand, isOwnedClientRegistrationCommand
      needs packages: semver
   src/application/MacHopper.ts (support)
      exposes: macHopperInstallDisclosure, MacHopperInstallResult, MacHopperInstallHost, installMacHopper, systemMacHopperInstallHost
      needs packages: zod
      capabilities: Spawns OS processes (Node child_process); Deletes files or directories
   src/application/SupportedClients.ts (seed)
      exposes: SetupClient, GROK_BOT_MANUAL_REGISTRATION_REMEDIATION, manualRegistrationRemediation, SUPPORTED_CLIENT_DEFINITIONS, clientEvidencePaths, supportedClients
   src/application/UninstallFailure.ts (support)
      exposes: isUninstallFailure
   src/application/Update.ts (support)
      exposes: NpmInstallation, BunInstallation, UpdateInstallation, UpdateOutput, ReleaseLookupFailure, UpdateHost
      needs packages: semver
   src/artifacts/ArtifactResourceScope.ts (support)
      exposes: ArtifactResourceOwner, ArtifactCleanupAttempt, ArtifactResourceScope
   ```
3. **Step 3: layer 3 — 4 file(s)**

   ```
   src/application/ClientConfigurationDocument.ts (seed)
      exposes: ClientConfigurationFormat, ClientServersKey, ClientRegistrationDialect, ClientConfigurationDocument, clientConfigurationValuesEqual, clientConfigurationServersKey
      needs packages: jsonc-parser, smol-toml, yaml, zod
   src/application/RegularFileRead.ts (support)
      exposes: RegularFileReadOptions, RegularFileReadOutcome, RegularFileCleanupFailure, retryRegularFileCleanup, withRegularFile, readRegularFile
   src/application/UpdateFailure.ts (support)
      exposes: isUpdateFailure
   src/application/UpdateRuntime.ts (support)
      exposes: NpmInstallationHost, BunInstallationHost, runUpdateCommand, detectNpmInstallation, bunGlobalDirectory, detectBunInstallation
      needs packages: cross-spawn, semver
      capabilities: Spawns OS processes (Node child_process)
   ```
4. **Step 4: layer 4 — 2 file(s)**

   ```
   src/application/ClientRegistrationEnvironment.ts (support)
      exposes: clientRegistrationEnvironment
      needs packages: zod
   src/application/SetupSkill.ts (support)
      exposes: MANAGED_SKILL_FILES, isManagedSkillManifest, readSkillFile, SkillDestination, InstalledSkillIdentity, skillDestinations
      needs packages: write-file-atomic
      capabilities: Writes files
   ```
5. **Step 5: layer 5 — 3 file(s)**

   ```
   src/application/ClientConfigurationFiles.ts (seed)
      exposes: ClientConfigurationFileError, readConfigurationText, readConfigurationFile, readClientConfigurationFiles, effectiveClientConfiguration
   src/application/Doctor.ts (support)
      exposes: DoctorCheck, DoctorProviderCheck, DoctorProviderInspection, DoctorHost, DoctorReport, DoctorScope
   src/application/Uninstall.ts (support)
      exposes: UninstallFileSystem, UninstallItem, UninstallResult, UninstallHost, runUninstall, systemUninstallHost
      needs packages: write-file-atomic, zod
      capabilities: Deletes files or directories; Writes files
   ```
6. **Step 6: layer 6 — 3 file(s)**

   ```
   src/application/GeminiClientSettings.ts (support)
      exposes: readClientPolicyBlock
      needs packages: jsonc-parser, zod
   src/application/SetupRegistrationEnvironment.ts (support)
      exposes: providerRegistrationEnvironment
   src/application/SetupTypes.ts (seed)
      exposes: SetupProviderEnvironment, SetupInitialState, ClientConfigurationResult, ClientConfigurationInspection, SetupHost, SetupResult
   ```
7. **Step 7: layer 7 — 3 file(s)**

   ```
   src/application/SetupClientConfiguration.ts (seed)
      exposes: configureClientConfiguration, clientConfigurationAligned, inspectClientConfiguration
      needs packages: write-file-atomic
      capabilities: Writes files
   src/application/SetupPlan.ts (seed)
      exposes: SetupDiscovery, discoverSetupState, planSetupActions
   src/cli/interactiveSetup.ts (seed)
      exposes: confirmInteractiveSetup, renderSetupProgress, renderInteractiveSetupResult
      needs packages: @clack/prompts
   ```
8. **Step 8: layer 8 — 1 file(s)**

   ```
   src/application/SetupHost.ts (seed)
      exposes: setupRegistrationCommand, filterClientsNeedingConfigure, hostRemediation, systemSetupHost, detectClients
   ```
9. **Step 9: layer 9 — 1 file(s)**

   ```
   src/application/Setup.ts (seed)
      exposes: runSetup
   ```
10. **Step 10: composition — 1 file(s)**

   ```
   src/cli/setupCommands.ts (seed)
      exposes: registerSetupCommands
      needs packages: incur, pino
   ```

> Seeds plus two levels of their internal dependencies, ordered so each step only needs earlier steps. Build and test each step before the next.

#### Existing tests that exercise it  _(parsed)_

| Test file | Covers | Evidence |
|---|---|---|
| src/cliLogging.test.ts | src/application/Setup.ts, src/application/SetupTypes.ts, src/application/Uninstall.ts | `src/cliLogging.test.ts:1` |
| src/setupEnvironment.test.ts | src/application/ClientRegistrationIdentity.ts, src/application/Setup.ts, src/application/SetupHost.ts | `src/setupEnvironment.test.ts:1` |
| src/application/Doctor.systemHost.test.ts | src/application/Doctor.ts | `src/application/Doctor.systemHost.test.ts:1` |
| src/application/Doctor.test.ts | src/application/Doctor.ts, src/domain/runtimeVersion.ts | `src/application/Doctor.test.ts:1` |
| src/application/LinuxHopper.test.ts | src/application/LinuxHopper.ts | `src/application/LinuxHopper.test.ts:1` |
| src/application/MacHopper.test.ts | src/application/MacHopper.ts | `src/application/MacHopper.test.ts:1` |
| src/application/Setup.configuration.test.ts | src/application/Setup.ts, src/application/SetupHost.ts | `src/application/Setup.configuration.test.ts:1` |
| src/application/Setup.initialSnapshot.test.ts | src/application/Setup.ts | `src/application/Setup.initialSnapshot.test.ts:1` |
| src/application/Setup.planning.test.ts | src/application/Setup.ts, src/application/SetupTypes.ts | `src/application/Setup.planning.test.ts:1` |
| src/application/Setup.recovery.test.ts | src/application/Setup.ts, src/domain/runtimeVersion.ts | `src/application/Setup.recovery.test.ts:1` |
| src/application/Update.test.ts | src/application/Update.ts, src/application/UpdateRuntime.ts | `src/application/Update.test.ts:1` |
| src/application/UpdateRuntime.release.test.ts | src/application/UpdateRuntime.ts | `src/application/UpdateRuntime.release.test.ts:1` |
| src/domain/runtimeVersion.test.ts | src/domain/runtimeVersion.ts | `src/domain/runtimeVersion.test.ts:1` |
| src/ghidra/GhidraDoctor.test.ts | src/application/Doctor.ts, src/application/SetupRegistrationEnvironment.ts | `src/ghidra/GhidraDoctor.test.ts:1` |
| src/ida/IdaDoctor.test.ts | src/application/SetupRegistrationEnvironment.ts | `src/ida/IdaDoctor.test.ts:1` |
| tests/boundary/cli/packageRunnerRegistration.test.ts | src/application/ClientRegistrationIdentity.ts | `tests/boundary/cli/packageRunnerRegistration.test.ts:1` |
| tests/boundary/filesystem/clientConfigurationBom.test.ts | src/application/ClientConfigurationDocument.ts, src/application/SetupClientConfiguration.ts, src/application/SupportedClients.ts | `tests/boundary/filesystem/clientConfigurationBom.test.ts:1` |
| tests/boundary/filesystem/clientConfigurationDialects.test.ts | src/application/ClientRegistrationIdentity.ts, src/application/SetupClientConfiguration.ts, src/application/SupportedClients.ts | `tests/boundary/filesystem/clientConfigurationDialects.test.ts:1` |
| tests/boundary/filesystem/clientConfigurationEnvironment.test.ts | src/application/ClientConfigurationDocument.ts, src/application/SetupClientConfiguration.ts | `tests/boundary/filesystem/clientConfigurationEnvironment.test.ts:1` |
| tests/boundary/filesystem/clientConfigurationTransactions.test.ts | src/application/SetupClientConfiguration.ts, src/application/Uninstall.ts | `tests/boundary/filesystem/clientConfigurationTransactions.test.ts:1` |
| tests/boundary/filesystem/clientLifecycle.test.ts | src/application/SetupClientConfiguration.ts, src/application/SetupHost.ts, src/application/SupportedClients.ts | `tests/boundary/filesystem/clientLifecycle.test.ts:1` |
| tests/boundary/filesystem/evidenceBundleFiles.test.ts | src/application/RegularFileRead.ts | `tests/boundary/filesystem/evidenceBundleFiles.test.ts:1` |
| tests/boundary/filesystem/hermesClientConfiguration.test.ts | src/application/ClientRegistrationIdentity.ts, src/application/SetupClientConfiguration.ts, src/application/SupportedClients.ts | `tests/boundary/filesystem/hermesClientConfiguration.test.ts:1` |
| tests/boundary/filesystem/ompClientConfiguration.test.ts | src/application/SetupClientConfiguration.ts, src/application/SupportedClients.ts, src/application/Uninstall.ts | `tests/boundary/filesystem/ompClientConfiguration.test.ts:1` |
| tests/boundary/filesystem/piClientConfiguration.test.ts | src/application/ClientConfigurationDocument.ts, src/application/SetupClientConfiguration.ts, src/application/SetupHost.ts | `tests/boundary/filesystem/piClientConfiguration.test.ts:1` |

_11 more rows in report.json._

> Port these alongside the code: they are the executable spec of the original behavior.

## Open questions

_What should be confirmed before relying on this reading?_

#### Open questions before you rebuild  _(heuristic)_

1. **Deletes files or directories (7 site(s))**

   ```
   Static reading shows the call, not what it does at runtime. Confirm the exact programs, hosts, or paths involved before reproducing it.
   ```
2. **Writes files (6 site(s))**

   ```
   Static reading shows the call, not what it does at runtime. Confirm the exact programs, hosts, or paths involved before reproducing it.
   ```
3. **Spawns OS processes (Node child_process) (4 site(s))**

   ```
   Static reading shows the call, not what it does at runtime. Confirm the exact programs, hosts, or paths involved before reproducing it.
   ```
4. **Installs system software (4 site(s))**

   ```
   Static reading shows the call, not what it does at runtime. Confirm the exact programs, hosts, or paths involved before reproducing it.
   ```
5. **Requests elevated privileges (1 site(s))**

   ```
   Static reading shows the call, not what it does at runtime. Confirm the exact programs, hosts, or paths involved before reproducing it.
   ```
6. **32 environment variable(s) change behavior**

   ```
   Defaults and accepted values are worth confirming: XDG_CACHE_HOME, HOME, CODEX_HOME, XDG_CONFIG_HOME, HOPPER_LAUNCHER_PATH, REA_ILSPY_CMD_PATH, HERMES_DATA_DIR_SUFFIX, LOCALAPPDATA
   ```

> What static analysis cannot settle on its own.

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

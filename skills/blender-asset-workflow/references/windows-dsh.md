# Windows + DSH: setup through modeling verification

Use this guide only when DSH is the selected host for this Blender skill on native Windows. Web and headless are both valid workflows. A user choosing Web does not need to switch to headless; a CLI-only run does not require starting a Web server. For Blender installation and its scene-safe 30-second probe, use [Windows setup](windows-setup.md).

## Contents

- [Install and identify the runtime](#install-and-identify-the-runtime)
- [Choose Web or headless](#choose-web-or-headless)
- [Prepare an independent test workspace](#prepare-an-independent-test-workspace)
- [Configure credentials and the model](#configure-credentials-and-the-model)
- [Verify skill discovery and tool access](#verify-skill-discovery-and-tool-access)
- [Probe Blender and run the modeling test](#probe-blender-and-run-the-modeling-test)
- [Windows failures and recovery](#windows-failures-and-recovery)
- [Evidence and maintenance](#evidence-and-maintenance)

## Install and identify the runtime

First reuse an existing installation. Run these short checks in PowerShell:

```powershell
Get-Command node, npm.cmd, dsh.cmd, python -ErrorAction SilentlyContinue |
    Select-Object Name, Source
node --version
npm.cmd --version
python --version
dsh.cmd --version
dsh.cmd --help
```

Check each result separately; a later successful command does not erase an earlier failure. A WindowsApps Python alias is not a working interpreter. Standalone Python is used for local checks/supervision; Blender's bundled Python supplies `bpy`.

If DSH is absent and installation is requested, use the official npm package. Confirm Node requirements for the selected release using the [upstream repository](https://github.com/deepseek-ai/deepseek-harness) and npm metadata; record the actual versions. Node 24.14.0, npm 11.9.0 and DSH 0.2.1-rc.5 worked in the recorded test. This is a tested combination, not a claim that it is the latest or the minimum supported version.

```powershell
npm.cmd view '@deepseek-ai/dsh' version engines --json
# Reproduce the recorded release; select another version deliberately if needed.
npm.cmd install --global '@deepseek-ai/dsh@0.2.1-rc.5'
if ($LASTEXITCODE -ne 0) { throw "DSH install failed: $LASTEXITCODE" }
dsh.cmd --version
```

Install/download sequentially. Reuse the user's Node installation; do not run an unrequested upgrade. Keep npm output and the first failure if retrying. If the command is missing after a successful install, inspect `npm.cmd prefix --global`, look for `dsh.cmd` there, and invoke its absolute path. Add that existing directory to the user PATH only when setup is authorized, preserving existing entries. Open a new terminal to verify PATH changes; existing processes retain their old environment. `dsh.cmd` and `npm.cmd` avoid PowerShell choosing `.ps1` shims blocked by execution policy; no system-wide execution-policy change is needed.

## Choose Web or headless

| User workflow | Launch from the intended project | What counts as working |
|---|---|---|
| Interactive browser session | `dsh.cmd web` | A model response and actual skill/tool use in that Web session |
| One-shot CLI task | `dsh.cmd --profile headless '<task>'` | Successful final response, exit code, and required tool/artifact evidence |
| Headless with a local overlay | `dsh.cmd --profile headless --patch $Patch '<task>'` | Same checks, using the exact overlay/home intended for the task |

For Web, keep the hosting terminal/process alive and open the address it prints. The URL's access token is local UI authentication; do not publish it in screenshots or use it as an API key. `--no-open` suppresses automatic browser launch if desired. Closing the hosting process ends that Web server. The invoking directory is the default workspace: starting in a home directory can unintentionally give the task the wrong working directory.

Web credential setup and Web modeling can stay in Web. If later switching to headless, follow [DSH authentication](dsh-authentication.md) first: the tested headless profile ignores GUI-saved keys and sign-ins by default. Never instruct a user to save a key in Web and then assume stock headless can use it.

## Prepare an independent test workspace

For ordinary modeling, use the user's intended project and existing skill installation. The following optional recipe is for an explicitly requested clean-state compatibility test. It creates a unique directory, a separate `DSH_HOME`, and a project-local skill copy. It is not a VM or an OS security sandbox; it still uses the same Windows account, installed programs and process environment.

Start in an existing writable parent directory. Set `$SkillSource` to the installed or checked-out skill folder. This example uses the normal user installation. It copies only that folder, and refuses an existing target:

```powershell
$SkillSource = Join-Path $env:USERPROFILE '.agents\skills\blender-asset-workflow'
if (-not (Test-Path -LiteralPath (Join-Path $SkillSource 'SKILL.md') -PathType Leaf)) {
    throw 'Set SkillSource to an existing skill folder containing SKILL.md'
}
$TestRoot = Join-Path (Get-Location).Path ('dsh-blender-test-' + [guid]::NewGuid().ToString('N'))
$Project = Join-Path $TestRoot 'project'
$TestHome = Join-Path $TestRoot 'dsh-home'
$SkillParent = Join-Path $Project '.agents\skills'
$SkillTarget = Join-Path $SkillParent 'blender-asset-workflow'
if (Test-Path -LiteralPath $SkillTarget) { throw 'Skill target already exists; stop' }
New-Item -ItemType Directory -Path $SkillParent, $TestHome -ErrorAction Stop | Out-Null
Copy-Item -LiteralPath $SkillSource -Destination $SkillTarget -Recurse
$Patch = Join-Path $TestRoot 'test.patch.yml'
$SkillYamlPath = $SkillParent.Replace('\', '/').Replace("'", "''")
$PatchText = @"
- id: skill-filesystem
  config:
    includeDefaultRoots: false
    customSkillDirs:
      - '$SkillYamlPath'
    watch: false
"@
[IO.File]::WriteAllText($Patch, $PatchText, [Text.UTF8Encoding]::new($false))
```

This overlay restricts skill discovery to the copied folder's parent. Without it, default project/user roots can silently supply another installed copy. Do not edit the copied skill during the test. Record its source commit and file hashes before and after; ignore generated bytecode when comparing source files. Copying files alone does not prove host discovery.

For the test session, save the old home before selecting the new one. Keep the working directory and environment consistent throughout all following steps:

```powershell
$PreviousDshHome = [Environment]::GetEnvironmentVariable('DSH_HOME', 'Process')
$PreviousLocation = (Get-Location).Path
$env:DSH_HOME = $TestHome
Set-Location -LiteralPath $Project
```

After stopping this test's Web/CLI processes, restore the shell state, including after a failed test:

```powershell
[Environment]::SetEnvironmentVariable('DSH_HOME', $PreviousDshHome, 'Process')
Set-Location -LiteralPath $PreviousLocation
```

Keep artifacts and failed-attempt evidence until reviewed. No recursive cleanup is needed to finish this test. Reusing an existing target/home is a different test and must be described as such.

## Configure credentials and the model

Read [DSH authentication](dsh-authentication.md) and choose one path:

1. **Web only:** launch `dsh.cmd --profile web --patch $Patch` in the project, configure the provider's key or supported account login in that home, choose a model, and test there.
2. **Headless with injected API key:** supply the key locally through the process environment/secret mechanism; leave the managed store disabled. Include `$Patch` when invoking the probe so skill isolation stays active.
3. **Headless with a saved DSH credential:** add the restore entries to `$Patch`. With a new home, either configure credentials there or explicitly reference the original DSH store. Do not assume the new home has the old login.

Combine entries in one overlay; avoid duplicate entry IDs. Include the provider/model override when reproducibility requires it. Check the installed profile's configuration rather than assuming a Web selection is inherited by headless. The auth reference explains precedence and the difference between the API-key and account routes.

## Verify skill discovery and tool access

Before an expensive modeling run, create a random, non-secret local marker:

```powershell
$Marker = 'DSH_FILE_PROBE_' + [guid]::NewGuid().ToString('N')
[IO.File]::WriteAllText((Join-Path $Project 'probe.txt'), $Marker, [Text.UTF8Encoding]::new($false))
```

Send this task in the chosen Web session or headless invocation:

> Load blender-asset-workflow using the skill tool. Report the loaded skill path. Read probe.txt in the current workspace using a file tool and return its exact contents. Do not modify files or inspect credential files or other projects.

For headless:

```powershell
$ProbeTask = 'Load blender-asset-workflow using the skill tool and report its path. Read probe.txt using a file tool and return its exact contents. Do not modify files or inspect credentials or other projects.'
dsh.cmd --profile headless --patch $Patch --json $ProbeTask
if ($LASTEXITCODE -ne 0) { throw "DSH skill/tool probe failed: $LASTEXITCODE" }
```

Require an actual skill-tool load from the intended path and a file-tool result matching `$Marker`. A model saying it knows the skill is insufficient. `--json` provides events for this check; retain locally and summarize session ID, relevant tool calls, final outcome and exit code. Do not publish full event streams or model reasoning. Use a fresh session for a cold test; only pass `--session-id` when intentionally resuming from the same workspace.

When automating, opt into a supervisor with a chosen deadline, for example 120 seconds for this small probe and 900 seconds for a small modeling test. Record timeout separately from a model/tool error; those values are examples, not universal limits. On Windows, launch the Node executable and the installed DSH `lib/bin.js` as an argument list with `subprocess.CREATE_NO_WINDOW`, a fixed `cwd`, and a child-specific environment. Resolve the global package directory with `npm.cmd root --global`; do not hard-code a user's AppData path. Use `process.wait(timeout=...)`; on timeout terminate only that created PID tree (for example `taskkill.exe /PID <pid> /T /F`) and verify exit. Never terminate all `node.exe` or `blender.exe` processes. A deadline supervisor is not an RSS cap or a security boundary. Normal interactive modeling does not require enabling a resource guard.

## Probe Blender and run the modeling test

Skip Windows system-memory discovery in the normal workflow. `Get-CimInstance` or `systeminfo` access is not required to start Blender or build an asset. If a host already attempted a query and the sandbox denied it, note that memory information is unavailable, then proceed with one Blender process and inexpensive previews. Do not ask for elevation or try other commands merely to fill in that metric. Resource diagnostics/protection are a separate, explicitly requested workflow; an actual Blender failure still needs its own diagnosis.

Resolve the installed `blender.exe` by absolute path and set the child process's `BLENDER` environment value. A parent process with stale PATH may need its own PATH updated or the executable passed explicitly. If successful `bpy` execution is not already established for the same executable/environment in this task, run the separate factory-startup, 30-second probe from [Windows setup](windows-setup.md#bounded-scene-safe-connectivity-probe). It must print the version and exit successfully before reporting CLI connectivity. Installing `bpy` into standalone Python is not a repair for Blender discovery.

After that check, start the modeling script and produce the first saved candidate plus a cheap preview. Do not add routine GPU/Cycles device discovery, render-engine enumeration, or exploratory noise/material API probes. Inspect a specific capability only for an explicit requirement or an actual build/render failure; preserve the candidate while repairing that step. A diagnostic warning does not establish that an untested rendering path is unusable. If the user asks for progress, report the actual state briefly and continue the authorized task; do not end execution with a promise to continue later.

For a small modeling smoke test, give the chosen DSH surface this contract, replacing the output path with a **new absolute directory**:

> Load blender-asset-workflow and follow it. Build an original low-poly desk lamp about 0.45 m tall, with separate named base, stem, shade and bulb objects. Use the resolved Blender executable in a new factory-startup background process. Work only in this project and a new output directory. Save lamp.blend, write overall, side and opening-facing previews from that saved candidate, and actually inspect the image pixels. Reopen the BLEND in a fresh process and check dimensions, object structure and basic mesh defects. Preserve failed check reports when repairing. Use independent review if available; otherwise label the result self-check only. Deliver the BLEND, PNGs, scripts, verification, hashes and actual failures. Do not open, modify or save any existing user scene or change user preferences.

Do not feed a previous builder/model to the agent when claiming an original cold-start test. Avoid parallel Blender writers and output reuse. Use absolute paths for executables, scripts, BLEND files and output files; use PowerShell's call operator for an executable path held in a variable:

```powershell
# Set these variables to the actual new build paths before running.
& $env:BLENDER --background --factory-startup --python-exit-code 1 --python $BuildScript
if ($LASTEXITCODE -ne 0) { throw "Blender build failed: $LASTEXITCODE" }
& $env:BLENDER --background $Candidate --python-exit-code 1 --python $InspectScript -- --report $Report
if ($LASTEXITCODE -ne 0) { throw "Blender inspection failed: $LASTEXITCODE" }
```

The first command expects a task-specific builder that writes the new candidate explicitly. The second expects this skill's `inspect_scene.py`; set `$InspectScript` to its absolute path and `$Report` to a new file. Blender evaluates CLI arguments in order: load the candidate before the inspection script. Do not apply `--factory-startup` after loading a saved candidate. The bundled POSIX resource guard and Linux example runner are not Windows supervisors.

Acceptance requires more than exit 0:

- Saved `.blend` exists and reopens; the inspected file's SHA-256 matches the delivered candidate.
- Required PNGs exist, depict that saved candidate, and have actually been viewed. A terminal log saying “rendered” is not visual review.
- Measurements match the contract; check named parts when the constraint applies to a part. An overall lamp bounding box cannot test whether its base is circular.
- Relevant geometry defects and repairs are reported. Counts of passed assertions do not certify aesthetics, manifoldness, exact collisions or engine compatibility.
- State whether review was independent or only self-check. A fresh Blender process is not an independent reviewer.

Deliver clickable absolute local paths supported by the host, preview images, a compact report and remaining limitations. If that Web version cannot display an image inline, retain the PNG and provide a usable local path; do not claim an unseen preview was reviewed. Export/reimport GLB or another format only when requested, and report it untested otherwise.

## Windows failures and recovery

| Failure or observation | Recovery and accurate reporting |
|---|---|
| `.ps1` shim blocked / command not found | Use `.cmd`; inspect npm prefix and PATH, then test in a new terminal. Do not weaken execution policy globally |
| `--profile <name> is required` with an overlay | Use `dsh.cmd --profile headless --patch <absolute-path> ...` |
| Web works, headless reports missing credential | Follow the authentication reference; do not reinstall Blender or force the user to change surfaces |
| Skill missing or wrong copy loaded | Check invocation cwd, `.agents/skills/<name>/SKILL.md`, the skill-filesystem overlay and the actual loaded path |
| `all_proxy` names an unsupported SOCKS proxy | The observed release warned that it connected directly for that scheme. If the network requires a proxy, configure an actually available HTTP/HTTPS proxy endpoint before launch; changing `socks5://` text to `http://` cannot convert the proxy server |
| Browser opens but an automated Web health check returns 401 | Use the printed token flow and retain its session cookies through redirects. Do not disable Web authentication; an unauthenticated request is not a server-startup test |
| Port already in use | Identify the existing server or select another port supported by `dsh.cmd web --help`; do not kill unrelated processes |
| Blender missing from DSH despite a successful install | Check the DSH process's inherited PATH and exact executable; restart that host or pass an absolute path |
| MSI 1603 / access denied | Read the installer log; follow the per-user/portable options in Windows setup when appropriate. 1603 alone does not prove an ACL issue |
| Unicode text looks broken in PowerShell | Verify bytes with Python `read_text(encoding='utf-8')` before rewriting. Use UTF-8 files and PowerShell here-strings, not Bash heredocs |
| Blender thumbnail-cache write warning | Record it. Check actual save/reopen/render exit codes and files; do not silently ignore failures or treat an incidental cache warning as a failed scene save |
| Windows sandbox initialization reports `SetNamedSecurityInfoW` / `grantWrite` access denied | Distinguish host sandbox initialization from Blender execution. A nested restricted launcher failed in the recorded test; an authorized launch from the normal user context worked with DSH's own sandbox retained. Do not infer that Blender needs administrator rights or change ACLs from this error alone |
| Model/tool deadline expires | Report the timed-out stage and whether the owned process tree stopped. Preserve partial evidence; do not claim successful completion |

Do not dump all environment variables while investigating proxies or credentials. Report only the required configuration category and redacted error. Keep failures distinct: host authentication, provider inference, skill discovery, tool execution, Blender startup, modeling and artifact verification each need their own evidence.

## Evidence and maintenance

The repository's [recorded Windows DSH test](https://github.com/2409324124/blender-asset-workflow-skill/blob/main/tests/WINDOWS-DSH.md) covers the tested CLI/API-key path and its limits (the report is outside the installed skill folder). Interactive Web modeling is a separate acceptance path and was not established by that CLI result. A user's later Web test should record its own outcome before upgrading this claim.

Upstream references: [DSH CLI profiles and overlays](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md), [headless mode](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/headless/README.md), [skill filesystem](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md), and [authentication sources and mature-project patterns](dsh-authentication.md#references-and-documentation-patterns).

On DSH upgrades, verify the headless credential defaults, profile/overlay grammar, provider/model IDs, skill root precedence and Windows proxy behavior against the installed release, then repeat the small same-surface probe before modeling. Preserve older results as dated evidence; do not silently relabel them as validation of a new release.

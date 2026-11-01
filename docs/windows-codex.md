# Windows + Codex: install, connect, model

**Install skill → confirm loading → find/install Blender → 30-second connection test → model.**

Use a local Codex session running natively on Windows, with an intended project folder open and a working model connection. The PowerShell paths below refer to that Windows account. A WSL or hosted/cloud session has its own filesystem and executable environment; a Windows installation does not prove it works there.

## 1. Install the skill

The simplest route is to send this request to Codex. It installs the skill and checks connectivity; it does not authorize a Blender download:

> Install `skills/blender-asset-workflow` from https://github.com/2409324124/blender-asset-workflow-skill into my Windows user directory `~/.agents/skills/blender-asset-workflow`. Copy only that skill folder, including its references and scripts. Stop if the target already exists; do not overwrite it. Confirm that Codex discovers the installed skill and read its SKILL.md, reporting the loaded path. Check Python and locate an existing Blender. Follow the skill's Windows setup reference for one separate factory-startup background bpy probe with a 30-second timeout; print the Blender version and exit without opening or saving any user scene or preferences. If Blender is not found, explain the installation options and obtain permission before installing. If it is found but the probe fails, report and diagnose that failure instead of reinstalling. Report the actual results.

For native Windows, the personal destination is `%USERPROFILE%\.agents\skills\blender-asset-workflow` (PowerShell: `$env:USERPROFILE`). For project-only installation, use `<project>\.agents\skills\blender-asset-workflow`. Choose one scope and verify the loaded copy, especially when multiple copies exist. Only the skill bundle belongs there, not the whole repository or its showcase images.

### Optional manual PowerShell installation

Use this instead of the agent installation request. Run it from an existing writable working folder with Git available; prefer a short path to avoid Windows Git path-length limits. It clones into a new checkout for access to the source, then copies only the skill folder to the personal destination. The target-exists check runs before downloading anything.

```powershell
$ErrorActionPreference = 'Stop'
$SkillRoot = Join-Path $env:USERPROFILE '.agents\skills'
$Destination = Join-Path $SkillRoot 'blender-asset-workflow'
if (Test-Path -LiteralPath $Destination) {
    throw 'Skill target already exists; stop and inspect it before choosing an update'
}
$Checkout = Join-Path (Get-Location).Path ('blender-skill-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
git clone --depth 1 https://github.com/2409324124/blender-asset-workflow-skill.git $Checkout
if ($LASTEXITCODE -ne 0) { throw 'Repository clone failed; check access and Git output' }
$Source = Join-Path $Checkout 'skills\blender-asset-workflow'
if (-not (Test-Path -LiteralPath (Join-Path $Source 'SKILL.md') -PathType Leaf)) {
    throw 'Source skill is missing SKILL.md'
}
New-Item -ItemType Directory -Path $SkillRoot -Force | Out-Null
New-Item -ItemType Directory -Path $Destination -ErrorAction Stop | Out-Null
Get-ChildItem -LiteralPath $Source -Force |
    Copy-Item -Destination $Destination -Recurse -ErrorAction Stop
Get-Item -LiteralPath (Join-Path $Destination 'SKILL.md')
```

An existing or partially copied target is not an invitation to add `-Force` and overwrite it. Inspect it first; updating an existing installation is a separate choice. Keep the checkout outside the skill directory. This block copies files only; continue to discovery verification.

## 2. Confirm Codex loads it

Check the skill selector/catalog available in your Codex client. CLI and IDE users can use `/skills` or `$` to select a skill. Codex detects skill changes automatically; restart it if the new skill does not appear. These locations and discovery behavior follow the [official Codex skills documentation](https://learn.chatgpt.com/docs/build-skills).

Ask Codex:

> Load blender-asset-workflow from the installed skill catalog. Report the exact loaded SKILL.md path and read it. If the skill is not discovered, say so; do not treat a file listing as a successful load.

If it is missing, check the selected user/project scope, the folder nesting (`blender-asset-workflow/SKILL.md`), and whether the client is using native Windows or another environment. Resolve a wrong or stale copy before testing the workflow. Do not install a second copy merely to conceal a discovery failure.

## 3. Find Blender or install it with permission

Ask Codex to reuse a working installation and follow [Windows discovery](../skills/blender-asset-workflow/references/windows-setup.md#discover-before-downloading). Check Python by running it, and search for Blender beyond PATH, including per-user and portable installations. Blender provides the Python runtime that imports `bpy`; standalone Python is used for the bounded probe and supporting checks.

- **Blender found:** use its absolute executable path for the connection test. A missing PATH entry is not a missing installation.
- **Blender absent:** follow [installation choices and consent](../skills/blender-asset-workflow/references/blender-install.md#2-not-found-stop-and-ask). Choose guided manual installation or ask Codex to install it; review the proposed version, official source, location, administrator requirement and PATH changes before authorizing them.
- **Blender found but cannot run:** retain the error and diagnose it. Do not automatically download or reinstall Blender.

The existing [Windows setup guide](../skills/blender-asset-workflow/references/windows-setup.md) covers MSI versus portable ZIP, official checksum verification, interrupted downloads, installer logs, per-user installation and PATH. Reuse prior explicit authorization for the same installation plan; installing the skill alone is not that authorization. If standalone Python is missing, report that prerequisite and arrange its installation with permission before running the documented Python supervisor.

## 4. Run the 30-second connection test

Resolve the exact `blender.exe` path and set `$env:BLENDER` to it for the current PowerShell process. Run the [bounded Windows probe](../skills/blender-asset-workflow/references/windows-setup.md#bounded-scene-safe-connectivity-probe). It starts a separate hidden background process with `--factory-startup`, imports `bpy`, prints `BLENDER_PROBE_VERSION=...`, and exits. It does not open a user scene or save preferences.

Success requires the version marker and exit code 0 within 30 seconds. `blender --version`, a PATH entry or an installer exit code alone is not the connection test. Report a timeout or startup error as such. If this exact executable/environment already passed in the current task, reuse that evidence instead of repeating the probe. After an authorized PATH change, already-running Codex processes may retain the old PATH: use the absolute executable immediately, then verify command discovery in a newly opened terminal.

No separate preference initialization is required for ordinary background modeling. If you explicitly want preferences initialized, follow [initialization](../skills/blender-asset-workflow/references/windows-setup.md#initialization-and-optional-modeling-smoke-test); that intentionally writes configuration and is separate from this read-only probe.

## 5. Start modeling

Once the skill is loaded and Blender executes successfully, give Codex the actual model request. For example:

> Use blender-asset-workflow to make a simple low-poly wooden stool with a square seat, four legs and a height of about 45 cm. Work in a new output directory in this project. Deliver a .blend file and a preview that clearly shows the structure. Reuse the successful Blender probe, start building, reopen the final saved file and actually inspect the preview. Follow the skill's independent QA workflow and state any unavailable review capability or unresolved issue.

Codex writes task-specific Python and runs it through Blender CLI. Neither DSH nor a Blender MCP server is required. Use the direct Windows route; the repository's Linux example runner and POSIX resource guard are not Windows launchers. Do not block ordinary modeling on system-memory queries or repeat successful environment checks.

Delivery should identify the saved file and preview, actual verification and any failures. The [Windows DSH test record](../tests/WINDOWS-DSH.md) demonstrates Blender CLI on Windows under that host; it is not a claim that every Codex client/version or permission setup has been tested. Verify the loaded skill, executable and final artifacts in your own Codex session.

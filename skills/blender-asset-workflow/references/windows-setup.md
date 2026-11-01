# Windows setup and initialization

When the selected host is DSH, also read [Windows DSH](windows-dsh.md) for its installation, Web/CLI workflows, credentials, skill discovery and end-to-end modeling checks. Blender connectivity and host authentication are separate outcomes.

Use this reference when Blender is missing, CLI discovery fails, or the user requests Windows installation/initialization. Keep the modeling workflow in `SKILL.md`; do not reinstall a working environment on each task. A request to install this skill does not authorize downloading/installing Blender, changing PATH or saving preferences. If Blender is missing, stop and ask the user to choose guided or automatic installation, as in [Blender install](blender-install.md). Before an automatic install, list the version, source, location, admin rights and PATH changes, and proceed only after explicit consent.

## Discover before downloading

- Check standalone Python by actually running it (for example, `python --version`); a WindowsApps execution alias is not proof of a usable interpreter. Blender bundles its own Python for `bpy`; do not install `bpy` into standalone Python to repair CLI connectivity.
- Try the user's explicit executable, `Get-Command blender -ErrorAction SilentlyContinue`, then relevant installed-app records and usual locations under `Program Files\Blender Foundation` and `$env:LOCALAPPDATA\Programs\Blender Foundation`. Resolve a portable installation if the user already has one. Absence from PATH alone does not establish that Blender is uninstalled.
- Confirm OS architecture, for example `[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture`. Select x64 or ARM64 accordingly and check the chosen release's OS/GPU requirements. Do not hard-code a release number, username or drive.
- Run the bounded probe below against the resolved executable. On success, reuse it. If a found executable fails to start, times out or fails the `bpy` check, preserve its actual error/exit status and diagnose that specific failure; do not treat it as absence or automatically reinstall. Ask about installation only when discovery finds no installation route, or obtain separate consent for a specifically diagnosed repair. See the [three discovery outcomes](blender-install.md#1-detect-first).

## Download only when needed and authorized

1. Select a supported stable or LTS release from [Blender downloads](https://www.blender.org/download/) / [LTS](https://www.blender.org/download/lts/), respecting explicit version or project compatibility constraints. Read the actual [official release directory](https://download.blender.org/release/) for the selected version and architecture. Use the Windows MSI for an installed app or ZIP for a portable setup; avoid beta builds unless requested.
2. Download one package at a time into a known destination, with a `.part` name, bounded network timeouts and a finite retry budget (for example, three retries). On interruption, resume only when HTTP `206` and `Content-Range` confirm the requested byte offset. If the server returns a full `200` response, do not append it to the partial file. Preserve or replace that partial file deliberately and restart within the retry budget. If the remote file identity changes, restart rather than combining different versions.
3. Fetch the matching official `.sha256` file. Match the checksum entry's **whole filename**, not a substring: `package.msi` also occurs in `package.msix`. Require exactly one match. Compare SHA-256 for the complete downloaded bytes and check the expected size when supplied. A local hash without comparison to the official value is not verification.
4. Rename the verified `.part` to the final filename. On mismatch, stop and report it; do not run the package. Record release, architecture, source URL, size, checksum result and any download failure. Keep installers and temporary downloads outside the installed skill folder.

## Install and expose the executable

Use a verified MSI with logging and `/norestart`; a silent installer can fail without displaying an error. Wait for it and inspect the **process exit code** and log, rather than treating successful `Start-Process` invocation as completed installation. Exit code `0` means success; `3010` means success with a restart required. Report other codes and diagnose the log. `1603` is generic: it is not always a permissions problem.

For an MSI whose log identifies insufficient access to `Program Files` (for example, Error 1303), use an authorized elevated install or the package's supported per-user location. The Blender MSI tested in this workflow accepted `ALLUSERS=""` and `INSTALL_ROOT`; confirm these properties for the selected package before relying on them. A verified portable ZIP is another option when appropriate. Do not change directory ACLs to force installation.

Example per-user retry after confirming those MSI properties. `$Installer` is the absolute path to the verified MSI and `$InstallLog` is a new absolute log path chosen for this attempt; set both before running. Derive `$ReleaseSeries` from the selected package (major.minor), not from this document:

```powershell
$InstallRoot = Join-Path $env:LOCALAPPDATA "Programs\Blender Foundation\Blender $ReleaseSeries"
$MsiArgs = @('/i', ('"' + $Installer + '"'), '/qn', '/norestart',
    'ALLUSERS=""', ('INSTALL_ROOT="' + $InstallRoot + '"'),
    '/L*v', ('"' + $InstallLog + '"'))
$InstallProcess = Start-Process -FilePath 'msiexec.exe' -ArgumentList $MsiArgs -WindowStyle Hidden -Wait -PassThru
if ($InstallProcess.ExitCode -notin @(0, 3010)) {
    throw "MSI failed: $($InstallProcess.ExitCode); inspect $InstallLog"
}
if ($InstallProcess.ExitCode -eq 3010) { Write-Output 'Restart required; do not restart automatically' }
```

Locate the installed `blender.exe` and probe that exact path. For CLI setup, append its containing directory to the **user** PATH only if not already present (case-insensitive, ignoring a trailing separator); preserve all existing entries. Keep the directory unquoted in PATH. Already-running terminals/apps can retain their old environment: use the explicit executable now and verify `blender` from a newly opened terminal later. The repository tests accept `BLENDER` as an explicit executable path; this variable is a test convention, not a Blender installation requirement.

## Bounded, scene-safe connectivity probe

Set `$env:BLENDER` to the resolved executable path, without embedded quote characters. Run this in PowerShell with the standalone Python already verified above. It launches one hidden, separate factory-startup background process, imports `bpy`, prints the version and exits. It neither opens a user BLEND nor saves a scene or preferences.

```powershell
@'
import os, subprocess, sys

command = [
    os.environ["BLENDER"], "--background", "--factory-startup",
    "--python-exit-code", "1", "--python-expr",
    'import bpy; print("BLENDER_PROBE_VERSION=" + bpy.app.version_string)',
]
try:
    result = subprocess.run(
        command, timeout=30, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
except subprocess.TimeoutExpired:
    print("Blender probe timed out after 30 seconds", file=sys.stderr)
    sys.exit(124)
except OSError as error:
    print(f"Blender probe could not start: {error}", file=sys.stderr)
    sys.exit(1)
print(result.stdout, end="")
print(result.stderr, end="", file=sys.stderr)
if result.returncode:
    sys.exit(result.returncode)
if not any(line.startswith("BLENDER_PROBE_VERSION=") for line in result.stdout.splitlines()):
    print("Version marker missing; bpy probe not confirmed", file=sys.stderr)
    sys.exit(1)
'@ | python -
if ($LASTEXITCODE -ne 0) { throw "Blender probe failed: $LASTEXITCODE" }
```

This timeout supervises the direct Blender child only. The probe launches no descendants. It provides no RSS limit; the POSIX `guarded_run.py` and Linux example runner remain unsupported on Windows. See [runtime limits](runtime.md) before supervising modeling scripts.

## Initialization and optional modeling smoke test

Treat connectivity, preference initialization and modeling as separate outcomes. If the user requested initialization, inspect the running release's `bpy.utils.user_resource('CONFIG')` location. Preserve an existing `userpref.blend` and `startup.blend`. If preferences are absent, a separate factory-startup process can create the configuration directory and call `bpy.ops.wm.save_userpref()`; check its return status and the resulting file. This writes preferences intentionally and must not be described as the read-only probe. Do not save a startup scene or migrate another release's configuration unless requested.

When the user also requests a modeling smoke test, choose a small neutral asset in a new output directory. Use one background process at a time with a finite per-job timeout, then reopen the saved BLEND in a fresh process for inspection and preview rendering. Use **absolute paths** for scripts, scenes, reports and render outputs; verify that the renderer wrote to the intended directory. Actually view the resulting image and report the tested stages. Follow the skill's independent-review rules; successful rendering alone does not establish visual correctness or independent QA.

If the task also installs this skill, copying files is distinct from host discovery. Confirm that the host lists/loads the skill; an unavailable or timed-out discovery interface means unconfirmed discovery until later evidence establishes it.

Report the actual executable/version, Python availability, installation result (including any failed attempt), PATH/configuration changes, probe status/exit code and any uncompleted stage. Do not claim a successful probe certifies every Blender feature, external exporter or target engine.

Sources: [Windows installation](https://docs.blender.org/manual/en/latest/getting_started/installing/windows.html), [Windows CLI](https://docs.blender.org/manual/en/latest/advanced/command_line/launch/windows.html), [CLI arguments and ordering](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html).

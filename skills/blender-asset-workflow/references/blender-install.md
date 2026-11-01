# Installing Blender (all systems)

Read this when the `bpy` probe fails or Blender cannot be found. Installing this skill does **not** give permission to install Blender.

## 1. Detect first

1. Reuse a successful `bpy` execution from the current task with the same executable and environment. Otherwise resolve the user's explicit executable or discover an existing installation:
   - **Windows:** follow [Windows setup](windows-setup.md#discover-before-downloading).
   - **macOS:** `/Applications/Blender.app/Contents/MacOS/Blender` (also check `~/Applications`).
   - **Linux:** `command -v blender`, installed Snap/Flatpak records, and any unpacked Blender location the user names.
2. If an executable or installed launcher is found, run one minimal background factory-startup `bpy` probe against that exact route. Not being on PATH does not mean Blender is missing.
3. Classify the result before deciding what to do:
   - **Probe succeeds:** reuse this installation and proceed to the task-specific builder.
   - **No executable/installed launcher found after discovery:** report that discovery result and use section 2 to ask for installation consent.
   - **Executable/launcher found, but startup or probe fails:** retain the command, exit status, stderr and timeout result. Diagnose the observed failure narrowly (for example, access permissions, missing runtime dependencies, a launcher/path mistake or timeout). Do not label it “not installed,” automatically reinstall, or repeatedly increase timeouts. If a targeted repair needs installation, elevation or environment changes, explain it and obtain the appropriate consent first. If unresolved, report “found but not executable/validated” and the blocker; do not claim modeling succeeded.

A stale explicit path is not proof that no installation exists: finish discovery before entering the absent-installation branch.

## 2. Not found? Stop and ask

Only when discovery found no executable or installed launcher, stop and ask the user to pick one:

1. **I teach you:** give the manual steps below, one at a time.
2. **I install it for you:** first list
   - the version (recommend the current LTS from [Blender LTS](https://www.blender.org/download/lts/)),
   - the source (official URL or package manager),
   - the install location,
   - whether admin rights / `sudo` are needed,
   - any PATH changes.

   Install only after the user clearly says yes to that list.

If the user says no or does not answer, do not install anything. Report that Blender was not found by the checks performed and modeling cannot run yet.

## 3. Install by system

Get Blender only from [blender.org](https://www.blender.org/download/), the [official release directory](https://download.blender.org/release/) or the package managers below. Avoid beta builds unless asked.

### Windows

Use [Windows setup](windows-setup.md). It covers MSI/ZIP choice, checksum checks, per-user install and PATH.

### macOS

- **Manual:** download the `.dmg` for your chip (Apple Silicon or Intel) from [blender.org](https://www.blender.org/download/), open it and drag Blender into Applications. See the [macOS install guide](https://docs.blender.org/manual/en/latest/getting_started/installing/macos.html).
- **Automatic (with consent):** `brew install --cask blender` ([Homebrew cask](https://formulae.brew.sh/cask/blender)).
- The CLI path is `/Applications/Blender.app/Contents/MacOS/Blender`. See [macOS command line](https://docs.blender.org/manual/en/latest/advanced/command_line/launch/macos.html).

### Linux

- **Manual:** download the `.tar.xz` from [blender.org](https://www.blender.org/download/), unpack it to a folder you own and run `./blender` from there. See the [Linux install guide](https://docs.blender.org/manual/en/latest/getting_started/installing/linux.html).
- **Automatic (with consent):**
  - `sudo snap install blender --classic` ([Snap](https://snapcraft.io/blender)), or
  - `flatpak install flathub org.blender.Blender` ([Flathub](https://flathub.org/apps/org.blender.Blender)); run it as `flatpak run org.blender.Blender`.
- Distro packages (`apt`, `dnf`, …) can be old. Check the version before using them.

**Flatpak launcher versus executable path:** `flatpak run org.blender.Blender` is a direct command with separate arguments, not a single executable path. Repository `BLENDER` and `--blender` options accept one executable, not shell command text. Do not put that whole command string in either option or enable shell-string execution to make it work. For those interfaces, use an explicitly created executable wrapper whose body forwards arguments unchanged, for example:

```sh
#!/bin/sh
exec flatpak run org.blender.Blender "$@"
```

Give that wrapper a chosen path, make it executable with consent, and pass its path as `BLENDER`/`--blender`. Alternatively invoke Flatpak directly with separate arguments. Probe the selected route; Flatpak sandbox/file-access restrictions may differ from native Blender. No Flatpak runtime compatibility is claimed by this example.


## 4. Versions

Prefer the current LTS. This skill was tested with **Blender 4.3.2 on Linux** and **Blender 5.2.3 on Windows**. Other versions may work; report the version you used.

## 5. Verify

Re-run the `bpy` probe with the **new executable path** (a new terminal may be needed for PATH). Report the Blender version it prints. If it still fails, follow the found-but-failed diagnostic branch above; do not claim success or automatically reinstall again.

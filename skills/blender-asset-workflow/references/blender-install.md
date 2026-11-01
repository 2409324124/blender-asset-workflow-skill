# Installing Blender (all systems)

Read this when the `bpy` probe fails or Blender cannot be found. Installing this skill does **not** give permission to install Blender.

## 1. Detect first

1. Run the minimal `bpy` probe from `SKILL.md` (factory startup, background, prints the version). If it works, stop here.
2. If it fails, look in common places:
   - **Windows:** follow [Windows setup](windows-setup.md#discover-before-downloading).
   - **macOS:** `/Applications/Blender.app/Contents/MacOS/Blender` (also check `~/Applications`).
   - **Linux:** `which blender`, `snap list blender`, `flatpak info org.blender.Blender`, and any unpacked `blender-*-linux-x64/blender` the user names.
3. If you find one, run the probe against that exact path. Not being on PATH does not mean Blender is missing.

## 2. Not found? Stop and ask

You **must** stop and ask the user to pick one:

1. **I teach you:** give the manual steps below, one at a time.
2. **I install it for you:** first list
   - the version (recommend the current LTS from [Blender LTS](https://www.blender.org/download/lts/)),
   - the source (official URL or package manager),
   - the install location,
   - whether admin rights / `sudo` are needed,
   - any PATH changes.

   Install only after the user clearly says yes to that list.

If the user says no or does not answer, do not install anything. Report that Blender is missing and modeling cannot run.

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

## 4. Versions

Prefer the current LTS. This skill was tested with **Blender 4.3.2 on Linux** and **Blender 5.2.3 on Windows**. Other versions may work; report the version you used.

## 5. Verify

Re-run the `bpy` probe with the **new executable path** (a new terminal may be needed for PATH). Report the Blender version it prints. If it still fails, report the real error; do not claim success.

"""Copy a DSH profile and disable only the bundled skill in plugin 3.0.4.

The bridge and all other plugin tools remain installed. The source profile is
never modified. The pinned source hash prevents silently patching another build.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


EXPECTED_SOURCE_SHA256 = "2ce4c82fde86a388030079214fc6b68e34d31e5646221d20ad821eb588cc1f4f"
OLD = b"    registerBundledSkill(ctx);"
NEW = b"    // Experiment isolation: keep bridge tools, disable bundled skill provider."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_profile", type=Path)
    parser.add_argument("output_profile", type=Path)
    args = parser.parse_args()
    source = args.source_profile.resolve(strict=True)
    output = args.output_profile.absolute()
    plugin = source / "node_modules" / "dsh-blender-plugin"
    package = json.loads((plugin / "package.json").read_text())
    if package.get("version") != "3.0.4":
        parser.error("source profile must contain dsh-blender-plugin 3.0.4")
    entry = plugin / "lib" / "plugin.js"
    original = entry.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != EXPECTED_SOURCE_SHA256 or original.count(OLD) != 1:
        parser.error("plugin entry does not match the recorded 3.0.4 build")
    if output.exists() or output.is_symlink():
        parser.error("output profile already exists")
    # A profile under its own source cannot be copied safely.
    if output.resolve().is_relative_to(source):
        parser.error("output profile must be outside the source profile")
    if (source / "node_modules").is_symlink():
        parser.error("source node_modules must be a directory, not a symlink")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Always make a private physical plugin copy, including when pnpm links it
    # into a shared store. Never write through any source symlink.
    def ignore_plugin(directory, names):
        if Path(directory) == source / "node_modules":
            return {"dsh-blender-plugin"}
        return set()

    shutil.copytree(source, output, symlinks=True, ignore=ignore_plugin)
    copied_plugin = output / "node_modules" / "dsh-blender-plugin"
    shutil.copytree(plugin.resolve(), copied_plugin, symlinks=False)
    patched = original.replace(OLD, NEW)
    (copied_plugin / "lib" / "plugin.js").write_bytes(patched)
    print(json.dumps({
        "plugin_version": package["version"],
        "source_sha256": before,
        "modified_sha256": hashlib.sha256(patched).hexdigest(),
        "change": "disable registerBundledSkill only",
        "profile": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()

"""Rebuild one frozen trial skill pack from a checkout containing this report."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SUBTREE = 'skills/blender-asset-workflow'
BASE = 'd84ca8355ca558893cff7c16712a5909033ec549'
PR = '037f540451a6e897d5629af28bc9a15f28e0384e'
GEOMETRY = ('scripts/section_loft.py', 'references/parametric-surfaces.md')
STUDIO = ('scripts/surface_studio.py', 'references/surface-presentation.md')
ROUTES = [
    '- **Parameterized hard surfaces:** for repeated or varying sections and evenly spaced path features, read [parametric surfaces](references/parametric-surfaces.md).',
    '- **Surface presentation or material delivery:** for a controlled finish study or GLB appearance check, read [surface presentation](references/surface-presentation.md).',
]


def git_read(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def rebuild(arm, output):
    if output.exists():
        raise FileExistsError(output)
    revision = BASE if arm == 'B0' else PR
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as temp:
        scratch = Path(temp)
        pack = scratch / 'skill'
        for filename in git_read('ls-tree', '-r', '--name-only', revision, SUBTREE).decode().splitlines():
            dest = pack / Path(filename).relative_to(SUBTREE)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(git_read('show', f'{revision}:{filename}'))
        if arm in ('B2', 'B3'):
            candidates = scratch / 'candidates'
            for name in GEOMETRY + STUDIO:
                dest = candidates / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / SUBTREE / name, dest)
            subprocess.run(['patch', '-s', '-p1', '-i', str(HERE / 'frozen-candidate.patch')],
                           cwd=candidates, check=True)
            for name in GEOMETRY + (STUDIO if arm == 'B3' else ()):
                shutil.copyfile(candidates / name, pack / name)
            entry = pack / 'SKILL.md'
            marker = '## Default execution contract'
            lines = ROUTES if arm == 'B3' else ROUTES[:1]
            entry.write_text(entry.read_text().replace(marker, '\n'.join(lines) + '\n\n' + marker))
        manifest = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(pack).as_posix()}\n'
                           for p in sorted(pack.rglob('*')) if p.is_file())
        if manifest != (HERE / f'{arm}-files.sha256').read_text():
            raise ValueError('Reconstructed files differ from the recorded trial pack')
        pack.rename(output)
        return hashlib.sha256(manifest.encode()).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arm', choices=['B0', 'B1', 'B2', 'B3'])
    parser.add_argument('output', type=Path, help='New output directory')
    args = parser.parse_args()
    print(rebuild(args.arm, args.output.resolve()))

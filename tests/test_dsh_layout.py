"""Offline bundle contract fixtures, NOT a dsh provider/runtime implementation."""
import pathlib
import re
import shutil
import tempfile
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills/blender-asset-workflow'

class DshBundleLayoutTests(unittest.TestCase):
    def test_direct_bundle_frontmatter_and_helpers(self):
        with tempfile.TemporaryDirectory(prefix='dsh project ') as directory:
            root = pathlib.Path(directory) / '.dsh/skills'
            target = root / 'blender-asset-workflow'
            shutil.copytree(SOURCE, target)
            self.assertEqual(target.parent, root)
            text = (target / 'SKILL.md').read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'))
            front = text.split('---', 2)[1]
            self.assertRegex(front, r'(?m)^name: blender-asset-workflow$')
            self.assertRegex(front, r'(?m)^description: .+\S')
            for name in ['references/independent-qa.md', 'references/numeric-pitfalls.md',
                         'scripts/white_preview.py', 'scripts/png_privacy.py']:
                self.assertEqual((target/name).read_bytes(), (SOURCE/name).read_bytes())
            for match in re.finditer(r'\]\(((?:references|scripts)/[^)#]+)\)', text):
                self.assertTrue((target/match.group(1)).is_file())
    def test_existing_bundle_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)/'.dsh/skills/blender-asset-workflow'
            target.mkdir(parents=True)
            marker = target/'SKILL.md'
            marker.write_text('existing user copy — 用户内容', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                shutil.copytree(SOURCE, target)
            self.assertEqual(marker.read_text(encoding='utf-8'),'existing user copy — 用户内容')

    @unittest.skipUnless(shutil.which('bash'), 'Bash copy example not tested: bash unavailable')
    def test_documented_bash_copy_and_repeat_refusal(self):
        guide = (ROOT/'docs/dsh.md').read_text(encoding='utf-8')
        command = re.search(r'```bash\n(.*?)```', guide, re.S).group(1)
        with tempfile.TemporaryDirectory(prefix='dsh copy space ') as directory:
            project = pathlib.Path(directory)
            shutil.copytree(SOURCE, project/'skills/blender-asset-workflow')
            result = subprocess.run(['bash', '-c', command], cwd=project,
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            destination = project/'.dsh/skills/blender-asset-workflow'
            self.assertEqual((destination/'SKILL.md').read_bytes(), (SOURCE/'SKILL.md').read_bytes())
            marker = destination/'user-marker.txt'
            marker.write_text('用户内容', encoding='utf-8')
            result = subprocess.run(['bash', '-c', command], cwd=project,
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(encoding='utf-8'), '用户内容')

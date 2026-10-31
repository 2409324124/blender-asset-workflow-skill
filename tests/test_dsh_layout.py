"""Offline bundle contract fixtures, NOT a dsh provider/runtime implementation."""
import pathlib
import re
import shutil
import tempfile
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
            text = (target / 'SKILL.md').read_text()
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
            marker = target/'SKILL.md';marker.write_text('existing user copy')
            with self.assertRaises(FileExistsError):shutil.copytree(SOURCE,target)
            self.assertEqual(marker.read_text(),'existing user copy')

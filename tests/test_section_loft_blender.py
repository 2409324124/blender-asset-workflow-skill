from pathlib import Path
import subprocess
import tempfile
import unittest

from blender_executable import resolve_blender

BLENDER = resolve_blender()


@unittest.skipUnless(BLENDER, 'Set BLENDER to run the native saved-mesh fixture')
class SectionBlenderTests(unittest.TestCase):
    def test_saved_sections(self):
        fixture = Path(__file__).with_name('section_loft_scene.py')
        with tempfile.TemporaryDirectory() as output:
            run = subprocess.run([BLENDER, '-b', '--factory-startup', '--python-exit-code', '1',
                                  '--python', str(fixture), '--', output],
                                 capture_output=True, text=True, timeout=100)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            for arm in ('before', 'after'):
                self.assertTrue((Path(output) / f'{arm}.blend').is_file())
                self.assertTrue((Path(output) / f'{arm}.svg').is_file())

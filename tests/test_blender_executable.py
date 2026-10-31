import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch
from blender_executable import resolve_blender

class ExecutableTests(unittest.TestCase):
    def test_explicit_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='blender path ') as directory:
            path = pathlib.Path(directory)/('blender.exe' if os.name == 'nt' else 'blender')
            path.write_text('fixture');path.chmod(0o700)
            with patch.dict(os.environ, {'BLENDER': str(path)}):
                self.assertEqual(resolve_blender(), str(path))
    def test_invalid_explicit_fails(self):
        for value in ['', '/missing blender executable']:
            with patch.dict(os.environ, {'BLENDER': value}):
                with self.assertRaises(RuntimeError):resolve_blender()
    def test_default_missing_is_none(self):
        with patch.dict(os.environ, {}, clear=True), patch('shutil.which', return_value=None):
            self.assertIsNone(resolve_blender())

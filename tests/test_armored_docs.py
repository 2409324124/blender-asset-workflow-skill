"""Check packaged documentation/evidence, not vehicle realism or Blender geometry."""
import hashlib
import json
from pathlib import Path
import re
import struct
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


class ArmoredDocumentationTests(unittest.TestCase):
    def test_local_links_resolve(self):
        documents = [
            ROOT / 'skills/blender-asset-workflow/SKILL.md',
            ROOT / 'skills/blender-asset-workflow/references/armored-vehicles.md',
            ROOT / 'docs/cases/tunguska-refinement.md',
        ]
        for document in documents:
            for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', document.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                path = unquote(target.split('#', 1)[0])
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / path).is_file())

    def test_bundled_image_hashes_and_png_dimensions(self):
        evidence = json.loads((ROOT / 'docs/cases/tunguska-evidence.json').read_text())
        self.assertTrue(evidence['images'])
        for name, record in evidence['images'].items():
            path = (ROOT / name).resolve()
            with self.subTest(image=name):
                self.assertTrue(path.is_relative_to(ROOT / 'docs/showcase/tunguska'))
                data = path.read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'])
                self.assertGreater(record['width'], 0)
                self.assertGreater(record['height'], 0)
                if path.suffix == '.png':
                    self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
                    self.assertEqual(struct.unpack('>II', data[16:24]),
                                     (record['width'], record['height']))

    def test_evidence_is_portable_metadata(self):
        text = (ROOT / 'docs/cases/tunguska-evidence.json').read_text()
        self.assertNotIn('/workspace/', text)
        self.assertNotIn('/home/box/', text)
        evidence = json.loads(text)
        self.assertRegex(evidence['frozen_geometry_sha256'], r'^[0-9a-f]{64}$')
        self.assertEqual(evidence['frozen_geometry_sha256'],
                         evidence['presentation_r1_checks']['source_sha256'])


if __name__ == '__main__':
    unittest.main()

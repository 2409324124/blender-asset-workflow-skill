import math
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/blender-asset-workflow/scripts'))
from section_loft import SectionLoft, perimeter_samples


class SectionTests(unittest.TestCase):
    rectangle = [(0, 0), (3, 0), (3, 1), (0, 1)]

    def test_snapshot_drives_preview_and_mesh(self):
        ring = self.rectangle.copy()
        top = [(2*x, y + 2) for x, y in ring]
        solid = SectionLoft([(2, ring), (6, top)])
        ring.clear()
        verts, faces = solid.mesh()
        self.assertEqual(verts[4:], [(x, y, 6) for x, y in top])
        self.assertEqual(faces[0], (3, 2, 1, 0))
        self.assertEqual(faces[-1], (4, 5, 6, 7))
        directed = [(face[i-1], v) for face in faces for i, v in enumerate(face)]
        self.assertCountEqual(directed, [(v, u) for u, v in directed])
        polygons = ElementTree.fromstring(solid.svg()).findall('{*}polygon')
        for polygon, (_, loop) in zip(polygons, solid.stations):
            xy = [tuple(map(float, pair.split(','))) for pair in polygon.get('points').split()]
            self.assertEqual(xy, [(x, -y) for x, y in loop])
        self.assertEqual(len(polygons), 2)

    def test_invalid_stations(self):
        r = self.rectangle
        for stations in ([], [(0, r)], [(0, r), (0, r)], [(0, r), (math.inf, r)],
                         [(0, r), (1, r[:-1])], [(0, r), (1, r[::-1])]):
            with self.subTest(stations=stations), self.assertRaises(ValueError):
                SectionLoft(stations)

    def test_invalid_contours(self):
        for ring in ([(0, 0), (1, 0), (2, 0)], self.rectangle + [self.rectangle[0]],
                     [(0, 0), (1, 1), (0, 1), (1, 0)], [(0, 0), (math.nan, 0), (0, 1)],
                     [(0, 0), (3, 0), (1, .4), (0, 2)]):
            with self.subTest(ring=ring), self.assertRaises(ValueError):
                SectionLoft([(0, ring), (1, ring)])

    def test_uniform_distance_corner_and_seam(self):
        samples = perimeter_samples(self.rectangle, 8)
        self.assertEqual([p for p, _ in samples],
                         [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (2, 1), (1, 1), (0, 1)])
        self.assertEqual(samples[3][1], (0, 1))
        self.assertEqual(perimeter_samples(self.rectangle, 8, .875), samples[-1:] + samples[:-1])

    def test_roundoff_at_corners_uses_outgoing_edge(self):
        ring = [(0, 0), (12, 0), (12, 35), (0, 35)]
        samples = perimeter_samples(ring, 94)
        for i, pair in [(12, ((12, 0), (0, 1))), (47, ((12, 35), (-1, 0))),
                        (59, ((0, 35), (0, -1)))]:
            self.assertEqual(samples[i], pair)
        # Just before a corner but safely outside floating-point uncertainty.
        (x, y), tangent = perimeter_samples(ring, 1, (12 - 1e-9) / 94)[0]
        self.assertLess(x, 12)
        self.assertEqual((y, tangent), (0, (1, 0)))

    def test_bad_sampling_inputs(self):
        for count, phase in ((0, 0), (False, 0), (1, 1), (1, -.1), (1, math.nan)):
            with self.subTest(count=count, phase=phase), self.assertRaises(ValueError):
                perimeter_samples(self.rectangle, count, phase)
        with self.assertRaises(ValueError):
            perimeter_samples(self.rectangle + [self.rectangle[0]], 2)

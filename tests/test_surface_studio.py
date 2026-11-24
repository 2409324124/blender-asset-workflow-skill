"""Parameter boundaries and a rendered Blender-to-GLB round trip on an original gauge."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from blender_executable import resolve_blender

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/blender-asset-workflow/scripts"))
from surface_studio import PROFILES, QUALITY, parameters, render_still


class SurfaceParameters(unittest.TestCase):
    def test_material_boundaries(self):
        for role in PROFILES:
            self.assertIsInstance(parameters(role)["color"], tuple)
        before = parameters("glass")
        self.assertEqual(parameters("glass", color=[0, 0.1, 1], transmission=0,
                                    ior=3)["color"], (0, 0.1, 1))
        self.assertEqual(parameters("glass"), before)
        for values in ({"gloss": 1}, {"color": [1, 2]}, {"color": [0, -1, 1]},
                       {"roughness": float("nan")}, {"metallic": True},
                       {"transmission": 1.001}, {"ior": 0.99}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                parameters("glass", **values)
        with self.assertRaises(ValueError):
            parameters("chrome")

    def test_review_geometry_is_consistent_across_profiles(self):
        w, h, samples = QUALITY["preview"]
        fw, fh, fs = QUALITY["final"]
        self.assertEqual(w * fh, fw * h)
        self.assertGreater(fw, w)
        self.assertGreater(fs, samples)


    def test_publish_failures_preserve_the_destination_and_restore_state(self):
        scene = SimpleNamespace(
            name="test", render=SimpleNamespace(image_settings=SimpleNamespace(), filepath="original"),
            cycles=SimpleNamespace(), view_layers=[SimpleNamespace(material_override="source")])
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "review.png"
            # A dangling link is an existing destination, including when its target
            # is in another directory. Reject it before rendering.
            if sys.platform != "win32":
                missing = Path(directory) / "missing.png"
                dest.symlink_to(missing)
                with patch.dict(sys.modules, {"bpy": SimpleNamespace()}), self.assertRaises(FileExistsError):
                    render_still(scene, dest)
                self.assertFalse(missing.exists())
                dest.unlink()
            for failure in ("renderer", "cleanup", "competing_writer"):
                with self.subTest(failure=failure):
                    def render(**kwargs):
                        Path(scene.render.filepath).write_bytes(b"temporary render bytes")
                        if failure == "renderer":
                            raise RuntimeError("interrupted render")
                        if failure == "competing_writer":
                            dest.write_bytes(b"published by another writer")

                    fake = SimpleNamespace(ops=SimpleNamespace(render=SimpleNamespace(render=render)))
                    error = ValueError("invalid PNG") if failure == "cleanup" else None
                    with patch.dict(sys.modules, {"bpy": fake}), patch("png_privacy.clean_file", side_effect=error):
                        with self.assertRaises((RuntimeError, ValueError, FileExistsError)):
                            render_still(scene, dest, override="gray")
                    self.assertEqual(scene.render.filepath, "original")
                    self.assertEqual(scene.view_layers[0].material_override, "source")
                    if failure == "competing_writer":
                        self.assertEqual(dest.read_bytes(), b"published by another writer")
                        dest.unlink()
                    self.assertEqual(list(Path(directory).iterdir()), [])


BLENDER = resolve_blender()


@unittest.skipUnless(BLENDER, "set BLENDER or PATH for actual GLB and image comparisons")
class SurfaceBlenderTests(unittest.TestCase):
    def test_exported_appearance(self):
        with tempfile.TemporaryDirectory() as temp:
            run = subprocess.run([BLENDER, "-b", "--factory-startup", "-t", "4",
                                  "--python-exit-code", "1", "--python", str(ROOT / "tests/surface_fixture.py"),
                                  "--", temp], capture_output=True, text=True, timeout=240)
            self.assertEqual(run.returncode, 0, (run.stdout + run.stderr)[-4000:])
            result = json.loads((Path(temp) / "metrics.json").read_text())
            # Fixture-specific tolerances allow CPU sampling/denoiser variation.
            portable = result["portable_vs_import"]["mean_absolute_rgb_8bit"]
            native_effect = result["native_grain_effect"]["mean_absolute_rgb_8bit"]
            self.assertLess(portable, 1)
            self.assertGreater(native_effect, 0.3)
            self.assertGreater(result["grain_vs_import"]["mean_absolute_rgb_8bit"], portable + 0.25)
            self.assertLess(result["imported_grain_effect"]["mean_absolute_rgb_8bit"], 0.15)
            self.assertEqual(result["grain_glb"]["image_textures"], 0)

"""Blender numeric verification for the portable blade example; no image QA.

Run with Blender --background --factory-startup --python-exit-code 2.
SPDX-License-Identifier: GPL-3.0-only
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile

import bpy
import bmesh


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def coordinates(mesh):
    return [tuple(v.co) for v in mesh.vertices]


def topology(mesh):
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        return {"vertices": len(bm.verts), "faces": len(bm.faces),
                "non_manifold_edges": sum(not e.is_manifold for e in bm.edges),
                "inconsistent_edges": sum(not e.is_contiguous for e in bm.edges),
                "degenerate_faces": sum(f.calc_area() <= 1e-16 for f in bm.faces),
                "signed_volume_m3": bm.calc_volume(signed=True)}
    finally:
        bm.free()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", type=Path, default=Path(__file__).resolve().parents[1]
                        / "skills/blender-asset-workflow/scripts/parametric_blade.py")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--compare-source", type=Path,
                        help="Optional owner-local CFM56 geometry.py comparison")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if args.report.exists():
        raise FileExistsError(args.report)
    before = (len(bpy.data.scenes), len(bpy.data.objects), len(bpy.data.meshes))
    example = load(args.example, "blade_example")
    checks = []

    def check(name, passed, **detail):
        checks.append({"name": name, "passed": bool(passed), **detail})

    check("import creates no scenes, objects or meshes", before ==
          (len(bpy.data.scenes), len(bpy.data.objects), len(bpy.data.meshes)))
    law = copy.deepcopy(example.FAN_LAW)
    parameters = {"x": 0.34, "rh": 0.7747 * 0.268, "rt": 0.7747,
                  "nspan": 12, "nchord": 24}
    mesh, sections = example.blade("Verify.Default", law=law, **parameters)
    base = coordinates(mesh)

    def inspect(name, candidate, params):
        topo = topology(candidate)
        check(name + ": closed, oriented, nondegenerate, positive volume",
              topo["non_manifold_edges"] == topo["inconsistent_edges"] == topo["degenerate_faces"] == 0
              and topo["signed_volume_m3"] > 0, topology=topo)
        points = coordinates(candidate)
        check(name + ": finite coordinates", all(math.isfinite(v) for p in points for v in p))
        size = 2 * params["nchord"] + 1
        error = max(abs(math.hypot(p[1], p[2]) - (params["rh"] +
                    (i // size) / params["nspan"] * (params["rt"] - params["rh"])))
                    for i, p in enumerate(points))
        check(name + ": all section vertices keep prescribed radius", error < 2e-7,
              max_radius_error_m=error)
        return points

    inspect("default", mesh, parameters)
    variants = [
        ("tip_radius", {"rt": 0.790}, {}),
        ("chord_scale", {"scale": 1.1}, {}),
        ("thickness", {}, {"thickness_ratio": [v * 1.1 for v in law["thickness_ratio"]]}),
        ("twist", {}, {"twist_deg": [v + 5 for v in law["twist_deg"]]}),
        ("camber", {}, {"camber": 0.038}),
        ("sweep", {}, {"axial_sweep_m": 0.036}),
        ("lean", {}, {"lean_rad": 0.032}),
        ("station", {"x": 0.44}, {}),
        ("sampling", {"nspan": 24, "nchord": 48}, {}),
    ]
    for name, edits, law_edits in variants:
        params = {**parameters, **edits}
        candidate, _ = example.blade("Verify." + name, law={**law, **law_edits}, **params)
        points = inspect(name, candidate, params)
        changed = len(points) != len(base) or max(math.dist(a, b) for a, b in zip(base, points)) > 1e-6
        check(name + ": geometry responds", changed)
        if name == "station":
            error = max(math.dist((a[0] + 0.1, a[1], a[2]), b) for a, b in zip(base, points))
            check("station changes only axial position by 0.1 m", error < 2e-7, max_error_m=error)
        if name == "sweep":
            size = 2 * parameters["nchord"] + 1
            error = max(math.dist((a[0] + .01 * ((i // size) / parameters["nspan"])**2,
                                  a[1], a[2]), b) for i, (a, b) in enumerate(zip(base, points)))
            check("sweep produces the prescribed axial offset without radial changes",
                  error < 2e-7, max_error_m=error)

    repeated, _ = example.blade("Verify.RepeatedDefault", law=law, **parameters)
    check("repeated default reproduces identical vertex coordinates", coordinates(repeated) == base)
    try:
        example.blade("Verify.Invalid", law=law, **{**parameters, "rt": 0.1})
    except ValueError:
        check("invalid radial domain is rejected", True)
    else:
        check("invalid radial domain is rejected", False)
    scene = example.demo()
    blades = [o for o in scene.objects if o.type == "MESH"]
    check("demo has 24 blade objects sharing one mesh", len(blades) == 24
          and len({o.data.as_pointer() for o in blades}) == 1)
    check("demo blades share one rotor parent", len({o.parent.as_pointer() for o in blades}) == 1)
    check("demo array angles follow one full turn about X", all(
        abs(o.rotation_euler.x - 2 * math.pi * i / 24) < 5e-7
        and o.rotation_euler.y == o.rotation_euler.z == 0
        for i, o in enumerate(sorted(blades, key=lambda o: o.name))))
    with tempfile.TemporaryDirectory(prefix="blade-existing-") as directory:
        existing = Path(directory) / "existing.blend"
        existing.write_bytes(b"existing-output-sentinel")
        before = (len(bpy.data.scenes), len(bpy.data.objects), len(bpy.data.meshes),
                  bpy.context.window.scene.as_pointer() if bpy.context.window else None)
        refused = False
        try:
            example.demo(save=existing)
        except FileExistsError:
            refused = True
        after = (len(bpy.data.scenes), len(bpy.data.objects), len(bpy.data.meshes),
                 bpy.context.window.scene.as_pointer() if bpy.context.window else None)
        check("existing output is refused before scene changes", refused and before == after
              and existing.read_bytes() == b"existing-output-sentinel")

    comparison = None
    if args.compare_source:
        original = load(args.compare_source, "owner_cfm_geometry")
        material = bpy.data.materials.new("Verify.Comparison")
        reference, _ = original.blade("Verify.Original", law=law, mat=material, **parameters)
        error = max(math.dist(a, b) for a, b in zip(base, coordinates(reference)))
        # Blender may rotate a polygon's starting index between the two bmesh passes.
        def canonical_face(polygon):
            indices = list(polygon.vertices)
            start = indices.index(min(indices))
            return tuple(indices[start:] + indices[:start])
        same_topology = sorted(canonical_face(p) for p in reference.polygons) == sorted(
            canonical_face(p) for p in mesh.polygons)
        check("owner-local source: default coordinates and oriented face cycles match",
              len(reference.vertices) == len(base) and error < 2e-7 and same_topology,
              max_coordinate_error_m=error)
        comparison = {"source_label": "cfm56_7b_parametric/src/geometry.py",
                      "sha256": hashlib.sha256(args.compare_source.read_bytes()).hexdigest(),
                      "scope": "Owner-local source comparison; the historical engine project is not bundled"}

    result = {"schema_version": 1, "passed": all(c["passed"] for c in checks),
              "blender_version": bpy.app.version_string,
              "example_sha256": hashlib.sha256(args.example.read_bytes()).hexdigest(),
              "verification_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "parameters": parameters, "law": law, "variants": variants,
              "checks": checks, "owner_local_comparison": comparison,
              "scope": "Numeric source-mesh checks on one default and nine independent variants; no render, modifier, export, aerodynamic or full-engine verification"}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"passed": result["passed"], "checks": len(checks),
                      "failed": [c["name"] for c in checks if not c["passed"]]}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

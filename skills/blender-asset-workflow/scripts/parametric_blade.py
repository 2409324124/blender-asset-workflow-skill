"""Runnable radial-blade example: metres, +X axis, static sampled mesh.

Adapted from the owner's CFM56 display-study geometry (interp3/mesh_data/blade).
SPDX-License-Identifier: GPL-3.0-only
The shape values describe a display study, not a manufacturer's airfoil.
Importing this file does not create objects or modify a scene.
"""
import argparse
import json
import math
from pathlib import Path
import sys


FAN_LAW = {
    "chord_m": [0.105, 0.264, 0.270],
    "thickness_ratio": [0.145, 0.065, 0.032],
    "twist_deg": [64.0, 44.0, 28.0],
    "camber": 0.028,
    "axial_sweep_m": 0.026,
    "lean_rad": 0.022,
}


def interp3(values, s):
    """Piecewise-linear root/mid/tip law, with s in [0, 1]."""
    i = min(1, int(s * 2))
    q = s * 2 - i
    return values[i] * (1 - q) + values[i + 1] * q


def blade(name, x, rh, rt, law, nspan=12, nchord=24, scale=1.0):
    """Return (closed Blender Mesh, section metadata); add no scene objects.

    x/rh/rt/chord/sweep use metres; twist uses degrees; lean uses radians.
    nspan is an interval count: the mesh has nspan + 1 radial sections.
    scale changes chord only; it is not an overall object scale.
    """
    import bpy
    import bmesh

    scalars = [x, rh, rt, scale, law["camber"], law["axial_sweep_m"], law["lean_rad"]]
    for key in ("chord_m", "thickness_ratio", "twist_deg"):
        if len(law[key]) != 3:
            raise ValueError(f"{key} requires root, mid and tip values")
        scalars.extend(law[key])
    if not all(math.isfinite(v) for v in scalars):
        raise ValueError("Blade parameters must be finite")
    if not 0 < rh < rt or scale <= 0:
        raise ValueError("Require 0 < rh < rt and scale > 0")
    if not isinstance(nspan, int) or not isinstance(nchord, int) or nspan < 1 or nchord < 3:
        raise ValueError("Require integer nspan >= 1 and nchord >= 3")
    if min(law["chord_m"]) <= 0 or min(law["thickness_ratio"]) <= 0:
        raise ValueError("Chord and thickness ratio must be positive")

    verts, faces, sections = [], [], []
    contour_size = 2 * nchord + 1
    for j in range(nspan + 1):
        s = j / nspan
        r = rh + s * (rt - rh)
        chord = interp3(law["chord_m"], s) * scale
        tau = interp3(law["thickness_ratio"], s)
        beta = math.radians(interp3(law["twist_deg"], s))
        camber = law["camber"]
        upper, lower = [], []
        for i in range(nchord + 1):
            u = 0.5 * (1 - math.cos(math.pi * i / nchord))
            yc = 4 * camber * u * (1 - u)
            yt = 5 * tau * (0.2969 * math.sqrt(u) - 0.1260 * u
                            - 0.3516 * u**2 + 0.2843 * u**3 - 0.1015 * u**4)
            normal_angle = math.atan(4 * camber * (1 - 2 * u))
            upper.append((u - 0.5 - yt * math.sin(normal_angle), yc + yt * math.cos(normal_angle)))
            lower.append((u - 0.5 + yt * math.sin(normal_angle), yc - yt * math.cos(normal_angle)))
        # One leading-edge vertex, two distinct finite-thickness trailing-edge vertices.
        for u, v in upper + list(reversed(lower[1:])):
            axial = chord * (u * math.cos(beta) - v * math.sin(beta))
            tangent = chord * (u * math.sin(beta) + v * math.cos(beta))
            phi = tangent / r + law["lean_rad"] * s**2
            verts.append((x + axial + law["axial_sweep_m"] * s**2,
                          r * math.sin(phi), r * math.cos(phi)))
        sections.append({"s": s, "radius_m": r, "chord_m": chord,
                         "thickness_ratio": tau, "twist_deg": math.degrees(beta)})

    for j in range(nspan):
        for k in range(contour_size):
            faces.append((j * contour_size + k, j * contour_size + (k + 1) % contour_size,
                          (j + 1) * contour_size + (k + 1) % contour_size,
                          (j + 1) * contour_size + k))
    # Pair upper/lower strips, avoiding a center fan across a concave airfoil.
    for j in (0, nspan):
        base = j * contour_size
        lower_index = lambda i: base + 2 * nchord + 1 - i
        faces.append((base, base + 1, lower_index(1)))
        for i in range(1, nchord):
            faces.append((base + i, base + i + 1, lower_index(i + 1), lower_index(i)))

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    try:
        vertices = [bm.verts.new(v) for v in verts]
        for face in faces:
            bm.faces.new([vertices[i] for i in face])
        caps = [f for f in bm.faces if
                all(abs(math.hypot(v.co.y, v.co.z) - rh) < 1e-6 for v in f.verts) or
                all(abs(math.hypot(v.co.y, v.co.z) - rt) < 1e-6 for v in f.verts)]
        bmesh.ops.triangulate(bm, faces=caps)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        for face in bm.faces:
            face.smooth = True
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    return mesh, sections


def demo(save=None):
    """Create one new scene with 24 objects sharing a single blade Mesh."""
    import bpy

    destination = Path(save).expanduser().resolve() if save else None
    if destination:
        if destination.exists():
            raise FileExistsError(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.data.scenes.new("ParametricBladeDemo")
    scene.unit_settings.system = "METRIC"
    mesh, sections = blade("Demo.FanBlade", x=0.34, rh=0.7747 * 0.268,
                           rt=0.7747, law=FAN_LAW)
    rotor = bpy.data.objects.new("Demo.LP_ROTOR", None)
    scene.collection.objects.link(rotor)
    for i in range(24):
        obj = bpy.data.objects.new(f"Demo.Fan.{i + 1:02d}", mesh)
        scene.collection.objects.link(obj)
        obj.parent = rotor
        obj.rotation_euler.x = 2 * math.pi * i / 24
    if bpy.context.window:
        bpy.context.window.scene = scene
    if destination:
        bpy.ops.wm.save_as_mainfile(filepath=str(destination))
    print(json.dumps({"scene": scene.name, "blade_objects": 24,
                      "shared_blade_meshes": 1, "vertices_per_blade": len(mesh.vertices),
                      "sections": sections}, ensure_ascii=False))
    return scene


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", help="Optional new .blend path; existing files are refused")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    demo(args.save)

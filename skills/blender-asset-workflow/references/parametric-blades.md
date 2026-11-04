# Parametric radial blades: a runnable geometry recipe

Use this route for a fan, compressor or turbine **display blade** whose sections, dimensions and spanwise laws are known or explicitly assumed. The bundled [Python example](../scripts/parametric_blade.py) builds a closed sampled Mesh with root/mid/tip shape controls. It can be called through Blender Python in a GUI, bridge or MCP session; the CLI command below is a reproducible isolated example.

The example is **IMPLEMENTED** and numerically checked on Blender 5.2.2 LTS. Its shape values are display assumptions adapted from an owner-local CFM56 study. They are not manufacturer airfoil coordinates, an aerodynamic solution, a mechanical fit or a continuous CAD surface. The [case study](https://github.com/2409324124/blender-asset-workflow-skill/blob/main/docs/aviation-parametric-case-study.md) explains which parts of that workflow were stable and which required repair.

## Run the complete example

From a repository checkout:

```sh
blender -b --factory-startup --python-exit-code 2 \
  --python skills/blender-asset-workflow/scripts/parametric_blade.py \
  -- --save /tmp/parametric-blade-demo.blend
```

For an installed skill, substitute the absolute helper path and a suitable new output path. Windows can use the same Blender arguments with quoted Windows paths. The helper refuses an existing output file. Only Linux/Blender 5.2.2 was exercised for this example; no new cross-platform validation is claimed.

Importing the module creates no Blender data. Calling `blade(...)` creates one Mesh and returns section metadata. Running the helper creates a new scene containing 24 blade objects sharing one Mesh and one parent. It does not clear existing scenes, render, add materials, create a casing or animate the rotor. Saving is optional and saves the Blender file, including any other loaded scenes; use the isolated command for the standalone demo.

## Parameters and their observable effects

The local engine axis is **+X**; lengths are **metres**. `s=0`, `0.5`, `1` identify root, midspan and tip. The local chord reference is midchord, not an established mechanical pitch axis.

| Input | Example | Meaning and useful check |
|---|---|---|
| `x`, `rh`, `rt` | `.34`, `.7747*.268`, `.7747` | Axial reference, root radius, tip radius; require `0 < rh < rt`. Changing `x` translates the blade axially. |
| `chord_m` | `[.105,.264,.270]` | Root/mid/tip chord. Measure chord in the cylindrical developed plane rather than as a 3D endpoint distance. |
| `thickness_ratio` | `[.145,.065,.032]` | Relative thickness at those three stations; absolute thickness also depends on local chord. |
| `twist_deg` | `[64,44,28]` | Three section stagger angles in degrees. This recipe uses piecewise-linear interpolation, not the earlier GE90 study's free-vortex law. |
| `camber` | `.028` | Dimensionless maximum of a parabolic mean line. It is not the piecewise mean line of a standard NACA four-digit designation. |
| `axial_sweep_m` | `.026` | Axial stacking offset `s²*sweep`; here the tip receives a 26 mm axial offset. |
| `lean_rad` | `.022` | Circumferential angular offset `s²*lean`, already in radians. |
| `scale` | `1.0` | Chord multiplier, including the section thickness; it leaves prescribed radii unchanged. |
| `nspan`, `nchord` | `12`, `24` | Radial interval count and chord intervals per side: 13 sections, 49 points per section. Sampling density is separate from shape dimensions. |
| Array count | `24` | Number of objects sharing the template Mesh. Different counts require renewed adjacent-blade and root-slot checks. |

Keep wind-tunnel, manufacturer or measured shape laws when available. For a study model, identify assumed laws explicitly. Fan, booster, HPC, HPT and LPT need their own chord/thickness/twist laws; a different material does not turn a fan profile into a turbine profile. Camber and twist signs must be interpreted with the chosen axis and rotation direction; the recipe alone does not establish a working incidence.

## Minimal call in a live Blender session

Use the absolute `scripts` path of the installed skill. The import and all values needed by the call are explicit, so the snippet does not rely on variables left by an earlier tool invocation.

```python
from pathlib import Path
import sys
import bpy

skill_scripts = Path("/absolute/path/to/blender-asset-workflow/scripts")
sys.path.insert(0, str(skill_scripts))
from parametric_blade import blade, FAN_LAW

law = {**FAN_LAW, "twist_deg": [64.0, 46.0, 30.0]}
mesh, sections = blade("Study.Blade", x=0.34, rh=0.2076196,
                       rt=0.7747, law=law, nspan=12, nchord=24)
obj = bpy.data.objects.new("Study.Blade", mesh)
bpy.context.scene.collection.objects.link(obj)
print(sections)
```

This is a new sampled Mesh. Editing the Python law afterwards does not update existing geometry; call the builder and deliberately replace/relink the intended object. It does not install a live Geometry Nodes dependency.

## The useful geometry, in code

`interp3([a,b,c],s)` interpolates `a→b` on `[0,.5]` and `b→c` on `[.5,1]`. Separate laws give each control a clear effect. This interpolation has no first-derivative continuity guarantee at midspan. If smooth derivative continuity is needed, specify the interpolation and overshoot constraints before changing it.

Each section uses cosine chord sampling, a parabolic mean line and NACA-style thickness:

```python
u = 0.5 * (1 - math.cos(math.pi * i / nchord))
yc = 4 * camber * u * (1 - u)
yt = 5 * tau * (0.2969 * math.sqrt(u) - 0.1260 * u
                - 0.3516 * u**2 + 0.2843 * u**3 - 0.1015 * u**4)
normal_angle = math.atan(4 * camber * (1 - 2 * u))
upper = (u - 0.5 - yt * math.sin(normal_angle), yc + yt * math.cos(normal_angle))
lower = (u - 0.5 + yt * math.sin(normal_angle), yc - yt * math.cos(normal_angle))
```

Thickness is applied along the mean-line normal. Retain one leading-edge point and two distinct trailing-edge points: the `-0.1015` coefficient leaves finite trailing-edge thickness. The full helper handles contour ordering and closure.

After obtaining a nondimensional contour point `(u,v)`, rotate and map it onto its prescribed cylinder:

```python
s = j / nspan
r = rh + s * (rt - rh)
chord = interp3(law["chord_m"], s) * scale
beta = math.radians(interp3(law["twist_deg"], s))
axial = chord * (u * math.cos(beta) - v * math.sin(beta))
tangent = chord * (u * math.sin(beta) + v * math.cos(beta))
phi = tangent / r + law["lean_rad"] * s**2
point = (x + axial + law["axial_sweep_m"] * s**2,
         r * math.sin(phi), r * math.cos(phi))
```

The mapping preserves `sqrt(Y²+Z²)=r` for every vertex of that section. A flat placement `(x+axial,tangent,r)` instead produces radius `sqrt(r²+tangent²)`. For a propeller with a planar circular shank, define the root transition separately; mapping that circle wholesale onto a cylinder would change its intended shape.

Connect matching section indices with quads. Close root and tip with paired upper/lower strips and triangulate the caps. A center fan can leave a concave, highly cambered contour. The example does not add EdgeSplit; modifier-evaluated and exported topology need separate checks.

## Repetition, assembly and dependencies

Generate one template and place the array angle only in the object transform:

```python
for i in range(count):
    obj = bpy.data.objects.new(f"Blade.{i:03d}", mesh)
    collection.objects.link(obj)
    obj.parent = rotor
    obj.rotation_euler.x = 2 * math.pi * i / count
```

`mesh`, `collection`, `rotor` and `count` are caller-owned inputs in this abbreviated assembly snippet. Keep an axis-aligned local parent; handle any world-orientation transform at a common assembly root. Do not also add the array angle to template vertices. Shared Mesh objects reduce duplicated source geometry; they are not an Array modifier or Geometry Nodes instances.

Define rotor and stator installation rules separately. Casing clearance must cover the full chord and sweep footprint: `rt + gap` checked only at the nominal stage center misses a blade crossing a taper. Use actual vertices or a conservative full-footprint envelope and account for the polygonal casing's inward deviation. Roots, platforms, slots and hubs remain separate assembly tasks.

For every exposed parameter, document its consumer and affected geometry. A configuration key is useful only when a builder reads it and the intended measurement changes. In an engine, a proposed chain such as `fan radius → hub radius/height → liner/case radius` must also name which axial interfaces remain independently fixed.

## Verification scope

From a repository checkout, run the numeric check in a new Blender process:

```sh
blender -b --factory-startup --python-exit-code 2 \
  --python tests/verify_parametric_blade.py \
  -- --report /tmp/parametric-blades-validation.json
```

The [recorded result](https://github.com/2409324124/blender-asset-workflow-skill/blob/main/docs/evidence/parametric-blades-validation.json) covers one default and nine independent changes: tip radius, chord scale, thickness, twist, camber, sweep, lean, axial station and sampling. It checks source topology, orientation, finite coordinates, radial constraints, changed geometry, selected displacement invariants, repeated-default coordinates and shared-Mesh construction. The optional owner-local comparison is not needed to run the public check. Case notes and the recorded report are repository documentation linked online; they are not copied when installing only the skill folder.

This is numeric source-Mesh evidence. It does not establish visual quality, neighbor clearance, modifier/export quality, all parameter combinations or aerodynamic performance. For a modeling delivery, continue with the skill's saved-artifact and actual-image QA. The [case study](https://github.com/2409324124/blender-asset-workflow-skill/blob/main/docs/aviation-parametric-case-study.md) explains how those later checks changed the historical engine result.

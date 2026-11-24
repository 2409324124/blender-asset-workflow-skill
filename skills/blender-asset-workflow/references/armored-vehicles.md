# Armored vehicle modeling and refinement

Use this supplement for **visual, non-functional hard-surface assets**: tracked or wheeled hulls, turrets, running gear, exterior mounts and painted surfaces. It is not a manufacturing, internal-mechanism or weapon-performance guide. Apply the main skill's runtime, consent and independent-review rules unchanged.

## 1. Define identity before adding parts

Write a short contract with the exact variant, reference dates, intended viewing distance, detail budget, axes, known scale and deliverables. Record unknown dimensions as unknown. Do not mix museum, parade, exercise and upgraded-variant photographs into one supposedly authoritative vehicle.

Build a reference sheet by subsystem: hull/nose, turret, wheels/tracks, sensors, exterior fittings and finish. For every claimed feature, keep a source link, view direction and confidence: observed, inferred or unresolved. A photo is perspective evidence, not a dimensioned orthographic drawing.

- Start with side/front/rear and elevated views showing the same variant where possible.
- Match landmark relationships, not an isolated overall bounding box: hull-to-turret ratio, roof height, wheel spacing, overhang, turret position, sensor silhouette and side-mount spacing.
- If drawing SVG guides, preserve a common scale and shared landmarks across projections. Keep observed outlines separate from inferred/hidden edges. A projection generated from the model is a useful consistency check, **not independent evidence that the model matches reality**.
- Do not invent a parade scheme, insignia or unit number when the specific reference is missing. A clean military-green study can be labeled a provisional color direction instead.

## 2. Block out planes and mass, not a collection of boxes

Use a coarse silhouette pass before fittings. Check hull and turret separately, then together, in side/front/top and perspective views. Fix the largest proportion errors before subdividing details.

For armor surfaces, identify the major planes and their intersections explicitly. Construct a hull or turret from cross-sections, profile extrusions or a controlled loft; keep intended planar regions coplanar. Place vertices at actual changes in slope. A random bevel on every box is not a substitute for the correct armor break.

| Region | Construct and inspect | Reject before detail work |
| --- | --- | --- |
| Hull/nose | Upper/lower slopes, roof transition, side taper and overhang | Generic rectangular nose, drifting roof line, floating deck |
| Turret | Main volumes, cheek slopes, bustle and collar junction | Stacked cylinders/boxes that miss the reference silhouette |
| Running gear | Wheel centers/radii, visible suspension relationships, track path and clearance | Equally spaced decorative disks, disconnected shoes, unsupported track runs |
| Sensors/mounts | Mounting face, support direction, silhouette and mechanical ownership | Oversized crossbars, floating brackets, unexplained intersections |
| Exterior fittings | Real attachment points, cable thickness/lay, handles and hinge placement | Thin placeholder loops, details scattered to disguise wrong proportions |

Use cylinders only where the reference actually curves. Allocate radial segments based on silhouette and close-up distance; do not globally subdivide flat armor. Deliberate low-poly faceting is valid only when the target style accepts it, not when a realistic material merely makes the facets more visible.

## 3. Split by structural and revision ownership

Keep semantic assemblies for hull armor, hull fittings, left/right running gear, track runs, turret armor, turret fittings, sensors and side mounts. Keep the hierarchy and articulation roots separate from the visible surfaces; see [assembly](assembly.md).

Before a local repair, freeze the source and record its hash. List which objects may change, what must remain identical and which views must be regenerated. Preserve approved geometry and parent/pivot transforms; do not repair a local feature by rebuilding the entire vehicle.

Do not duplicate a left assembly blindly when asymmetry is visible. Check orientation, winding, normals and material assignment after mirroring. A geometric overlap can be an intentional seated joint; an AABB overlap alone cannot decide whether it is correct.

## 4. Refine one reference-backed region at a time

For each issue: **reference crop → matched model crop → visible discrepancy → bounded edit → same-view comparison → independent re-review**.

1. Match the view as closely as the source permits, preserving lens/projection assumptions. Do not stretch either image to manufacture agreement.
2. Write the discrepancy literally: wrong silhouette, missing opening, oversized support, flat wheel hub, cable too thin or connection not seated.
3. Repair the structure that causes it. Model a visible shallow opening with an actual rim/recess when the camera can see into it; dark paint on a cap cannot demonstrate an opening. Do not turn an exterior-art task into an internal/functional reconstruction.
4. Use loops around the opening, step or joint deliberately; avoid excessive support density elsewhere. Retain an appropriate edge radius for the intended view rather than beveling every edge equally.
5. Compare both sides, a close-up and the whole vehicle. An improved local part may still be oversized or stylistically inconsistent overall.
6. Record what remains approximate. Missing references are not permission to fabricate detail.

Prioritize planes/proportions and attachment relationships, then medium-scale structures, then small fittings. More bolts do not fix an incorrect hull.

## 5. Separate surface construction from shading

Do not diagnose every bright band as a material error or every triangular highlight as a normal error. Freeze camera, geometry and exposure; change one diagnostic variable at a time.

| Symptom | Read-only diagnostic first | Repair only after confirmation |
| --- | --- | --- |
| Unwanted breaks across nominally flat armor | Flat neutral preview, face-normal display, section/vertex planarity and non-planar n-gons | Rebuild the intended plane or control triangulation; do not conceal a warped face with smoothing |
| Rounded/melted plate boundaries | Compare flat versus smooth shading, split/sharp edges and modifier order | Preserve intentional hard edges; use smoothing or weighted normals only where appropriate |
| Dark patches or seams | Check winding, duplicate/internal faces, coincident surfaces and material boundaries | Correct the responsible topology/normal issue rather than brightening the world |
| Exposed polygon facets | Inspect neutral and material views at intended delivery size | Add segments only to necessary curves, or explicitly accept the low-poly style |
| Near-white broad bands on paint | Compare a neutral material and a roughness-only variation under fixed lights | Reduce excessive coat/specular response, tune roughness or soften lights; do not move vertices unless shape evidence calls for it |
| Vehicle still feels generic | Recheck real reference silhouettes, plate transitions and medium-scale mounting structure | Return to geometry; do not cycle through colors indefinitely |

Use a neutral gray/clay pass, a simple diffuse pass and a material pass of the same geometry. Keep cavities/AO subtle: they can exaggerate gaps or hide missing contacts. A glossy pass is useful for revealing surface discontinuities, but is not automatically the final finish. Smooth shading and weighted normals are techniques, not universal fixes.

## 6. Build material families under controlled light

Start with the actual finish reference. Distinguish painted armor, painted mounts/tubes, exposed steel, rubber and glass; do not assign one shiny material to every dark part.

- **Paint:** treat it as a dielectric coating, not bare metal. Tune color, roughness and any clearcoat together. Strong coat and low roughness can create a polished-metal appearance even with a plausible green base color.
- **Bare metal:** reserve a metal response for visibly exposed parts. Do not assume a fitting is unpainted just because it is metal underneath.
- **Rubber:** keep broader, weaker reflections and enough lighting to read its shape; pure black can crush the running gear.
- **Glass/lenses:** distinguish them from both armor and chrome, without inventing transparency through an opaque vehicle interior.
- **Wear:** match the requested condition. A clean parade vehicle is not automatically a high-gloss toy; a field vehicle is not automatically covered in rust and mud.

Any roughness numbers are renderer/lighting-specific starting points, not official vehicle-paint specifications. Do not equate a linear shader color with the same numeric display-space RGB. Keep color management and exposure fixed when comparing revisions.

Use a broad key/fill setup and a restrained background. Preserve dark running-gear detail and painted highlights without clipping. Do not change geometry, paint and lighting in the same diagnostic experiment. Compare **identical cameras** before deciding that the finish improved.

Procedural shader details are not automatically preserved in GLB. Inspect the actual target material or bake supported textures when required; report omitted shader behavior rather than claiming native/export visual equivalence from matching bounds.

## 7. Use separate acceptance gates

| Gate | Required evidence | What it does not prove |
| --- | --- | --- |
| Reference identity | Variant/source sheet and uncertainty labels | Exact dimensions from perspective photos |
| Geometry appearance | Whole-vehicle silhouette, armor-plane and local comparison images actually viewed | Correctness from object names/counts |
| Surface/finish | Neutral diagnostic views and same-camera material views | Realism from a green palette or a successful render |
| Artifact integrity | Reopened native file; actual export/reimport; geometry, hierarchy and bounds checks | Similarity to the real vehicle or matching exported shaders |
| User acceptance | The requested whole-vehicle appearance reviewed after the latest changes | Permanent approval of every later revision |

A bounded part review may pass while the whole vehicle still fails. Keep technical passes when valid, but reopen visual acceptance when the user rejects the appearance. Stop at the finite repair budget in [independent QA](independent-qa.md); report unresolved problems instead of issuing another blanket “final” label.

## 8. Handoff

Give the next worker the frozen source/hash, permitted changes, prohibited changes, camera settings, actual preview paths, remaining issues and test scope. Nominate one geometry writer, one presentation writer and a separate reviewer when available. One person coordinates the issue list and final package so old geometry and new renders cannot be mixed.

Deliver editable native files, requested exports, white and material views, a compact change table and a limitations note. Keep reference-photo licenses separate from self-generated evidence. Copy only the skill folder when installing; the repository's historical case images are not runtime inputs.

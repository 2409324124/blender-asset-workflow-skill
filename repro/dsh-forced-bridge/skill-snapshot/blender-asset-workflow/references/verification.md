# Verification that does not overclaim

Reopen the saved `.blend` in a fresh process. Inventory objects/meshes, units, parents, evaluated world bounds, counts and materials. Verify finite coordinates, actual dimensions and task-specific invariants. Inspect topology only where meaningful: an intentionally open sheet is not automatically defective. Raw polygon counts and triangulated delivery counts are different measures.

`inspect_scene.py` produces factual bounds and count diagnostics; it catches empty/non-finite mesh scenes but does **not** certify manifoldness, normals, silhouette, scale correctness, clearances or aesthetic quality. Pair its JSON with visual review and project-specific assertions. With `--import-glb path`, it resets to an empty factory scene (independent of hidden, excluded or unselectable objects) and imports the actual GLB before inspection. It never saves the source. Example:

`blender -b --python-exit-code 1 --python scripts/inspect_scene.py -- --import-glb final.glb --report glb-inspection.json`

## Delivery export
Export the intended collections/objects, excluding helpers. Use explicit selection, apply the appropriate modifier/animation options and record the export settings. Reimport into an empty scene in a **different process**. Compare dimensions, semantic part inventory, orientation, materials and intended static/animated representation against the native file. Names and vertex counts can change during export, so do not claim a numerical mismatch is automatically corruption.

GLB can duplicate vertices along normals/UV seams. Indexed boundary-edge counts can therefore look open while triangles coincide spatially. If this occurs, inspect the actual exported triangles and, on a diagnostic copy only, compare position-welded topology using a stated scale-appropriate tolerance. Keep raw and diagnostic results; do not silently weld the delivered asset, inflate tolerances to pass, or assume every seam is harmless. Check degenerates and orientation where needed. Blender's smooth appearance does not establish correct exported normals.

## Preview fidelity
`white_preview.py` makes a flat-color Workbench preview from visible mesh geometry, using evaluated mesh bounds and a temporary orthographic camera fitted to the projected extents and actual frame/pixel aspect. Non-mesh text/curves are not included in this helper’s framing inventory; convert a preview copy or explicitly frame them when they extend beyond meshes. It does not save or export. Existing visibility exclusions remain excluded. Automatic framing is an overview, not a substitute for a chosen close-up/interior view. For cutaways, temporarily hide specified roof/wall objects only in a fresh preview process and label the view; verify those objects remain in the final native/export files.

Review actual pixels at useful size. Require views appropriate to the task, not a fixed universal screenshot count. Wireframe helps see topology density and redundant detail but does not prove shape accuracy. Record the final source hash alongside images so an older good preview cannot conceal a newer broken export.

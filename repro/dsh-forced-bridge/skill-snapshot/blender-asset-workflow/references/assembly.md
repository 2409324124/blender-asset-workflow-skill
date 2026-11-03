# Assembly, semantic parts and articulation

Choose and document a module contract: world units, up/forward axes, ground datum, local origin, footprint and connection faces. Keep these compatible across separately built modules. Name objects semantically so visual defects can be assigned to geometry, not guessed from object indices. Export only intended assets, excluding preview cameras, cutaway substitutes and diagnostic overlays.

## Preserve world transforms
Appending a hierarchy is not the same as copying visible meshes. Capture `matrix_world.copy()` after dependency-graph evaluation. If changing parentage, explicitly restore the captured world matrix after linking/parenting. For a module placement transform T, compare every included object's resulting world matrix against `T @ source_world`, not merely the root or a total bounding box. Decide whether to preserve a hierarchy or bake evaluated geometry; do not apply both parent transforms and baked world coordinates.

Use copies and distinct names for assembly. Compare source and assembled object inventories, dimensions and landmarks, and inspect the result visually. A huge distant object may indicate a parent-transform error rather than a camera problem. Cameras and light rigs from a source module should not silently replace the assembled scene's rig.

## Only requested moving surfaces
Split the visible moving part, set its pivot and local axis, parent attached details correctly, and test both endpoints and an intermediate pose. Inspect collision/clearance and silhouette at each state. Do not invent internal mechanisms when only visible surface motion is requested. Blender drivers and constraints are not automatically preserved as runtime behavior by GLB export; state the supported representation (static pose, baked animation, etc.). Temporary test poses or disabled constraints must not be saved accidentally.

Shared boundaries, embedded objects and tangential contact may be intentional. Distinguish them from duplicate coplanar surfaces, unsupported floating props and unwanted penetration; do not force every object to be disjoint.

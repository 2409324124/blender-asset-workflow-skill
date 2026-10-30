# Numeric and evidence traps

This table restores project-independent lessons from the earlier reference-calibration/verification workflow. Metrics guide diagnosis; they do not replace looking at the saved deliverable.

| Tempting conclusion / symptom | What it actually establishes | Correct follow-up |
| --- | --- | --- |
| Source hash unchanged, so the assembled copy is correct | Only the source bytes are unchanged | Compare every included evaluated world transform against the intended placement, inventories and dimensions; inspect the assembled copy. Parent transforms can scatter an unchanged source. |
| AABB overlap means meshes penetrate | Only axis-aligned envelopes overlap | Inspect actual mesh surfaces/volumes and intended joints. Rotated/hollow/concave shapes can give false positives. A 2D projected crossing can hide a real 3D gap. |
| Zero overlap candidates means a defect-free scene | Only the specific sampled AABB test found no positive overlap above tolerance | Check missing parts, floating objects, tiny gaps, silhouette, excluded/non-mesh geometry and usability separately. Zero candidates is not certification. |
| Contact count should always be zero | Contact can be a normal connection or near-touch within tolerance | Preserve raw categories, exact named exemptions and reasons. Do not broaden tolerances or exemptions just to turn a report green. |
| Low polygon count or uniform mesh density proves quality | It describes tessellation, not resemblance or a useful shape | Inspect silhouette and semantic proportions first. Count native polygons and exported triangles separately. Required openings/joints can need more faces. |
| Native Blender looks fine; GLB boundary edges prove holes | Export may split vertices at UV/hard-normal seams | Inspect exported triangles/normals. Position-weld only a diagnostic copy at declared tolerance; preserve raw results and never silently alter the delivered mesh. Some gaps really are gaps. |
| Dissolving edges preserves every surface | N-gon export triangulation can create degenerates, flipped triangles or change a nonplanar face | Check actual exported triangles; restore stable triangulation instead of merely recalculating normals or changing tolerances. |
| Double-precision construction was valid | Stored/exported float precision may create tiny gaps or zero-area triangles | Reopen real files and assess scale-appropriate error. Do not coarsely weld away the intended contour. |
| Coincident positions must share one mesh vertex | Touching independent topology sectors may intentionally remain separate | Preserve semantic parts; indiscriminate position welding can create nonmanifold fans. |
| A polygon's vertex average is inside it | Not for concave polygons or holes | Sample valid triangulated interiors and validate actual API return types instead of assuming an older tessellation representation. |
| BVH overlapping triangle pairs equal a penetration count | Tangency/coplanar contact can produce pairs; containment can require a separate test | Report method and raw pairs; distinguish contact from transverse intersection/containment, using an appropriate independent check when ambiguous. |
| Tiny closest-distance error on long skinny coplanar triangles proves a visible defect | Numerical conditioning can dominate the reported error | Preserve failed diagnostics; cross-check planes/triangles at suitable precision before changing geometry. |
| An angle/driver was assigned, so the saved pose is correct | Animation or stale dependency-graph evaluation may override it | Read evaluated transforms at endpoint/intermediate poses; keep temporary diagnostic constraint changes out of the saved model. |
| Flicker disappears after changing camera clipping | It may only mask viewport depth precision, or hide duplicate surfaces | Inspect mesh and final export/render; display changes alone are not a geometry repair. |
| An old bevel modifier is harmless after a contour edit | Modifiers may now generate slivers or zero faces | Inspect evaluated geometry and the permitted local change; don't add more detail to conceal the problem. |
| Sampled RSS below the cap guarantees memory safety | Samples can miss peaks; Linux `/proc` RSS includes only observed processes in the owned group | Leave headroom. This is not a hard kernel memory sandbox. Jobs that change session/process group can escape this group observation; reparenting alone does not imply escape. Aggregate other workloads need separate supervision. |
| A fresh process is an independent reviewer | It isolates artifact state, not the author's reasoning | Use a distinct reviewer/context/person, or explicitly report self-check only. |
| Successful reimport proves the target game engine works | It establishes compatibility only with that importer/settings | Test the actual requested engine separately; static GLB does not imply Blender drivers, constraints or animation survived. |
| A previous pass applies to a new candidate | A verdict is bound to the files/images actually reviewed | Bind final hashes, inspect changed regions and neighboring preserved geometry again. Never mix previews from one candidate with another export. |

Review inherited defects separately from new ones. State unknowns instead of inventing dimensions, precision guarantees or a universal “quality score.”

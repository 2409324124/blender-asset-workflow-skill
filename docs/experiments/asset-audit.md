# Two archived exterior assets

The study opened four native files and imported four archived GLBs in empty scenes with Blender 4.5.16 LTS on Apple Silicon. Both manifests agreed on all 74 listed files, including byte length and SHA-256 (42,533,729 bytes). Archive commit `cf4ca2d45d2065d7b9427cd4d5164985e2be4221`. Immutable inputs were opened with embedded Python disabled. Mesh inspection and render experiments ran in memory or in local copies.

## Which evidence belongs to which asset?

| Input | Native SHA-256 | What can be traced |
| --- | --- | --- |
| T-90M working master | `8f6be86baf3e975b6a447c4db371044381dde5501fd8b88daa99540266d0c36d` | Archive manifest identifies this file. The three historical previews have separate file hashes and no verified link to this master. The beauty script changes scene presentation before rendering. |
| Tunguska v04 geometry | `0d69b666375417f5d11d7b59dd939f3ad6d0b73d6350516b70d7de9c6aa13d24` | Matches the existing case's frozen geometry digest. The historical scripts describe staged replacements. Some intermediate native inputs are absent. |
| Tunguska white / color | `fa6b344c0445c83ec60a28a9c538bda3d91633937d5255319a4104c280d3b6a2` / `41cc65297a4d79fd1e9d5f578936dd5273feb491331f9809dcc95f829364b2a2` | Both match the earlier presentation record. Color native additionally contains a studio floor. The archived color export contains the vehicle only. |

Both geometry masters have no saved camera. A0 therefore uses the saved asset in a documented comparison studio. Historical beauty images do not stand in for fresh A0 renders. The archive binds source and model copies to their respective hashes, but does not prove reproducibility of final files from one checkout. In particular, the T-90M assembly script has post-spec edits and Tunguska repairs expect particular intermediate hashes and directories.

### Direct source-to-mesh checks

We independently invoked only the archived exterior part generators and compared their outputs with the actual native mesh datablocks. The test converted source coordinates to Blender float32, compared ordered vertices, and compared polygon vertex cycles and material assignments while allowing reversed winding. On T-90M all five tested groups matched: hull, hull details, skirts, running gear and tracks. This is evidence of correspondence for those objects. The upper assembly and historical beauty renderer do not inherit that verdict.

On Tunguska, the base hull has the same 196 vertices, polygon connectivity and per-face materials as the v04 hull, but the coordinates differ (largest same-index displacement about 0.1034 scene units). Base detail, left/right running gear and left/right track meshes also differ in vertex count from v04. This directly demonstrates why rendering the base builder cannot stand in for opening the frozen v04 native file.

## Native and import inspection

| Vehicle geometry | Meshes with parents | Native base polygons / loop triangles | Native shading and modifiers | Reimported triangles |
| --- | ---: | ---: | --- | ---: |
| T-90M | 150 / 150 | 3,353 / 8,368 | 0 smooth faces, 0 explicit sharp edges, 0 meshes with custom normals. 41 bevel modifiers. 13 materials. | 11,152 |
| Tunguska v04 | 16 / 16 | 29,830 / 62,660 | 0 smooth faces, 0 explicit sharp edges or custom normals and no modifiers. 8 materials. | 62,660 |

These native counts describe mesh datablocks before modifiers. Both vehicle inventories have zero native boundary edges and zero edges shared by more than two faces. T-90M nevertheless has 208 faces below the audit area threshold (1e-13 in mesh-local squared units), concentrated in three exterior mesh objects. Actual import yields 420 below threshold. Tunguska has zero at that threshold. A closed indexed mesh can contain collapsed faces. No repair of historical originals was attempted.

In the color Tunguska BLEND, painted materials connect a noise texture through a range mapping into Principled roughness. In the archived GLB reimport the two painted materials have only Principled and output nodes. See the [render experiment](surface-ablation.md) for appearance under the same camera. File integrity, surface topology and perceived finish are separate findings.

## Source audit and transfer decisions

| Archive source read | What the file contributes | Transfer boundary |
| --- | --- | --- |
| T-90M `hull_generator.py` | Input parameters, derived stations, repeat placement and a mesh-building layer | Reuse the separation of design inputs and derived positions. Keep dimensions and vehicle-specific placements private. |
| T-90M `shared/geom.py` | Section extrusion, equal-ring loft, oriented primitives and sampling by cumulative path length | Express these as generic operations with explicit winding, seam and spacing contracts. |
| T-90M `shared/build_blender.py` | Builds native objects, collections, parents and materials, then applies asset-specific additions | Validate the saved result. Geometry added after specification evaluation can diverge from a diagram generated earlier. |
| T-90M `shared/turrets_v3.py` | Uses stacked outlines and local surface placement with variant-dependent silhouettes | Require a new item's actual reference sections. Exclude historical offsets, name-based fixes and identifiable vehicle layouts. |
| T-90M `shared/render_beauty_t90m.py` | Paint, exposed metal, rubber and glass families, layered noise, optional wear, bounds-aware framing, area lights, preview and final sample budgets | Separate material, camera, pose and light changes for attribution. Direct sunlight, microsurface response and wear are art-direction choices. The historical invocation changes several of these together. |
| Tunguska `base/geom.py` | Profile extrusion, ring loft, oriented cylinders, closed bands, bounded curved grids with stitched rims | A section needs corresponding landmarks and consistent winding. A grid needs explicit edge conditions. Validate on a civilian part before generalizing. |
| Tunguska `base/tunguska_spec.py` | Semantic assemblies and shared world-space mesh generation used for projected reference sheets | Generate SVG and mesh from the same design inputs. Compare the projection to independent reference evidence as a separate step. |
| Tunguska `v03/revise.py` | Profile-of-revolution wheel faces, selective mesh replacement and preservation fingerprints | The profile transfers to knobs, hubs and covers. Collapse zero-radius poles into one vertex. Historic list slices and object names bind the operation to this revision. |
| Tunguska `v03r1/repair.py` | Swept tubes on closed paths, replacing one exterior cable in a frozen scene | Commit to a consistent tangent frame across the seam. A fixed up vector fails at a parallel tangent. A coordinate box plus an expected vertex count is a one-file guard. |
| Tunguska `material-r1/material_preview.py` | Uses the existing orthographic fit, changes paint nodes, saves the native scene and exports selected objects | Preserve a separate asset scene. Freeze geometry for a finish study. The reported whole-vehicle visual rejection still stands. |

For an industrial shell, the section locations, landmarks and profile coordinates are the design inputs. Derive faces, projected outlines and consistency checks from them. For a repeat, use distance along the closed perimeter and retain the tangent at that distance. For a hose or handwheel, a curve bevel or native revolve can suffice. Use a sampled surface grid only when the design calls for curvature in both directions. Existing runtime, bounds, overlap and white-preview helpers remain the first route for their respective jobs.

Original privacy and rights restrictions apply to both archives. No private source, dimensions, model or newly rendered archive image is included here.

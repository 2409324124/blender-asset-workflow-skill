# Conservative overlap review hints

Use `scripts/overlap_audit.py` on a freshly reopened saved scene to prioritize furniture-to-wall, furniture-to-window-frame, and other proximity review. It computes evaluated mesh vertices in world space, then compares **axis-aligned bounding boxes (AABBs)**. Hidden mesh objects are included, so hiding a roof for a preview does not erase it from the audit.

```sh
blender -b candidate.blend --python-exit-code 1 --python scripts/overlap_audit.py -- --report overlap-review.json --allowlist allowed-joints.json
```

Omit `--allowlist` when no exceptions are authorized. Outputs refuse overwrite. Tolerance defaults to `1e-5` in scene coordinate units; set it for the model scale if necessary, not to make real discrepancies disappear.

## Read the categories honestly
- `candidates`: positive AABB overlap on all three axes beyond tolerance. These are **review hints**, not proven mesh intersections. Rotated, hollow, concave or disjoint mesh parts can have overlapping boxes without intersecting surfaces.
- `contacts`: touching or near-touching bounds within tolerance. Contact is not automatically an error. Small genuine overlaps below the chosen tolerance are not distinguished here.
- `exemptions`: a specific pair found in an explicit allowlist, with its reason and raw classification. Exemptions are recorded, not deleted from evidence. They do not prove that the connection is well modeled.
- `separated_pairs`: separated AABBs; no broad-phase overlap for that pair at this saved state.

Example policy (exact existing names, no wildcards or scene-wide ignore):

```json
[{"objects":["WindowFrameLeft","WallLeft"],"reason":"Frame is intentionally seated in its wall opening"}]
```

Use exemptions only for deliberately designed joints confirmed by context and visual review. Do not blanket-exempt all furniture or all same-parent objects. Unknown names, duplicate pairs and missing reasons fail validation.

## Pair diagnostics with views
Keep the final native/export geometry intact. From a separate process or after saving, produce an overall white view, a roof-off top view, and close-ups of affected furniture/walls/window frames. Keep the wall or frame relevant to a suspected overlap visible; a cutaway that hides it cannot establish clearance. Label temporary omissions. If a candidate is ambiguous, inspect the evaluated geometry directly or use a dedicated mesh intersection/distance analysis with declared tolerances; do not relabel a bounding-box result as mesh-certified.

Scope: mesh objects only, one evaluated saved state, quadratic pair enumeration. No animation sweep, physical simulation, clearance-distance/code-compliance certificate, exhaustive normal/manifold checks, or safe-layout guarantee. Non-mesh instances/curves/text require conversion or separate review. The helper is intended for small scenes, not millions of objects.

# Shape a part from its sections

Use a section study when a brief distinguishes the end, shoulder and middle of a shell. Mark the stations on a side silhouette. Sketch the closed cross-section at each one and mark a corresponding feature (for example, the corner where the right wall meets the floor). Choose local XY for these contours and +Z along the part. Record the transform into scene axes. Keep dimensions in the asset's declared units.

## A single outline source

The optional standard-library module `scripts/section_loft.py` accepts small, strictly convex, counterclockwise polygons. Start every ring at the same physical feature and visit corresponding corners in order. Omit a repeated closing corner. Equal counts alone allow accidental twists. Two matching rings give a straight extrusion. Change width, height or corner positions at intermediate stations to form a loft.

```python
import bpy
from section_loft import SectionLoft  # add the skill's scripts directory to sys.path

def contour(w, h):
    return [(-w, 0), (w, 0), (w, .68*h), (.61*w, h),
            (-.61*w, h), (-w, .68*h)]

shell = SectionLoft([(0, contour(.42, .55)), (.25, contour(.52, .68)),
                     (.92, contour(.52, .68)), (1.2, contour(.34, .48))])
vertices, faces = shell.mesh()
mesh = bpy.data.meshes.new("Shroud")
mesh.from_pydata(vertices, [], faces)
mesh.update()
# A builder can save shell.svg() alongside the candidate at a fresh .svg path.
```

The validated station tuple drives the preview contours, both end caps and the side triangles. View the SVG along the station axis, then inspect a side view as well. The overlay collapses axial distances. Check corner-to-corner rails for twists and inspect the diagonal selected on each nonplanar side. For a faceted casting with planar cheeks, preserve the direction of each corresponding bevel edge as the width changes. Independently scaling a section in X and Y can introduce a diagonal lighting break. Input validation checks ring shape and station order. The caller owns correspondence, intersections between stations and stored/exported precision. Reopen the saved mesh and measure the named section against the contract.

## Place repeated details

`perimeter_samples(contour, count, phase)` returns `((x, y), (tx, ty))` pairs spaced by distance along a closed 2D polyline. Use this for repeated latches, stitch marks or clips along a nonuniformly segmented rim. Phase is a fraction of the full circuit. The sampler omits the duplicate terminal arc distance. A self-crossing path can revisit a position. At a corner the tangent follows the outgoing edge. Use `atan2(ty, tx)` to rotate an object's local +X axis onto the tangent. Offset a clip in the outward direction `(ty, -tx)` only for counterclockwise contours. Check clip width and clearance around sharp corners. Equal travel distances can give different straight-line gaps across a corner.

## Choose a smaller construction where it fits

| Shape question | Construction and review |
| --- | --- |
| Constant section with one or more openings | Extrude a properly triangulated region with explicit inner boundaries. The convex helper has solid caps. Check the opening in a backlit view. |
| Wheel, knob or collar with a changing radius | Revolve a radius/axial profile around its declared axis. Join the angular seam once, collapse any axis pole to a single vertex, and preserve the bore if specified. A plain cylinder suffices for a constant outer radius and solid ends. |
| Hose following a spatial route | Use a Blender curve with a circular bevel. Inspect bend radius, endpoint placement and clearance in two views. An asymmetric section requires a controlled roll around the tangent. |
| Repeats on an open or spatial path | Accumulate length along the evaluated centerline, explicitly decide whether both endpoints get a copy, and provide a stable up direction or transported frame. The closed planar sampler covers flat rims. |
| Nonparallel sections, saddles or open patches | Build a grid with explicit row and column correspondence. Set open and wrapped boundaries separately and inspect triangle normals, seams and the side silhouette. Use this extra freedom only when a simpler surface misses a landmark. |

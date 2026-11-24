# Surface and presentation review

Use this route when the delivery requests colored materials, product rendering or GLB appearance. Start with the accepted geometry and name the part and visual cue each material should convey. Keep an asset-only collection. A presentation scene can link that collection and own its camera, lights and floor. For a plain gray geometry check, the existing Workbench preview is cheaper.

## Material choices

The optional [surface_studio.py](../scripts/surface_studio.py) helper creates ordinary Principled materials. Defaults below are editable starting points for a bench instrument. Colors are scene-linear RGB. Convert color-managed sRGB swatches before entering these values. Roughness, metallic and transmission range from 0 to 1. IOR accepts 1 through 3 in this helper.

| Surface role | Base color, linear RGB | Metallic | Roughness | Transmission | Look for in the reference |
|---|---|---:|---:|---:|---|
| `painted` | .038, .215, .185 | 0 | .32 | 0 | A continuous highlight that follows the enamelled body and breaks at seams |
| `bare_metal` | .68, .71, .73 | 1 | .25 | 0 | The shape, width and contrast of reflections across turned or chamfered surfaces |
| `rubber` | .025, .028, .033 | 0 | .66 | 0 | A broad reflection and enough separation to read feet, grips or seals |
| `glass` | .98, .995, 1 | 0 | .06 | 1 | A highlight across the cover while the graphic behind it stays legible |

All roles start at IOR 1.5. Painted metal can expose a second, metallic substrate at documented contact points. Assign that material to selected faces or use an authored local mask with a portable representation. Keep decorative wear out of a clean factory finish. Use the intended finish as the criterion for highlights; polished bezels and enamel often need a strong reflection to describe their shape.

## One camera for gray, color and delivery

In a Blender Python build script, put this skill's `scripts` directory on `sys.path`. The source scene must be active. Pass a dedicated, visible collection of static meshes and optional transform empties; keep the whole parent hierarchy in scope. Convert or evaluate instances, animated geometry, render-only modifiers and other specialized geometry separately. Multiple review scenes can share one source mesh. Editing a linked mesh or its material changes all its appearances, so use an asset revision or a copy for a destructive experiment.

```python
from surface_studio import render_still, studio, surface

# housing is an unassigned mesh in the asset collection.
housing.data.materials.append(surface("Enamel", "painted", roughness=0.28))
stage = studio(asset, direction=(1, -2.65, 0.98), exposure=0)
clay = surface("Gray diagnostic", "painted", color=(0.42, 0.42, 0.42), roughness=0.54)
render_still(stage, output_dir / "gray.png", override=clay)
render_still(stage, output_dir / "color.png")
render_still(stage, output_dir / "hero.png", quality="final")
```

The temporary gray override covers the stage floor and the entire asset, including glass. Use it to inspect silhouette, relief and edge catchlight. An opaque gray lens hides the dial artwork. The color pass restores the lens and original part materials. A native file saved from a build with a review scene will also contain the rig. Save the asset-only version before adding the stage when a clean native asset is required.

The stage uses a broad key and fill, a rear strip, a neutral environment and a floor scaled to the asset. The camera is orthographic and the frame fits the asset's evaluated mesh bounds. Inspect the actual image for clearance on every edge, floor contact and highlights that describe curved parts. When a bezel disappears, move a reflecting softbox or adjust its shape before altering the bezel finish. Match overall exposure to the reference once, then lock it. Cycles CPU, sRGB display, AgX, look None, gamma 1 and fixed seed 29 keep the pass conditions explicit. Preview uses 480 × 360 at 24 samples and final uses 1200 × 900 at 96 samples. Both use denoising and the same aspect ratio. The output directory must exist and support hard links. The helper renders to a temporary file, strips identifying PNG metadata and publishes only to a fresh name. [Blender color management](https://docs.blender.org/manual/en/4.4/render/color_management.html)

## Test optional layers and export

1. Render the simple material baseline. Only add a layer for a visible feature, such as stippling on cast paint or a polished contact on a latch. Keep the rest fixed and compare at the delivery size.
2. For a Blender-only study, `micro_bump(material, frequency=36, distance=0.014, strength=0.72)` creates object-space noise feeding the normal. Those deliberately pronounced values demonstrate the loss case on a roughly three-unit gauge. Apply object scale first and select frequency and distance for the actual part units and image scale.
3. For portable microstructure, author or bake a UV tangent-space normal texture and connect the non-color image through a Normal Map node. Inspect the actual GLB for an embedded image, UV coordinates and `normalTexture`. The included demonstration validates the procedural loss and face-assigned substrate. Baking and consumer-specific normal orientation require their own checks. [Blender glTF material documentation](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html)
4. Export selected asset members from the active **source** scene with `use_selection=True, use_active_scene=True, export_cameras=False, export_lights=False`. Open the actual GLB in an empty scene. Link those imported objects into the existing stage for the comparison and remove its source collection temporarily. Verify material factors, material use on faces, mesh inventory and extensions. Preserve source and imported images at identical resolution, settings and camera transform.
5. Inspect the native and imported images together. Check the narrow metal reflection, glass legibility, small wear locations and shade transition on the painted shell. A whole-frame error average alone can miss a lost material occupying a few pixels. For a named target viewer, render the same GLB there and inspect its handling of transmission, IOR, lighting and display transform.

In the repository checkout, `docs/experiments/presentation-transfer.md` records the fixed-stage round trip, the lost procedural detail and both quality levels.

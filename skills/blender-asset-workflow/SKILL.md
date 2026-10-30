---
name: blender-asset-workflow
description: Build and revise low-poly hard-surface assets and modular scenes in Blender, with preserved baselines, low-cost geometry previews, and reopened/exported artifact verification. Use for procedural modeling and assembly, not as a character sculpting or production rigging pipeline.
---
# Blender asset workflow

Create reviewable geometry before spending on presentation. Works with ordinary Blender 4.3 Python and CLI; no external service or plugin is required.

## Choose the job
- **New asset or scene:** write a short design contract: style, known scale (or explicitly relative scale), axes, footprint, silhouette landmarks, semantic parts, and requested deliverables. Original procedural work does not require traced drawings or SVG.
- **Revision:** identify the exact baseline file and hash, requested variant, changed region, and approved regions to preserve. Read [revisions and references](references/revisions.md).
- **Assembly or moving parts:** read [scene assembly](references/assembly.md) for hierarchy, units, pivots, and ownership.

## Build and inspect
1. Check Blender version and available memory. Start one headless process; choose bounded resource limits before parallelizing. Read [runtime](references/runtime.md). Independent assets can be built in separate files; never have two writers mutate the same scene or output path.
2. Construct a coarse silhouette and major proportions in semantic objects/collections. Allocate faces where curvature, openings or motion require them, not to make grid density look uniform. Do not substitute bevels, dark materials, or detail for correct proportions.
3. Save a new candidate `.blend`. Make cheap white/solid previews from that saved file: overall perspective plus relevant orthographic and detail views. For interior scenes include a clearly labeled cutaway or interior view; an intact roof cannot demonstrate contents. Wireframe is topology evidence, not a physical cross-section.
4. **Actually view the preview pixels.** Compare against the contract/reference and fix conspicuous silhouette, scale, clearance, floating/intersection and block-like placeholder issues. Do not report an unseen screenshot as reviewed. Keep approved geometry unchanged unless the user authorizes the change.
5. Reopen the final saved file and, when requested, export and reimport the actual delivery format. Read [verification](references/verification.md). Numeric checks are necessary evidence, never proof of resemblance or aesthetics. For furniture/wall/window proximity hints and explicit normal-joint exceptions, read [overlap checks](references/overlap-checks.md).
6. Deliver the final paths, hashes, previews and compact factual verification/limitations. Bind previews to the candidate they depict. Offer or produce beauty renders only after the geometry preview when authorized and budget allows. Respect a user's explicit render priority instead of imposing approval gates.

## Helpers
Run helpers from this skill folder (or substitute their absolute paths):

```sh
python3 scripts/guarded_run.py --timeout 180 --report run.json -- blender -b --python build.py
blender -b candidate.blend --python-exit-code 1 --python scripts/inspect_scene.py -- --report inspection.json
blender -b candidate.blend --python-exit-code 1 --python scripts/white_preview.py -- --output white.png --view iso
```
`build.py` is your own task-specific builder, not a bundled model. Set resource limits for the current machine; the example timeout is illustrative. Helpers refuse to overwrite existing output reports/images. They do not save changes into the loaded `.blend`. Export explicitly before reimport inspection; no helper automatically certifies an asset or publishes it.

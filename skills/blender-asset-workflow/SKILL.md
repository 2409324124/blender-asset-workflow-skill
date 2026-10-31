---
name: blender-asset-workflow
description: Build and revise low-poly hard-surface assets and modular scenes in Blender, with preserved baselines, low-cost geometry previews, and reopened/exported artifact verification. Use for procedural modeling and assembly, not as a character sculpting or production rigging pipeline.
---
# Blender asset workflow

Create reviewable geometry before spending on presentation. **Independent QA and the numeric-pitfall discipline are core to this skill.** Works with ordinary Blender 4.3 Python and CLI; no external service or plugin is required.

## Choose the job
- **Windows with DSH:** for host installation, Web/headless selection, credentials, skill discovery or an isolated compatibility test, read [Windows DSH](references/windows-dsh.md). Verify the chosen surface actually loads this skill and can call the model; a working Web login does not prove headless authentication.
- **New asset or scene:** write a short design contract: style, known scale (or explicitly relative scale), axes, footprint, silhouette landmarks, semantic parts, and requested deliverables. Original procedural work does not require traced drawings or SVG.
- **Simple model:** keep that contract proportionate to the user's request. Default to a recognizable, usable model and inexpensive previews; do not add photorealism, elaborate textures, beauty-render variants or extra export formats unless requested. User-requested detail or polish belongs in the acceptance criteria; self-imposed embellishments do not.
- **Revision:** identify the exact baseline file and hash, requested variant, changed region, and approved regions to preserve. Read [revisions and references](references/revisions.md).
- **Assembly or moving parts:** read [scene assembly](references/assembly.md) for hierarchy, units, pivots, and ownership.

## Default execution contract

Work automatically through build → independent QA → bounded repair → re-review → delivery, without routine user sign-off gates. Read [independent QA](references/independent-qa.md) before choosing builder/reviewer roles; a fresh Blender process alone is not an independent reviewer. If a distinct reviewer is unavailable, label the outcome self-check only. Respect real resource, input and external permission boundaries; never invent a pass or retry indefinitely.

**Confirm Blender can execute, then build.** Reuse a successful `bpy` execution from the current task with the same executable and environment. Otherwise run one minimal background factory-startup probe that imports `bpy`, prints the version and exits. Once it succeeds, write and run the task-specific builder to produce the first saved candidate and a cheap preview. Do not precede ordinary modeling with an inventory of memory, GPU devices, render engines, noise functions or material sockets. Diagnose a specific capability only when the requested task requires it or an actual operation fails. A progress question does not cancel the modeling task: answer briefly and continue execution unless the user asks to stop.

**Deliver when the requested result passes.** Let the model choose separate, finite repair budgets for builder self-checks and independent QA, proportionate to the requested result, task complexity, defect severity and execution cost. There is no fixed default pass count; self-check repairs never consume the independent QA allowance. Fix concrete failures of the request, file usability or visible geometry; optional aesthetic preferences do not block delivery. Do not keep adjusting color, exposure, pore detail or gloss unless the user requested that refinement. See [QA acceptance and stopping rules](references/independent-qa.md#acceptance-and-stopping-rules) for defect triage, budget accounting and unresolved failures. A user-specified quality target or repair budget takes precedence.

## Build and inspect
1. Confirm Blender execution using the minimal check above; do not repeat a successful check without an executable/environment change or a new startup failure. On Windows, read [Windows setup](references/windows-setup.md) when locating, installing or initializing Blender, or diagnosing a failed CLI probe. Reuse a working installation; installing the skill alone does not authorize installing Blender. Start one headless process; assess resource headroom only when choosing parallel execution. Read [runtime](references/runtime.md). Independent assets can be built in separate files; never have two writers mutate the same scene or output path.
2. Construct a coarse silhouette and major proportions in semantic objects/collections. Allocate faces where curvature, openings or motion require them, not to make grid density look uniform. Do not substitute bevels, dark materials, or detail for correct proportions.
3. Save a new candidate `.blend`. Make cheap white/solid previews from that saved file: overall perspective plus relevant orthographic and detail views. For interior scenes include a clearly labeled cutaway or interior view; an intact roof cannot demonstrate contents. Wireframe is topology evidence, not a physical cross-section.
4. **Actually view the preview pixels.** Compare against the contract/reference and fix conspicuous silhouette, scale, clearance, floating/intersection and block-like placeholder issues. Do not report an unseen screenshot as reviewed. Keep approved geometry unchanged unless the user authorizes the change.
5. Reopen the final saved file and, when requested, export and reimport the actual delivery format. Read [verification](references/verification.md). Numeric checks are necessary evidence, never proof of resemblance or aesthetics. For furniture/wall/window proximity hints and explicit normal-joint exceptions, read [overlap checks](references/overlap-checks.md).
6. Run the independent review/repair loop against the frozen saved artifacts and actual image pixels. Use the [numeric pitfalls table](references/numeric-pitfalls.md) to interpret metrics, not to turn them into universal pass criteria.
7. Deliver the final paths, hashes, previews and compact factual verification/limitations, explicitly distinguishing independent QA from self-check. Bind previews to the candidate they depict. Offer or produce beauty renders only after the geometry preview when authorized and budget allows. Respect a user's explicit render priority instead of imposing approval gates.

## Helpers
Run helpers from this skill folder (or substitute their absolute paths):

The guarded command below is POSIX-only. On Windows, use the bounded probe in [Windows setup](references/windows-setup.md) for connectivity and direct Blender CLI for modeling jobs, with the resource guard off by default. Only when the user explicitly enables resource protection should you use a compatible supervisor with process-tree cleanup; otherwise report that no process-tree/RSS protection is active, without blocking ordinary modeling. Resolve input, script and output paths to absolute paths before launching Blender.

```sh
python3 scripts/guarded_run.py --timeout 180 --report run.json -- blender -b --python build.py
blender -b candidate.blend --python-exit-code 1 --python scripts/inspect_scene.py -- --report inspection.json
blender -b candidate.blend --python-exit-code 1 --python scripts/white_preview.py -- --output white.png --view iso
```
`build.py` is your own task-specific builder, not a bundled model. Set resource limits for the current machine; the example timeout is illustrative. Helpers refuse to overwrite existing output reports/images. They do not save changes into the loaded `.blend`. Export explicitly before reimport inspection; no helper automatically certifies an asset or publishes it.

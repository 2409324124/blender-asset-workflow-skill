# Blender Asset Workflow — v0.2 private review draft

A compact, project-independent skill for low-poly hard-surface modeling and modular scene assembly with Blender. Native geometry first, cheap white previews next, visual and export checks before presentation.

**Status:** private repository review draft; not installed or publicly released. No license has been selected or granted by this draft. The frozen v0.1 package completed one independent fresh-context functional test; v0.2 contains narrow post-test helper corrections and has not had another independent modeling test.

Read [`skills/blender-asset-workflow/SKILL.md`](skills/blender-asset-workflow/SKILL.md). This folder is the portable skill package; repository showcase and tests are not required inputs. Requires Blender 4.3-compatible Python; the optional guard requires POSIX Python 3. No external plugins or online services are required.

## Historical gun shop and street showcase

![Earlier NIGHT SHIFT gun shop and neighboring storefronts](docs/showcase/gunstore-street.png)

This user-selected screenshot depicts the earlier gun-shop and four-store street project that motivated this workflow. It is historical project work, **not an output of the independent generic-skill cold test**. The owner authorized this image for this private repository; future public redistribution requires a separate rights review. Only the screenshot is included, not the earlier project's models or source code.

## First independent test — frozen v0.1

![Original fictional café, white geometry preview](docs/showcase/morvi-white-v01.png)

An independent first-use test created the fictional **MORVI coffee & toast** café from scratch using frozen v0.1 and ordinary Blender/Python, without historical model files or the skill author's modeling guidance. The tester used Blender's frontend for the requested genuine build recording, then serialized headless checks and cheap Workbench previews. Final native/GLB comparison found 128 evaluated objects and 9,724 triangles each, with maximum per-object world-bound difference about 0.00000024 m.

The first candidate needed a staff-aisle correction; the first preview framing clipped edges and was widened before final pixel review. This is one functional result, not a universal quality guarantee or a controlled skill/no-skill comparison. The model is a white/solid static scene, with simplified equipment, no authored beauty materials, no glass panes, no architecture-code certification or engine integration test. The preview shown is the tester's final v0.1 result, **not** a rerun with v0.2.

v0.2 corrects empty-import isolation, nonfinite resource limits, descendant-termination test evidence, and camera fitting against the actual projected frame. It adds neutral regression fixtures rather than bundling the café builder or model as a required input.

## Historical scene

The selected historical screenshot appears above at the owner's request. Underlying historical models and project source are not included. MORVI remains the separate original white-preview functional-test example; it is not the main visual showcase.

## Validation
Helper regression tests use newly created neutral primitive geometry, not historical models. See `tests/RESULTS.md` for observed results and limits. Capability claims remain limited to tested behavior, not every Blender task.

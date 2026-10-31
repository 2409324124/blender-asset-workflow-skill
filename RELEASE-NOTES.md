# v0.4 release candidate

Prepared 2026-10-31. This document describes the candidate; it is not evidence that a GitHub release or public distribution has occurred.

## Included

- A portable Blender skill for low-poly hard-surface assets and modular scenes, with baseline preservation and semantic assembly guidance.
- Independent reviewer/evidence protocol: inspect actual saved pixels, reopen native artifacts and reimport exports; report self-check honestly when no distinct reviewer runs.
- Numeric-pitfall table explaining why hashes, AABBs, polygon counts and fresh processes are not quality certificates.
- White-preview framing, scene inventory/GLB reimport, conservative overlap hints with explicit joint exceptions, and a bounded process runner.
- A runnable original minimal-shop example producing BLEND, GLB, three inspection views and reports without overwriting an existing output directory.

## Validation evidence

The recorded Linux / Blender 4.3.2 v0.4 regression run passed 17 tests. An independent v0.3 review also ran 17 tests, rebuilt the minimal example (45 meshes / 540 triangles native and GLB; zero measured world-bound difference) and inspected all three actual images. These are dated local results, not hosted CI. See [tests/RESULTS.md](tests/RESULTS.md) for timings, corrections and limitations.

The original MORVI café was a separate frozen-v0.1 independent functional test. Historical showcase images and later presentation work do not retroactively establish a v0.4 cold test.

## Known limits

- Blender 4.3.2 on Linux is the tested configuration. Live sampled RSS checks and the example runner require Linux; the timeout guard requires POSIX. macOS is untested and Windows is not supported by those runners.
- RSS sampling is not a hard memory sandbox. Preview framing inventories visible meshes, not FONT/CURVE geometry.
- AABB overlap hints are not exact mesh collision detection. Matching bounds, triangle counts and export reimport do not certify appearance, manifoldness, building-code compliance or target-engine behavior.
- No character-sculpting, production rigging, UV-baking or animation-export certification is claimed. Hosts must actually supply a distinct reviewer to claim independent QA.

## License and assets

Code, skill instructions and maintained text: GPL-3.0-only. Showcase images are separately scoped and are not covered by that grant. See [LICENSING.md](LICENSING.md) and [PROVENANCE.md](PROVENANCE.md). Installation instructions are in the [README](README.md).

## Release-preparation fixes — 2026-10-31

Integration tests now accept `BLENDER` executable paths, including spaces, and reject invalid explicit settings instead of skipping. Default discovery without Blender remains an explicitly reported skip. New white-preview and example PNGs remove text, EXIF and time metadata without re-encoding image data. Direct Windows/PowerShell usage is documented, but Windows execution remains untested; the bounded runner is still Linux-only. See the dated test evidence for the added regression results.

## Official dsh integration guide — 2026-10-31

Added an official dsh project-local setup prompt and [execution/visual-review capability guide](docs/dsh.md). The portable skill is unchanged and requires no dsh-specific plugin, model or credential. Offline layout checks pass, and actual dsh 0.2.1-rc.5 provider discovery/loading was verified without model calls on the pre-Windows-doc skill revision. A subsequent real Linux/Flash smoke test completed skill loading, table construction, actual image delivery and fresh independent saved-file/GLB review. See the dated test record; other platforms/models remain unverified.

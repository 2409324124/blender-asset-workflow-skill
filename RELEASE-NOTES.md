# Release notes

## v0.1.1 — Skill + DSH worker 桥优化版

Prepared 2026-11-03. This release packages the validated DSH bridge integration route, experiment evidence and reproducible setup. The historical v0.4 development-candidate record below is retained; this release does not relabel its tests or change the portable modeling skill.

### Included

- Optional `dsh-blender-plugin@3.0.4` real-time bridge configuration, with a hash-checked helper that disables only the bundled modeling skill registration in an isolated plugin copy. The bridge and other plugin tools remain available; the plugin is installed separately and is not vendored.
- A completed dreamcore-bedroom example showing that DSH can use the third-party bridge tools and our skill instead of the plugin's bundled modeling skill. This is evidence for that task, not full plugin feature equivalence.
- [A/B/C final render comparisons, workflow analysis and QA boundaries](repro/dsh-forced-bridge/REPORT.md), plus sanitized call summaries, source/scene checksums and a read-only targeted surface audit.
- Actual token counts split into non-cached input, cached reads and output. A includes a separately counted independent reviewer and has three attempts with unknown usage; B's interrupted run and recovery are separate; C reports self-check only. Token differences are not isolated bridge savings or monetary billing estimates.
- A visible README/DSH-guide entry, `VERSION`, and updated checksums. The default plugin-free skill workflow remains available.

### Validation and limits

The modeling experiments used DSH 0.2.1-rc.5, Blender 5.2.2 LTS and the recorded skill snapshot. That snapshot differs from `skills/blender-asset-workflow`; these renders are not a new end-to-end test of the portable skill shipped in this release. Exact versions and hashes are in the [evidence manifest](repro/dsh-forced-bridge/results/evidence-manifest.json).

Release preparation reran the existing 27-test suite on Linux with Blender 5.2.2 LTS: all passed in 6.573 seconds, with no skips. Python helper compilation, report links, usage de-duplication checks and version consistency passed; the release checksum manifest is refreshed. These are local checks, not hosted CI.

Skill-registration isolation and successful bridge-assisted delivery are verified. This release does not add a separate worker bridge implementation, change QA stopping logic, or fix the curtains/bunny/pillow intersections found in C. A used independent review while C declared self-check only; B required a recovery prompt and changed rendering settings. Each is a single observation, not a controlled quality or speed ranking. The next PR will change only our skill workflow and repeat C's complete prompt/configuration from a fresh scene.

## Historical v0.4 development candidate

Prepared 2026-10-31. This document describes the candidate; it is not evidence that a GitHub release or public distribution has occurred.

### Included

- A portable Blender skill for low-poly hard-surface assets and modular scenes, with baseline preservation and semantic assembly guidance.
- Independent reviewer/evidence protocol: inspect actual saved pixels, reopen native artifacts and reimport exports; report self-check honestly when no distinct reviewer runs.
- Numeric-pitfall table explaining why hashes, AABBs, polygon counts and fresh processes are not quality certificates.
- White-preview framing, scene inventory/GLB reimport, conservative overlap hints with explicit joint exceptions, and a bounded process runner.
- A runnable original minimal-shop example producing BLEND, GLB, three inspection views and reports without overwriting an existing output directory.

### Validation evidence

The recorded Linux / Blender 4.3.2 v0.4 regression run passed 17 tests. An independent v0.3 review also ran 17 tests, rebuilt the minimal example (45 meshes / 540 triangles native and GLB; zero measured world-bound difference) and inspected all three actual images. These are dated local results, not hosted CI. See [tests/RESULTS.md](tests/RESULTS.md) for timings, corrections and limitations.

The original MORVI café was a separate frozen-v0.1 independent functional test. Historical showcase images and later presentation work do not retroactively establish a v0.4 cold test.

### Known limits

- Blender 4.3.2 on Linux is the tested configuration. Live sampled RSS checks and the example runner require Linux; the timeout guard requires POSIX. macOS is untested and Windows is not supported by those runners.
- RSS sampling is not a hard memory sandbox. Preview framing inventories visible meshes, not FONT/CURVE geometry.
- AABB overlap hints are not exact mesh collision detection. Matching bounds, triangle counts and export reimport do not certify appearance, manifoldness, building-code compliance or target-engine behavior.
- No character-sculpting, production rigging, UV-baking or animation-export certification is claimed. Hosts must actually supply a distinct reviewer to claim independent QA.

### License and assets

Code, skill instructions and maintained text: GPL-3.0-only. Showcase images are separately scoped and are not covered by that grant. See [LICENSING.md](LICENSING.md) and [PROVENANCE.md](PROVENANCE.md). Installation instructions are in the [README](README.md).

### Release-preparation fixes — 2026-10-31

Integration tests now accept `BLENDER` executable paths, including spaces, and reject invalid explicit settings instead of skipping. Default discovery without Blender remains an explicitly reported skip. New white-preview and example PNGs remove text, EXIF and time metadata without re-encoding image data. Direct Windows/PowerShell usage is documented, but Windows execution remains untested; the bounded runner is still Linux-only. See the dated test evidence for the added regression results.

### Official dsh integration guide — 2026-10-31

Added an official dsh project-local setup prompt and [execution/visual-review capability guide](docs/dsh.md). The portable skill is unchanged and requires no dsh-specific plugin, model or credential. Offline layout checks pass, and actual dsh 0.2.1-rc.5 provider discovery/loading was verified without model calls on the pre-Windows-doc skill revision. A subsequent real Linux/Flash smoke test completed skill loading, table construction, actual image delivery and fresh independent saved-file/GLB review. See the dated test record; other platforms/models remain unverified.

### Windows validation and README update — 2026-11-01

Later work validated Windows: DSH with Blender 5.2.3 (see [tests/WINDOWS-DSH.md](tests/WINDOWS-DSH.md)) and Codex on Windows with several models built. The local regression suite now has 27 tests (Blender integration tests skip when Blender is absent). Earlier sections above remain as dated historical records. Claude Code and macOS remain untested. The README now leads with the geometry-first, blockout-first workflow and an agent × OS status table.

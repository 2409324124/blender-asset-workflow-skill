# Blender Asset Workflow

**v0.1.1 — DSH workflow update:** Added a verified real-time Blender bridge workflow for incremental modeling and visual feedback. See the [release notes](RELEASE-NOTES.md) and [experiment report](repro/dsh-forced-bridge/REPORT.md).

**Plan the geometry. Validate the blockout. Refine with visual feedback.**

An open-source AI agent skill for procedural low-poly modeling with Blender CLI, Python/bpy and independent visual QA.

Instead of jumping directly from natural language to detailed meshes, the workflow starts with a **geometry plan and a coarse blockout**. It validates proportions, silhouettes and structural relationships through inexpensive Blender previews before investing in further detail.

> **No Blender?** The agent asks before installing anything. See [No Blender?](#no-blender).

![RIVET tire and repair shop](docs/showcase/rivet-locked-main.png)

## How it works

**Natural language → Geometry planning → Coarse blockout → White previews → Visual QA → Iterative refinement → BLEND verification (GLB export/reimport when requested)**

## Roadmap

**One geometry-first workflow, three execution routes.** The project keeps its portable Blender Python/bpy + CLI path while validating optional real-time adapters:

| Backend | Current status | Role |
|---|---|---|
| **DSH real-time bridge** | Validated in one DSH + third-party plugin experiment ([PR #10](https://github.com/2409324124/blender-asset-workflow-skill/pull/10)) | Persistent Blender scene, incremental edits and immediate feedback; clean cross-platform installs still need testing. |
| **BlenderMCP** | Planned integration; not yet validated with this skill | Interactive MCP route for compatible agents, subject to host/Blender service availability. |
| **Python/bpy + Blender CLI** | Existing portable baseline, validated on Linux and Windows | Plugin-free fallback for headless environments; optimize cold-start, rebuild and preview costs. |

**Next:** (P0) incremental geometry/adjacency QA and audit-failure handling; (P0) BlenderMCP integration and DSH clean-install smoke tests; (P1) prompt expansion and optional user clarification; (P1) backend capability detection and comparable quality/cost benchmarks; (P2) faster headless bpy feedback. This is a priority-based plan, not a dated release commitment.

See the [detailed roadmap](docs/ROADMAP.md) and [recorded test evidence](tests/RESULTS.md).

## What makes it different?

- **Geometry-first planning:** define scale, axes, silhouettes, semantic parts and assembly constraints before detailed modeling.
- **Blockout-driven iteration:** build coarse geometry first and inspect proportions using lightweight multi-view white previews.
- **Independent visual QA:** a separate reviewer, when available, inspects actual rendered images and saved geometry rather than trusting the builder's claims. If no separate reviewer runs, the result is reported as self-check only.
- **Bounded automatic repair:** fix reviewed issues within a finite repair budget (default two passes), preserve approved geometry, re-review changes, and stop with an honest report when limits are reached.
- **Artifact verification:** reopen saved BLEND files and, when requested, reimport actual GLB exports, checking geometry, dimensions and structure.
- **Numeric traps:** hashes, polygon counts, AABB hints and successful reimports are evidence—not guarantees of resemblance or correct geometry.

## Designed for AI agent workflows

Built around Blender's native Python API and headless CLI, without requiring Blender MCP or external modeling plugins.

Supports **Codex, Claude Code and DeepSeek Harness (DSH)**.

Focused on low-poly hard-surface assets and modular scenes.

| Agent | Windows | Linux | macOS |
|---|---|---|---|
| DSH | Tested (Blender 5.2.3) | Tested (Blender 4.3.2) | Documented |
| Codex | Tested | Documented | Documented |
| Claude Code | Documented | Documented | Documented |

"Documented" means install instructions exist but no recorded end-to-end run **for that agent × OS combination**. A platform-level test does not automatically validate every agent or execution backend.

**Platform testing status (as of 2026-11-04):** Linux is verified with recorded Blender CLI/regression and DSH model-assisted tests; Windows has recorded DSH/Codex tests. **macOS has also been tested according to the project maintainer**, but the agent, Blender version, test command and artifacts have not yet been added to this repository. Its agent-specific matrix cells remain "Documented" until reproducible evidence is recorded. See [test records](tests/RESULTS.md).

Read the [skill](skills/blender-asset-workflow/SKILL.md), [QA protocol](skills/blender-asset-workflow/references/independent-qa.md) and [numeric-pitfall table](skills/blender-asset-workflow/references/numeric-pitfalls.md).

### Parametric aviation geometry

For radial fan, compressor or turbine display blades, use the [parameter guide and runnable recipe](skills/blender-asset-workflow/references/parametric-blades.md). It includes root/mid/tip chord, thickness and twist controls, cylindrical mapping, cap topology and shared-Mesh repetition. The [aviation case study](docs/aviation-parametric-case-study.md) explains how reusable geometry, reference documents and targeted repairs contributed to a CFM56 study, with explicit limits on historical evidence and parameter coverage. This adds a geometry example, not a manufacturer-airfoil or full-engine CAD claim.

### Optional DSH real-time bridge route — v0.1.1

DSH can also use the third-party `dsh-blender-plugin@3.0.4` bridge with our skill for persistent scene execution and immediate visual feedback. The dreamcore-bedroom experiment completed after disabling the plugin's bundled modeling skill registration in an isolated copy. This release includes the configuration, isolation helper, final render comparisons and token evidence; it does not bundle the plugin or add an independent worker implementation.

Follow the [isolated setup](repro/dsh-forced-bridge/REPRODUCE.md) to reproduce that experiment. It uses the recorded [skill snapshot](repro/dsh-forced-bridge/skill-snapshot/blender-asset-workflow/SKILL.md), which differs from the portable skill under `skills/`. The experiment validates that exact combination; it does not certify every skill revision. The portable skill remains usable without the plugin. See the [report](repro/dsh-forced-bridge/REPORT.md) for QA differences, known intersections and the limits of the token comparison.

## Install and run

Requires Python 3 and Blender CLI. Tested: **Blender 4.3.2 on Linux** and **Blender 5.2.3 on Windows**; the current [LTS](https://www.blender.org/download/lts/) is recommended. No external Blender plug-ins or model downloads are needed.

### Windows + Codex: start here

Follow the [Windows + Codex setup guide](docs/windows-codex.md) in your local Codex session:

1. [Install the skill](docs/windows-codex.md#1-install-the-skill) into your user or project skill directory; keep existing copies intact.
2. [Confirm Codex loads it](docs/windows-codex.md#2-confirm-codex-loads-it) from the intended path.
3. [Find Blender or install it with permission](docs/windows-codex.md#3-find-blender-or-install-it-with-permission).
4. [Run the 30-second connection test](docs/windows-codex.md#4-run-the-30-second-connection-test) in a separate background process.
5. [Start modeling](docs/windows-codex.md#5-start-modeling) and receive a saved BLEND plus a checked preview.

The guide includes a copyable Codex request and optional PowerShell installation steps. This route uses Blender CLI and Python; DSH and Blender MCP are not prerequisites.

### No Blender?

That is fine. Ask your agent to set it up. It will first look for an existing Blender. If none is found, it stops and asks you to choose: it teaches you step by step, or it installs Blender for you. Before installing, it shows the version, source, location, admin rights and PATH changes, and waits for your yes. See [Blender install](skills/blender-asset-workflow/references/blender-install.md).

### One-message setup for local agent sessions

For dsh on Windows, see [Windows DSH](skills/blender-asset-workflow/references/windows-dsh.md); for API keys and logins, see [DSH credentials](skills/blender-asset-workflow/references/dsh-authentication.md).

Copy the relevant request into your local agent; hosted/cloud sessions may use different installation locations.

**Codex** — [Windows step-by-step guide](docs/windows-codex.md)
> Install `skills/blender-asset-workflow` from https://github.com/2409324124/blender-asset-workflow-skill into `~/.agents/skills/blender-asset-workflow` (on Windows: `%USERPROFILE%\.agents\skills\blender-asset-workflow`). Copy only that folder, stop if it already exists, verify skill discovery and read `SKILL.md`. Check Python availability and Blender CLI connectivity by launching a separate factory-startup background process with a 30-second timeout, running a minimal Python probe that imports `bpy` and prints the Blender version, then exiting without opening, modifying or saving any user scene. Report the actual result and any failure. If Blender is missing, stop and ask me before installing anything.

**Claude Code**
> Install `skills/blender-asset-workflow` from https://github.com/2409324124/blender-asset-workflow-skill into `~/.claude/skills/blender-asset-workflow`. Copy only that folder, stop if it already exists, verify skill discovery and read `SKILL.md`. Check Python availability and Blender CLI connectivity by launching a separate factory-startup background process with a 30-second timeout, running a minimal Python probe that imports `bpy` and prints the Blender version, then exiting without opening, modifying or saving any user scene. Report the actual result and any failure. If Blender is missing, stop and ask me before installing anything.

**Official dsh**
> Copy this repository's `skills/blender-asset-workflow` into the intended project's `.dsh/skills/blender-asset-workflow` without overwriting an existing copy; verify actual skill discovery/loading, run a 30-second isolated Blender CLI `bpy` probe, and check image-input and fresh-reviewer capabilities before claiming independent visual QA. Follow [the dsh guide](docs/dsh.md); report missing capabilities rather than silently substituting another route. If Blender is missing, stop and ask me before installing anything.

These are instructions for an agent, not executable shell commands or a promise of unattended authentication.

For the Linux example runner, use a repository checkout (this is separate from installing the skill):

```sh
git clone https://github.com/2409324124/blender-asset-workflow-skill.git
cd blender-asset-workflow-skill
python3 examples/minimal-shop/run_example.py --output ./runs/shop-001 --max-rss-mib 2048
```

Outputs: BLEND, GLB, white overview, roof-off top view, furniture close-up and verification reports. The runner refuses existing output directories. Adjust the memory budget to your machine; arrange independent visual review separately. See [example options](examples/minimal-shop/README.md).

**Optional resource management:** the Linux example runner enables timeout and sampled RSS protection. On Windows, use the direct Blender CLI instructions below with the guard **off by default**; that route has no guard protection, and the Linux runner does not automatically downgrade to it.

**Platform limits:** live RSS checks and the example runner are **Linux-only**. RSS is sampled, not a hard sandbox. The separate timeout/process-group guard targets POSIX; its macOS behavior is not covered by a recorded test, and Windows is unsupported by those runners. The direct macOS Blender CLI route (`/Applications/Blender.app/Contents/MacOS/Blender`) has maintainer-reported testing but no reproducible environment/command record in this repository yet. Windows was tested through the dsh CLI route on Blender 5.2.3 and through Codex; see [Windows test record](tests/WINDOWS-DSH.md).

## Validation

Current release: **v0.1.1**. Older v0.4 labels in the evidence are historical development-candidate records. Local regression suite: **27 tests** (Blender integration tests are skipped when Blender is absent). Independent example review: **45 meshes / 540 triangles**, matching native/GLB bounds, all three preview images inspected. These are specific local checks, not hosted CI or a universal quality certificate.

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

See [test evidence](tests/RESULTS.md) and [release notes](RELEASE-NOTES.md). AABB hints are not exact mesh-collision checks; target-engine integration, character sculpting and production rigging are outside this validation.

## License and showcases

Code, skill and maintained text: **[GPL-3.0-only](LICENSE)**. Showcase images are the owner's stated original work and are separately scoped—not automatically GPL. See [license scope](LICENSING.md) and [image provenance](PROVENANCE.md).

## Further details

### Discovery and installation scope

The prompts above use personal installation directories. For project-only use, copy the same folder to `.agents/skills/blender-asset-workflow` (Codex) or `.claude/skills/blender-asset-workflow` (Claude Code). Do not copy showcase images or example outputs into the skill directory.

Codex discovers skills automatically; restart if the new skill is not listed. Claude Code also discovers skills automatically; if its top-level skills directory was created during an existing session, run `/reload-skills`. A file copy is not proof of discovery: ask the host to list/read the skill before using it. Current host references: [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code skills](https://code.claude.com/docs/en/skills).

### What independent review means

The builder supplies saved artifacts and an evidence handoff; the reviewer uses a separate reasoning context rather than trusting the builder's summary. Review includes actual preview pixels, reopened native geometry and reimported exports, with findings tied to artifacts. A fresh Blender process alone does not create independent reasoning. Repairs are bounded by an explicit budget and require re-review; unresolved failures are reported instead of silently passed.

### Reading the numbers

The overlap helper reports conservative AABB candidates, contact/near-contact pairs and precisely named allowed joints. It does not compute an exact mesh collision verdict. Zero candidates does not prove a scene has no defects. Source hashes help establish file identity, not correct geometry copying; triangle counts do not measure resemblance; matching native/GLB bounds do not establish engine shading or split-normal correctness. The [numeric-pitfall table](skills/blender-asset-workflow/references/numeric-pitfalls.md) explains these and other traps.

### Historical examples

The RIVET lead image is a visual showcase, not by itself a QA report. The original MORVI café white preview records the frozen-v0.1 independent functional test, which required aisle and framing corrections. The earlier NIGHT SHIFT street image is historical project work, not a generic-skill cold-test output. Their sources are listed in [PROVENANCE.md](PROVENANCE.md); scene/model files are not bundled as required skill inputs.


### Blender executable and Windows

For integration tests, set `BLENDER` to an executable path (spaces are supported), or leave it unset to search `PATH`. An invalid explicit value is an error. If the default executable is absent, integration tests are marked **skipped**: an `OK (skipped=...)` summary is not full Blender validation.

Headless operation is not Linux-specific. On Windows, Blender's own Python can directly run modeling, preview and inspection scripts; it was tested through the dsh CLI route on Blender 5.2.3 (see [Windows test record](tests/WINDOWS-DSH.md)). The Linux example runner and POSIX guard are not Windows-compatible. See [direct PowerShell steps](examples/minimal-shop/README.md#windows-direct-blender-route) and [Blender's Windows CLI documentation](https://docs.blender.org/manual/en/latest/advanced/command_line/launch/windows.html). These direct commands do not provide the runner's timeout/RSS protection or its combined verification report.

New preview PNGs have text, EXIF and time chunks removed without re-encoding image data; this does not anonymize visible scene content or other output files.

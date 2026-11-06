# Roadmap — Blender Asset Workflow

_Last updated: 2026-11-04. Priorities are milestones, not calendar promises._

## Project direction

**Natural-language intent → geometry plan → blockout → execution → observation → targeted repair → verified asset.**

The skill owns modeling methodology, semantic parts, spatial relationships and QA evidence. Execution backends are adapters, not separate modeling products. Preserve the plugin-free Blender CLI/bpy path; keep DSH and BlenderMCP optional. A successful backend probe or screenshot is not a geometry-quality pass.

## Execution routes

| Route | Current evidence | Remaining work |
|---|---|---|
| **DSH real-time bridge** | [PR #10](https://github.com/2409324124/blender-asset-workflow-skill/pull/10) validated a DSH + third-party `dsh-blender-plugin@3.0.4` bridge-tools + our-skill dreamcore bedroom run. This repo does **not** ship a self-developed Worker. | Fresh installs across platforms and headless hosts; tool/skill discovery, version and port conflicts, recovery, and clear QA failures. |
| **BlenderMCP** | Candidate interoperability route, not yet validated as this skill's backend. | Prove an end-to-end model/edit/observe/save/reopen cycle; document actual supported agent, Blender session and service setup. |
| **Native Python/bpy + CLI** | Existing headless baseline. See [test records](../tests/RESULTS.md). | Reduce process restarts, whole-scene rebuilds and preview overhead without assuming a graphical desktop or image-reading model. |

Choose an available route after checking the actual host capabilities, not from the agent's brand name. Do not assume that a DSH-specific tool is callable as MCP. A headless Blender process can render previews; an agent without image-input capability must report that visual QA was unavailable.

## Milestones and acceptance criteria

| Priority | Workstream | Definition of done |
|---|---|---|
| **P0** | **Incremental QA and correct stopping** | Encode important adjacency/contact/clearance relationships in a design contract. After a change, recheck affected objects and neighbors, including evaluated CURVE/modifier geometry where relevant. Tool completion must not hide an internal audit `ok:false`. Report unresolved checks, cap repairs and never promote incomplete self-checks to independent passes. |
| **P0** | **BlenderMCP proof of integration** | In at least one documented compatible agent and Blender configuration, load this skill, produce a new asset, edit one semantic part, observe actual scene output, save/reopen the BLEND and capture tool/runtime failures. |
| **P0** | **DSH bridge installation portability** | Reproduce a clean install and a small end-to-end build/observe/save flow on each *claimed* platform. Verify actual skill selection, Blender startup, plugin version, headless/GUI behavior and teardown. Report platforms without completed runs as pending. |
| **P1** | **Requirement planning and clarification** | Expand short requests into a concise, inspectable design contract: explicit user requests, inferred geometry, defaults, spatial constraints and open decisions. Ask only high-impact ambiguous questions when a host supports interactive user questions; otherwise proceed with labeled assumptions. Do not prompt for routine bevel/face-count decisions. |
| **P1** | **Backend capability discovery and fallback** | Make route choice auditable: detect working DSH bridge/MCP/Blender CLI, image-input capability and reviewer availability, then select a supported execution path. Do not claim silent fallback preserves identical QA coverage. |
| **P1** | **Comparable benchmark** | Use one fixed modeling prompt and acceptance contract across routes. Record agent/model/version, Blender/platform, startup, calls, elapsed time, non-cached/cache/output tokens, image reads, independent-vs-self QA and unresolved geometry defects. Avoid calling one uncontrolled run a causal speed result. |
| **P2** | **Headless bpy feedback efficiency** | First benchmark cold-start, save/reopen, rebuild and image-render costs. Try semantic partial edits and structured geometry reports before committing to a new persistent bpy worker. Measure gains and recovery complexity. |

## Immediate next PR

Focus on **P0 incremental QA** against the recorded C configuration in [PR #10's report](../repro/dsh-forced-bridge/REPORT.md). Keep the same full prompt and bridge setup; change only the portable skill's QA instructions, then rebuild from an empty scene. Compare planned adjacency relationships, post-transform checks, failed-audit handling and final geometry (not just tool count and duration). Specifically verify curtain/window-frame and bunny/pillow/pillow relationships. The 15/16 flagged pairs in the original targeted check are *pairwise intersection evidence*, not 15 independently confirmed visual defects.

## Validation ledger

- **Linux:** dated automated tests and real DSH modeling/visual reviewer runs are recorded in [tests/RESULTS.md](../tests/RESULTS.md).
- **Windows:** actual DSH/Blender and Codex records exist; see [tests/WINDOWS-DSH.md](../tests/WINDOWS-DSH.md).
- **macOS:** project maintainer reports testing completed; a reproducible test record and exact validated agent/backend are still **pending**. Do not silently change the DSH/Codex/Claude × macOS cells in README to tested.
- **DSH bridge:** third-party plugin integration established for the [specific recorded experiment](../repro/dsh-forced-bridge/REPORT.md); not proof of clean installs on all operating systems.
- **BlenderMCP:** proposed route; no skill-specific end-to-end evidence yet.

Keep test entries specific to **agent × OS × Blender × backend × task**. Update the README compatibility table only after that combination has an identifiable evidence record.

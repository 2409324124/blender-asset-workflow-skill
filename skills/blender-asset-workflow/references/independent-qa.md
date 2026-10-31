# Independent QA and automatic repair loop

Independent review is a core workflow, not an optional congratulatory summary. Automate it when the host can run an independent reviewer. A separate Blender process provides **artifact isolation**, not independent reasoning by itself.

## Acceptance and stopping rules

Judge the candidate against the user's requested result. A simple object without a request for photorealism or fine material work needs recognizable geometry, requested parts/style/scale, usable saved files and sufficient viewed previews. Keep review proportionate: one overall view plus only the additional views needed to check relevant details. Do not introduce a texture showcase, a lighting comparison or an unrequested export as a new acceptance requirement. Builder-authored design notes cannot silently raise the user's quality target.

Classify each finding before changing the candidate:

- **Required correction:** an evidenced failure of the request or basic usability, such as an unreadable file, a missing requested part, a visibly detached component, a conspicuously wrong silhouette, or incorrect required scale. Name the object/view or failed operation and the acceptance criterion it violates. Requested visual fidelity is a valid criterion; this rule does not excuse a visibly wrong model.
- **Optional refinement:** a preference among otherwise acceptable colors, exposures, surface roughness, pore densities or lighting arrangements. These do not produce `needs_changes` and do not trigger more edits/renders unless the user requested that refinement. Deliver the passing candidate; mention an optional improvement only when useful.
- **Uncertain finding:** gather one targeted check when it could establish a material defect. If it remains unresolved, state the uncertainty without repeatedly changing geometry or rendering alternatives. Missing evidence for a required check must not be labeled a pass.

Set the repair budget before inspecting the first saved candidate and preview. **Self-checks and independent QA consume the same budget:** by default at most one repair pass for a simple model, or two for a more involved task. A pass is one consolidated set of defect-driven edits followed by a rebuild/render and check of the changed result; individual edits within that set are not separate passes. Do not restart the count when handing off to a reviewer, changing materials, renaming a candidate or returning to the builder. Keep a short finding list and remaining-pass count in the task record. New user-requested revisions can establish a new scope and budget.

If the candidate meets the request, stop editing and deliver after the required artifact checks; an unused repair allowance is not a quota. A re-review checks the fixes and related regressions, not a fresh search for aesthetic upgrades. Newly discovered material defects still need an honest verdict. At budget exhaustion, preserve and report the best current candidate with unresolved required findings and an incomplete/needs-changes status; never fabricate a pass or spend extra cycles on optional polish. User-requested precision, photorealism, refinement or an explicit budget overrides the corresponding default, but still needs a finite stopping condition.

## Roles and minimal handoff

**Builder** owns construction and bounded repairs. Save a versioned candidate and exported deliverables, then freeze those bytes for review. Record hashes of the actual native/export files and their bound preview images. Preserve the previous accepted baseline and the user's raw requested changes.

**Reviewer** is a separate agent/person/review context that has not authored the candidate. Give it:
- The raw task, references the user supplied, requested variant, accepted baseline, constraints and changed/preserved regions.
- Candidate BLEND, actual exported GLB when requested, source-bound preview files, and paths/hashes sufficient to locate precisely those files.
- Relevant acceptance criteria and resource limits; read-only ownership of source artifacts, with a separate output directory for inspection.

Do not include the builder's predicted verdict, suggested answer, or an “all checks green” summary as the reviewer’s substitute for evidence. Build logs can help diagnose a failure after initial inspection. No particular model/provider is required. Use a fresh context where possible, not two role labels in one uninterrupted author's reasoning.

## Reviewer executes these steps

1. Verify received hashes; open the saved candidate, not the builder’s unsaved session. Compare the stated change against the accepted baseline, including per-object world transforms when modules were assembled.
2. Independently inspect actual pixels: overall silhouette, relevant orthographic view, and close-ups/cutaways for affected details. If views conceal an affected region, generate another from the saved candidate in a fresh process. **Opening an image filename or trusting its caption is not visual review.** Check the final saved state, not only a prettier older image.
3. Reopen native and, only when GLB delivery was requested, reimport the actual GLB into an empty process. For example, from this skill directory, with separate nonexisting report paths (the second command applies only to a requested GLB):

```sh
blender -b candidate.blend --python-exit-code 1 --python scripts/inspect_scene.py -- --report reviewer-native.json
blender -b --python-exit-code 1 --python scripts/inspect_scene.py -- --import-glb candidate.glb --report reviewer-glb.json
```

Compare relevant object inventory, units, bounds, orientation, hierarchy/materials and supported poses. Inspect raw export geometry when normals or seams are at issue. An inventory success is not a complete QA pass.
4. Use overlap hints when relevant, with [explicit joint exceptions](overlap-checks.md). Inspect candidates and suspicious projected intersections; distinguish genuine intersections from contacts, small gaps, bounding-box false positives and occlusion. Read [numeric pitfalls](numeric-pitfalls.md) before interpreting a suspicious “green” metric.
5. Return an evidence-based verdict: `pass`, `needs_changes`, or `blocked/inconclusive`; identify reviewer independence or state `self-check only`. Include candidate hashes, actual files/images viewed, commands/results, observed defects with object names/view locations, and remaining limitations. Never label an unviewed image, untested engine integration or unavailable independent review as passed.

## Default automatic orchestration — no routine user sign-off gate

Builder → freeze candidate → independent review → bounded local repair → new candidate → independent re-review → delivery. Do not ask the user to approve each stage when the requested work and changes are already authorized. The reviewer reports findings; the builder fixes them without asking for routine permission.

Use the shared repair budget from [acceptance and stopping rules](#acceptance-and-stopping-rules), including any passes already spent on builder self-checks. Re-review changed parts and related preserved boundaries using new hashes, not stale approval. Keep each candidate and each review result identifiable; never overwrite a failed review with a fabricated pass. A deterministic data failure should be diagnosed directly rather than consuming repeated expensive render cycles.

Stop and report the best current candidate plus unresolved findings when the repair budget/resource limit is reached, evidence remains ambiguous, required input is missing, or permission blocks the next action. Do not loosen tolerances, expand exceptions, hide objects or remove tests to manufacture a pass. A fresh review after a real fix is different from repeatedly asking reviewers for a nicer verdict.

If an independent reviewer cannot be invoked in the current host, perform the same artifact and pixel checks yourself, clearly label them **self-check only; independent QA unavailable**, and deliver that limitation. Do not invent a reviewer, a second-context execution or its verdict. The included example runner automates build/data checks/previews; it does not by itself provide independent visual QA.

Automation never grants permission to publish, change repository visibility, upload unapproved assets, install software or bypass host/tool authorization. Pause at a real external authorization boundary, not at an invented modeling approval gate.

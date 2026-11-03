# Independent QA and automatic repair loop

Independent review is a core workflow, not an optional congratulatory summary. Automate it when the host can run an independent reviewer. A separate Blender process provides **artifact isolation**, not independent reasoning by itself.

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
3. Reopen native and reimport the actual GLB into an empty process. For example, from this skill directory, with separate nonexisting report paths:

```sh
blender -b candidate.blend --python-exit-code 1 --python scripts/inspect_scene.py -- --report reviewer-native.json
blender -b --python-exit-code 1 --python scripts/inspect_scene.py -- --import-glb candidate.glb --report reviewer-glb.json
```

Compare relevant object inventory, units, bounds, orientation, hierarchy/materials and supported poses. Inspect raw export geometry when normals or seams are at issue. An inventory success is not a complete QA pass.
4. Use overlap hints when relevant, with [explicit joint exceptions](overlap-checks.md). Inspect candidates and suspicious projected intersections; distinguish genuine intersections from contacts, small gaps, bounding-box false positives and occlusion. Read [numeric pitfalls](numeric-pitfalls.md) before interpreting a suspicious “green” metric.
5. Return an evidence-based verdict: `pass`, `needs_changes`, or `blocked/inconclusive`; identify reviewer independence or state `self-check only`. Include candidate hashes, actual files/images viewed, commands/results, observed defects with object names/view locations, and remaining limitations. Never label an unviewed image, untested engine integration or unavailable independent review as passed.

## Default automatic orchestration — no routine user sign-off gate

Builder → freeze candidate → independent review → bounded local repair → new candidate → independent re-review → delivery. Do not ask the user to approve each stage when the requested work and changes are already authorized. The reviewer reports findings; the builder fixes them without asking for routine permission.

Set a finite repair budget before the first review, proportional to the request and machine budget. If unspecified, start with **at most two repair passes**; a user-defined budget takes precedence. Re-review changed parts and related preserved boundaries using new hashes, not stale approval. Keep each candidate and each review result identifiable; never overwrite a failed review with a fabricated pass. A deterministic data failure should be diagnosed directly rather than consuming repeated expensive render cycles.

Stop and report the best current candidate plus unresolved findings when the repair budget/resource limit is reached, evidence remains ambiguous, required input is missing, or permission blocks the next action. Do not loosen tolerances, expand exceptions, hide objects or remove tests to manufacture a pass. A fresh review after a real fix is different from repeatedly asking reviewers for a nicer verdict.

If an independent reviewer cannot be invoked in the current host, perform the same artifact and pixel checks yourself, clearly label them **self-check only; independent QA unavailable**, and deliver that limitation. Do not invent a reviewer, a second-context execution or its verdict. The included example runner automates build/data checks/previews; it does not by itself provide independent visual QA.

Automation never grants permission to publish, change repository visibility, upload unapproved assets, install software or bypass host/tool authorization. Pause at a real external authorization boundary, not at an invented modeling approval gate.

# Independent QA and automatic repair loop

Independent review is a core workflow, not an optional congratulatory summary. Automate it when the host can run an independent reviewer. A separate Blender process provides **artifact isolation**, not independent reasoning by itself.

## Acceptance and stopping rules

Judge the candidate against the user's requested result. A simple object without a request for photorealism or fine material work needs recognizable geometry, requested parts/style/scale, usable saved files and sufficient viewed previews. Keep review proportionate: one overall view plus only the additional views needed to check relevant details. Do not introduce a texture showcase, a lighting comparison or an unrequested export as a new acceptance requirement. Builder-authored design notes cannot silently raise the user's quality target.

Classify each finding before changing the candidate:

- **Required correction:** an evidenced failure of the request or basic usability, such as an unreadable file, a missing requested part, a visibly detached component, a conspicuously wrong silhouette, or incorrect required scale. Name the object/view or failed operation and the acceptance criterion it violates. Requested visual fidelity is a valid criterion; this rule does not excuse a visibly wrong model.
- **Optional refinement:** a preference among otherwise acceptable colors, exposures, surface roughness, pore densities or lighting arrangements. These do not produce `needs_changes` and do not trigger more edits/renders unless the user requested that refinement. Deliver the passing candidate; mention an optional improvement only when useful.
- **Uncertain finding:** gather targeted evidence when it could establish a material defect. If it remains unresolved, state the uncertainty without repeatedly changing geometry or rendering alternatives. Missing evidence for a required check must not be labeled a pass.

Let the model choose **separate, finite repair budgets** for builder self-checks and independent QA. There is no fixed default number of passes. Choose each allowance from the user's requested quality, model complexity, observed defect severity, uncertainty and rebuild/render cost; use a small allowance for a simple model and more only when the required work justifies it. An explicit user budget takes precedence. Record the chosen allowance and consumed passes briefly before that stage's repair loop; do not ask the user to set routine budgets.

- **Builder self-check budget:** covers corrections made after the first saved candidate and preview, before independent review. When that allowance is exhausted, stop self-directed edits and pass the best inspectable candidate plus known unresolved findings to independent QA. Do not represent it as passed. If no usable candidate exists, report the build failure rather than pretending review can validate it.
- **Independent QA repair budget:** begins with the first independent verdict and covers repairs requested by that review and subsequent re-reviews. Initial inspection is not a repair pass. Builder self-checks do not reduce this allowance, even when the builder performs the QA-requested fixes. Lack of remaining builder allowance must not skip independent review or its available repair work. When no independent reviewer is available, retain the self-check outcome and label the limitation; do not create a fictitious second QA stage.

A pass is one consolidated set of defect-driven edits followed by a rebuild/render and check of the changed result; individual edits within that set are not separate passes. Keep separate counters and a short finding list. Renaming candidates, changing material parameters or handing work back to the builder does not reset the relevant counter. Revise a stage's allowance only for a documented change in required scope or newly evidenced material defects, never just to keep polishing; retain the consumed count. Any user-imposed overall time or cost ceiling still applies.

If the candidate meets the request, stop editing and deliver after the required artifact checks; an unused repair allowance is not a quota. A re-review checks the fixes and related regressions, not a fresh search for aesthetic upgrades. Newly discovered material defects still need an honest verdict. At the end of the applicable review/repair stage, preserve and report the best current candidate with unresolved required findings and an incomplete/needs-changes status; never fabricate a pass or spend extra cycles on optional polish. User-requested precision, photorealism, refinement or an explicit budget overrides the corresponding default, but still needs a finite stopping condition.

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

Use the independently chosen QA repair budget from [acceptance and stopping rules](#acceptance-and-stopping-rules). Do not charge builder self-check passes against it. Re-review changed parts and related preserved boundaries using new hashes, not stale approval. Keep each candidate and each review result identifiable; never overwrite a failed review with a fabricated pass. A deterministic data failure should be diagnosed directly rather than consuming repeated expensive render cycles.

After the stage-specific handoff described above, stop and report the best current candidate plus unresolved findings when the applicable repair budget/resource limit is reached, evidence remains ambiguous, required input is missing, or permission blocks the next action. Do not loosen tolerances, expand exceptions, hide objects or remove tests to manufacture a pass. A fresh review after a real fix is different from repeatedly asking reviewers for a nicer verdict.

If an independent reviewer cannot be invoked in the current host, perform the same artifact and pixel checks yourself, clearly label them **self-check only; independent QA unavailable**, and deliver that limitation. Do not invent a reviewer, a second-context execution or its verdict. The included example runner automates build/data checks/previews; it does not by itself provide independent visual QA.

Automation never grants permission to publish, change repository visibility, upload unapproved assets, install software or bypass host/tool authorization. Pause at a real external authorization boundary, not at an invented modeling approval gate.

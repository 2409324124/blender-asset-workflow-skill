# Aviation case study: a stable blade recipe, an iterative assembly

The owner's CFM56-7B26 SAC modeling case suggests a useful division of work: keep a small set of explicit geometry recipes stable, then inspect and refine the relationships between parts. It does **not** demonstrate an error-free first attempt or a complete engineering model of the engine.

## Evidence and public reproduction

The complete engine, historical source snapshots, references and engine validation reports remain in the owner's local case records. They are **not included in this repository**. Historical results below are reported evidence from that case, not independently reproducible whole-engine verification in this PR.

The public, runnable scope is the isolated blade recipe:

- [Blade method and parameter contract](../skills/blender-asset-workflow/references/parametric-blades.md)
- [Standalone blade example](../skills/blender-asset-workflow/scripts/parametric_blade.py)
- [Numeric invariant verification script](../tests/verify_parametric_blade.py)
- [Recorded example validation](evidence/parametric-blades-validation.json)

The example's report applies to its recorded inputs and checks. It does not reproduce the historical engine, validate a CFM proprietary airfoil, or establish visual quality by itself.

This page uses **IMPLEMENTED** for identified code behavior, **VERIFIED** only for bounded checks with available evidence, **INFERRED** for explanations, and **PROPOSED** for future work. Statements about unpublished engine code are explicitly marked as reported historical evidence rather than public VERIFIED claims.

## What the recipe made explicit

The owner reports the following **IMPLEMENTED** behavior in the historical engine:

| Design choice | Concrete implementation | Reusable lesson |
|---|---|---|
| Separate geometry from assembly | A geometry module accepted explicit coordinates, shape laws and materials without importing old engine generators or their scene/report globals. | Reuse mathematical principles without also inheriting cleanup, saving and scene-construction side effects. Blender Mesh creation still has data-block side effects; it is not a pure function. |
| Meaningful shape controls | Root/midspan/tip values independently controlled chord, thickness ratio and twist through piecewise linear interpolation. Sweep and lean used quadratic span laws. | Expose controls that describe the shape, rather than asking the agent to adjust many unrelated vertices. These were analytic display laws, not recovered CFM design data. |
| Matched section loft | Cosine chord sampling, a NACA-style thickness distribution and parabolic camber produced consistently ordered section rings. Adjacent rings were connected and root/tip caps closed. | A fixed topology recipe narrows implementation choices while allowing different spanwise laws. Finite trailing-edge thickness must not be accidentally welded away. |
| Cylindrical mapping | With engine axis +X, circumferential coordinate `t` became angle `phi = t/r + lean(s)`, then `y = r*sin(phi)`, `z = r*cos(phi)`. | Every point in a section has the intended cylindrical radius `r`; tangent-plane chord width does not enlarge the radial envelope. Coordinate conventions must be explicit when transferring the method. |
| Shared blade mesh | Each row created one source Mesh and placed objects at `2*pi*i/N` around +X. | Shape generation and repetition are separate responsibilities. This is shared Mesh data, not an Array modifier or Geometry Nodes instance system. |
| Mechanical ownership | Fan/booster/LPT belonged to the LP rotor; HPC/HPT to the HP rotor; stators and cases to fixed parents. | Parent structure expresses motion ownership and enables bounded checks that the other rotor remains still. Names alone do not prove that relationship. |
| Physical/display separation | One physical assembly supplied display copies for cutaways, exploded views and interface close-ups. Copies retained source identifiers. | A pulled-out root or shifted platform can explain an interface without silently changing the physical assembly. |
| Complete chord envelope | Final case construction used each rotor/stator row's actual axial vertex bounds, rather than only its stage center, to constrain the inner wall. | Neighboring geometry must clear the entire blade footprint. This radial envelope is not a general mesh-to-mesh collision solver. Polygonal wall clearance needs its own conservative check. |

The portable example demonstrates the section, interpolation and cylindrical-mapping ideas. It does not bundle the engine assembly, cases, root interfaces, rotor hierarchy or display scenes.

## What the documents contributed

The reported workflow used different sources for different questions:

| Input | Useful role | Boundary |
|---|---|---|
| Textbook index, selected figures and component cards | Identify shafts, disks, drums, cases, liners, supports and their structural relationships. | General engine diagrams do not recover the exact geometry of a particular CFM56 variant. No textbook figures are redistributed here. |
| Public type and incident documentation | Constrain variant, SAC configuration, spool/stage structure, 24 fan blades and a few nominal overall dimensions; record conflicting source statements. | Overall diameter, length or maximum chord does not determine internal stations or spanwise airfoils. Some counts were already specified in the owner's request. |
| Uncalibrated photographs | Guide visible external proportions, attachment categories and connection positions. | The photos did not supply engineering dimensions or recover hidden fan geometry. They are not redistributed here. |
| Existing algorithm notes and reuse contracts | Locate tested section, cylindrical mapping, revolution and sweep principles; identify implicit globals and known topology pitfalls. | Reusing a method does not transfer a previous model's verification status. |
| Parameter and validation records | Separate reference constraints from display assumptions; record rebuild behavior, failed checks and repairs. | A report written after modeling explains the outcome; it cannot be treated as an input that caused the first candidate. |

## What was stable, and what required repair

**Reported owner-session source review:** the first-written and final versions of nine geometry functions had identical Python ASTs: `interp3`, `mesh_data`, `revolve`, `shell_profile`, `annulus`, `blade`, `dovetail`, `box_mesh` and `tube_mesh`. This is a historical review assertion about unpublished snapshots, not a public replayable check. It covers those function bodies, not the whole generator or the success of its first execution. Later functions included a dovetail-compatible slotted rim and a display clipping helper.

The owner reports delivery within one user instruction, with multiple internal build/check/repair cycles. Repairs included:

- Cases that cleared stage centers but intersected the front/back portions of blades or stators; the final construction used full chord footprints.
- A disk rim that needed an actual narrowing slot neck to express the dovetail interface.
- Front structure that needed radius-dependent dimensions and transitions.
- Overlapping close-up labels, detached-looking pipes in the exploded view and foreground structure obscuring the HP demonstration; display selection and framing were revised.

Stable single-part mathematics and a successful final presentation therefore coexist with assembly and presentation iteration. They should not be collapsed into a claim that the whole engine came out correctly in one pass.

The related AV-60K case also started from detailed owner-provided equations. Its reported first tangent-plane construction enlarged the physical tip envelope by about **0.25 mm**. A later weighted cylindrical mapping preserved the planar circular root while enforcing cylindrical blade stacking. Clear equations narrowed the problem, but actual mesh coordinates still needed verification.

## Why this likely helped

These explanations are **INFERRED**, not results of a controlled comparison with and without documentation:

- A specific variant, units, axis and mechanical ownership reduced ambiguity about what each part represented and how it should move.
- Explicit recipes and prior failure notes reduced the number of geometric choices the builder had to invent. The reported stability of the core functions is consistent with that explanation.
- Chord, thickness, twist, sweep and lean provided directed ways to change appearance while preserving the construction method.
- Separate checks located different defects at the appropriate level: vertex geometry, repeated transforms, neighboring-wall clearance, motion ownership or visible presentation.
- Display copies allowed explanation and framing to improve without turning a diagnostic offset into a physical assembly change.

Material, lighting, camera choices and repeated inspection also contributed to the reported final presentation. The case does not isolate their effects or justify a success-rate or speed multiplier for documentation.

## Parameterization still had limits

The historical engine used JSON configuration and Python rebuilds to generate static Mesh data. It was not a live Geometry Nodes dimension system. The owner's source review also found that fields in a configuration file were not necessarily effective controls:

| Reported historical source behavior | Consequence |
|---|---|
| `geometry.engine_length_m` was not consumed; exhaust stations still contained fixed coordinates. | It was not a working whole-engine length control. |
| `geometry.combustor.case_inner_radius_m` was not consumed by the case construction. | Editing the field did not establish a new case/liner/interface relationship. |
| `sampling.small_theta` was not consumed; several small parts supplied explicit sample counts. | The sampling table overstated the connected input surface. |
| `fan_x_m` moved the blade/root/shim/spacer/platform definitions, while the disk had fixed axial stations and the rim used a separate interval. | It was not a synchronized translation control for the entire fan assembly. |

The reported engine rebuild matrix covered only default → one combined edit → restored default. The edit set fan tip radius to **0.790 m**, tip gap to **0.004 m** and total case/liner thickness to **0.026 m**. It reportedly checked the corresponding dependency response, no accumulation of tagged generated data and restoration of the original source-geometry signature. It did not cover the disconnected fields above or every combination in the stated editable ranges.

**PROPOSED:** for future assets, document every editable field's consumer, dependent parts and exercised values. Start with a single-section/blade example, then validate repeated transforms and full footprints before adding neighboring shells and presentation copies. Publish portable checks with the method, and preserve the distinction between a useful procedural display model and a verified engineering design.

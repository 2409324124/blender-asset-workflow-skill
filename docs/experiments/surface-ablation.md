# Fixed-view surface trials on two existing meshes

**Decision.** Select the treatment from the visible defect and the delivery distance. On the coarse T-90M wheels, extra radial samples reduced the corners in the outline. On the already denser Tunguska wheels, smoothing selected curved faces made the reflection follow the recessed bowl. Neither asset showed a whole-vehicle shape improvement from changing paint roughness. The historical visual rejection remains open.

## Inputs and controls

A0 used each geometry master's original mesh, modifiers and materials. Neither master had a camera. We supplied a fixed orthographic studio and fitted it once per asset and view, using the original evaluated mesh points. Every A arm reopened the same input. All seven camera matrices and scales were checked against A0 after rendering. Each arm has orthographic front, side and top, a low front oblique, a higher three-quarter view, and two close-ups covering a wheel and the vehicle nose. This gives **112 actual renders** across two assets and eight arms.

The CPU Cycles run used Blender 4.5.16 LTS, 640 × 420 RGB, 12 samples, fixed seed 23, denoising, no adaptive sampling, AgX, look None, exposure 0, gamma 1. All lights and the neutral surround were shared except for A6. The comparable material stays in the asset throughout A0–A4. We inspected the images at overview and close-up sizes. Mean absolute RGB differences below use 8-bit pixels. A larger difference measures a change, not its value.

| Arm | Intervention on a fresh copy | T-90M wheel crop Δ | Tunguska wheel crop Δ | Observed effect and decision |
| --- | --- | ---: | ---: | --- |
| A0 | Saved geometry and original materials | 0 | 0 | T-90M shows chord corners and broad flat disks. Tunguska already has a recessed bowl and finer curved outlines. |
| A1 | Smooth curved faces of identified wheel rings, leaving planar caps and body plates flat | 0.251 | 0.934 | The curved side reads more evenly on T-90M, though corners remain. On Tunguska the interrupted band on the outer wheel lip becomes continuous; the rim reads softer. Keep this as a local option and inspect its hard boundary. |
| A2 | Mark wheel edges above 0.78 radians sharp, leaving baseline face smoothing unchanged | 0 | 0 | All seven rendered views on both assets match their A0 pixels. Splits alone did not improve the baseline's flat faces. This result does not predict the response on an already smooth surface. |
| A3 | Insert one midpoint on each circumferential edge of the selected rotational components and reproject it to its original ring radius | 0.371 | 0.301 | The chord corners are less conspicuous on T-90M. The gain on Tunguska's finer wheels is small at this resolution. Preserve the hub center, cross section and caps. |
| A4 | Two-segment local bevel at selected wheel creases, 0.005 scene units, clamped for overlap | 0.170 | 1.401 | T-90M still shows chord corners. On Tunguska the new highlights read as extra concentric lines. This produced the largest wheel-crop change without the best match to the intended rim. Exclude from A7. |
| A5 | Paint roughness only, modulated by noise and a range centered on the native roughness | 0.017 | 0.100 | Nose-crop differences are 0.083 and 0.205 respectively. Little visible gain at overview size. Plate transitions, outline and missing shapes survive the change. No default finish or highlight reduction follows. |
| A6 | Double the fill light energy from 750 to 1,500, retaining its shape, position and every other control | 0.148 | 0.223 | Nose differences rise to 4.676 and 4.907. The deck brightens, while the sheltered wheel region changes little. Useful as a lighting diagnosis only. |
| A7 | T-90M A3 + A1; Tunguska A1 only | 0.492 | 0.934 | T-90M gains a rounder exterior contour and smoother side. Its flat central appearance persists. Tunguska retains the dish profile with smoother rim shading. No second technique was added where it lacked a clear benefit. |

A whole-vehicle T-90M reference shows articulated side-panel outlines and large-scale changes of plane over the wheels; the archived exterior still reads as a long straight band in side view. Two further archive-linked exhibition close-ups show thin overlapping lips and open shadow gaps. They offer evidence for local edge treatment, but neither shows an entire vehicle or a road wheel. The Tunguska reference pair shows the front cover in a particular state and gives a clear side-panel rhythm. A wheel-only change cannot validate those features. Reference photos and lab cameras have different pose, lens and lighting. [T-90M whole vehicle](https://commons.wikimedia.org/wiki/File:T-90M.jpg) · [T-90M local view 1](https://commons.wikimedia.org/wiki/File:T-90M_02.jpg) · [T-90M local view 2](https://commons.wikimedia.org/wiki/File:T-90M_04.jpg) · [Tunguska reference sources](../cases/tunguska-refinement.md#read-only-diagnosis-after-the-rejection)

The low view, side and nose crops also exposed limits outside the edits. The round front cover and collar retain their original steps, the Tunguska observation panel is a broad rectangle and the adjacent service doors retain their outline. The exterior cable is visible but its routing was not corrected; the repeated track pads still read as a band. A7 preserves these regions. Distinguish a projected silhouette error (geometry), collapsed faces (topology), discontinuous highlights on a curved band (shading), lost roughness variation (material/export), and an occluded dark region (lighting). Each observation has a different follow-up.

## Native and export evidence

The A7 BLEND files were saved, reopened, exported as GLB and the actual GLBs were imported in fresh Blender processes. Only the intended running-gear mesh changed on T-90M; 156 other objects retained their audited geometry, world transforms, parents, material assignments and modifier identities as applicable. Two running-gear meshes changed on Tunguska, with 24 other objects preserved. Modified meshes had zero boundary edges, zero edges with more than two incident faces and zero faces under the audit area threshold both before and after. The T-90M wheel object grew from 472 to 696 faces. Both Tunguska objects retained 7,034 faces each.

The following pairs were rendered on one studio per pair at 16 fixed samples. For the archived color and white models we removed the saved presentation lights and excluded the studio floor from the comparison. The same source-space pose, target and camera were used for each import. The original archive GLBs were imported as delivered. The A7 rows use exports from this study.

| Actual BLEND / GLB pair | Three-quarter RGB Δ | Nose RGB Δ | Wheel RGB Δ | Pixel review |
| --- | ---: | ---: | ---: | --- |
| T-90M archived | 0.003 | 0.008 | 0.024 | Matched overall plate and wheel appearance at this size. |
| Tunguska geometry master | 0.029 | 0.083 | 0.044 | Main landmarks and pale finish retained. |
| Tunguska white | 0.078 | 0.130 | 0.201 | White surface and visible wheel relief retained. |
| Tunguska color | 2.701 | 4.201 | 1.275 | Noticeable change in green deck response. The imported paint lacks the native procedural roughness connection. The image difference alone does not isolate that connection from other export behavior. |
| T-90M A7 | 0.019 | 0.022 | 0.279 | Rounded outer outline visible in both; small wheel shading differences. |
| Tunguska A7 | 0.161 | 0.283 | 0.522 | Bowl remains legible in both. Local normals and thin edge highlights can differ. |

## QA false alarms and unresolved issues

A separate topology pass tested a specific alarm: “a mesh with raw indexed boundary edges will still have boundary edges after coincident position seams are joined.” The unit was one imported mesh in a master GLB. In an ephemeral copy, weld by world-space position within 1e-6, then count boundary edges again. Of **166 flagged meshes, 163 cleared and three remained flagged** (147/150 cleared on T-90M and 16/16 on Tunguska). The 163 are false positives for **persistent position boundaries under this test**, not 163 certified watertight solids. Three actual T-90M objects still had boundaries; multi-face edges and degenerate faces need separate inspection. Presentation variants share geometry and were excluded from this denominator. The delivered meshes were untouched.

Screening hard edges in isolation similarly produced a null visual result in A2. Whole-vehicle resemblance remains unaccepted. The wheel study leaves the T-90M collapsed-face findings, the Tunguska front silhouette and external cover details unresolved. Next test one reference-matched geometric change at a time. A material adjustment that fails the image check does not enter the default workflow.

### Acceptance by deliverable

| Gate | Evidence and disposition |
| --- | --- |
| Reference shape and part identity | The selected wheel profiles were compared in the low view and the wheel close-up. Major side and front landmarks still diverge. Whole-vehicle acceptance remains open. |
| Geometry and topology | Reopened A7 changed only the selected running-gear meshes. Their boundary, multi-face-edge and collapsed-face counts stayed at zero. The separate T-90M collapsed-face finding still needs an object-level repair. |
| Flat, curved and edge shading | A1, A2, A3 and A4 isolate different causes of a rim defect. The T-90M outline benefits from additional radial samples. The Tunguska bowl benefits from selective smoothing. |
| Local components | The wheel treatment has close-up evidence. The surrounding skirts, inspection panels, cable and track appearance still need reference-specific work. A separate [blind trial](agent-comparison.md) tests cosmetic covers against deliberately illustrative targets. |
| Material and light | A5 gave little visible improvement. A6 brightened the deck. The [gauge study](presentation-transfer.md) tests material separation and identifies the lost procedural bump under a fixed studio. |
| Parameterization and reuse | The [civilian compressor](geometry-transfer.md) uses a single station table for the mesh, SVG and dimension checks. An independent rebuild reproduced four render digests. |
| Editable native delivery | Both revised BLEND files reopened. Protected source objects retained their audited properties. |
| Actual interchange delivery | Reimported native/export image pairs are shown in the local boards and measured above. The archived color variant and the original gauge demonstrate two different material changes on export. A named downstream renderer would need a further test. |
| Original skill behavior | The base, original PR and candidate ran on the same Mac. Linux-specific guard behavior was measured separately. [Regression results](../../tests/RESULTS.md) |

The private lab retains all native candidates, exports, close-ups, before/after boards, scripts, hashes and per-view measurements. Public example images are provided in the original [industrial geometry experiment](geometry-transfer.md) and [material/export experiment](presentation-transfer.md). See also the [input audit](asset-audit.md) and [machine-readable measurements](surface-results.json).

---
name: blender-modeling
description: >-
  DISABLED for this controlled A/B. Do not use this skill's recipes or gates.
  Load blender-asset-workflow instead. Blender bridge tools (blender_rt_*) remain
  available from the host plugin and may be used while following blender-asset-workflow.
---

# blender-modeling (disabled)

This project overrides the bundled `blender-modeling` skill for a fair comparison.

**Required:** `skill(name="blender-asset-workflow")` and follow that skill only.
**Allowed:** DSH Blender bridge tools (`blender_rt_*`, viewport, worker, see, plan, …).
**Forbidden:** treating this file as the modeling playbook; loading the bundled modeling skill content as authority.

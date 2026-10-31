# Official dsh integration

This guide targets [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness), not a third-party adapter. No adapter, provider credentials or model configuration is bundled. Interface references were checked on 2026-10-31; verify the installed session's capabilities rather than assuming a permanent model/tool list.

## Load the portable skill

From the intended project root, copy the **whole** `skills/blender-asset-workflow` directory to `.dsh/skills/blender-asset-workflow`; stop if that destination exists. The bundle includes its references and Python helpers, not repository showcase images. The entrypoint has the required `name` and `description` frontmatter.

The [official filesystem provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md) scans direct child bundles, not arbitrary nested repository folders. Its project root is the nearest Git ancestor, or the working directory without one. A nested folder inside another Git repository still inherits that repository root; placing `.dsh/skills` only in the nested folder will not make it a project root. Use the intended existing root (or intentionally establish a separate project boundary), rather than silently initializing repositories. Start the session in the intended project and verify the discovered source path: higher-priority project entries can shadow another installed copy. The repository's source `skills/` directory is not itself a default discovery root.

After copying, verify that the actual session catalog contains `blender-asset-workflow`, then use its skill-loading tool to read `SKILL.md` and the relevant references. A filesystem fixture passing is **not** proof that dsh loaded it. No custom plugin is required for the skill format.

## Check execution and review capabilities

| Need | Actual-session check |
| --- | --- |
| Run Blender | Inspect the available [shell executor](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/shell/README.md) and its permissions; use the active Bash or PowerShell route. Run a separate factory-startup background Blender process, with a 30-second timeout, executing `import bpy; print(bpy.app.version_string)`. Require successful exit and version output. Do not open or save any user scene. Do not merely check `PATH` or `--version`. |
| Inspect pixels | The filesystem provider documents [`read_image(file_path)`](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/fs/tool-fs/README.md), but registration requires durable attachments and execution requires image-input support from the actual selected model. Check both at runtime, then read an actual generated preview. Relative paths use the session working directory. Reading a filename or image dimensions is not visual review. |
| Independent reviewer | Use an available, permitted [subagent provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/tool-subagent/README.md) to spawn a fresh reviewer context, not a history-inheriting fork. Inspect actual configured tool names, depth limits and routing permission; do not assume a literal tool name or that a requested model route is enabled. Give the reviewer the design contract and frozen artifact paths, not an author's all-green conclusion. |
| Saved-artifact checks | Reviewer reopens the saved BLEND, reimports the actual GLB and inspects actual preview pixels according to the [independent QA protocol](../skills/blender-asset-workflow/references/independent-qa.md). Fresh shell processes alone do not count as independent reviewers. |

If image input/attachments are unavailable, mark **visual QA not performed**. If no distinct reviewer can actually run, mark **self-check only**. Report exactly which stage is blocked; do not silently substitute a text-only answer or invent independence. If another reviewer route is available, use it only within its existing permissions and name the route used.

Blender CLI + Python remains the modeling path; Blender MCP is not required. Optional Linux timeout/RSS guards remain as documented in the README. On Windows use the direct PowerShell path with the resource guard off by default—without its protection. The Linux example runner does not silently downgrade on Windows. Do not disable sandboxing, install software, change network settings or read credentials to make a probe pass.

## Validation boundary and first live check

Offline fixtures verify our bundle layout/frontmatter and a non-overwriting temporary copy. Separately, the actual installed official dsh `0.2.1-rc.5` filesystem provider and `SkillRegistry.snapshot/get` were exercised without a key: the catalog completed and loaded `blender-asset-workflow` as `project-dsh` (4,302-byte entrypoint body from the pre-Windows-doc revision). This was real provider discovery, not a mock, but not a UI/session tool call or model-assisted test. A separate bounded Blender CLI probe exited successfully and reported Blender 4.3.2.

The real provider test initially found no skill because its nested workspace inherited an ancestor Git root. An intentionally separate test-project Git boundary corrected discovery. This is evidence for the root rule above, not a recommendation to initialize Git without authorization.

Model-assisted live verification remains pending until an authorized configured dsh session is available. The user configures credentials privately in that application; no key belongs in chat, this repository or logs. Only the machine/session location and chosen model identifier are needed to coordinate testing. Then verify, in order:

1. Actual skill catalog and loaded source path.
2. Bounded CLI probe and available execution route.
3. A new tiny neutral model saved to a fresh output directory, with preview and GLB.
4. Actual image delivery to an image-capable reviewer, independent saved-file/export checks and a recorded verdict.

Report missing stages explicitly; passing the offline fixture is not an end-to-end compatibility claim.

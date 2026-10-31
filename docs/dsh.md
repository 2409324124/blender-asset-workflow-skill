# Official dsh integration

This guide targets [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness), not a third-party adapter. No adapter, provider credentials or model configuration is bundled. Interface references were checked on 2026-10-31. **Only official dsh 0.2.1-rc.5 has been tested here.** Verify the installed session's capabilities; other versions are not implicitly certified.

## Install dsh first

Follow the official [installation and launch instructions](https://github.com/deepseek-ai/deepseek-harness#run). Installing this skill does not install dsh or authorize an agent to install software. Reuse an existing installation where possible.

## Load the portable skill

1. Choose the intended project root. The [official filesystem provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md) uses the nearest Git ancestor, or the working directory if there is none. A nested folder inside a Git repository still inherits that repository's root.
2. Copy the **whole** `skills/blender-asset-workflow` bundle into `<project>/.dsh/skills/blender-asset-workflow`. Do not overwrite an existing copy. The repository's source `skills/` directory is not automatically discovered.
3. Start dsh in that project. Check the actual catalog entry and source path, then load `SKILL.md` and its references. Higher-priority copies can shadow another installation. A successful copy is not proof of discovery.

From this repository checkout, use either command block below. Set the project variable to your intended root; `.` means this checkout. Do not initialize Git merely to make discovery work without authorization.

**Bash**

```bash
(
  set -eu
  source_dir="$(pwd)/skills/blender-asset-workflow"
  project_dir="$(pwd)" # Change to the intended project root if different.
  destination="$project_dir/.dsh/skills/blender-asset-workflow"
  test -f "$source_dir/SKILL.md"
  mkdir -p "$project_dir/.dsh/skills"
  mkdir "$destination" # Fails if any destination already exists.
  cp -R "$source_dir/." "$destination/"
)
```

**PowerShell**

```powershell
$Source = Join-Path (Get-Location) 'skills/blender-asset-workflow'
$Project = (Get-Location).Path # Change to the intended project root if different.
$Root = Join-Path $Project '.dsh/skills'
$Destination = Join-Path $Root 'blender-asset-workflow'
if (-not (Test-Path -LiteralPath (Join-Path $Source 'SKILL.md'))) {
    throw 'Source skill not found; run from the repository checkout'
}
New-Item -ItemType Directory -Path $Root -Force -ErrorAction Stop | Out-Null
New-Item -ItemType Directory -Path $Destination -ErrorAction Stop | Out-Null
Get-ChildItem -LiteralPath $Source -Force |
    Copy-Item -Destination $Destination -Recurse -ErrorAction Stop
```

Both routes refuse an existing destination rather than replacing it. A failed copy may leave a partial destination; inspect it instead of retrying with overwrite enabled. The bundle includes references and Python helpers, not repository showcase images. No custom dsh plugin is needed for this skill format.

## Check execution and review capabilities

| Need | Actual-session check |
| --- | --- |
| Run Blender | Inspect the available [shell executor](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/shell/README.md) and its permissions; use the active Bash or PowerShell route. Run a separate factory-startup background Blender process, with a 30-second timeout, executing `import bpy; print(bpy.app.version_string)`. Require successful exit and version output. Do not open or save any user scene. Do not merely check `PATH` or `--version`. |
| Inspect pixels | The filesystem provider documents [`read_image(file_path)`](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/fs/tool-fs/README.md), but registration requires durable attachments and execution requires image-input support from the actual selected model. Check both at runtime, then read an actual generated preview. Relative paths use the session working directory. Reading a filename or image dimensions is not visual review. |
| Independent reviewer | Use an available, permitted [subagent provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/tool-subagent/README.md) to spawn a fresh reviewer context, not a history-inheriting fork. Inspect actual configured tool names, depth limits and routing permission; do not assume a literal tool name or that a requested model route is enabled. Give the reviewer the design contract and frozen artifact paths, not an author's all-green conclusion. |
| Saved-artifact checks | Reviewer reopens the saved BLEND, reimports the actual GLB and inspects actual preview pixels according to the [independent QA protocol](../skills/blender-asset-workflow/references/independent-qa.md). Fresh shell processes alone do not count as independent reviewers. |

If image input/attachments are unavailable, mark **visual QA not performed**. If no distinct reviewer can actually run, mark **self-check only**. Report exactly which stage is blocked; do not silently substitute a text-only answer or invent independence. If another reviewer route is available, use it only within its existing permissions and name the route used.

Blender CLI + Python remains the modeling path; Blender MCP is not required. Optional Linux timeout/RSS guards remain as documented in the README. On Windows use the direct PowerShell path with the resource guard off by default—without its protection. The Linux example runner does not silently downgrade on Windows. Do not disable sandboxing, install software, change network settings or read credentials to make a probe pass.

## Validation evidence

These observations apply to **dsh 0.2.1-rc.5 only**, on Linux with Blender 4.3.2. They do not certify other dsh versions, models or platforms.

- **Offline fixtures:** check bundle layout, frontmatter, required files and refusal to overwrite an existing copy. They do not invoke dsh or a model.
- **Actual provider check:** installed `SkillRegistry.snapshot/get` and `FileSystemSkillProvider` discovered `blender-asset-workflow` as `project-dsh`. The catalog completed and loaded a 4,302-byte entrypoint body from the pre-Windows-doc revision. This was not a mock, but it was not a model/UI test either.
- **Project-root correction:** the first provider check found no skill because a nested workspace inherited an ancestor Git root. An intentionally separate test-project boundary corrected discovery. Do not initialize Git without authorization.
- **CLI probe:** a separate 30-second-bounded background Blender probe exited successfully and reported 4.3.2.
- **Model-assisted smoke test:** the configured `deepseek-official/deepseek-flash` route loaded the real skill and built an original five-mesh/60-triangle table. It saved BLEND/GLB and produced a 256×256 preview. Builder and fresh reviewer received actual image content through `read_image`. The reviewer independently reopened/reimported the saved files and returned pass.
- **Observed cost:** 19 builder and 8 reviewer tool calls. All guarded Blender calls exited 0. Maximum sampled RSS was 451.1 MiB; the longest individual guarded call was 3.822 seconds. Nonfatal export/render/cache warnings did not prevent artifact verification.

This is one small Linux/Flash example, not a general scene-quality guarantee.

### Environment boundary

A launch that discarded existing proxy/CA settings could not reach the provider. Preserve the deployment's already-authorized network/trust configuration. Do not invent proxy values or weaken TLS.

The tested official headless configuration enabled its credential module to use the application's saved credential store. The user configures credentials privately in that application; no key belongs in chat, this repository or logs.

### Repeat on a new session

Do not treat a previous result as permanent capability certification:

1. Verify the actual catalog entry and loaded source path.
2. Run the bounded CLI probe and report the available execution route.
3. Build a tiny neutral model in a fresh output directory; save a preview and GLB.
4. Verify actual image delivery to an image-capable reviewer.
5. Have a fresh reviewer reopen/reimport the saved artifacts and record a verdict.

Report missing stages explicitly. The offline fixture alone is not an end-to-end compatibility claim. Coordinate using only the machine/session location and chosen model identifier—not credential values.

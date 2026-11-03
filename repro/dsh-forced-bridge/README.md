# 复现：「一句话 + 固定用桥前缀」臂 / Repro: one-sentence + fixed bridge prefix arm

固定 dreamcore-bedroom 对照实验中 `ours-dsh-bridge-forced` 这一臂的完整配置，便于在别的机器上复现。
Pins the exact configuration of the `ours-dsh-bridge-forced` arm so it can be reproduced elsewhere.

> **单次运行，不是统计结论。** Single run only; results are a signal, not a statistic.
> 本 PR 不修改仓库 `skills/` 下的 skill；`skill-snapshot/` 是该次运行实际加载的版本，与 main (8b9befa) 不同。

## 固定版本 / Pinned versions

| 组件 | 版本 |
|---|---|
| DSH (`dsh --version`) | 0.2.1-rc.5 |
| dsh-blender-plugin (npm, BSD-3-Clause, **不随仓库分发**) | 3.0.4 |
| Profile bundles | `@deepseek-ai/dsh-base`, `@deepseek-ai/dsh-headless`, `dsh-blender-plugin` |
| Blender | 4.5.3 LTS |
| Skill | `skill-snapshot/blender-asset-workflow/`（逐字拷贝自运行目录 `.dsh/skills/`） |
| 模型 | DeepSeek API（`llm-deepseek-api-key` provider）；API key 不在仓库中 |

### 快照与 main 的差异 / Snapshot vs main (8b9befa)
- `SKILL.md`、`references/windows-setup.md` 内容不同
- 快照多 `scripts/hard_gate.py`、`scripts/gated_write.sh`
- 快照没有 `references/blender-install.md`

### 快照 sha256
```
a5ac81176f2925fc911bea1e68da5e0676193e6ae9d09e7a8ccb92efdf3af38b  blender-asset-workflow/SKILL.md
073cda67b871405255e85876ba6c7c9c986abd927ab42cf550f23189ad59b2f6  blender-asset-workflow/references/assembly.md
b3d7597e7896119ab8a2c64ec3c0394a0a644573cee651220bab97944799c5ee  blender-asset-workflow/references/dsh-authentication.md
62648c1fff4729c1b5cc77494dfbab96e5ff21c4cb0eca9c5a005045050e897f  blender-asset-workflow/references/independent-qa.md
42c816dd234505d7903c39cbfb2b0b5a4ba2f1fe8fbabece7dbfa7799deb3acc  blender-asset-workflow/references/numeric-pitfalls.md
5c8dd1a42e733798af34d021150ac5214f3298aa59ac9b813f8b507b4389ee35  blender-asset-workflow/references/overlap-checks.md
cfea205543cedcbf0aafcca185b6874f143cf9236f668b9438b518ff9dd3f85e  blender-asset-workflow/references/revisions.md
2ae642dd7c87c72511e46c19a9d24e8ce3ccb2d65d4fc051b7f0591d4fd3aa09  blender-asset-workflow/references/runtime.md
065672120658283f96e36e4169c46c60e05864f99a427188b83fe20f50e5b7c1  blender-asset-workflow/references/verification.md
957049a75c2e062c549201ebbf564263f5b748630ec18cb1841fe73e40ef4e8b  blender-asset-workflow/references/windows-dsh.md
aa011afe1cd2859c89c368c6c7e20c8ec61943b4c1b723148a91242de0bba8ca  blender-asset-workflow/references/windows-setup.md
a4f0dfcc144fafd42659976fb55cc3bc283def5ece7893d9e77b288544b83b5f  blender-asset-workflow/scripts/gated_write.sh
4f15d64fdf0814cc65687237c3218a0160436f1d9d52474af21743862aa54df9  blender-asset-workflow/scripts/guarded_run.py
9681de9e51441d07d4887c45d7202b225c36cc5c001a7a7723c400fad29e1bec  blender-asset-workflow/scripts/hard_gate.py
44dead68e15ef2a5a9a34d6d650c71565ba6cb7ff4c0a36a6600fc7e5aeddd28  blender-asset-workflow/scripts/inspect_scene.py
b6c9677cbec9ebb675d4e7a27abcc2973940386c13a1474e7bf1c00ee52f5b25  blender-asset-workflow/scripts/overlap_audit.py
78d0a496f1b1ea5c12267c78ce06e1c6577d2e8e43a11fa7d89565adf0a47346  blender-asset-workflow/scripts/png_privacy.py
d959c576bc195d622c7f922e8985cd1429fb65b980d31641c656105408a120d6  blender-asset-workflow/scripts/white_preview.py
```
校验：`cd skill-snapshot && sha256sum -c ../SHA256SUMS.snapshot`

## 目录 / Files
- `input_prompt.txt` — 固定前缀 + 原话（整场只发一次，中途不催）
- `skill-snapshot/blender-asset-workflow/` — 实际加载的 skill
- `stub/blender-modeling/SKILL.md` — 禁用插件自带 modeling skill 的空壳
- `profile/` — profile 配置（`package.json`、`cordis*.yml`、`pnpm-*`；无密钥）
- `count_calls.py` — 从 jsonl 统计工具调用
- `results/beauty_960.jpg` — 本次成片缩略图

## 步骤 / Steps
前提：Node + npm、pnpm、Blender 4.5.3 在 PATH、DeepSeek API key（按 DSH 文档配置，勿提交）。

```bash
npm i -g @deepseek-ai/dsh@0.2.1-rc.5
dsh --version                    # 0.2.1-rc.5

# 建 profile 并装插件 3.0.4
mkdir -p ~/.dsh/profiles/bridge-ours
cp repro/dsh-forced-bridge/profile/* ~/.dsh/profiles/bridge-ours/
dsh plugin --profile bridge-ours install   # 按 package.json / pnpm-lock.yaml 安装 dsh-blender-plugin@3.0.4
# 或：dsh plugin --profile bridge-ours add dsh-blender-plugin@3.0.4

# 项目工作目录，放 skill 快照 + 空壳
RUN=~/runs/forced-bridge && mkdir -p $RUN/.dsh/skills && cd $RUN
cp -a <repo>/repro/dsh-forced-bridge/skill-snapshot/blender-asset-workflow .dsh/skills/
cp -a <repo>/repro/dsh-forced-bridge/stub/blender-modeling .dsh/skills/
cp <repo>/repro/dsh-forced-bridge/input_prompt.txt .
find .dsh > skills_listing.txt

# headless 一次性运行（JSON 事件流）
date +%s > start_epoch
dsh --profile bridge-ours --json "$(cat input_prompt.txt)" > dsh_run.jsonl 2> dsh_stderr.log
python3 <repo>/repro/dsh-forced-bridge/count_calls.py dsh_run.jsonl
```

## 预期检查 / Expected checks
1. `skills` 只出现 `blender-asset-workflow`（一次）。
2. 第一次建模类调用为 `blender_rt_*`（本次：`blender_rt_commands` → `blender_viewport` → `blender_rt_worker` start/exec）。
3. `bash blender -b` 计数为 0。

## 本次结果 / This run's numbers
约 67 分钟，DSH 自行退出。总计 201：`blender_rt_worker` 96（exec 77 / see 17 / start 2），read_image 45，bash 37，write 15，`blender_rt_headless` 3，其它桥 3；bash 跑 `blender -b` 0 次。
注：无独立 QA（仅模型自查）；GLB 是运行结束后补导的，不算该臂产出；显示器为平板而非 CRT。

## 未能精确固定 / Not pinned exactly
- 当次 headless 命令行没有逐字记录；上面的命令按 trace 记录的 `dsh --profile … --json` 形式重建。
- 模型 ID 与采样参数取决于 DeepSeek provider 的默认值，未固定。
- `@deepseek-ai/dsh-base` / `dsh-headless` bundle 版本随 DSH 0.2.1-rc.5 自带。

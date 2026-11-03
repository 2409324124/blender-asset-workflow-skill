# DSH 梦核卧室：实验与工作流报告

记录 dreamcore-bedroom 的历史强制用桥实验及三组配置的运行证据。工作流问题、证据与改进方案见 [实验报告](REPORT.md)；配置、实际加载、产物与缺陷见 [三组对照](RESULTS.md)。B 含中断后续接，不是三次都在原条件下完整完成。

**主要验证结果：关闭第三方插件自带建模 skill 后，DSH 仍通过实时桥工具与我们的 skill 完成了梦核卧室。** [报告](REPORT.md)直接展示 A/B/C 最终渲染，并说明 skill 隔离已完成、实时执行路线奏效，以及为何这尚不等于 QA 打转或穿模已被修复。

This directory preserves the historical forced-bridge record and documents three subsequent configurations, including B's interrupted run and recovery. See the [workflow report](REPORT.md) and [comparison results](RESULTS.md).

> **单次实例观察，不是统计结论；B 含中断后续接。** These are observations, not statistics; B includes recovery.
> 本 PR 不修改仓库 `skills/` 下的 skill；`skill-snapshot/` 是该次运行实际加载的版本，与 main (8b9befa) 不同。

## 历史 67 分钟运行的记录版本 / Historical run versions

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
- `input_prompt.txt` — 固定前缀 + 原话；B/C 初始运行只发一次，B 续接另加恢复指令并单独记录
- `skill-snapshot/blender-asset-workflow/` — 实际加载的 skill
- `stub/blender-modeling/SKILL.md` — 禁用提示空壳；单独放入嵌套运行目录不能保证覆盖插件 skill
- `profile/` — profile 配置（`package.json`、`cordis*.yml`、`pnpm-*`；无密钥）
- `count_calls.py` / `summarize_trace.py` — 严格读取事件流、生成调用统计及脱敏序列
- `summarize_usage.py` / `results/token-usage.json` — 从实际记录提取非缓存输入、缓存与输出 token；A 的独立 reviewer 单列，缺失用量不按零处理
- `prepare_bridge_only.py` / `REPRODUCE.md` — 隔离插件副本并仅关闭内置 skill 注册，及三组复现步骤
- `profile-no-bridge/` / `input_prompt_no_bridge.txt` — 无 DSH Blender 插件配置及去掉强制用桥前缀的需求正文
- `REPORT.md` / `RESULTS.md` — 工作流分析与下一 PR 方案，以及成图和运行条件
- `audit_selected_surfaces.py` / `results/arm-c-selected-surfaces.json` — 针对 C 已保存场景的只读相交证据
- `results/evidence-manifest.json` / `results/arm-c-workflow-evidence.json` — 版本、提示词和产物哈希，以及自查范围与关键调用索引
- `results/beauty_960.jpg` — 原记录成片缩略图
- `results/rerun_hero_960.jpg` — 本机再跑的一张成片。点图片打开文件。

本机历史再跑[成片](results/rerun_hero_960.jpg)（Blender 5.2.2，约 34 分钟，95 次调用）。事件流显示实际加载的是插件自带 `blender-modeling`，不是预期空壳；我们的 skill 当时是否可被发现缺少证据，不把它当作完整 B 组。原记录的数字和 `beauty_960.jpg` 不变。A/B/C 的图片和条件集中展示在 [RESULTS.md](RESULTS.md)。

## 复现 / Reproduction

详见 [三组隔离复现步骤](REPRODUCE.md)。之前将空壳放在嵌套运行目录下的做法并未成功覆盖插件 skill，不能作为有效隔离方式；仅有文件清单也不能证明模型实际加载了 skill。C 组采用隔离插件副本并关闭该副本中的 `registerBundledSkill`，保留桥及插件其他工具。预检和正式运行都应核对工具返回内容与实际 skill 调用。

## 历史运行结果 / Historical run numbers
原记录报告约 67 分钟，DSH 自行退出。报告总计 201：`blender_rt_worker` 96（exec 77 / see 17 / start 2），read_image 45，bash 37，write 15，`blender_rt_headless` 3，其它桥 3；bash 跑 `blender -b` 0 次。
原始完整事件流不在本仓库，以上数据未能独立复核。原记录无独立 QA（仅模型自查）；GLB 是运行结束后补导的，不算该臂产出；显示器为平板而非 CRT。

## 未能精确固定 / Not pinned exactly
- 历史运行的 headless 命令行没有逐字记录；复现步骤按记录的 `dsh --profile … --json` 形式重建，不能代替原始命令证据。
- 模型 ID 与采样参数取决于 DeepSeek provider 的默认值，未固定。
- `@deepseek-ai/dsh-base` / `dsh-headless` bundle 版本随 DSH 0.2.1-rc.5 自带。

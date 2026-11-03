# 三组实验的隔离复现

本文件描述实验环境，不提供 DeepSeek 凭证。使用 Node >= 24.9、DSH 0.2.1-rc.5、pnpm、可运行的 Blender，按 DSH 官方方式在本机配置 `DEEPSEEK_API_KEY`。运行前确认目标路径为空、磁盘和算力足够；三次运行各自独立，可能耗时较长。原始事件流包含提示词、模型生成的代码和本机路径，公开前应检查；不要提交密钥或未经检查的原始日志。

从仓库根目录执行，以下变量只用于这次实验：

```bash
export REPRO_SOURCE="$PWD/repro/dsh-forced-bridge"
export REPRO_RUN="$PWD/runs/three-arm-repro"
for arm in a b c; do
  mkdir -p "$REPRO_RUN/$arm/work" "$REPRO_RUN/$arm/dsh-home/profiles" \
    "$REPRO_RUN/$arm/dsh-home/skills" "$REPRO_RUN/$arm/agents-home"
  cp -a "$REPRO_SOURCE/skill-snapshot/blender-asset-workflow" \
    "$REPRO_RUN/$arm/dsh-home/skills/"
done

# A：只有 DSH base/headless 和我们的 skill，没有插件。
mkdir -p "$REPRO_RUN/a/dsh-home/profiles/bridge-ours"
cp "$REPRO_SOURCE/profile-no-bridge/package.json" "$REPRO_RUN/a/dsh-home/profiles/bridge-ours/"
cp "$REPRO_SOURCE/profile/cordis.yml" "$REPRO_SOURCE/profile/cordis.patch.yml" \
  "$REPRO_RUN/a/dsh-home/profiles/bridge-ours/"
cp "$REPRO_SOURCE/input_prompt_no_bridge.txt" "$REPRO_RUN/a/work/input_prompt.txt"

# B：安装未经修改的第三方插件；两种 skill 都可被发现。
cp -a "$REPRO_SOURCE/profile" "$REPRO_RUN/b/dsh-home/profiles/bridge-ours"
DSH_HOME="$REPRO_RUN/b/dsh-home" dsh plugin --profile bridge-ours install
cp "$REPRO_SOURCE/input_prompt.txt" "$REPRO_RUN/b/work/input_prompt.txt"

# C：复制 B 的 profile；仅在副本中禁用插件的 skill 注册。
python3 "$REPRO_SOURCE/prepare_bridge_only.py" \
  "$REPRO_RUN/b/dsh-home/profiles/bridge-ours" "$REPRO_RUN/c/dsh-home/profiles/bridge-ours"
cp -a "$REPRO_SOURCE/stub/blender-modeling" "$REPRO_RUN/c/dsh-home/skills/"
cp "$REPRO_SOURCE/input_prompt.txt" "$REPRO_RUN/c/work/input_prompt.txt"
```

`prepare_bridge_only.py` 会检查插件版本和原始 `lib/plugin.js` 的 SHA-256，拒绝修改其他构建或覆盖现有输出，并显示修改前后哈希。它复制整个 profile，只有副本的插件入口被修改；其他插件工具仍然存在。空壳本身并不保证覆盖插件的同名 skill。

正式运行前，在**单独的会话**验证 skill 和工具，不要把预检指令追加到建模提示词：

- A：确认组合配置没有 `dsh-blender-plugin`，调用 `skill(blender-asset-workflow)` 并检查返回内容和目录。
- B：分别调用 `skill(blender-modeling)` 和 `skill(blender-asset-workflow)`，核对返回目录。两者可用不等于正式运行一定会调用两者。
- C：分别调用两种 skill，确认 `blender-modeling` 返回的是禁用空壳，另一项返回我们的快照；再确认桥工具可用。正式运行后还须检查实际 skill 调用。

在一组完成后再启动下一组，避免争用 Blender。示例中 B、C 使用隔离端口，避免误连接现有 Blender 会话；如端口已占用，请改用空闲端口并记录环境差异。确认 DSH 可正常访问模型，并为每组分别执行：

本机 B 组曾在主图渲染调用超时后启动第二个渲染作业，随后系统卡死并重启；具体原因未确认。**超时或 worker 存活状态都不能证明原渲染已结束**。下次运行应先明确检查正在运行的 Blender 进程及渲染状态，确认旧任务完成或已安全停止后才启动新作业，同时记录内存、交换分区和显存的连续采样。若更改采样数、资源限制或其他运行条件，须记录差异，不将结果冒充原配置的同条件复现。

```bash
# arm 设为 a、b 或 c；在新 shell 中按顺序分别运行。
arm=a
(
  cd "$REPRO_RUN/$arm/work"
  export DSH_HOME="$REPRO_RUN/$arm/dsh-home" AGENTS_HOME="$REPRO_RUN/$arm/agents-home"
  export DSH_BLENDER_EXE="$(command -v blender)"
  if [ "$arm" != a ]; then
    export DSH_BLENDER_ADDON_PORT=19876 DSH_BLENDER_HTTP_PORT=19877 DSH_BLENDER_WORKER_PORT=19879
  fi
  dsh --profile bridge-ours --json "$(cat input_prompt.txt)" > ../run.jsonl 2> ../run.stderr
)
python3 "$REPRO_SOURCE/count_calls.py" "$REPRO_RUN/$arm/run.jsonl"
python3 "$REPRO_SOURCE/summarize_trace.py" "$REPRO_RUN/$arm/run.jsonl" > "$REPRO_RUN/$arm/trace-summary.json"
```

`count_calls.py` 对空事件流和无效 JSON 报错；其 bash 背景命令扫描只识别字面命令，不能证明动态 shell 代码没有启动 Blender。`summarize_trace.py` 只导出工具名、有限的操作名、状态、顺序和原始日志哈希，不输出命令、完整结果或路径；输出前仍应人工检查。`tool_result` 的 `completed` 不等于 Blender 操作成功，需查看原始结果。保留场景及其相关贴图、截图、日志和版本信息，并明确独立审核是否可用。

## 复核 C 的指定对象相交

`audit_selected_surfaces.py` 只用于本次 C 场景中已有的对象名；它不是建模工具，也不会修复或保存场景。使用保留的 C 场景副本，输出到新的报告路径：

```bash
blender --factory-startup -noaudio --background /path/to/C/dreamcore_bedroom.blend \
  --disable-autoexec --threads 2 --python-exit-code 1 \
  --python "$REPRO_SOURCE/audit_selected_surfaces.py" -- --report selected-surfaces.json
```

输入文件 SHA-256 应与 `results/arm-c-selected-surfaces.json` 一致。脚本将求值后的网格及曲线转换到世界坐标，通过 BVH 筛选后验证严格的边／三角形穿越。正结果证明表面穿越；负结果不能证明不存在完全包含、共面接触或其他未测对象的相交。输出只包含指定配对、计数、方法与场景哈希，不包含本机路径。

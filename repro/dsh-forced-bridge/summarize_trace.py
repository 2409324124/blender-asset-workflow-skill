"""Make a shareable call sequence without prompts, commands, paths or results."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


def summarize(path):
    raw = path.read_bytes()
    counts = Counter()
    sequence = []
    result_statuses = Counter()
    skills = {}
    final_events = 0
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except (ValueError, UnicodeError) as exc:
            raise ValueError(f"line {number}: invalid JSON") from exc
        if not isinstance(event, dict):
            raise ValueError(f"line {number}: event must be an object")
        kind = event.get("type")
        if kind == "final":
            final_events += 1
        if kind == "tool_result":
            status = event.get("status")
            result_statuses[status if status in ("completed", "error", "failed") else "other"] += 1
        if kind != "tool_call":
            continue
        tool = event.get("tool")
        inputs = event.get("input") or {}
        if not isinstance(tool, str) or not re.fullmatch(r"[a-zA-Z0-9_]+", tool) or not isinstance(inputs, dict):
            raise ValueError(f"line {number}: invalid tool call")
        counts[tool] += 1
        call = {"index": len(sequence) + 1, "tool": tool}
        if tool == "skill":
            skill = inputs.get("name")
            call["skill"] = skill if skill in ("blender-modeling", "blender-asset-workflow") else "other"
            skills[call["skill"]] = skills.get(call["skill"], 0) + 1
        if tool.startswith("blender_"):
            operation = inputs.get("op") or inputs.get("action")
            if isinstance(operation, str) and re.fullmatch(r"[a-zA-Z0-9_]{1,48}", operation):
                call["operation"] = operation
        sequence.append(call)
    if not sequence:
        raise ValueError("no tool calls; no execution evidence")
    return {
        "trace_sha256": hashlib.sha256(raw).hexdigest(),
        "call_count": len(sequence),
        "tool_counts": dict(counts.most_common()),
        "skill_calls": skills,
        "tool_result_statuses": dict(result_statuses),
        "final_events": final_events,
        "calls": sequence,
        "limitations": "Names and statuses only. A completed tool event does not prove its operation succeeded; inspect the original trace.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args()
    try:
        result = summarize(args.jsonl)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

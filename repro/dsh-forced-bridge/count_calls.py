"""Summarize DSH tool calls; reject malformed or empty execution evidence."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shlex
import sys


def background_invocations(command):
    """Find literal Blender background commands; dynamic shell code may evade this."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True
        lexer.commenters = ""
        words = list(lexer)
    except ValueError:
        return None
    matches = []
    for i, word in enumerate(words):
        name = Path(word).name.lower()
        if not re.fullmatch(r"blender(?:\.exe)?", name):
            continue
        args = []
        for arg in words[i + 1:]:
            if re.fullmatch(r"[;&|()]+", arg):
                break
            args.append(arg)
        if "-b" in args or "--background" in args:
            matches.append(word)
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, nargs="?", default=Path("dsh_run.jsonl"))
    args = parser.parse_args()
    counts, sub = Counter(), Counter()
    skills, sequence, background, unparsed_shell = [], [], [], 0
    try:
        with args.jsonl.open(encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"line {number}: invalid JSON: {exc.msg}") from exc
                if not isinstance(event, dict):
                    raise ValueError(f"line {number}: event must be an object")
                if event.get("type") != "tool_call":
                    continue
                tool, inputs = event.get("tool"), event.get("input") or {}
                if not isinstance(tool, str) or not isinstance(inputs, dict):
                    raise ValueError(f"line {number}: invalid tool_call")
                counts[tool] += 1
                sequence.append(tool)
                if tool == "skill":
                    skills.append(inputs.get("name"))
                if tool.startswith("blender_"):
                    operation = inputs.get("op") or inputs.get("action") or inputs.get("command") or ""
                    sub[f"{tool}:{str(operation)[:20]}"] += 1
                if tool == "bash":
                    command = inputs.get("command")
                    if not isinstance(command, str):
                        unparsed_shell += 1
                        continue
                    matches = background_invocations(command)
                    if matches is None:
                        unparsed_shell += 1
                    elif matches:
                        background.append((number, command[:160]))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not sequence:
        print("error: no tool_call events; cannot infer execution behavior", file=sys.stderr)
        return 1
    print("total", sum(counts.values()))
    print(dict(counts.most_common()))
    print(dict(sub.most_common(20)))
    print("skills", skills)
    print("bash literal blender background calls", len(background))
    for line, command in background[:10]:
        print(" ", f"line {line}:", command)
    print("bash commands not parsed", unparsed_shell)
    print("first6", sequence[:6])
    print("note: literal shell scan only; inspect dynamic commands and tool results separately")
    return 2 if unparsed_shell else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
# Usage: gated_write.sh scene.blend gate.json [gate flags...] -- <write command...>
# Runs hard_gate.py; only runs the write command (white_preview / GLB export) if export_allowed.
set -u; B=$1; G=$2; shift 2; GF=(); while [ $# -gt 0 ] && [ "$1" != "--" ]; do GF+=("$1"); shift; done; shift
D=$(dirname "$(readlink -f "$0")")
blender -b "$B" --python "$D/hard_gate.py" -- --out "$G" "${GF[@]}" >/dev/null 2>&1; rc=$?
if [ $rc -ne 0 ]; then echo "BLOCKED: $(python3 -c "import json;print(json.load(open('$G'))['blocked'])" 2>/dev/null || echo gate crashed rc=$rc)" >&2; exit 2; fi
echo "gate: $(python3 -c "import json;print(json.load(open('$G'))['verdict'])")" ; exec "$@"

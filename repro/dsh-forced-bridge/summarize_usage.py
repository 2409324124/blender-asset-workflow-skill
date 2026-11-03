"""Export reported token counts without prompts, code, responses or paths.

For DSH 0.2.1-rc.5: JSONL uses step_end aggregates; persisted v4 sessions
use one usage value per assistant message/attempt. Never sum both formats.
Compressed v4 sessions require the zstd command.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys


FIELDS = ('inputTokens', 'cacheReadTokens', 'cacheWriteTokens', 'outputTokens', 'totalTokens')


def summarize(path):
    raw = path.read_bytes()
    compressed = path.suffix == '.zstd'
    decoded = subprocess.run(['zstd', '-q', '-d', '-c', str(path)], check=True,
                             capture_output=True).stdout if compressed else raw
    totals = Counter()
    missing_fields = Counter()
    reports = missing = starts = ends = 0
    for number, line in enumerate(decoded.splitlines(), 1):
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError(f'line {number}: event must be an object')
        if compressed:
            starts += event.get('type') == 'step/start'
            ends += event.get('type') == 'step/end'
            if event.get('type') not in ('assistant/message', 'assistant/attempt'):
                continue
            data = event.get('data') or {}
            usage = data.get('usage')
            if not isinstance(usage, dict):
                samples = [item.get('chunk', {}).get('usage') for item in data.get('stream', [])
                           if isinstance(item, dict) and item.get('chunk', {}).get('type') == 'usage']
                usage = samples[-1] if samples else None
        else:
            starts += event.get('type') == 'status' and event.get('phase') == 'step_start'
            ends += event.get('type') == 'status' and event.get('phase') == 'step_end'
            if event.get('type') != 'status' or event.get('phase') != 'step_end':
                continue
            usage = event.get('usage')
        if not isinstance(usage, dict):
            missing += 1
            continue
        reports += 1
        for field in FIELDS:
            value = usage.get(field)
            if value is None:
                missing_fields[field] += 1
            elif isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                totals[field] += value
            else:
                raise ValueError(f'line {number}: invalid {field}')
    if not reports:
        raise ValueError('no reported token usage')
    return {
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'format': 'session-v4-zstd' if compressed else 'headless-jsonl',
        'usage_records': reports,
        'records_without_usage': missing,
        'unclosed_steps': max(0, starts - ends),
        'reported_totals': {field: totals[field] if missing_fields[field] < reports else None for field in FIELDS},
        'records_missing_fields': dict(missing_fields),
        'limitations': 'Reported usage only; unknown attempts are not zero. Sum a direct usage OR its mirrored stream value, never both. Do not add a session to its matching headless log. Excludes prechecks, title generation, external reviewers and monetary pricing.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        result = summarize(args.source)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

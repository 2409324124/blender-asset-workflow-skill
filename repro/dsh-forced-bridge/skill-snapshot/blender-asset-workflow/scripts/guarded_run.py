#!/usr/bin/env python3
"""Run an owned process group with bounded cleanup. POSIX; Linux RSS optional."""
import argparse, json, math, os, signal, subprocess, sys, time
from pathlib import Path


def group_rss(pgid):
    total = 0
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if os.getpgid(int(entry.name)) != pgid:
                continue
            for line in (entry / 'status').read_text().splitlines():
                if line.startswith('VmRSS:'):
                    total += int(line.split()[1]) * 1024
        except (OSError, ProcessLookupError, ValueError):
            pass
    return total


def group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def stop_group(proc, grace):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    until = time.monotonic() + grace
    while group_alive(proc.pid) and time.monotonic() < until:
        proc.poll()  # reap group leader even if descendants remain
        time.sleep(.05)
    if group_alive(proc.pid):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    proc.wait(timeout=max(1., grace))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--timeout', type=float, required=True)
    p.add_argument('--grace', type=float, default=2.)
    p.add_argument('--max-rss-mib', type=float)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    if os.name != 'posix': p.error('POSIX process groups required')
    if not all(math.isfinite(v) and v > 0 for v in (a.timeout, a.grace)):
        p.error('timeout/grace must be finite and positive')
    if not command: p.error('command required after --')
    if a.max_rss_mib is not None and (not math.isfinite(a.max_rss_mib) or a.max_rss_mib <= 0 or not sys.platform.startswith('linux')):
        p.error('finite positive --max-rss-mib is supported only on Linux')
    # Reserve report before execution; never clobber an earlier run.
    with a.report.open('x') as report:
        start = time.monotonic(); peak = 0; reason = 'exited'; proc = None
        try:
            proc = subprocess.Popen(command, start_new_session=True)
            while proc.poll() is None:
                if sys.platform.startswith('linux'):
                    peak = max(peak, group_rss(proc.pid))
                if time.monotonic() - start > a.timeout:
                    reason = 'timeout'; break
                if a.max_rss_mib is not None and peak > a.max_rss_mib * 1024**2:
                    reason = 'rss_limit'; break
                time.sleep(.1)
            if reason != 'exited' or group_alive(proc.pid):
                stop_group(proc, a.grace)
            rc = proc.wait()
        except BaseException as error:
            if proc is not None:
                stop_group(proc, a.grace)
            json.dump({'reason':'runner_error','error':str(error)}, report, indent=2)
            raise
        result = {'command':command,'reason':reason,'child_returncode':rc,
                  'elapsed_seconds':time.monotonic()-start,
                  'sampled_group_peak_rss_bytes':peak if sys.platform.startswith('linux') else None}
        json.dump(result, report, indent=2)
    return 124 if reason == 'timeout' else 125 if reason == 'rss_limit' else (rc if rc >= 0 else 128-rc)

if __name__ == '__main__':
    sys.exit(main())

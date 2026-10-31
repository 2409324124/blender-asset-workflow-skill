# Headless execution and resource budgets

Use `blender -b --python-exit-code 1 --python task.py -- ...`. Verify the installed version before relying on API properties. Save the native candidate before previews so a render failure cannot erase the modeling result. Preview from a separate fresh process; never save its temporary material, visibility or camera overrides into the delivery model.

Check actual memory availability first (Linux `/proc/meminfo`, otherwise system monitor). One Blender process is the starting point, not a universal concurrency limit. Measure a representative job, retain headroom for the system and other tasks, then parallelize independent modeling jobs with unique paths. Serialize costly rendering if budget is tight. Prefer Workbench/solid white output; white materials alone do not make a high-sample path-traced render cheap.

`guarded_run.py` requires Python 3 and POSIX. Timeout handling uses POSIX process groups (Linux tested; macOS untested). Limits must be finite and positive. Optional live RSS limiting is **Linux-only**, includes the process group, and is a sampled guard rather than a hard memory sandbox. Linux `VmRSS`/`MemAvailable` are KiB; the helper converts them to bytes. On unsupported platforms requesting RSS limits fails clearly rather than silently ignoring the limit. On timeout or RSS breach it sends process-group TERM, waits bounded grace, sends KILL if necessary, and reaps its direct child. Terminated orphan descendants can remain zombies until the operating system reaps them; the regression checks they are no longer running. Exit codes: child status normally; 124 timeout; 125 RSS limit. Its JSON records sampled peak RSS, not an exact kernel peak.

Example for a chosen machine budget (not a recommended universal value):
`python3 scripts/guarded_run.py --timeout 120 --max-rss-mib 2048 --report run-01.json -- blender -b --python-exit-code 1 --python build.py`

A tool failure is not evidence the model failed visually. Preserve the log, isolate the error and retry only the affected step. Never report measured resource values from an old run as current.

Generated white previews remove PNG text, EXIF and time chunks without re-encoding image data. This does not remove visible scene information, anonymize BLEND files or sanitize arbitrary external images. The minimal example applies the same cleanup to all three previews.

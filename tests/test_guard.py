import json, pathlib, subprocess, sys, tempfile, time, unittest
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'skills/blender-asset-workflow/scripts/guarded_run.py'
class GuardTests(unittest.TestCase):
 def run_case(self, code, extra=(), timeout='3'):
  with tempfile.TemporaryDirectory() as d:
   report=pathlib.Path(d)/'report.json'; start=time.monotonic()
   p=subprocess.run([sys.executable,str(SCRIPT),'--timeout',timeout,'--grace','.2','--report',str(report),*extra,'--',sys.executable,'-c',code],timeout=10)
   return p.returncode,json.loads(report.read_text()),time.monotonic()-start
 def test_success(self):
  rc,r,_=self.run_case('print("neutral fixture")'); self.assertEqual(rc,0);self.assertEqual(r['reason'],'exited')
 def test_child_error(self):
  rc,r,_=self.run_case('raise SystemExit(7)');self.assertEqual(rc,7)
 def test_term_ignored(self):
  rc,r,t=self.run_case('import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(20)',timeout='.3');self.assertEqual(rc,124);self.assertLess(t,4)
 def test_descendant_cleanup(self):
  if not sys.platform.startswith('linux'): self.skipTest('Linux /proc termination evidence')
  with tempfile.TemporaryDirectory() as d:
   pidfile=pathlib.Path(d)/'descendant.pid'
   child='import os,signal,time,pathlib;signal.signal(signal.SIGTERM,signal.SIG_IGN);pathlib.Path('+repr(str(pidfile))+').write_text(str(os.getpid()));time.sleep(20)'
   leader='import subprocess,sys,time,pathlib;subprocess.Popen([sys.executable,"-c",'+repr(child)+']);p=pathlib.Path('+repr(str(pidfile))+');\nwhile not p.exists(): time.sleep(.01)'
   rc,r,t=self.run_case(leader);self.assertEqual(rc,0);self.assertLess(t,4)
   pid=int(pidfile.read_text());status=pathlib.Path('/proc')/str(pid)/'status'
   # A terminated orphan may remain a zombie until PID 1 reaps it. It must
   # never remain a running/sleeping TERM-ignoring process after the guard.
   if status.exists():
    state=next(line for line in status.read_text().splitlines() if line.startswith('State:'))
    self.assertIn(state.split()[1],['Z','X'],state)
 def test_nonfinite_limits_rejected(self):
  for option in ['--timeout','--grace','--max-rss-mib']:
   for value in ['nan','inf','-inf']:
    with self.subTest(option=option,value=value), tempfile.TemporaryDirectory() as d:
     report=pathlib.Path(d)/'report.json';marker=pathlib.Path(d)/'ran'
     cmd=[sys.executable,str(SCRIPT),'--timeout','1',option+'='+value,'--report',str(report),'--',sys.executable,'-c','from pathlib import Path;Path('+repr(str(marker))+').touch()']
     proc=subprocess.run(cmd,capture_output=True,timeout=3)
     self.assertEqual(proc.returncode,2);self.assertFalse(marker.exists());self.assertFalse(report.exists())
 def test_memory(self):
  if not sys.platform.startswith('linux'): self.skipTest('Linux RSS')
  rc,r,t=self.run_case('import time;x=bytearray(80*1024*1024);time.sleep(10)',extra=('--max-rss-mib','40'));self.assertEqual(rc,125);self.assertGreater(r['sampled_group_peak_rss_bytes'],40*1024**2)
if __name__=='__main__':unittest.main()

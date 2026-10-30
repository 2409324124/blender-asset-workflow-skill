#!/usr/bin/env python3
"""Build/preview/verify a neutral shop, one bounded Blender process at a time."""
import argparse, hashlib, json, math, shutil, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SCRIPTS=ROOT/'skills/blender-asset-workflow/scripts'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True);p.add_argument('--blender',default='blender')
p.add_argument('--timeout',type=float,default=120);p.add_argument('--max-rss-mib',type=float,default=2048)
a=p.parse_args()
if not all(math.isfinite(x) and x>0 for x in (a.timeout,a.max_rss_mib)):p.error('limits must be finite and positive')
blender=shutil.which(a.blender)
if not blender:p.error('Blender executable not found')
if not sys.platform.startswith('linux'):p.error('This bounded example runner currently requires Linux RSS monitoring')
out=a.output.resolve()
if out.exists():p.error('output already exists; choose a new directory')
out.mkdir(parents=True,exist_ok=False)
start=time.monotonic()
def run(label,arguments):
 cmd=[sys.executable,str(SCRIPTS/'guarded_run.py'),'--timeout',str(a.timeout),'--max-rss-mib',str(a.max_rss_mib),'--report',str(out/(label+'-resources.json')),'--',blender,'-b','-t','2',*map(str,arguments)]
 with (out/(label+'.log')).open('x') as log:
  subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
run('build',['--python-exit-code','1','--python',HERE/'build.py','--','--output',out])
hash_before=hashlib.sha256((out/'shop.blend').read_bytes()).hexdigest()
run('native-inspect',[out/'shop.blend','--python-exit-code','1','--python',SCRIPTS/'inspect_scene.py','--','--report',out/'native.json'])
run('glb-inspect',['--python-exit-code','1','--python',SCRIPTS/'inspect_scene.py','--','--import-glb',out/'shop.glb','--report',out/'glb.json'])
x=json.loads((out/'native.json').read_text());y=json.loads((out/'glb.json').read_text())
native={o['name']:o for o in x['meshes']};glb={o['name']:o for o in y['meshes']}
if native.keys()!=glb.keys():raise RuntimeError('native/GLB object inventory differs')
if sum(o['triangles'] for o in native.values())!=sum(o['triangles'] for o in glb.values()):raise RuntimeError('native/GLB triangle counts differ')
max_error=max(abs(a-b) for name in native for field in ['bounds_min','bounds_max'] for a,b in zip(native[name][field],glb[name][field]))
if max_error>1e-5:raise RuntimeError('native/GLB world bounds differ')
if native['Roof']['hide_render']:raise RuntimeError('preview visibility leaked into source')
if hash_before!=hashlib.sha256((out/'shop.blend').read_bytes()).hexdigest():raise RuntimeError('inspection altered source')
result={'mesh_objects':len(native),'native_triangles':sum(o['triangles'] for o in native.values()),
 'glb_triangles':sum(o['triangles'] for o in glb.values()),'max_world_bound_error':max_error,
 'roof_preserved':True,'elapsed_seconds':time.monotonic()-start,
 'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.suffix in ['.blend','.glb','.png']},
 'scope':'Roundtrip data checks; preview pixels and overlap candidates still require review.'}
(out/'verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

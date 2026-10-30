"""Integration regression: requires Blender in PATH; transient neutral fixture."""
import hashlib, json, pathlib, shutil, subprocess, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/blender-asset-workflow/scripts'
@unittest.skipUnless(shutil.which('blender'),'Blender required')
class BlenderTests(unittest.TestCase):
 def run_blender(self,*args,ok=True):
  p=subprocess.run(['blender','-b',*map(str,args)],capture_output=True,text=True,timeout=90)
  if ok:self.assertEqual(p.returncode,0,p.stdout+p.stderr)
  else:self.assertNotEqual(p.returncode,0)
 def test_artifact_roundtrip_and_preview(self):
  with tempfile.TemporaryDirectory() as directory:
   d=pathlib.Path(directory)
   self.run_blender('--python-exit-code','1','--python',ROOT/'tests/make_fixture.py','--',d)
   source=d/'fixture.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
   self.run_blender(source,'--python-exit-code','1','--python',SCRIPTS/'inspect_scene.py','--','--report',d/'native.json')
   self.run_blender('--python-exit-code','1','--python',SCRIPTS/'inspect_scene.py','--','--import-glb',d/'fixture.glb','--report',d/'glb.json')
   a=json.loads((d/'native.json').read_text());b=json.loads((d/'glb.json').read_text())
   self.assertEqual(len(a['meshes']),2);self.assertEqual(len(b['meshes']),2)
   for x,y in zip(a['meshes'],b['meshes']):
    self.assertEqual(x['name'],y['name']);self.assertEqual(x['parent'],y['parent'])
    for k in ['bounds_min','bounds_max']:
     for u,v in zip(x[k],y[k]):self.assertAlmostEqual(u,v,places=5)
    for row1,row2 in zip(x['matrix_world'],y['matrix_world']):
     for u,v in zip(row1,row2):self.assertAlmostEqual(u,v,places=5)
   self.assertEqual(a['meshes'][0]['bounds_min'],[-2.,-1.,0.]);self.assertEqual(a['meshes'][0]['bounds_max'],[2.,1.,1.])
   self.run_blender(source,'--python-exit-code','1','--python',SCRIPTS/'white_preview.py','--','--output',d/'white.png','--size','256')
   self.assertEqual((d/'white.png').read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
   self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
   self.run_blender(source,'--python-exit-code','1','--python',SCRIPTS/'inspect_scene.py','--','--report',d/'native.json',ok=False)
 def test_hidden_scene_glb_import_is_empty(self):
  with tempfile.TemporaryDirectory() as directory:
   d=pathlib.Path(directory)
   self.run_blender('--python-exit-code','1','--python',ROOT/'tests/make_fixture.py','--',d)
   self.run_blender('--python-exit-code','1','--python',ROOT/'tests/hidden_scene_fixture.py','--',d/'stale.blend')
   self.run_blender(d/'stale.blend','--python-exit-code','1','--python',SCRIPTS/'inspect_scene.py','--','--import-glb',d/'fixture.glb','--report',d/'clean.json')
   data=json.loads((d/'clean.json').read_text())
   self.assertEqual({o['name'] for o in data['meshes']},{'Base','Upright'})
 def test_long_box_projected_framing(self):
  self.run_blender('--python-exit-code','1','--python',ROOT/'tests/framing_fixture.py','--',SCRIPTS/'white_preview.py')
 def test_overlap_actual_scene(self):
  self.run_blender('--python-exit-code','1','--python',ROOT/'tests/overlap_scene_fixture.py','--',SCRIPTS/'overlap_audit.py')
if __name__=='__main__':unittest.main()

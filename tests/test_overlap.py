import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).resolve().parents[1]/'skills/blender-asset-workflow/scripts/overlap_audit.py'
spec=importlib.util.spec_from_file_location('audit',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def obj(name,lo,hi):return {'name':name,'bounds':[lo,hi]}
class OverlapTests(unittest.TestCase):
 def setUp(self):self.wall=obj('Wall',[0,0,0],[1,1,1])
 def test_detect_candidate(self):
  r=m.audit([self.wall,obj('Furniture',[.8,.2,.2],[2,.8,.8])]);self.assertEqual(len(r['candidates']),1)
 def test_explicit_exception(self):
  r=m.audit([self.wall,obj('WindowFrame',[.9,.1,.1],[1.1,.9,.9])],[{'objects':['Wall','WindowFrame'],'reason':'Named frame insertion joint'}]);self.assertEqual(len(r['exemptions']),1);self.assertFalse(r['candidates'])
 def test_touch_is_not_candidate(self):
  r=m.audit([self.wall,obj('Touch',[1,0,0],[2,1,1])]);self.assertEqual(len(r['contacts']),1);self.assertFalse(r['candidates'])
 def test_separation(self):
  r=m.audit([self.wall,obj('Far',[2,0,0],[3,1,1])]);self.assertEqual(r['separated_pairs'],1)
 def test_stale_exception_rejected(self):
  with self.assertRaises(ValueError):m.audit([self.wall],[{'objects':['Wall','Missing'],'reason':'invalid'}])
 def test_blanket_missing_reason_rejected(self):
  with self.assertRaises(ValueError):m.audit([self.wall,obj('B',[0,0,0],[1,1,1])],[{'objects':['Wall','B'],'reason':''}])
 def test_invalid_tolerance(self):
  with self.assertRaises(ValueError):m.classify_bounds([[0,0,0],[1,1,1]],[[0,0,0],[1,1,1]],float('nan'))
if __name__=='__main__':unittest.main()

import sys
# usage: python3 count_calls.py path/to/dsh_run.jsonl
import json,collections,re
c=collections.Counter();sub=collections.Counter();bb=[];skills=[];seq=[]
for l in open(sys.argv[1] if len(sys.argv)>1 else 'dsh_run.jsonl'):
  try:e=json.loads(l)
  except:continue
  if e.get('type')!='tool_call':continue
  t=e['tool'];i=e.get('input') or {};c[t]+=1;seq.append(t)
  if t=='skill':skills.append(i.get('name'))
  if t.startswith('blender_rt') or t.startswith('blender_'):
    sub[t+':'+str(i.get('op') or i.get('action') or i.get('command') or '')[:20]]+=1
  if t=='bash':
    cmd=json.dumps(i,ensure_ascii=False)
    if re.search(r'blender\b[^"]*\s-b\b|blender\s+--background',cmd):bb.append(cmd[:160])
print('total',sum(c.values()));print(dict(c.most_common()));print(dict(sub.most_common(20)))
print('skills',skills);print('bash blender -b',len(bb));[print(' ',x) for x in bb[:10]]
print('first6',seq[:6])

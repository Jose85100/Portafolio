import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'notebooks/pilot_evsi.ipynb'; nb=json.loads(p.read_text())
for i,c in enumerate(nb['cells'],1):
 if c['cell_type']=='code':
  r=subprocess.run([sys.executable,'-c',''.join(c['source'])],cwd=root,text=True,capture_output=True)
  c['execution_count']=i;c['outputs']=[{'output_type':'stream','name':'stdout','text':r.stdout+r.stderr}]
  if r.returncode: raise SystemExit(r.stderr)
p.write_text(json.dumps(nb,indent=1)+'\n');print('executed',sum(c['cell_type']=='code' for c in nb['cells']),'cells')

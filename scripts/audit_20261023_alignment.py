"""Bounded weekly inventory: Git snapshots plus actual notebook structure, not quality scores."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reviews/2026-10-23-alignment'
REFS=['origin/main','origin/research/2026-10-23-multi-domain-cycle','origin/research/2026-10-23-christoffersen-sequential']
START='2026-10-17T00:00:00-05:00';END='2026-10-24T00:00:00-05:00'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def run():
 OUT.mkdir(parents=True,exist_ok=True)
 commits=[]
 raw=git('log',*REFS,'--since='+START,'--until='+END,'--format=%H%x09%cI%x09%s')
 for line in raw.splitlines():
    sha,date,title=line.split('\t',2)
    commits.append({'sha':sha,'committer_time':date,'title':title})
 (OUT/'commits.json').write_text(json.dumps({'start_inclusive':START,'end_exclusive':END,'refs':{r:git('rev-parse',r) for r in REFS},'commits':commits},indent=2)+'\n')
 before=git('rev-list','-1','--before='+START,'origin/main')
 weekly=set(git('diff','--name-only',before,'HEAD').splitlines())
 for ref in REFS[1:]:weekly.update(git('diff','--name-only','origin/main...'+ref).splitlines())
 weekly.update(git('ls-files','--others','--exclude-standard').splitlines())
 stats=[]
 for p in sorted(ROOT.rglob('*.ipynb')):
    if '.venv' in p.parts:continue
    relative=str(p.relative_to(ROOT));nb=nbf.read(p,as_version=4);nbf.validate(nb)
    cells=[x for x in nb.cells if x.cell_type=='code']
    stats.append({'path':relative,'weekly_changed':relative in weekly,'cells':len(nb.cells),'code_cells':len(cells),
      'code_lines':sum(len(x.source.splitlines()) for x in cells),
      'executed_code_cells':sum(x.execution_count is not None for x in cells),
      'saved_error_outputs':sum(o.output_type=='error' for c in cells for o in c.outputs),
      'figures':sum('image/png' in o.get('data',{}) for c in cells for o in c.outputs),
      'display_equation_delimiters':sum(x.source.count('$$') for x in nb.cells if x.cell_type=='markdown'),
      'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 with (OUT/'notebooks.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(stats[0]),lineterminator="\n");w.writeheader();w.writerows(stats)
 # Links in changed Markdown are checked without treating diagrams/code as targets.
 broken=[];checked=0
 for relative in sorted(weekly):
    p=ROOT/relative
    if p.suffix!='.md' or not p.is_file():continue
    for target in re.findall(r'\]\(([^)\s]+)(?:\s+[^)]*)?\)',re.sub(r'\$\$.*?\$\$', '', p.read_text(), flags=re.S)):
        if re.match(r'(https?://|mailto:|#)',target):continue
        if target=='1+r':continue # formula, not a Markdown link
        local=target.split('#')[0]
        if not local:continue
        checked+=1
        if not (p.parent/local).exists():broken.append({'file':relative,'target':target})
 result={'window':'2026-10-17 through 2026-10-23 America/Bogota','base_before_week':before,
  'notebooks_total':len(stats),'notebooks_changed_week':sum(x['weekly_changed'] for x in stats),
  'saved_notebooks_with_errors':[x['path'] for x in stats if x['saved_error_outputs']],
  'weekly_brief_notebooks':[x['path'] for x in stats if x['weekly_changed'] and x['code_cells']<8],
  'changed_markdown_links_checked':checked,'broken_local_links':broken,
  'interpretation':'Schema and saved-output inspection only for inventory; execution.json identifies new executions. PR69 snapshot inspected separately; no claim of full weekly regression.'}
 (OUT/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':run()

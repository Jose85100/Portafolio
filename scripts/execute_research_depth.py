"""Run each research notebook in a fresh process, retaining real rich outputs."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from deepen_20261023_notebooks import TARGETS


def execute_one(path,mode,qa):
    path=Path(path).resolve();os.chdir(path.parent);sys.path.insert(0,str(path.parent))
    nb=nbf.read(path,as_version=4)
    if mode=='kernel':
        from nbclient import NotebookClient
        NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(path.parent)}}).execute()
    else:
        from IPython.terminal.interactiveshell import TerminalInteractiveShell
        from IPython.utils.capture import capture_output
        shell=TerminalInteractiveShell.instance()
        shell.display_formatter.active_types=['text/plain','text/html','image/png','application/json']
        # The subprocess contains only this notebook's imports and state.
        shell.run_line_magic('matplotlib','inline')
        for cell in nb.cells:
            if cell.cell_type!='code':continue
            cell.outputs=[]
            with capture_output() as captured:
                result=shell.run_cell(cell.source,store_history=True)
            if result.error_before_exec or result.error_in_exec:
                sys.stderr.write(captured.stdout+captured.stderr)
                raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
            cell.execution_count=shell.execution_count-1
            if captured.stdout:cell.outputs.append(nbf.v4.new_output('stream',name='stdout',text=captured.stdout))
            if captured.stderr:cell.outputs.append(nbf.v4.new_output('stream',name='stderr',text=captured.stderr))
            for output in captured.outputs:
                cell.outputs.append(nbf.v4.new_output('display_data',data=output.data,metadata=output.metadata))
    academic_metrics={}
    for cell in nb.cells:
        for output in cell.get('outputs',[]):
            if output.get('output_type')=='stream' and output.get('name')=='stdout':
                for line in output.text.splitlines():
                    if line.startswith('ACADEMIC_METRICS:'):
                        academic_metrics.update(json.loads(line.split(':',1)[1]))
    if path in TARGETS:
        index=TARGETS.index(path)
        summaries=[
            'Se contrastaron AR y Wald, inversión en un grid y un escenario heterocedástico. Las tablas distinguen relevancia, exclusión y aproximaciones asintóticas.',
            'Se verificaron Chen, shuffle, reversión, escala y aliasing; la firma truncada no identifica toda trayectoria.',
            'Se midieron falsas alertas por canal, deriva, contaminación y repetición de calibración. Los p-valores de anomalía no son probabilidades de fraude.',
            'Se separaron cobertura total, intervalos finitos y cobertura útil; eliminar la masa de test cambia el método.',
            'Se reconstruyeron EVSI y EVPI y se estudió prior, costo y demora. El diseño elegido se restringe al grid sintético.',
            'La temperatura ajustada fue 2,376 frente a 2,4 del generador. La diferencia de costo económico menos umbral fijo fue −5,132 unidades por caso; IC bootstrap percentil 95% [−5,686; −4,671], condicionado a eficacia asumida.',
            'Sumar transferencias al salario sobreestimó el ingreso en 2.450.000 COP por caso en promedio en este corpus. Los cinco casos de mutación literal retuvieron solo el original; un span semánticamente mal etiquetado sí pasó.'
        ]
        nb.cells=[c for c in nb.cells if not c.metadata.get('depth_summary')]
        if academic_metrics:
            summaries[index]+='\n\nResultados académicos adicionales (valores del experimento):\n\n```json\n'+json.dumps(academic_metrics,ensure_ascii=False,indent=2)+'\n```'
        summary=nbf.v4.new_markdown_cell('## Lectura de los resultados ejecutados\n\n'+summaries[index]+'\n\nDatos sintéticos. Esta sección acompaña las salidas guardadas y no es una medición comercial o bancaria.')
        summary.metadata['depth_summary']=True
        summary.id=hashlib.sha256((str(path.relative_to(ROOT))+'summary').encode()).hexdigest()[:12]
        nb.cells.insert(1,summary)
    nb.metadata['execution_mode']=mode
    nbf.validate(nb);nbf.write(nb,path)
    image_count=0
    if qa:
        from nbconvert import HTMLExporter
        html,_=HTMLExporter().from_notebook_node(nb)
        qa=Path(qa);qa.mkdir(parents=True,exist_ok=True)
        stem=path.parent.name
        (qa/(stem+'.html')).write_text(html)
        for cell in nb.cells:
            for out in cell.get('outputs',[]):
                if 'image/png' in out.get('data',{}):
                    image_count+=1
                    (qa/f'{stem}-{image_count}.png').write_bytes(base64.b64decode(out.data['image/png']))
    return {'path':str(path.relative_to(ROOT)),'cells':len(nb.cells),
            'code_cells':sum(c.cell_type=='code' for c in nb.cells),
            'code_lines':sum(len(c.source.splitlines()) for c in nb.cells if c.cell_type=='code'),
            'figures':sum('image/png' in o.get('data',{}) for c in nb.cells for o in c.get('outputs',[])),
            'mode':mode,'academic_metrics':academic_metrics,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['kernel','ipython'],default='kernel')
    parser.add_argument('--one');parser.add_argument('--qa-dir');parser.add_argument('--result')
    parser.add_argument('--evidence',default='reviews/2026-10-23-academic/execution.json')
    args=parser.parse_args()
    if args.one:
        row=execute_one(args.one,args.mode,args.qa_dir)
        if args.result:Path(args.result).write_text(json.dumps(row,indent=2))
        print(json.dumps(row));sys.exit(0)
    results=[]
    for path in TARGETS:
        with tempfile.TemporaryDirectory() as td:
            result=Path(td)/'result.json'
            command=[sys.executable,__file__,'--one',str(path),'--mode',args.mode,'--result',str(result)]
            if args.qa_dir:command+=['--qa-dir',str(Path(args.qa_dir).resolve())]
            subprocess.run(command,check=True,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},timeout=240)
            results.append(json.loads(result.read_text()))
    dest=ROOT/args.evidence;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({'notebooks':results,'scope':'actual cell execution; synthetic data'},indent=2)+'\n')

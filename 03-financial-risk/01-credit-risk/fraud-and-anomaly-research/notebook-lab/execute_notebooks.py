"""Reproduce notebooks with nbclient or socketless IPython in isolated processes.

Default is a standard Jupyter kernel. --execution-mode ipython is for hosts that
forbid local sockets; all code cells still execute in order with rich MIME outputs.
"""
from pathlib import Path
import argparse,base64,hashlib,json,time,subprocess,sys,os,platform
import nbformat
from nbconvert import HTMLExporter
BASE=Path(__file__).resolve().parents[1]


def execute_one(path,mode):
    path=Path(path).resolve();os.chdir(path.parent)
    nb=nbformat.read(path,as_version=4)
    if mode=='nbclient':
        from nbclient import NotebookClient
        nb=NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(path.parent)}}).execute()
    else:
        from IPython.terminal.interactiveshell import TerminalInteractiveShell
        from IPython.utils.capture import capture_output
        shell=TerminalInteractiveShell.instance()
        shell.display_formatter.active_types=['text/plain','text/html','image/png','application/json']
        for index,cell in enumerate(nb.cells):
            if cell.cell_type!='code':continue
            with capture_output() as captured:
                result=shell.run_cell(cell.source,store_history=True)
            if result.error_before_exec or result.error_in_exec:
                raise RuntimeError(f'{path.name}, cell {index}: {captured.stdout}\n{captured.stderr}') from (result.error_before_exec or result.error_in_exec)
            outputs=[]
            if captured.stdout:outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
            if captured.stderr:outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
            for rich in captured.outputs:
                outputs.append(nbformat.v4.new_output('display_data',data=rich.data,metadata=rich.metadata))
            cell.execution_count=shell.execution_count-1;cell.outputs=outputs
    metrics=None
    for cell in nb.cells:
        for output in cell.get('outputs',[]):
            if output.output_type=='error':raise RuntimeError('Saved execution error')
            if output.output_type=='stream':
                for line in output.get('text','').splitlines():
                    if line.startswith('LAB_METRICS:'):metrics=json.loads(line.split(':',1)[1])
    if not metrics:raise RuntimeError('Missing computed summary')
    nb.cells[1].source='## Resumen de la ejecución\n\nDatos sintéticos; resultados de esta ejecución:\n\n'+'\n'.join(f'- **{key}:** {value}' for key,value in metrics.items())+'\n\nLos supuestos, límites y contraejemplos se explican junto a cada experimento.'
    nb.metadata['execution_method']=mode+' in dedicated process'
    nb.metadata['language_info']['version']=platform.python_version()
    nbformat.validate(nb);nbformat.write(nb,path)


def execute(pattern='*.ipynb',qa_dir=None,mode='nbclient'):
    results=[];paths=sorted(BASE.glob('*/notebooks/'+pattern))
    if not paths:raise RuntimeError('No notebooks found')
    for path in paths:
        started=time.monotonic()
        subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(path),'--execution-mode',mode],check=True,cwd=path.parent,timeout=240)
        nb=nbformat.read(path,as_version=4);metrics=None;figures=[]
        for cell in nb.cells:
            for output in cell.get('outputs',[]):
                if output.output_type=='stream':
                    for line in output.get('text','').splitlines():
                        if line.startswith('LAB_METRICS:'):metrics=json.loads(line.split(':',1)[1])
                if 'image/png' in output.get('data',{}):figures.append(output['data']['image/png'])
        if not metrics or len(figures)<2:raise RuntimeError('Missing metrics or figures: '+str(path))
        if qa_dir:
            folder=Path(qa_dir)/path.parent.parent.name/path.stem;folder.mkdir(parents=True,exist_ok=True)
            exporter=HTMLExporter();exporter.exclude_input_prompt=True;exporter.exclude_output_prompt=True
            html,_=exporter.from_notebook_node(nb);(folder/'preview.html').write_text(html)
            for i,png in enumerate(figures):(folder/f'figure-{i+1}.png').write_bytes(base64.b64decode(png))
        result=dict(path=str(path.relative_to(BASE)),cells=len(nb.cells),code_cells=sum(c.cell_type=='code' for c in nb.cells),figures=len(figures),execution_mode=mode,seconds=round(time.monotonic()-started,3),metrics=metrics,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
    (BASE/'notebook-lab'/'execution_evidence.json').write_text(json.dumps({'date':'2026-10-21','scope':'synthetic experiments, independent processes','notebooks':results},indent=2,ensure_ascii=False)+'\n')
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pattern',default='*.ipynb');parser.add_argument('--qa-dir');parser.add_argument('--execution-mode',choices=['nbclient','ipython'],default='nbclient');parser.add_argument('--worker')
    args=parser.parse_args()
    if args.worker:execute_one(args.worker,args.execution_mode)
    else:execute(args.pattern,args.qa_dir,args.execution_mode)

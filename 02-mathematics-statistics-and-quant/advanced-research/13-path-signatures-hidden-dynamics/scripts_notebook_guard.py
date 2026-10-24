"""Execute a fresh IPython namespace and save the guard experiment notebook."""
from pathlib import Path

import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
nb.metadata.execution = {'executor': 'IPython in-process', 'limitation': 'Sandbox blocks Jupyter kernel sockets; cells really run in a fresh shell namespace and errors abort'}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(r'''# Guardia condicional contra aliasing de área
## Resumen
Dos aproximaciones iguales no prueban convergencia: cuatro de ocho casos deterministas se estancan falsamente en área cero. Una cota de velocidad externa permite certificar correctamente ocho signos; no elimina toda incertidumbre de área.
## Contexto y método
Para una curva planar $L$-Lipschitz en tiempos conocidos y muestras $x_i$, sea $A_P$ el área del polígono, cerrado por la cuerda final. En cada arco, trasladar origen a $x_i$ anula la contribución de su cuerda y acota el error por $\frac12(L\Delta t_i)^2$. Así:
$$|A-A_P|\leq B=\frac{L^2}{2}\sum_i(\Delta t_i)^2.$$
Signo positivo si $A_P>B$, negativo si $A_P<-B$; de lo contrario abstención y refinamiento.
### Supuestos clave
$L$ es una cota **conocida externa**, no el máximo de pendientes observadas. Comprobar secantes es necesario pero no suficiente. Cota analítica en aritmética exacta; floats no usan redondeo dirigido, por lo que no se afirma certificación formal intervalar de máquina.
## Datos
Círculos sintéticos con 1,2,4,8 vueltas y dos orientaciones. Analítica $A=\pm\pi k$, $L=2\pi k$. Semilla 20261024; 200 grillas irregulares; sin datos operativos.'''),
    code("import csv, json\nfrom pathlib import Path\nfrom IPython.display import display, Image\nconfig=json.loads(Path('config_guard.json').read_text())\nsummary=json.loads(Path('results/guard_summary.json').read_text())\nconfig"),
    md('## Resultados\nLa comparación usa tres reglas distintas: presupuesto fijo, meseta y cota. No se comparan como si ofrecieran la misma garantía. Certificar signo puede dejar error de área considerable.'),
    code("summary"),
    code("display(Image(filename='results/guard_audit.png'))"),
    md('### Resultados crudos y recursos\nEl CSV guarda tiempo y pico Python tracemalloc por ejecución. Segmentos finales no equivalen al total de evaluaciones: el prototipo reevalúa todos los nodos tras duplicar.'),
    code("rows=list(csv.DictReader(Path('results/guard_comparison.csv').open()))\n[{k:r[k] for k in ['turns','orientation','method','segments','area_error','seconds','peak_python_bytes']} for r in rows if r['orientation']=='1']"),
    md('## Pruebas y caso negativo\nUn L falso puede pasar la prueba de secantes y producir signo erróneo. Esto refuta la idea de aprender una garantía global de muestras finitas sin supuestos.'),
    code("from src.aliasing_guard import certify_area\nfrom src.benchmark_guard import curve\nimport numpy as np\nt=np.linspace(0,1,9)\nfalse=certify_area(curve(t,7,1),t,6.2)\nassert false.sign==-1\nassert summary['irregular_enclosed']==config['irregular_trials']\nassert summary['methods']['certified']['abstentions']==0\nassert summary['methods']['certified']['wrong_signs']==0\nprint('Supuesto falso:',false)\nprint('Área real:',7*np.pi)"),
    md('## Conclusiones\nEl guardia corrige la política de parada en estos casos y evita confundir estabilidad entre mallas con resolución. Con presupuesto ocho se abstiene seis veces; bajo L falso puede fallar. Madurez S2, sin promoción a validación externa. Referencias primarias verificadas en fuentes_guard.md; informe_guard.md contiene derivación y 14 puntos.')
]
InteractiveShell.clear_instance()
shell=InteractiveShell.instance()
count=0
for cell in nb.cells:
    if cell.cell_type!='code':
        continue
    count+=1
    with capture_output() as captured:
        result=shell.run_cell(cell.source,store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
    cell.execution_count=count
    cell.outputs=[]
    for name,value in [('stdout',captured.stdout),('stderr',captured.stderr)]:
        if value:
            cell.outputs.append(nbf.v4.new_output('stream',name=name,text=value))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output('display_data',data=output.data,metadata=output.metadata))
nbf.validate(nb)
nbf.write(nb,root/'notebook_guard.ipynb')

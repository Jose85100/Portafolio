"""Build and execute a portable, narrative experiment notebook."""
from pathlib import Path
import os
import nbformat as nbf
from nbclient import NotebookClient
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output


def main():
    root = Path(__file__).resolve().parents[1]
    nb = nbf.v4.new_notebook()
    nb.metadata.kernelspec = {'display_name': 'Innovation EVSI', 'language': 'python', 'name': 'python3'}
    nb.cells = [
        nbf.v4.new_markdown_cell('# Cuándo comprar evidencia antes de escalar IA\n\n## Resumen\nCaso sintético: el mejor candidato es un piloto de 50 observaciones con valor esperado neto 5.140,42 unidades frente a 0 al decidir hoy. El piloto fijo de 100 obtiene 5.138,22: la diferencia de diseño es pequeña, no una ventaja comercial demostrada.'),
        nbf.v4.new_markdown_cell('## Contexto y método\nSea $p\\sim Beta(a,b)$ la probabilidad desconocida de éxito operativo de una tarea. No es uplift causal. La utilidad de escalar es $U(p)=N(vp-c)-F$ y detener vale cero. Un piloto IID $K\\mid p\\sim Bin(n,p)$ actualiza a $Beta(a+K,b+n-K)$.\n\n$EVSI(n)=\\sum_k P(K=k)\\max(0,U(E[p\\mid k]))-\\max(0,U(E[p]))$. El valor neto resta el costo fijo y variable del piloto. Se enumera un conjunto finito, no se afirma óptimo global.\n\n### Supuestos clave\nUna etapa, neutralidad al riesgo, población futura fija separada del piloto, costos y valor por éxito conocidos; no descuento, drift, externalidades ni efectos de red. El piloto no genera beneficios contabilizados. La decisión usa solo su resultado, nunca el p latente.'),
        nbf.v4.new_code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\nfrom IPython.display import display, Image\nfrom src.evsi import Case, choose, evaluate\ncfg=json.loads(Path('config.json').read_text())\nsummary=json.loads(Path('results/summary.json').read_text())\ndisplay(cfg)"),
        nbf.v4.new_markdown_cell('## Resultados: baseline y tamaño de piloto\nTodos los valores son expectativas bajo el prior sintético; no ingresos observados.'),
        nbf.v4.new_code_cell("designs=pd.read_csv('results/designs.csv')\ndisplay(designs.round(3))\ndisplay(Image(filename='results/decision_curve.png'))"),
        nbf.v4.new_markdown_cell('## Validación independiente por simulación\n200.000 réplicas generan p y luego K, aplican la política a K y evalúan utilidad al p verdadero. El error estándar mide ruido MC bajo el modelo, no incertidumbre de negocio.'),
        nbf.v4.new_code_cell("display({k:summary[k] for k in ['selected','evpi','mc_mean','mc_standard_error']})\nassert abs(summary['mc_mean']-summary['selected']['net_value']) < 5*summary['mc_standard_error']\nassert 0<=summary['selected']['evsi']<=summary['evpi']\nassert summary['selected']['increment']>=cfg['hypothesis_min_increment']"),
        nbf.v4.new_markdown_cell('## Sensibilidad y decisiones\nExperimentar si el mejor valor neto supera decidir hoy. Escalar si la mejor opción sin estudio tiene utilidad positiva; detener en otro caso. Ajustar/rediseñar: variar costos, prior, horizonte y métricas si el piloto no es transferible. Esta herramienta no identifica efectos causales.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/sensitivity.csv').round(3))"),
        nbf.v4.new_markdown_cell('## Conclusiones y límites\nLa información gratuita no empeora valor esperado; información costosa puede destruirlo. El n=100 casi empata n=50; no sobredimensionar esa diferencia. No se valida un producto IA real. La innovación es integrar un gate exacto auditable en un programa ejecutivo S1, no inventar EVSI. Referencias, fallos y rúbrica están en informe.md y referencias.bib.')
    ]
    nbf.validate(nb)
    if os.environ.get('NOTEBOOK_KERNEL') == '1':
        NotebookClient(nb, timeout=120, kernel_name='python3', resources={'metadata': {'path': str(root)}}).execute()
        nb.metadata['execution_mode'] = 'nbclient-jupyter-kernel'
    else:
        # All cells genuinely execute in one fresh namespace. This mode avoids
        # ZeroMQ sockets prohibited in the managed runner; it is not kernel QA.
        shell = InteractiveShell.instance()
        shell.reset(new_session=True)
        previous = Path.cwd()
        os.chdir(root)
        count = 0
        try:
            for cell in nb.cells:
                if cell.cell_type != 'code':
                    continue
                count += 1
                with capture_output() as captured:
                    result = shell.run_cell(cell.source, store_history=False)
                if result.error_before_exec or result.error_in_exec:
                    raise RuntimeError(f'Notebook cell {count} failed') from (result.error_before_exec or result.error_in_exec)
                outputs = []
                if captured.stdout:
                    outputs.append(nbf.v4.new_output('stream', name='stdout', text=captured.stdout))
                if captured.stderr:
                    outputs.append(nbf.v4.new_output('stream', name='stderr', text=captured.stderr))
                for output in captured.outputs:
                    outputs.append(nbf.v4.new_output('display_data', data=output.data, metadata=output.metadata))
                cell.outputs = outputs
                cell.execution_count = count
        finally:
            os.chdir(previous)
        nb.metadata['execution_mode'] = 'IPython in-process sequential capture; no Jupyter socket kernel'
    nbf.write(nb, root / 'notebook.ipynb')
    print('Executed notebook.ipynb top-to-bottom')


if __name__ == '__main__':
    main()

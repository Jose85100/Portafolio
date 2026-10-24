"""Execute an additional robust decision notebook in a fresh IPython namespace."""
import os
from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output


def main():
    root = Path(__file__).resolve().parents[1]
    nb = nbf.v4.new_notebook()
    nb.metadata.kernelspec = {'display_name': 'Python3', 'language': 'python', 'name': 'python3'}
    nb.metadata.execution_mode = 'IPython in-process real sequential capture; not kernel validation'
    nb.cells = [
        nbf.v4.new_markdown_cell('# Innovación: prior incierto y costo de esperar\n\n## Resumen\nEn el caso sintético, una regla común conservadora mejora el peor valor de 86,72 a120,45 unidades sin demora. Con descuento diario0,2, el baseline nominal pierde363,95 bajo el prior pesimista; el gate robusto elige no estudiar y obtiene0. No se afirma dominancia universal.'),
        nbf.v4.new_markdown_cell('## Contexto y método\nUna política terminal se fija **antes** de observar el prior verdadero. Para cada K, escala solo si todos los priors del conjunto dan utilidad posterior positiva. Cada prior evalúa esa misma regla: no se escoge una política oráculo por escenario. El estudio de n observaciones demora n/q días, y el payoff futuro se multiplica por exp(-r n/q); el costo del piloto se paga hoy.\n\nSe maximiza el peor valor sobre un conjunto finito de priors, tamaños y una familia restringida de reglas. No es una solución minimax sobre todas las políticas. No hay actualización de pesos de modelos ni robustez frente a distribuciones fuera del conjunto.'),
        nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\ncfg=json.loads(Path('robust-config.json').read_text())\ndisplay(cfg)"),
        nbf.v4.new_markdown_cell('## Resultados\nUnidad monetaria sintética común. Priors6/4,4/6,8/2; misma población futura10000, beneficio10 y costo6. Tasa de descuento de escenario; no estimación financiera real.'),
        nbf.v4.new_code_cell("table=pd.read_csv('results/robust-designs.csv')\ndisplay(table.round(3))\ndisplay(Image(filename='results/robust-decision.png'))"),
        nbf.v4.new_markdown_cell('## Validación y ablation\nPrior único y demora cero recupera el motor23. MC genera p y K; la acción depende solo de K y priors fijados. El p latente solo evalúa payoff. La opción n0 evita pagar evidencia inútil bajo las condiciones de este caso, pues todos pueden detener sin costo.'),
        nbf.v4.new_code_cell("summary=json.loads(Path('results/robust-summary.json').read_text())\ndisplay(summary)\nfor check in summary['mc_checks']:\n    assert abs(check['mc_mean']-check['exact']) < 5*check['mc_se']\nassert table.loc[table.policy.eq('robust'),'worst_value'].min()>=-1e-8"),
        nbf.v4.new_markdown_cell('## Decisión y límites\nContinuar con piloto cuando crea valor bajo el conjunto; detener si demora/costo elimina valor. Ajustar si prior no es defendible, metricas no son causales, ritmo del piloto cambia o hay costos omitidos. Robustez sacrifica valor nominal: con r0 baja5140,42 a4909,62. No prueba eficacia IA. Ver informe-2026-10-24.md y referencias.bib.')
    ]
    shell = InteractiveShell.instance()
    shell.reset(new_session=True)
    previous = Path.cwd()
    os.chdir(root)
    try:
        count = 0
        for cell in nb.cells:
            if cell.cell_type != 'code':
                continue
            count += 1
            with capture_output() as output:
                result = shell.run_cell(cell.source, store_history=False)
            if result.error_before_exec or result.error_in_exec:
                raise RuntimeError('notebook execution failed')
            cell.execution_count = count
            cell.outputs = []
            for name in ('stdout', 'stderr'):
                text = getattr(output, name)
                if text:
                    cell.outputs.append(nbf.v4.new_output('stream', name=name, text=text))
            for rich in output.outputs:
                cell.outputs.append(nbf.v4.new_output('display_data', data=rich.data, metadata=rich.metadata))
    finally:
        os.chdir(previous)
    nbf.validate(nb)
    nbf.write(nb, root/'robust-notebook.ipynb')
    assert any('image/png' in o.get('data', {}) for c in nb.cells if c.cell_type == 'code' for o in c.outputs)
    print('Executed robust-notebook.ipynb with rich outputs')


if __name__ == '__main__':
    main()

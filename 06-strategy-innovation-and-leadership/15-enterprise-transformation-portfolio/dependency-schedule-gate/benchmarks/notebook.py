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
        nbf.v4.new_markdown_cell('# Transformación: financiar no equivale a poder ejecutar\n\n## Resumen\nEl caso sintético inicial refuta una mejora mínima0,5: exacto ygreedy factible empatanNPV11,655966. Relajar precedencias produce18,628099pero un calendario inválido. La contribución es una certificación exacta pequeña de factibilidad temporal, no superioridad universal.'),
        nbf.v4.new_markdown_cell('## Modelo ysupuestos\nCada proyecto opcional empieza en un período entero, paga costo al inicio ycobra un beneficio único al terminar. Dependencias deben **terminar** antes del inicio, no basta seleccionarlas. Se respetan presupuesto de caja por período ycapacidad de personas durante toda duración. Budgets expiran: no acumulación, ni financiación con beneficios.\n\nObjetivoΣ[b_j/(1+r)^(inicio+duración)−c_j/(1+r)^inicio]. Todos datos sintéticos, duraciones deterministas yproyectos no preemptivos. Se enumera también rechazar cada proyecto. No mide riesgo empresarial.'),
        nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\ncfg=json.loads(Path('config.json').read_text())\nsummary=json.loads(Path('results/summary.json').read_text())\ndisplay(cfg)"),
        nbf.v4.new_markdown_cell('## Resultados: baseline factible ehipótesis refutada\nGreedy ordena por margen/costo, respeta dependencias temporales yomite actividades negativas que no habilitan otras. No se compara exacto con un greedy que malgaste deliberadamente presupuesto.'),
        nbf.v4.new_code_cell("display(summary)\ndisplay(pd.read_csv('results/schedules.csv'))\ndisplay(Image(filename='results/schedule.png'))"),
        nbf.v4.new_markdown_cell('## Sensibilidad yfallos\nAumentar beneficio de analytics puede cambiar elorden óptimo. La ganancia depende del caso; no extrapolar. La pruebaMILP independiente contrasta elvalor óptimo en una instancia distinta. El límite2millones de candidatos impide presentar una búsqueda exponencial como motor escalable.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/enabling-value.csv').round(5))\ndisplay(pd.read_csv('results/sensitivity.csv').round(5))\nassert summary['exact']['npv']>=summary['baseline']['npv']-1e-10\nassert summary['increment']==0\nassert not summary['relaxed_schedule_feasible_original']"),
        nbf.v4.new_markdown_cell('## Decisión ylímites\nContinuar con standalone0, platform1 yanalytics/automation3 bajo estos presupuestos. No ejecutar controls, cuyo valor neto es negativo. Ajustar si cambian duraciones, cobros, disponibilidad odependencias; detener si ningún portafolio tieneNPVpositivo. No optimiza contratar personal, incertidumbre, regulación nivalor causal. Ver informe.md yreferencias.bib.')
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
    nbf.write(nb, root/'notebook.ipynb')
    assert any('image/png' in o.get('data', {}) for c in nb.cells if c.cell_type == 'code' for o in c.outputs)
    print('Executed notebook.ipynb with rich outputs')


if __name__ == '__main__':
    main()

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
        nbf.v4.new_markdown_cell('# Pricing: capacidad y presupuesto de pérdida\n\n## Resumen\nCaso sintético con precio único por período. La decisión sujeta a CVaR90%shortfall≤500 elige precio18; la política neutral elige22. El gate sacrifica beneficio esperado para respetar el presupuesto. No estima elasticidades ni demuestra rentabilidad real.'),
        nbf.v4.new_markdown_cell('## Método y supuestos\nDemanda fluida por escenario: D_s(p)=m_s sigmoid(5−0,25p). Se sirve min(capacidad,D); beneficio=(p−c)servido−F. Capacidad300, costo variable4 y fijo evitable1000. Detener no incurre costos. Precio único exante aplicado a todos escenarios; sin personalización ni discriminación.\n\nRiesgo=CVaR90% de shortfall max(−beneficio,0). La cola promedia exactamente10%de masa, partiendo átomos cuando corresponde. No se usa media de pérdidas≥VaR, que falla con átomos. Se enumera menú finito; no óptimo continuo ni pricing dinámico.'),
        nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\ncfg=json.loads(Path('config.json').read_text())\nsummary=json.loads(Path('results/summary.json').read_text())\ndisplay(cfg)"),
        nbf.v4.new_markdown_cell('## Resultados y baselines\nTodos son escenarios sintéticos conocidos antes de decidir. Benchmark plug-in usa demanda media y luego se evalúa con los mismos escenarios. Neutral maximiza beneficio esperado con capacidad sin presupuesto de cola.'),
        nbf.v4.new_code_cell("display(summary)\ndisplay(pd.read_csv('results/prices.csv').round(3))\ndisplay(Image(filename='results/pricing-frontier.png'))"),
        nbf.v4.new_markdown_cell('## Validación y sensibilidad\nTests contrastan CVaR con LP independiente, incluyen fracción de átomo, traslación/homogeneidad y presupuesto anidado. MC200000 evalúa media bajo los tres escenarios, no incertidumbre real. Un presupuesto estricto puede recomendar detener. El menú fino1601 elige19,26 yvalor2342,66: el18solo es óptimo del menúconfigurado, no continuo.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/sensitivity.csv').round(3))\ndisplay(pd.read_csv('results/scaling.csv').round(4))\nassert summary['constrained']['cvar_shortfall']<=cfg['budget']\nassert summary['constrained']['expected_profit']<=summary['risk_neutral']['expected_profit']\nassert abs(summary['mc_mean']-summary['constrained']['expected_profit'])<5*summary['mc_se']"),
        nbf.v4.new_markdown_cell('## Decisión y límites\nContinuar piloto controlado a precio propuesto solo si costos, capacidad y demanda son defendibles; ajustar al cambiar elasticidad/mezcla/costo; detener si el menú no crea valor dentro presupuesto. Demanda fluida fraccional no son ventas observadas; omite aleatoriedad individual, competencia, causalidad, dinámica y costos hundidos. Referencias y análisis crítico en informe.md.')
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

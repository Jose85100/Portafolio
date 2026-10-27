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
        nbf.v4.new_markdown_cell('# CFO: activar fondeo antes de que llegue tarde\n\n## Resumen\nCon demora2períodos, el umbralreactivo2 tiene brecha de caja en50% de masa de los escenarios; el umbralseleccionado6reduce esa masa a0, pagando costo0,74 en vez de0,132. Son escenarios sintéticos, no probabilidad real calibrada ni garantía de supervivencia.'),
        nbf.v4.new_markdown_cell('## Modelo e información disponible\nUna línea comprometida permite un giro único8, con comisión de solicitud0,5 einterés2%por período sobre principal desembolsado. El principal entra encaja ypasivo simultáneamente: no es ingreso niganancia. Sin amortización dentro del horizonte, caja−deuda= caja inicial+flujosoperativos−costos.\n\nOrden por período: llega fondeo pendiente; se observa caja yse decide solicitud; se paga comisión (yfondea inmediatamente si lead0); se monitorea piso; se liquida flujo neto einterés al cierre yse monitorea de nuevo. La solicitud usa caja observada, contrato yhorizonte, **no el flujo futuro del período**. Se permite solicitar solo si el giro llega dentro del horizonte.'),
        nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\ncfg=json.loads(Path('config.json').read_text())\nsummary=json.loads(Path('results/summary.json').read_text())\ndisplay(cfg)"),
        nbf.v4.new_markdown_cell('## Comparación de políticas\nEl menú incluye no solicitar. Se minimiza costo esperado sujeto a brecha≤10% de masa de escenarios. La política threshold6 queda fijada exante yse aplica igual atodos caminos.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/thresholds.csv').round(4))\ndisplay(Image(filename='results/funding.png'))\ndisplay(pd.read_csv('results/trajectories.csv').round(4))"),
        nbf.v4.new_markdown_cell('## Fallos, sensibilidad y reconciliación\nFuera del diseño, un burn−4por período produce incumplimiento incluso con el umbral elegido. Una demora mayor puede volver vacío elmenú factible. No se reemplaza falta de factibilidad con un resultado seguro inventado. El simulador sigue aritméticamente después de brecha solo para diagnóstico, no como continuación empresarial viable.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/lead-sensitivity.csv'))\ndisplay(summary['out_of_design_stress'])\nassert summary['selected']['breach_probability']<=cfg['max_breach']\nassert all(r['reconciliation_error']<1e-10 for r in summary['selected']['outcomes'])"),
        nbf.v4.new_markdown_cell('## Decisión y límites\nContinuar con solicitud al observar caja≤6solo bajo contrato/escenariosdefendibles; ajustar buffer omonto si aumenta la demora; rediseñar liquidez si ningún umbral es factible. No incluye revocación de líneas, covenants, vencimiento, costo de compromiso, amortización, financiación estatal nivalidación regulatoria. ComponenteS2 sintético; no una recomendación financiera real.')
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

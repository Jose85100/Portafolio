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
        nbf.v4.new_markdown_cell('# Consejo: ¿qué acción incentiva realmente el bono?\n\n## Resumen\nEn dos acciones sintéticas, bono inmediato por volumen induce volume_chasing y beneficio neto esperado−22,5. Diferir90% de forma contingente al resultado induce prudent: utilidad8,55 frente8,25, margenIC0,30 ybeneficio neto firma8,95. El consejo puede abstenerse del proyecto(0): incremento frente a esa alternativa8,95, no31,45. No es estimación de efecto en ejecutivos reales.'),
        nbf.v4.new_markdown_cell('## Modelo ysupuestos\nUn bono base B=rate×volumen paga(1−f)B ahora yfB solo si no ocurre fracaso. Éxito pagaB; fracaso paga(1−f)B≥0. El agente neutral al riesgo elige laacción que maximiza B(1−f q)−esfuerzo. La firma evalúa beneficio operativo esperado menos bono esperado, sin imponer laacción objetivo.\n\nEl diseñador busca elmenor f del menú con margenIC≥0,05, participación≥0, implementación real yvalor neto firma no negativo. No maximiza beneficio delprincipal entre todos los contratos. Sin descuento, impuestos oaversión alriesgo; fracaso observable,no manipulable yconsecuencias contractuales ciertas.'),
        nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\ncfg=json.loads(Path('config.json').read_text())\nsummary=json.loads(Path('results/summary.json').read_text())\ndisplay(cfg)"),
        nbf.v4.new_markdown_cell('## Baseline ycontratos\nLa respuesta del agente usa desempate adverso alprincipal; no se declara implementación en una indiferencia favorable inventada. Participation incluye alternativa externa0. Probabilidades ybeneficios son supuestos sintéticos conocidos.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/contracts.csv').round(4))\ndisplay(summary['selected'])\ndisplay(Image(filename='results/alignment.png'))"),
        nbf.v4.new_markdown_cell('## Falsación ylímites\nEl mínimo continuo analítico para margen0,05 es6,05/7≈0,864286; elmenú elige0,9, no óptimo continuo. Con tope0,8 no es implementable. Una tercera acción omitida rompe laalineación yda beneficio neto−30,73. Los bonos siempre respetan responsabilidad limitada yse restan como transferencias del beneficio operativo.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/sensitivity.csv'))\ndisplay(pd.read_csv('results/scaling.csv'))\ndisplay(summary['omitted_action_stress'])\nassert summary['selected']['ic_margin']>=cfg['required_margin']\nassert summary['selected']['implemented']==cfg['target']\nassert summary['omitted_action_stress']['name']!=cfg['target']"),
        nbf.v4.new_markdown_cell('## Decisión\nContinuar solo como auditoría de diseño: diferimiento contingente ymedida de calidad deben contrastarse con acciones/probabilidades/costos reales aprobados. Ajustar menú si hayaversión alriesgo odescuento. Detener propuesta si no existe contratoIC/IR. No interpreta legalidad, obligación regulatoria ni aplicabilidad de malus/clawback. ComponenteS2 sintético, programa13 sinrecertificar.')
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

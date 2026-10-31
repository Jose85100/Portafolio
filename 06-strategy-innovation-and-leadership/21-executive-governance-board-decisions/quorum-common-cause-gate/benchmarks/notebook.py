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
        nbf.v4.new_markdown_cell('# Junta: asistencia marginal no garantiza disponibilidad de quórum\n\n## Resumen\nEn el caso sintético, independencia de marginales predice0,8512sin reservas yparece cumplir meta0,85; mezcla exacta conausencia común da0,76. Dos participantes dereserva autorizados elevan disponibilidad a0,9139concoste2. No se mide calidad de votos ni aprobación.'),
        nbf.v4.new_markdown_cell('## Modelo ycondiciones\nComitébase4, quórumfijo3 ypresencia obligatoria del miembro0(risk_lead). Régimen normalpeso0,8: asistencia(0,95;1;1;1). Disrupción compartidapeso0,2: (0,95;0;0;0). Dentro de cada régimen se asume independencia; incondicionalmente los3miembros comparten ausencia. Reservas autorizadas tienenprobabilidad0,9ysonindependientesdelrégimen por supuesto.\n\nSe enumeran máscarasX∈{0,1}^N ycalculaΣr w_rΣX I(sumX≥3,X0=1)Πi p_ri^Xi(1−p_ri)^(1−Xi). El baseline reemplaza la mezcla porproducto de marginales. Objetivo: menorcoste de reservas que alcanza meta, manteniendo quórum3yrolobligatorio. No se autorizan sustituciones reales por elmodelo.'),
        nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\ncfg=json.loads(Path('config.json').read_text())\nsummary=json.loads(Path('results/summary.json').read_text())\ndisplay(cfg)"),
        nbf.v4.new_markdown_cell('## Planes ybaseline\nMismas probabilidades marginales, diferente distribución conjunta. Las224filas de máscaras para0/1/2reservas se guardan sin selección, incluidas masas0para conservar elespacio completo.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/plans.csv').round(5))\ndisplay(summary)\ndisplay(Image(filename='results/quorum.png'))"),
        nbf.v4.new_markdown_cell('## Falsación ylímites\nLa independencia no falla siempre hacia elmismo lado. Aquí da un falso pase. Elrolobligatorio conprobabilidad0,95limita toda disponibilidad a≤0,95; meta0,97es imposible. Si sube disrupción a0,8, dosreservas tampoco cumplen. Si quórum se eleva a4, no basta este menú. No se baja quórum para forzar factibilidad.'),
        nbf.v4.new_code_cell("display(pd.read_csv('results/sensitivity.csv'))\ndisplay(pd.read_csv('results/scaling.csv'))\nassert summary['baseline_independent']['availability']>=cfg['target']>summary['actual_baseline_availability']\nassert summary['selected_exact']['availability']>=cfg['target']"),
        nbf.v4.new_markdown_cell('## Decisión\nContinuar solo como prueba de resiliencia con2reservas elegibles si reglas vigentes ysupuestos lo permiten. Ajustar calendario/modos remotos si haycorrelación de ausencias. Detener propuesta cuando menú no alcanza meta. No asesoría legal, cambio de estatutos, evidencia de calidad decisional ni probabilidad de aprobación. ComponenteS2 sintético, programa21S1sinrecertificar.')
    ]
    from benchmarks.tutorial_cells import extension_cells
    nb.cells.extend(extension_cells())
    from benchmarks.joint_role_cells import joint_cells
    nb.cells.extend(joint_cells())
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

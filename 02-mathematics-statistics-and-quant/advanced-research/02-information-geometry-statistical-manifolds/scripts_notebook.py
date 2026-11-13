"""Create and genuinely execute the companion notebook, failing on any cell error."""

import argparse
from pathlib import Path
import nbformat as nbf


def execute_in_process(nb):
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output

    shell = InteractiveShell.instance()
    shell.reset(new_session=False)
    for i, cell in enumerate(c for c in nb.cells if c.cell_type == "code"):
        with capture_output() as captured:
            result = shell.run_cell(cell.source, store_history=False)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(f"cell {i + 1} failed") from (result.error_before_exec or result.error_in_exec)
        outputs = []
        if captured.stdout:
            outputs.append(nbf.v4.new_output("stream", name="stdout", text=captured.stdout))
        if captured.stderr:
            outputs.append(nbf.v4.new_output("stream", name="stderr", text=captured.stderr))
        for output in captured.outputs:
            outputs.append(nbf.v4.new_output("display_data", data=output.data, metadata=output.metadata))
        cell.outputs = outputs
        cell.execution_count = i + 1
    return nb


def build():
    cells = [
        nbf.v4.new_markdown_cell(
            "# Geometría categórica y detección de cambios\n## tl;dr\nFisher–Rao y Hellinger no añaden detecciones distintas con las mismas permutaciones. Verifique los resultados completos y límites abajo; no se reclama un detector financiero."
        ),
        nbf.v4.new_markdown_cell(
            "## Context & Methods\n### Key Assumptions\nDos muestras IID, vocabulario fijo y particiones compartidas. Métrica por una observación categórica, extensión continua a ceros. No aplica a datos temporales sin modificar el esquema de remuestreo. Fuentes: referencias.bib y fuentes.md.\n### 1. Configuración y controles"
        ),
        nbf.v4.new_code_cell(
            "import csv, json\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display, Image\nfrom src.geometry import fisher_rao, hellinger, local_fisher, geodesic\nfrom src.reference import oracle_fr\nfrom src.testing import permutation_test\nconfig=json.loads(Path('config.json').read_text())\nresult=json.loads(Path('benchmarks/results.json').read_text())\nprint(config['question'])\nprint(json.dumps(result['checks'],indent=2))\nassert all(result['passed'].values())"
        ),
        nbf.v4.new_markdown_cell(
            "### 2. Cuadrático local no es distancia global\nEl diámetro Fisher–Rao categórico es pi; la aproximación tangente depende del origen."
        ),
        nbf.v4.new_code_cell(
            "a=np.array([.99,.01]);b=np.array([.5,.5])\nprint({'FR':fisher_rao(a,b),'H':hellinger(a,b),'local_p':local_fisher(a,b),'local_q':local_fisher(b,a)})\nassert local_fisher(a,b)>np.pi\nfor t in [0,.25,.5,.75,1]:\n    g=geodesic(a,b,t)\n    print(t, g, fisher_rao(a,g))\n    assert np.isclose(fisher_rao(a,g),t*fisher_rao(a,b),atol=1e-10)"
        ),
        nbf.v4.new_markdown_cell(
            "## Data\n### 3. Datos observados y permutaciones reproducibles\ncounts.npz sigue el orden de replicates.csv; columnas de padding excluidas mediante K. No se vuelve a generar una muestra diferente."
        ),
        nbf.v4.new_code_cell(
            "rows=list(csv.DictReader(Path('benchmarks/replicates.csv').open()))\ncounts=np.load('benchmarks/counts.npz')['counts']\nrow=rows[1200];k=int(row['k'])\nagain=permutation_test(counts[1200,0,:k],counts[1200,1,:k],config['permutations'],int(row['permutation_seed']))\nprint({key:again[key] for key in ['p_fr','p_hellinger','p_pearson','p_pearson_asymptotic']})\nassert again['p_fr']==float(row['p_fr'])\nassert again['p_fr']==again['p_hellinger']\nprint('datasets:',len(rows),'particiones:',result['design']['random_partitions'])"
        ),
        nbf.v4.new_markdown_cell(
            "## Results\n### 4. Tasas y variabilidad entre datasets\nSe muestran los 4 métodos para K=32,n=100; los otros escenarios quedan en summary.csv. Wilson 95%, no simultáneos."
        ),
        nbf.v4.new_code_cell(
            "summary=list(csv.DictReader(Path('benchmarks/summary.csv').open()))\nfor row in summary:\n    if row['k']=='32' and row['n']=='100' and row['scenario'] in ['null_sparse','shift_rare']:\n        print(row['scenario'], row['method'], 'rate=',round(float(row['rate']),3),'95% Wilson=',[round(float(row[c]),3) for c in ['lower95','upper95']])\nprint('Diferencia máxima p FR/H:',max(abs(float(r['p_fr'])-float(r['p_hellinger'])) for r in rows))"
        ),
        nbf.v4.new_markdown_cell(
            "### 5. Figura reproducida desde CSV\nLas funciones de dibujo permanecen editables en src/benchmark.py. Los intervalos corresponden a réplicas de datasets, no a repeticiones de tiempo."
        ),
        nbf.v4.new_code_cell(
            "from src.benchmark import plot\ntiming=list(csv.DictReader(Path('benchmarks/timings.csv').open()))\nconverted=[{**r,'k':int(r['k']),'n':int(r['n']),'rate':float(r['rate']),'lower95':float(r['lower95']),'upper95':float(r['upper95'])} for r in summary]\nconverted_time=[{**r,'k':int(r['k']),'seconds':float(r['seconds'])} for r in timing]\nplot(converted,converted_time)\ndisplay(Image(filename='benchmarks/audit.png'))"
        ),
        nbf.v4.new_markdown_cell(
            "### 6. Referencia independiente de 80 dígitos\nLa referencia usa acos de afinidad de alta precisión, no la fórmula float64 por cuerda."
        ),
        nbf.v4.new_code_cell(
            "for step in [1e-12,1e-6,.1,1]:\n    q=(1-step)*a+step*b\n    ref=oracle_fr(a,q)\n    error=abs(fisher_rao(a,q)-ref)\n    print(step,ref,error)\n    assert error<1e-11"
        ),
        nbf.v4.new_markdown_cell(
            "## Takeaways\nLa equivalencia monótona predice el resultado: no hay ganancia exclusiva de potencia FR/H con el mismo test. La aproximación local no es una distancia global. Pearson permutado ofrece una comparación distinta y legítima. Solo 100 réplicas por escenario, 199 particiones y datos sintéticos: no certifica falsas alarmas de monitorización continua. Consulte informe.md, los 16 escenarios y las limitaciones. Figura inspeccionada por separado; revisión visual integral de este cuaderno en visor no reclamada."
        ),
    ]
    nb = nbf.v4.new_notebook(
        cells=cells,
        metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}},
    )
    return nb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", action="store_true")
    args = parser.parse_args()
    nb = build()
    if args.kernel:
        from nbclient import NotebookClient

        nb = NotebookClient(
            nb, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(Path.cwd())}}
        ).execute()
    else:
        nb = execute_in_process(nb)
    nbf.validate(nb)
    nbf.write(nb, "notebook.ipynb")
    print("Seis celdas ejecutadas y guardadas con outputs.")


if __name__ == "__main__":
    main()

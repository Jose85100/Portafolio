"""Narrative notebook with actual in-process IPython execution and visible outputs."""
import os
from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook(cells=[
    nbf.v4.new_markdown_cell('# Sovereign Clearing Audit\n## tl;dr\nEl componente estático del programa soberano-bancario avanza a S2 parcial: balance, pagos pro-rata, LP y oráculo racional. Impago bruto no equivale a pérdida social. Un residual pequeño no certifica precisión de pagos en redes casi cerradas.'),
    nbf.v4.new_markdown_cell('## Context & Methods\n### Key Assumptions\nL[i,j] es deuda de i con j; l_i es deuda externa; pbar_i=sum_j L[i,j]+l_i; Pi[i,j]=L[i,j]/pbar_i. Cada deudor debe algo fuera del sistema. Activos disponibles x_i(h)=cash_i+(1-h)*sovereign_i, liquidables al precio fijo supuesto. No hay precio endógeno, haircut estimado, costos de quiebra ni rescate.\n$$p=\\min(\\bar p,x+\\Pi^Tp).$$\nLa iteración desde0 y pbar produce cotas en aritmética exacta; se para por ancho L1≤1e-8. La implementación flotante no es aritmética de intervalos con redondeo dirigido.'),
    nbf.v4.new_code_cell("import sys,json,csv\nfrom pathlib import Path\nimport numpy as np\nsys.path.insert(0,str(Path('src').resolve()))\nfrom clearing import Network,assets,bracket,lp_clear,rational_clear,accounting\nconfig=json.loads(Path('results/config.json').read_text())\nnet=Network(np.array(config['liabilities']),np.array(config['outside']))\nx=assets(net,np.array(config['cash']),np.array(config['sovereign']),1.)\nr=bracket(net,x)\nprint('Pagos iterativos:',r.payments)\nprint('Pagos racionales:',rational_clear(net,x))\nprint('Ancho L1:',r.width_l1,'; LP error:',abs(lp_clear(net,x)-r.payments).sum())"),
    nbf.v4.new_markdown_cell('### Por qué el residual no basta\nEn este alcance anclado, beta=max_i sum_j Pi[i,j]<1. El mínimo por componente es1-Lipschitz y la norma1 inducida de Pi transpuesta es beta. Por tanto:\n$$\\|F(p)-F(q)\\|_1\\leq\\beta\\|p-q\\|_1,\\quad \\|p-p^*\\|_1\\leq\\frac{\\|F(p)-p\\|_1}{1-\\beta}.$$\nEs un argumento estándar condicionado al modelo y aritmética exacta, no una garantía formal del cálculo flotante. Al acercarse beta a1, un residual minúsculo puede coexistir con un error grande. El benchmark incluye una parada residual ajustada para una comparación de precisión más justa.'),
    nbf.v4.new_markdown_cell('## Data\nBalances, shocks y redes son sintéticos, seed20261018. La exposición soberana es un supuesto de balance, no datos TES. El contrafactual de una sola pasada usa cobros contractuales completos: no es otro equilibrio. Se compara también con el notebook estructural semanal existente, sin presentarlo como OLS genérico.'),
    nbf.v4.new_code_cell("print(config)\nprint('Conciliación al haircut total:',accounting(net,x,r.payments))\nprint(Path('results/weekly_regression.csv').read_text())"),
    nbf.v4.new_markdown_cell('## Results\nEn la economía pro-rata sin quiebra costosa, los pagos internos se cancelan al consolidar.\n$$\\sum_i x_i=\\sum_i (l_i/\\bar p_i)p_i+\\sum_i E_i.$$\nPor eso contar impagos de todas las obligaciones internas repetidamente no mide una pérdida agregada de bienestar.'),
    nbf.v4.new_code_cell("from IPython.display import Image,display\ndisplay(Image(filename='results/comparison.png'))"),
    nbf.v4.new_markdown_cell('### Control negativo y contraste independiente\nPara ancla externa1e-9 y recursos5e-10 por banco, la referencia racional paga1/2 cada banco. La parada por residual y el éxito nominal de LP pueden dar errores L1 cercanos a1.5. El esquema de cotas rechaza por presupuesto: es una limitación de alcance, no una solución rápida.'),
    nbf.v4.new_code_cell("for row in csv.DictReader(Path('results/near_closed.csv').open()):\n    if float(row['anchor'])==1e-9: print(row)\nprint(Path('results/coverage.txt').read_text())\nprint(json.loads(Path('results/metadata.json').read_text()))"),
    nbf.v4.new_markdown_cell('## Takeaways\nEvidencia de implementación y contabilidad, no causalidad ni validación bancaria. El juego dinámico, feedback fiscal, garantías, colateral y fire sales siguen S1. Ver informe.md: errores, presupuestos, benchmarks, prior art y límites. Las cotas flotantes se contrastan empíricamente con Fraction/LP; no se afirma un teorema numérico nuevo.')])
nb.metadata.kernelspec = dict(display_name='Python 3', language='python', name='python3')
nb.metadata.execution_method = 'Actual IPython in-process, captured stdout and image outputs'
os.chdir(root)
shell = InteractiveShell.instance()
count = 0
for cell in nb.cells:
    if cell.cell_type != 'code':
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=True)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError('Notebook execution failed')
    cell.execution_count = count
    cell.outputs = []
    for name, value in [('stdout', captured.stdout), ('stderr', captured.stderr)]:
        if value:
            cell.outputs.append(nbf.v4.new_output('stream', name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output('display_data', data=output.data, metadata=output.metadata))
nbf.validate(nb)
nbf.write(nb, root/'notebook.ipynb')

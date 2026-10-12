"""Genera el notebook ejecutable del laboratorio IFRS 9."""
from pathlib import Path
import nbformat as nbf

root = Path(__file__).parents[1]
nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell("# IFRS 9 — laboratorio ejecutable\n\n**Datos sintéticos; no es una estimación contable ni un modelo productivo.**\n\n## tl;dr\nEste notebook calcula ECL multiescenario, staging y una tabla de calibración reproducible."),
    nbf.v4.new_markdown_cell("## Contexto y ecuaciones\n\nLa pérdida esperada por horizonte es:\n\n$$ECL = \\sum_{t=1}^{T} PD_t^{marginal} \\times LGD_t \\times EAD_t \\times DF_t$$\n\nStage 1 usa 12 meses; Stages 2 y 3 usan horizonte de vida. Los escenarios se ponderan: $ECL^w=\\sum_s w_sECL_s$."),
    nbf.v4.new_code_cell("from pathlib import Path\nimport sys\nROOT = Path.cwd()\nif ROOT.name == 'notebooks':\n    ROOT = ROOT.parent\nsys.path.insert(0, str(ROOT))\nfrom src.ifrs9_engine import cartera_sintetica, ecl_componentes, ponderar_escenarios, backtest_pd\nimport numpy as np\nimport matplotlib.pyplot as plt\ncartera = cartera_sintetica(2_000, 91)\npesos = {'base': .60, 'adverso': .30, 'severo': .10}"),
    nbf.v4.new_code_cell("escenarios = {s: ecl_componentes(cartera, s) for s in pesos}\nresumen = {s: df.ecl.sum() for s, df in escenarios.items()}\nponderado = ponderar_escenarios(cartera, pesos)\nresumen, ponderado.ecl_ponderada.sum()"),
    nbf.v4.new_markdown_cell("## Resultados\nLa severidad del escenario aumenta PD y LGD por construcción; esto es una prueba de sensibilidad, no una proyección macroeconómica."),
    nbf.v4.new_code_cell("plt.style.use('seaborn-v0_8-whitegrid')\nfig, ax = plt.subplots(figsize=(7,4))\nax.bar(resumen.keys(), resumen.values(), color=['#2463eb','#f59e0b','#c2410c'])\nax.set(title='ECL por escenario sintético', ylabel='ECL')\nplt.show()"),
    nbf.v4.new_code_cell("base = escenarios['base']\nbase.groupby('stage').agg(cuentas=('loan_id','size'), ecl=('ecl','sum'), exposicion=('ead','sum')).round(2)"),
    nbf.v4.new_markdown_cell("## Backtesting de PD\nSe simulan defaults OOT coherentes con la PD para ilustrar la tabla de calibración. En uso real se reemplaza por una muestra OOT gobernada."),
    nbf.v4.new_code_cell("rng = np.random.default_rng(12)\ndefault_oot = rng.binomial(1, cartera.pd_12m)\ncalibracion = backtest_pd(cartera.pd_12m, default_oot)\ncalibracion"),
    nbf.v4.new_code_cell("fig, ax = plt.subplots(figsize=(6,5))\nax.plot(calibracion.pd_media, calibracion.default_observado, 'o-', label='OOT sintético')\nax.plot([0, max(calibracion.pd_media.max(), calibracion.default_observado.max())], [0, max(calibracion.pd_media.max(), calibracion.default_observado.max())], '--', color='gray', label='calibración perfecta')\nax.set(xlabel='PD media', ylabel='default observado', title='Backtesting de calibración')\nax.legend(); plt.show()"),
    nbf.v4.new_markdown_cell("## Límites\nNo incorpora definición regulatoria de default, datos observados, overlays de gestión, recuperación histórica, ni aprobación contable. Antes de uso productivo se requiere validación independiente, gobierno de modelos y fuentes trazables."),
]
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata.language_info = {"name": "python", "version": "3"}
nbf.write(nb, root / "notebooks" / "ifrs9_laboratory.ipynb")

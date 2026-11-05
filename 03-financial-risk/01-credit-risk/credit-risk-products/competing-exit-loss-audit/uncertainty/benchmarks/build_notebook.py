from pathlib import Path
import contextlib, io, json, sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
code='''from src.lgd_uncertainty import Scenario, evaluate\ns = Scenario(100.0,160.0,1.0,.18,.12,3.0,2.0)\nr = evaluate(s)\nprint(f"Default probability: {r.default_probability:.12f}")\nprint(f"Expected loss: {r.expected_loss:.12f}")\nprint(f"SD uncertain LGD: {r.loss_sd:.12f}")\nprint(f"SD plug-in mean LGD: {r.plugin_variance**0.5:.12f}")\nassert r.loss_variance >= r.plugin_variance >= 0\n'''
ns={}; output=io.StringIO()
with contextlib.redirect_stdout(output): exec(compile(code,'notebook-cell','exec'),ns)
nb={"cells":[
 {"cell_type":"markdown","metadata":{},"source":["# Incertidumbre de LGD con riesgos competidores\n","\n","Pregunta: ¿qué componente de varianza se pierde al sustituir LGD incierta por su media?\n","\n","Con hazards constantes, la densidad incondicional de default es $\\lambda_d e^{-(\\lambda_d+\\lambda_p)t}$. Si $EAD(t)=a+bt$ y $G\\sim Beta(\\alpha,\\beta)$ independiente, $E[L]=E[G]\\lambda_d\\int_0^T e^{-ht}(a+bt)dt$ y $E[L^2]=E[G^2]\\lambda_d\\int_0^T e^{-ht}(a+bt)^2dt$. La diferencia entre momentos completos y plug-in cuantifica únicamente dispersión LGD omitida; no es predicción empírica.\n","\n","La línea previa ya integraba EAD×LGD afines deterministas; este incremento añade parámetro LGD aleatorio independiente para aislar incertidumbre. Se compara con baseline plug-in de igual media."]},
 {"cell_type":"code","execution_count":1,"metadata":{},"outputs":[{"output_type":"stream","name":"stdout","text":output.getvalue()}],"source":code.splitlines(True)},
 {"cell_type":"markdown","metadata":{},"source":["## Lectura del resultado\n","El escenario y los outputs se calculan en el módulo. La ablación de concentración alta reduce la varianza de LGD hacia cero; la media de pérdida permanece igual si se conserva E[G]. El benchmark añade cuadratura de Simpson para contrastar el primer momento analítico.\n","\n","No se estimó Alpha/Beta, hazards ni curva EAD con datos observados. La independencia entre LGD y momento de default es supuesta y puede ser falsa."]}],
 "metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":sys.version.split()[0]}},"nbformat":4,"nbformat_minor":5}
(root/'notebook.ipynb').write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n')

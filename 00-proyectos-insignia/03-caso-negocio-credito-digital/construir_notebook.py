"""Genera y ejecuta notebook.ipynb del proyecto 03 (caso de inversión en crédito digital de consumo)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun import construir_notebook  # noqa: E402

C = []
md = lambda s: C.append(("md", s))  # noqa: E731
code = lambda s: C.append(("code", s))  # noqa: E731

md("""# Caso de inversión: crédito digital de consumo en Colombia

**Decisión que se le presenta a una junta o a un inversionista.** ¿Conviene lanzar una plataforma digital de crédito de
consumo en Colombia? Si conviene, ¿con qué producto, con qué estructura de fondeo, a qué escala y con cuánto capital?

**Método.** Primero los hechos observados (tamaño del mercado, entrantes digitales, precios frente al techo de usura y mora
por producto, todo de la SFC y de BanRep). Luego la economía unitaria, el plan a cinco años y la incertidumbre. Los supuestos
de negocio (CAC, costo operativo, LGD, fondeo, capital) están en un solo lugar, `caso.Supuestos`, y todos se someten a
sensibilidad y a Monte Carlo.

**Límite de los datos.** Las tasas semanales publicadas terminan en junio de 2022. El precio de entrada se construye con el
margen frente al techo de usura observado entonces, aplicado al techo vigente; no es la tasa de mercado de hoy.""")

code("""import sys, warnings
from dataclasses import replace
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path.cwd())); sys.path.insert(0, str(Path.cwd().parent))
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import caso as K
from comun import macro, cop_billones
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
FIG = Path("figuras"); FIG.mkdir(exist_ok=True)
tpm = float(macro().tpm.dropna().iloc[-1]); f_usura, usura_hoy = K.usura_vigente()
print(f"TPM vigente: {tpm:.2f}% | techo de usura de consumo vigente desde {f_usura}: {usura_hoy:.2f}% EA")""")

md("## 1. El mercado")
code("""mk = K.mercado()
tam = mk["tam"]
print(f"Saldo de consumo a {mk['ultimo']}: {cop_billones(tam.saldo_actual.sum())}; crecimiento anual compuesto "
      f"{(tam.saldo_actual.sum()/tam.saldo_inicial.sum())**(1/mk['anios'])-1:.1%} en {mk['anios']:.1f} años")
tam.assign(saldo_actual=lambda x: x.saldo_actual/1e12, saldo_inicial=lambda x: x.saldo_inicial/1e12).round(3)""")
code("""fig, ax = plt.subplots(1, 2, figsize=(13, 4))
(mk["digitales"].loc["2023-01":] / 1e12).plot(ax=ax[0]); ax[0].set_title("Saldo de consumo de entrantes digitales (billones)")
(100 * mk["cuota_digital_tarjeta"]).plot(ax=ax[1], color="tab:purple"); ax[1].set_title("Cuota digital en tarjeta de crédito (%)")
for a in ax: a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG / "entrantes_digitales.png", dpi=130); plt.show()
cd = mk["cuota_digital_tarjeta"]
print(f"Cuota de Nu, Lulo Bank y RappiPay en tarjeta: {cd.iloc[0]:.1%} ({cd.index[0]}) -> {cd.iloc[-1]:.1%} ({cd.index[-1]})")
print("Participación por tipo de entidad en consumo:", (100*mk["por_tipo"]).round(1).to_dict())""")
md("""**Lectura.** El mercado es grande y concentrado en bancos, pero la tarjeta ya demostró que un entrante digital puede tomar
cuota rápido. La evidencia de mercado favorece la tarjeta como cuña de entrada; la libranza, la mayor bolsa de saldo,
está dominada por bancos con convenios de nómina.""")

md("## 2. Precio: ¿cuánto espacio deja el techo de usura?")
code("""pr = K.precios()
pr.round(2).T""")
code("""for prod in K.PRODUCTOS:
    print(f"{prod}: margen mediano frente al techo {pr.loc[prod,'margen_usura_mediano_ponderado']:.1f} pp; "
          f"{pr.loc[prod,'monto_a_menos_de_2pp_del_techo']:.0%} del monto desembolsado a menos de 2 pp del techo; "
          f"ticket {pr.loc[prod,'ticket_millones']:.2f} millones")""")
md("""**Lectura.** En tarjeta casi la mitad del monto se desembolsa pegada al techo: el precio no es una palanca, la usura lo fija.
En libranza el techo no muerde (15 pp de margen) porque el riesgo es bajo y la competencia es por convenios, no por tasa.
Esto cambia la estrategia: en tarjeta se compite por producto y aprobación; en libranza, por distribución.""")

md("## 3. Riesgo observado por producto (del proyecto 01)")
code("""rg = K.riesgo_producto()
rg""")

md("""## 4. Economía unitaria y la pregunta del fondeo

Estado de resultados anual por peso de saldo, en estado estable. Se comparan dos estrategias: compañía de financiamiento con
fondeo mayorista (TPM + 3 pp) y banco digital con depósitos (TPM − 1 pp, más costo de servir cuentas y más capital mínimo).""")
code("""base = K.Supuestos()
filas = []
for est, kw in K.ESTRATEGIAS.items():
    s = replace(base, **kw)
    for prod in K.PRODUCTOS:
        filas.append({"estrategia": est, **K.economia_unitaria(prod, pr, rg, tpm, usura_hoy, s)})
U = pd.DataFrame(filas).set_index(["estrategia", "producto"])
U[["tasa_cliente", "rendimiento", "comisiones", "fondeo", "perdida", "opex", "cac", "roa", "roe"]].round(4)""")
code("""ke = base.costo_capital
mejor = U.roe.idxmax()
print(f"Costo de capital supuesto: {ke:.0%}. Mejor combinación: {mejor[1]} con {mejor[0].lower()}, ROE {U.roe.max():.1%}.")
print(f"Con fondeo mayorista ningún producto supera {U.xs(list(K.ESTRATEGIAS)[0]).roe.max():.1%} de ROE.")""")
md("""**Primera iteración, primera conclusión.** Con una TPM de 12,25% y un techo de 28,3%, el negocio de fondeo mayorista no
existe: el diferencial entre el techo y el costo del dinero no alcanza para cubrir pérdida, operación y adquisición. Ninguna
mejora de originación compensa ese diferencial. La decisión estructural es el fondeo, no el producto.""")

md("""## 5. Segunda iteración: configuración con depósitos y sin descuento de precio

El descuento de entrada de 2 pp destruye valor en tarjeta, donde el precio lo fija el techo. Se elimina, y se compite por
aprobación y experiencia.""")
code("""dep = replace(base, **K.ESTRATEGIAS["Banco digital con depósitos"], descuento_precio_pp=0.0)
U2 = pd.DataFrame([K.economia_unitaria(p, pr, rg, tpm, usura_hoy, dep) for p in K.PRODUCTOS]).set_index("producto")
# Estrés: pérdida al pico observado del ciclo de cada producto.
estres = {p: rg.loc[p, "icv90_pico"] / rg.loc[p, "icv90_promedio"] for p in K.PRODUCTOS}
U2["roe_estres_pico"] = [K.economia_unitaria(p, pr, rg, tpm, usura_hoy, replace(dep, multiplicador_perdida=estres[p]))["roe"] for p in K.PRODUCTOS]
U2["multiplicador_pico"] = pd.Series(estres)
U2[["tasa_cliente", "roa", "roe", "multiplicador_pico", "roe_estres_pico"]].round(3)""")

md("## 6. Incertidumbre: qué supuesto decide el caso")
code("""tor = K.tornado("Tarjeta de crédito", pr, rg, tpm, usura_hoy, dep)
fig, ax = plt.subplots(figsize=(8, 3.5))
y = np.arange(len(tor))
ax.barh(y, 100*(tor.roe_alto - tor.roe_base), left=100*tor.roe_base, color="tab:red", alpha=.6, label="valor alto")
ax.barh(y, 100*(tor.roe_bajo - tor.roe_base), left=100*tor.roe_base, color="tab:blue", alpha=.6, label="valor bajo")
ax.set_yticks(y, tor.supuesto); ax.axvline(100*tor.roe_base.iloc[0], color="k"); ax.axvline(100*ke, color="0.5", ls="--")
ax.set_xlabel("ROE (%)"); ax.set_title("Tarjeta, banco digital: sensibilidad del ROE"); ax.legend()
plt.tight_layout(); plt.savefig(FIG / "tornado_tarjeta.png", dpi=130); plt.show()
print("Supuesto más influyente:", tor.supuesto.iloc[0], f"(rango de ROE {tor.rango.iloc[0]:.1%})")""")
code("""MC = {p: K.montecarlo(p, pr, rg, tpm, usura_hoy, dep, n=5000) for p in K.PRODUCTOS}
mc = pd.DataFrame({p: {"roe_p5": m.roe.quantile(.05), "roe_p50": m.roe.median(), "roe_p95": m.roe.quantile(.95),
                       "prob_roe_sobre_ke": (m.spread > 0).mean(), "prob_perdida": (m.roe < 0).mean()} for p, m in MC.items()}).T
mc.round(3)""")

md("## 7. Escala: con costos fijos y capital mínimo, el tamaño decide")
code("""metas = (200_000, 400_000, 800_000, 1_200_000, 2_000_000)
E1 = K.escala("Tarjeta de crédito", pr, rg, tpm, usura_hoy, dep, metas)
E2 = K.escala("Libre inversión", pr, rg, tpm, usura_hoy, dep, metas)
tab = pd.concat({"Tarjeta": E1, "Libre inversión": E2}, axis=1)
fmt = tab.copy()
for k in ["Tarjeta", "Libre inversión"]:
    fmt[(k, "capital_aportado")] = fmt[(k, "capital_aportado")] / 1e9
    fmt[(k, "saldo_final")] = fmt[(k, "saldo_final")] / 1e12
print("capital_aportado en miles de millones; saldo_final en billones")
fmt.round(3)""")
md("""## 7b. Tercera iteración: tarjeta para adquirir, libre inversión para monetizar

La tarjeta sola no paga el costo de capital a ninguna escala razonable: el saldo por cliente es bajo frente al costo fijo y
al capital mínimo. Libre inversión rinde más por cliente, pero es el producto más cíclico. La combinación usual de los
entrantes digitales es adquirir con tarjeta y, después de 12 meses de comportamiento propio, ofrecer crédito de libre
inversión a una fracción de esos clientes. Supuestos del cruce (sensibilizables): 30% de los clientes, CAC de 50.000 pesos,
pérdida al 80% del promedio por selección con datos transaccionales, servicio compartido.""")
code("""filas = []
for m in metas:
    filas.append({"clientes_tarjeta": m, "estrategia": "Solo tarjeta", **K.indicadores_plan(K.plan("Tarjeta de crédito", pr, rg, tpm, usura_hoy, dep, clientes_meta=m))})
    filas.append({"clientes_tarjeta": m, "estrategia": "Tarjeta + cruce libre inversión", **K.indicadores_plan(K.plan_cruzado(pr, rg, tpm, usura_hoy, dep, m))})
ESC = pd.DataFrame(filas)
piv = ESC.pivot(index="clientes_tarjeta", columns="estrategia", values="tir_anual")
print("TIR anual por escala y estrategia (salida a 1,5x patrimonio):")
piv.round(3)""")
code("""cruz = ESC[ESC.estrategia == "Tarjeta + cruce libre inversión"].set_index("clientes_tarjeta")
cubre = cruz.index[cruz.tir_anual >= ke]
meta = int(cubre[0]) if len(cubre) else int(cruz.tir_anual.idxmax())
pl = K.plan_cruzado(pr, rg, tpm, usura_hoy, dep, meta)
ind = K.indicadores_plan(pl)
fig, ax = plt.subplots(1, 2, figsize=(13, 4))
(pl.set_index("mes")[["ingreso", "fondeo", "perdida", "opex", "cac"]] / 1e9).plot(ax=ax[0]); ax[0].set_title("Plan recomendado: flujos mensuales (miles de millones)")
(pl.set_index("mes")[["patrimonio", "capital_requerido"]] / 1e9).plot(ax=ax[1]); ax[1].set_title("Patrimonio y requerimiento (miles de millones)")
for a in ax: a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG / "plan_recomendado.png", dpi=130); plt.show()
solo = ESC[(ESC.estrategia == "Solo tarjeta")].set_index("clientes_tarjeta")
print(f"Escala mínima con TIR >= {ke:.0%}: {meta:,} clientes de tarjeta. Capital aportado {ind['capital_aportado']/1e9:,.0f} mil millones; "
      f"equilibrio mensual en el mes {ind['mes_equilibrio']}; ROE año 5 {ind['roe_anio5']:.1%}; TIR {ind['tir_anual']:.1%}.")
print(f"Solo tarjeta, misma escala: TIR {solo.loc[meta,'tir_anual']:.1%}.")""")

md("## 8. El ciclo de tasas como opción")
code("""sens = K.sensibilidad_tpm("Tarjeta de crédito", pr, rg, usura_hoy, dep)
print("Techo de usura fijo en el vigente; TPM variable:")
sens.round(3)""")
md("""Como el techo se ajusta con rezago y el fondeo se reprecia rápido, un ciclo de recortes abre un margen transitorio. La
entrada se puede escalonar: lanzar con escala mínima ahora y acelerar adquisición cuando la TPM baje.""")

md("## 9. Recomendación")
code("""p_tc = mc.loc["Tarjeta de crédito"]
print(f'''Recomendación: lanzar como banco digital fondeado con depósitos, con tarjeta como producto de adquisición y libre
inversión cruzada a clientes con historial; escala objetivo {meta:,} clientes de tarjeta. No entrar con fondeo mayorista ni con libranza.

1. Fondeo: con fondeo mayorista el mejor ROE de estado estable es {U.xs(list(K.ESTRATEGIAS)[0]).roe.max():.1%}; con depósitos y sin descuento, {U2.roe.max():.1%}.
2. Producto: la tarjeta adquiere (ROE {U2.roe['Tarjeta de crédito']:.1%}; {U2.roe_estres_pico['Tarjeta de crédito']:.1%} con la pérdida del pico) pero sola no paga
   el capital ({solo.loc[meta,'tir_anual']:.1%} de TIR a esta escala). El cruce a libre inversión lleva la TIR a {ind['tir_anual']:.1%}.
   Libre inversión como producto de adquisición es lo más riesgoso: ROE {U2.roe_estres_pico['Libre inversión']:.1%} en el pico y la mayor beta al ciclo (proyecto 01).
3. Precio: al techo, sin descuento; el {pr.loc['Tarjeta de crédito','monto_a_menos_de_2pp_del_techo']:.0%} del monto de tarjeta ya se desembolsa a menos de 2 pp del techo.
4. Capital: {ind['capital_aportado']/1e9:,.0f} mil millones de pesos en cinco años; equilibrio mensual en el mes {ind['mes_equilibrio']}.
5. Riesgo del caso (tarjeta, Monte Carlo): probabilidad de ROE sobre el costo de capital {p_tc['prob_roe_sobre_ke']:.0%}, de ROE negativo {p_tc['prob_perdida']:.0%}.
   El supuesto que decide es {tor.supuesto.iloc[0]}: la disciplina de costo por cliente vale más que cualquier mejora de originación.
6. Tiempo: escalonar la adquisición al ciclo de recortes de la TPM; cada 175 pb menos de TPM suben el ROE de la tarjeta unos {(sens.roe.loc[10.5]-sens.roe.loc[12.25]):.0%}.''')""")
md("""**Límites.** Precios con margen de 2022 frente al techo; pérdida anual aproximada por el ICV90 promedio; costos, CAC, LGD y
capital mínimo son supuestos de trabajo que deben reemplazarse por cotizaciones y datos propios antes de comprometer
capital; la salida a 1,5 veces patrimonio es convencional.""")

code("""import json
Path("resultados").mkdir(exist_ok=True)
U.to_csv("resultados/economia_unitaria_estrategias.csv"); U2.to_csv("resultados/economia_unitaria_recomendada.csv")
mc.to_csv("resultados/montecarlo_resumen.csv"); tab.to_csv("resultados/escala.csv"); pr.to_csv("resultados/precios_observados.csv")
Path("resultados/resumen.json").write_text(json.dumps({
    "tpm": tpm, "usura_vigente": usura_hoy, "roe_tarjeta_depositos": float(U2.roe["Tarjeta de crédito"]),
    "roe_max_mayorista": float(U.xs(list(K.ESTRATEGIAS)[0]).roe.max()), "plan_meta_clientes": meta,
    "tir_por_escala": {f"{k[0]}|{k[1]}": float(v) for k, v in ESC.set_index(["clientes_tarjeta", "estrategia"]).tir_anual.items()},
    "plan": {k: (float(v) if v is not None else None) for k, v in ind.items()},
    "prob_roe_sobre_ke_tarjeta": float(p_tc["prob_roe_sobre_ke"])}, indent=2, ensure_ascii=False))
print("Resultados guardados.")""")

if __name__ == "__main__":
    construir_notebook(C, Path(__file__).resolve().parent / "notebook.ipynb")
    print("notebook.ipynb ejecutado")

"""Genera y ejecuta notebook.ipynb del proyecto 01 (estrés y apetito de riesgo en consumo)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun import construir_notebook  # noqa: E402

C = []
md = lambda s: C.append(("md", s))  # noqa: E731
code = lambda s: C.append(("code", s))  # noqa: E731

md("""# Estrés macro y apetito de riesgo en la cartera de consumo colombiana

**Pregunta de negocio.** Un comité de riesgo de un banco o una fintech de consumo necesita responder cuatro cosas:
qué explicó el deterioro de 2023–2024, qué señal lo habría anticipado, cuánto podría costar un nuevo ciclo adverso
y qué límites de apetito deberían regir hoy por producto.

**Datos.** Todo sale de fuentes públicas oficiales, normalizadas en `../datos`:
- SFC: cartera por altura de mora y calificación, por entidad y producto, mensual de 2015-01 a 2026-08 (datos.gov.co `rvii-eis8`).
- BanRep: tasa de política monetaria (serie 59).
- DANE: desocupación (GEIH), IPC e ISE.

**Lo que no es.** La SFC publica saldos agregados por entidad, no créditos individuales. El ICV90 de aquí es saldo vencido a más de
90 días sobre saldo bruto: se mueve con los castigos y con el crecimiento del denominador, y no es una PD. Las LGD son supuestos
de trabajo explícitos. El resultado sirve para dimensionar y priorizar, no para provisionar.""")

code("""import sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path.cwd())); sys.path.insert(0, str(Path.cwd().parent))
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import estres as E
from comun import cartera, cop_billones
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
FIG = Path("figuras"); FIG.mkdir(exist_ok=True)
c = cartera(); s = E.series_consumo(c); p = E.por_producto(c); d = E.base_modelo(s)
co = c[c.familia == "Consumo"]
print(f"Filas entidad-producto-mes: {len(c):,} | consumo: {len(co):,} | entidades con consumo: {co.codigo_entidad.nunique()}")
print(f"Periodo: {s.index.min()} a {s.index.max()} | saldo de consumo último mes: {cop_billones(s.saldo.iloc[-1])}")
print(f"Filas que reconcilian vigente + vencida = saldo: {c.reconcilia.mean():.2%}")
assert c.reconcilia.mean() > 0.99""")

md("## 1. El ciclo observado")
code("""fig, ax = plt.subplots(1, 2, figsize=(13, 4))
(100 * s[["icv90", "temprana"]]).rename(columns={"icv90": "ICV 90+ días", "temprana": "Mora 31-60 días"}).plot(ax=ax[0])
ax[0].set_title("Consumo, sistema: saldo vencido / saldo bruto (%)"); ax[0].axvspan(s.index.get_loc("2020-04"), s.index.get_loc("2021-03"), color="0.9")
(100 * p["icv90"].unstack()[E.PRODUCTOS]).plot(ax=ax[1]); ax[1].set_title("ICV 90+ por producto (%)")
for a in ax: a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG / "ciclo_consumo.png", dpi=130); plt.show()
pico = s.icv90.idxmax(); valle = s.loc["2022-01":pico].icv90.idxmin()
print(f"Valle {valle}: {s.icv90[valle]:.2%} -> pico {pico}: {s.icv90[pico]:.2%} -> último {s.index[-1]}: {s.icv90.iloc[-1]:.2%}")""")

md("""**Lectura.** La franja gris son los alivios de la SFC de 2020 (Circulares 007 y 014): la mora reportada *cae* en plena
recesión porque los periodos de gracia congelan la altura de mora. Por eso ningún modelo estimado sobre esta muestra puede leer
2020 como un episodio normal, y el modelo satélite lleva una variable indicadora para ese periodo.""")

md("## 2. ¿Qué explicó el deterioro de 2023–2024? Descomposición tasa / mezcla")
code("""ss = E.shift_share(p, valle, pico)
tot = s.icv90[pico] - s.icv90[valle]
print(f"Cambio total del ICV90: {tot*1e4:,.0f} pb; suma de la descomposición: {ss.total.sum()*1e4:,.0f} pb")
assert abs(ss.total.sum() - tot) < 1e-3, "la descomposición debe cuadrar con el agregado (salvo productos que entran/salen)"
print(f"Efecto tasa (deterioro dentro de cada producto): {ss.efecto_tasa.sum()*1e4:,.0f} pb")
print(f"Efecto mezcla (cambio de composición): {ss.efecto_mezcla.sum()*1e4:,.0f} pb")
(1e4 * ss[["efecto_tasa", "efecto_mezcla", "interaccion"]]).round(0)""")

code("""lider = ss.index[0]
print(f"{lider} aporta {ss.total.iloc[0]/tot:.0%} del deterioro con {ss.peso_inicial.iloc[0]:.0%} del saldo inicial.")
print(f"Libre inversión + tarjeta: {(ss.loc[['Libre inversión','Tarjeta de crédito'],'total'].sum()/tot):.0%} del cambio.")""")

md("""**Lectura.** El deterioro fue un fenómeno de *tasa*, no de mezcla: los mismos productos se dañaron por dentro. La concentración
en libre inversión y tarjeta, que son los productos sin garantía ni descuento de nómina, apunta a la originación de 2021–2022
como origen. Libranza casi no se movió.""")

md("""## 3. Primera hipótesis: el desempleo como motor. Resultado: falsa en esta muestra

La intuición de manual es que la mora de consumo sigue al desempleo. Se mide la correlación del ICV90 con cada variable rezagada.""")
code("""corr = E.correlaciones_adelanto(d)
corr.round(2)""")
code("""print(f"Correlación máxima con desempleo (12m): {corr.desempleo_12m.max():.2f} | con inflación: {corr.inflacion.max():.2f} "
      f"(rezago {corr.inflacion.idxmax()}m) | con TPM: {corr.tpm.max():.2f} (rezago {corr.tpm.idxmax()}m)")
print(f"Crecimiento del crédito: contemporáneo {corr.crec.loc[0]:.2f}, a 18 meses {corr.crec.loc[18]:.2f}")""")
md("""**Lectura.** El desempleo no anticipa la mora en 2015–2026: los alivios de 2020 rompieron la relación justo en el mayor
choque de empleo de la muestra. Lo que sí anticipa es la combinación de inflación (que erosiona el ingreso disponible) y de tasas
(que encarecen el servicio de la deuda variable y la tarjeta), con 9 a 18 meses de rezago. El signo del crecimiento del crédito
cambia con el rezago: contemporáneamente el crédito que crece diluye la mora (más denominador sano); 18 meses después, esas
cosechas maduran y la mora sube. Ese es el mecanismo de cosecha que un comité debe vigilar.""")

md("""## 4. Alerta temprana a nivel entidad

Si la mora temprana (31–60 días) sirve como alerta, un aumento en una entidad debe anticipar su mora 90+ *más allá* del ciclo
común. Panel entidad-mes con efectos fijos de mes (que absorben el ciclo) y errores agrupados por entidad.""")
code("""pa = E.panel_alerta_temprana(c)
print(f"Observaciones: {pa['n']:,} de {pa['entidades']} entidades con más de 100.000 millones en consumo")
print(f"Beta: {pa['beta']:.2f} (t = {pa['t']:.1f}). Por cada 10 pb de aumento de mora temprana en 3 meses, "
      f"el ICV90 de la entidad sube {10*pa['beta']:.1f} pb en los 3 meses siguientes, descontado el ciclo.")
assert pa["t"] > 2.6""")
md("""**Lectura.** La mora temprana es una alerta útil y barata: está en el reporte mensual y anticipa la mora dura de la misma
entidad con un trimestre de ventaja. Se usa como segundo eje del semáforo de entidades (sección 8).""")

md("""## 5. Modelo satélite: selección de rezagos

Especificación: $\\text{logit}(ICV90_t) = c + \\rho\\,\\text{logit}(ICV90_{t-1}) + \\beta_1 TPM_{t-a} + \\beta_2 \\pi_{t-b} + \\beta_3 g_{t-k} + \\delta\\,\\text{alivios}_t$,
donde $g$ es el crecimiento anual del saldo de consumo. Los rezagos se eligen por AIC en una rejilla de 100 combinaciones,
todas estimadas **sobre la misma muestra** (si no, el AIC compara modelos con distinta cantidad de datos).""")
code("""tabla = E.seleccionar_rezagos(d)
print("Mejor especificación por AIC sin restricciones:")
tabla.head(3)[["tpm", "inflacion", "crec", "aic", "b_tpm", "b_inflacion", "b_crec", "signos_ok"]]""")
md("""**Segunda iteración.** El ganador por AIC tiene coeficiente **negativo** para la tasa de política: diría que subir tasas
reduce la mora, y un escenario adverso de tasas proyectaría *menos* deterioro. La causa es la colinealidad: BanRep sube la TPM
cuando sube la inflación, y el modelo reparte mal el efecto entre las dos. Un modelo de estrés con signos contrarios a la
teoría no es utilizable, así que la selección se restringe a especificaciones con los tres signos económicos esperados, como
se hace en los modelos satélite de supervisión.""")
code("""print(f"Especificaciones con signos coherentes: {tabla.signos_ok.sum()} de {len(tabla)}")
rez = E.rezagos_elegidos(tabla)
sat = E.ajustar(d, rez)
print("Rezagos elegidos:", rez, "| n =", len(sat.muestra), "| R2 =", round(sat.resultado.rsquared, 3))
sat.resultado.summary().tables[1]""")
code("""mlp = sat.multiplicadores_largo_plazo()
for v, m in mlp.items():
    print(f"Largo plazo, +1 pp en {v}: logit +{m:.3f}  ->  ICV90 desde {s.icv90.iloc[-1]:.2%} a "
          f"{1/(1+np.exp(-(np.log(s.icv90.iloc[-1]/(1-s.icv90.iloc[-1]))+m))):.2%}")
print(f"p-valor TPM: {sat.resultado.pvalues['tpm']:.2f}. El canal de tasa no queda identificado por separado de la inflación;"
      " el proyecto 02 lo evalúa como hallazgo de validación.")""")

md("## 6. Escenarios a 24 meses")
code("""esc = E.trayectorias_macro(d)
proy = {k: E.proyectar(sat, d, v) for k, v in esc.items()}
P = pd.DataFrame(proy)
fig, ax = plt.subplots(figsize=(10, 4))
(100 * s.icv90.loc["2021-01":]).plot(ax=ax, color="k", label="Observado")
for k, col in zip(P, ["tab:blue", "tab:orange", "tab:red"]):
    (100 * P[k]).plot(ax=ax, color=col, label=k)
ax.set_title("ICV 90+ consumo: observado y proyectado (%)"); ax.legend(); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG / "escenarios.png", dpi=130); plt.show()
resumen = pd.DataFrame({"pico": P.max(), "mes_pico": P.idxmax(), "fin_horizonte": P.iloc[-1]})
resumen""")
code("""crec_ult = d.crec.dropna().iloc[-1]
print(f"Crecimiento anual del saldo de consumo en el último mes: {crec_ult:.1f}%")
print(f"Aun en el escenario base el ICV90 pasa de {s.icv90.iloc[-1]:.2%} a {P['Base'].max():.2%}: la aceleración del crédito "
      "de 2025-2026 madura en mora con 12 meses de rezago aunque la macro no empeore.")
fin = P.iloc[-1]
print(f"Al final del horizonte, el adverso agrega {(fin['Adverso']-fin['Base'])*1e4:.0f} pb y el severo {(fin['Severo']-fin['Base'])*1e4:.0f} pb sobre el base.")""")
md("""**Lectura.** El hallazgo de más valor no es el escenario severo sino el base: la expansión reciente del crédito ya trae
incorporado un aumento de la mora. Los escenarios de estrés se separan del base tarde y poco, porque los choques de tasa e
inflación tardan entre 9 y 15 meses en transmitirse y sus coeficientes son pequeños; esa baja sensibilidad es justamente
uno de los puntos que revisa la validación independiente.""")

md("## 7. De la mora a la pérdida: impacto por producto")
code("""betas = E.sensibilidades_producto(p, s)
imp = E.impacto_perdida(proy, s, p, betas)
print(betas.round(3))
tab = imp.pivot(index="producto", columns="escenario", values="perdida_incremental")[["Base", "Adverso", "Severo"]] / 1e12
tab.loc["Total"] = tab.sum()
print("\\nPérdida incremental aproximada (billones de pesos) = (ICV90 pico - actual) x saldo x LGD supuesta")
tab.round(3)""")
code("""sev = imp.query("escenario == 'Severo'").set_index("producto")
print(f"Severo: {cop_billones(sev.perdida_incremental.sum())}, "
      f"{sev.perdida_incremental.sum()/sev.saldo.sum():.2%} del saldo de los cinco productos.")
print(f"Libre inversión concentra {sev.perdida_incremental['Libre inversión']/sev.perdida_incremental.sum():.0%} de la pérdida "
      f"con {sev.saldo['Libre inversión']/sev.saldo.sum():.0%} del saldo (beta {betas.b['Libre inversión']:.2f} frente al sistema).")""")

md("## 8. Marco de apetito y semáforo")
code("""apetito = E.marco_apetito(p, imp)
apetito""")
code("""sem = E.semaforo_entidades(c)
print(sem.senal.value_counts().to_string())
print(f"Saldo bajo 'Vigilar' o 'Seguimiento reforzado': {sem.loc[sem.senal!='Normal','saldo'].sum()/sem.saldo.sum():.1%}")
sem[["codigo", "tipo_entidad", "icv90", "vs_sistema", "delta_temprana_6m_pb", "senal"]].head(15)""")
md("""Las entidades se publican con código anónimo: es una señal estadística sobre datos agregados públicos, útil para
priorizar revisión, y no sustituye la información de supervisión ni la de la propia entidad.""")

md("## 9. Memo para el comité")
code("""amb = apetito.index[apetito.estado != "Verde"].tolist()
print(f'''1. El deterioro 2023-2024 fue de calidad de originación dentro de libre inversión y tarjeta ({(ss.loc[["Libre inversión","Tarjeta de crédito"],"total"].sum()/tot):.0%} del cambio), no de mezcla.
2. Alerta: la mora 31-60 días anticipa la 90+ de cada entidad un trimestre antes (beta {pa["beta"]:.2f}, t {pa["t"]:.1f}). Debe estar en el tablero mensual.
3. Escenario base: el ICV90 sube de {s.icv90.iloc[-1]:.2%} a {P["Base"].max():.2%} por maduración del crédito que crece al {crec_ult:.0f}% anual.
4. Severo: pérdida incremental de {cop_billones(sev.perdida_incremental.sum())}; el {sev.perdida_incremental["Libre inversión"]/sev.perdida_incremental.sum():.0%} en libre inversión.
5. Productos fuera de apetito hoy: {", ".join(amb) if amb else "ninguno"}.
Decisiones propuestas: endurecer cortes de originación de libre inversión antes de que madure la cosecha 2025-2026;
fijar límites por producto en los percentiles 75/90 de la tabla; revisar mensualmente las entidades o segmentos con alerta temprana.''')""")
md("""**Límites.** Datos agregados por entidad, no créditos; el ICV se mueve con castigos y ventas de cartera; LGD supuestas;
canal de tasa débilmente identificado; 104 meses de muestra efectiva con un periodo de alivios atípico. La validación
independiente de este modelo está en [`../02-validacion-modelo-satelite`](../02-validacion-modelo-satelite).""")

code("""import json
res = {"icv90_ultimo": float(s.icv90.iloc[-1]), "mes_ultimo": s.index[-1], "rezagos": rez,
       "coeficientes": sat.params.round(5).to_dict(), "pico_por_escenario": P.max().round(5).to_dict(),
       "perdida_incremental_billones": (tab["Severo"]).round(4).to_dict(),
       "alerta_temprana": {"beta": pa["beta"], "t": pa["t"], "n": pa["n"]},
       "estado_apetito": apetito.estado.to_dict()}
Path("resultados").mkdir(exist_ok=True)
Path("resultados/resumen.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float))
sem.drop(columns=[]).to_csv("resultados/semaforo_entidades_anonimo.csv", index=False)
P.to_csv("resultados/proyeccion_escenarios.csv")
print("Resultados guardados.")""")

if __name__ == "__main__":
    construir_notebook(C, Path(__file__).resolve().parent / "notebook.ipynb")
    print("notebook.ipynb ejecutado")

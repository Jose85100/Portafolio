"""Narrative notebook cells for the 2026-11-03 confidence-gated decision increment."""
from nbformat.v4 import new_code_cell, new_markdown_cell


def coattendance_cells():
    return [
        new_markdown_cell("""# 3 de noviembre — certificar antes de elegir una opción de asistencia

## Pregunta ejecutiva
Si las tasas de quórum de tres alternativas se estimaran con una muestra hipotética, ¿cambia el plan de menor costo al usar límites inferiores simultáneos en vez de la tasa observada? Esta es una extensión del mismo programa de disponibilidad del comité; no usa reuniones reales ni modifica el evento, las reglas de quórum o la elegibilidad.

**Uso correcto:** comparar métodos de incertidumbre y reconocer cuándo abstenerse. **No es una recomendación de nombramiento, presupuesto o gobierno.** Los 200 conteos por alternativa son diseñados y sintéticos."""),
        new_markdown_cell(r"""## Derivación: límites simultáneos sobre un menú fijado antes de observar los conteos

Para una opción (j), sea (X_j\sim\mathrm{Binomial}(n_j,p_j)) el número de sesiones hipotéticas que alcanzan el evento de quórum. La tasa puntual es (\widehat p_j=X_j/n_j); por sí sola no protege de seleccionar la opción que parece mejor por azar.

Con error familiar (\delta) y menú fijo de (m) opciones, Bonferroni asigna (\alpha_j=\delta/m). El límite inferior unilateral Clopper–Pearson para (x_j>0) es

\[
L^{CP}_j=\mathrm{Beta}^{-1}(\alpha_j; x_j,n_j-x_j+1),\qquad L^{CP}_j=0\;\text{si }x_j=0.
\]

Equivalentemente, para (x_j>0), invierte la cola binomial (P_{p=L}(X_j\ge x_j)=\alpha_j). La envolvente de Bonferroni garantiza cobertura simultánea de al menos (1-\delta) bajo el modelo binomial por opción, aunque las opciones dependan entre sí.

El baseline competitivo recibe exactamente el mismo presupuesto familiar y usa Hoeffding:

\[
L^{H}_j=\widehat p_j-\sqrt{\frac{\log(m/\delta)}{2n_j}}.
\]

La regla elige la opción de menor costo con (L_j\ge\tau). Si no existe, **se abstiene**. El límite Hoeffding puede ser negativo; no se recorta a cero para fabricar factibilidad. CP y Hoeffding son métodos clásicos: el aporte aquí es el puente auditable hacia la decisión del menú ya construido, más la prueba de estrés por deriva."""),
        new_code_cell("""import json
import pandas as pd
from IPython.display import display, Image
from src.coattendance_gate import PlanCount, select_plan
cfg = json.loads(open('config_coattendance.json').read())
decision = pd.read_csv('results/coattendance_decision.csv')
display(pd.read_csv('results/coattendance_synthetic_counts.csv'))
display(decision[['plan','cost','successes','trials','estimate','alpha_each','lower','hoeffding_lower','cp_pass','hoeffding_pass']].round(6))
plans = [PlanCount(**row) for row in cfg['fixed_menu']]
assert select_plan(plans, cfg['target'], cfg['family_alpha'], 'clopper_pearson') == 'B'
assert select_plan(plans, cfg['target'], cfg['family_alpha'], 'hoeffding') == 'C'
assert abs(float(decision.loc[decision.plan == 'B','lower'].iloc[0]) - 0.5736297217395927) < 1e-12
assert abs(float(decision.loc[decision.plan == 'B','hoeffding_lower'].iloc[0]) - 0.5488275659798814) < 1e-12"""),
        new_markdown_cell("""## Lo que mide la grilla exacta y el oráculo
Se evaluaron 606 combinaciones de tamaño muestral y probabilidad verdadera para cada método (1.212 filas método-celda), sumando la distribución binomial completa. Además, 230 límites CP se contrastan con una implementación separada que invierte por bisección la cola binomial mediante sumas finitas. Es una comprobación numérica de la implementación, no evidencia sobre juntas reales."""),
        new_code_cell("""coverage = pd.read_csv('results/coattendance_exact_coverage.csv')
oracle = pd.read_csv('results/coattendance_oracle_230.csv')
display(coverage.groupby('method').exact_coverage.agg(['min','mean','max']).round(6))
display(oracle.oracle_abs_error.agg(['max','mean']).to_frame('absolute error').round(14))
summary = json.loads(open('results/coattendance_summary.json').read())
assert summary['oracle_comparisons'] == 230
assert summary['exact_coverage_cells'] == 606
assert summary['oracle_max_abs_error'] < 1e-10
display(Image(filename='results/coattendance_gate.png'))"""),
        new_markdown_cell("""## Ablación adversa: la estacionariedad es sustantiva
La simulación genera la mitad de las sesiones con probabilidad de quórum 0,7 y la mitad después de una ruptura con probabilidad 0,5. Un límite calculado sobre el total histórico no certifica por ello la tasa vigente. En el experimento se compara la cobertura contra 0,5 después de la ruptura; la serie temporal no es IID Bernoulli con parámetro constante. La pérdida de cobertura se conserva como resultado negativo y delimita el alcance del certificado.

En la condición estacionaria, el parámetro de referencia es 0,6 y la cobertura Monte Carlo se acompaña de intervalos binomiales puntuales del 95%. Esos intervalos cuantifican error de simulación, no incertidumbre de observaciones reales ni una garantía para futuras poblaciones."""),
        new_code_cell("""mc = json.loads(open('results/coattendance_summary.json').read())['monte_carlo']
display(pd.DataFrame([{ 'scenario': s, 'method': method, **values }
                       for s, group in mc.items() for method, values in group.items()
                       if method in ('clopper_pearson','hoeffding')]))
display(Image(filename='results/coattendance_gate.png'))"""),
        new_markdown_cell("""## Interpretación ejecutiva y límites
En este menú y con los conteos sintéticos fijados, CP+Bonferroni selecciona B (costo abstracto 2) mientras el límite Hoeffding de igual error familiar selecciona C (costo 3). Esta diferencia muestra una decisión sensible al método; no prueba que CP sea universalmente superior ni que B tenga una tasa real suficiente. Se requiere calendario, definición estable de éxito, observaciones autorizadas, diagnóstico de deriva y tamaño de muestra preespecificado antes de cualquier aplicación. Si cambia el menú tras observar conteos, esta corrección por multiplicidad deja de cubrir el procedimiento de búsqueda."""),
        new_code_cell("""assert mc['stationary']['runs'] == 7200
assert mc['drift']['runs'] == 7200
assert mc['drift']['clopper_pearson']['coverage'] < mc['stationary']['clopper_pearson']['coverage']
display(pd.DataFrame([
    {'caso':'estacionario','CP':mc['stationary']['clopper_pearson']['coverage'],
     'Hoeffding':mc['stationary']['hoeffding']['coverage']},
    {'caso':'deriva, referencia actual 0.5','CP':mc['drift']['clopper_pearson']['coverage'],
     'Hoeffding':mc['drift']['hoeffding']['coverage']},
]).round(4))
display(pd.read_csv('results/coattendance_runtime.csv').groupby(['method','repetitions']).seconds.median().unstack().round(6))"""),
    ]

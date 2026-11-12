# Auditoría parcial de identidades — incremento1nov2026

## 1. Título y línea acumulativa

Extremos de exposición ante adjudicación parcial. Programa holdout de identidades:29 clausura,30 masa,31 calidad del grafo,1101 incertidumbre cuando falta adjudicación. Herramientas conectadas, no demo aislada. No cambios globales, shared ni contratos.

## 2. Hipótesis y novedad

H técnica: extremos calculados coinciden con min/max de todas las completaciones admitidas; umbral5508 configuraciones exhaustivas n≤6 y480 escenarios conteniendo verdad, caso completo igual a31. Config anterior a interpretación de resultados. Aporte respecto al repo:31 rechazaba toda adjudicación incompleta;1101 aprovecha equivalencia conocida sin rellenar desconocidos. Adaptación de ingeniería y auditoría con derivación combinatoria local; no originalidad científica mundial acreditada.

## 3. Estado del arte

prior_art1101.md compara cinco fuentes primarias verificadas1nov2026: Binette/Steorts arXiv2008.04443v3 (resumen/metadatos), Tamer2010 DOI10.1146/annurev.economics.050708.143401 (resumen editorial/concepto de identificación parcial), Kapoor/Narayanan2023 textoPMC, sklearn pair_confusion_matrix y NetworkX connected_components documentación oficial. No lectura íntegra de todos los papers ni búsqueda exhaustiva; no atribuir a Tamer esta fórmula. BibTeX claves partial1101*.

## 4. Brecha y tres candidatas

Tabla de seis criterios en prior_art1101.md: adjudicación parcial alta utilidad/continuidad elegida; disponibilidad temporal relevante pero falta contrato/fuente; DP eficiente útil pero menor prioridad que incertidumbre semántica. No confundir rotación con innovación. Equivalencia parcial completa implica que clases adjudicadas distintas no pueden fusionarse; enlaces positivos incompletos no cumplen ese supuesto.

## 5. Diseño y teoría

V finito, train/test congelado, subconjunto K adjudicado; desconocidos pueden formar clases nuevas o unirse a una conocida. Si ambos lados globales presentes, L=sum tamaños clases conocidas mixtas, H=L+u+sum mayores u_test tamaños clases purastrain+sum mayores u_train tamaños purastest. Derivación paso a paso y construcción alcanzable en derivacion1101.md y notebook Markdown LaTeX; todos son conteos de filas. Sin ambos lados L=H=0, matemáticamente trivial y sin holdout útil. No intervalos de confianza; no afirmación de todos los enteros alcanzables. Se conserva31 cuando K=V. Con K vacío [0,n]. Identidad real debe ser completación admitida, de otro modo no garantía.

Datos sintéticos31 reutilizados:4 regímenes×12 semillas×5 coberturas×2 patrones de selección=480 filas CSV.12 semillas no son poblaciones independientes; no inferencia. config_partial1101.json fuentes/generador/seeds/umbrales/coste. Hardware/versiones reales environment.json/versions.txt; dependencias directas fijadas requirements.txt. Fuente externa no requerida.

## 6. Implementación y reutilización

src/partial_audit.py tipado→dataclass PartialAudit con filas adjudicadas/desconocidas, cortes observados, cotas y decisión detected/conditional-zero/abstain. Reutiliza components/leaked_components29; auditor completo31 intacto. Excepciones IDs inválidos/fuera universo/asignación incorrecta. Coste O(n log n+L_id), memoria O(n+L_id), ordenación y clausuras; enteros exactos, no float. Python adecuado para auditoría/enseñanza; no traducción mecánica a otros lenguajes. EL83 y C++ existentes intactos. Diagramación editable Mermaid README.

## 7. Tests/benchmarks reales

36 tests pasan:28 regresión+8 nuevos; incluye5508 configuraciones con oráculo independiente que enumera particiones n≤6, adjudicación de prefijos y3 patrones de asignación. Además bordes completos/vacío/una sola cara, validación, invariancia al orden y negativo de adjudicación errónea. Ruff src/tests/benchmarks y mypy --strict4 núcleos pasan; no se midió cobertura de líneas.480 escenarios contienen verdad completa y notebook comprueba monotonicidad de cotas con muestras anidadas. Notebook6 celdas ejecutadas reales en proceso IPython,2 figuras visibles; no kernel Jupyter aislado ni frontend completo. Comando con instalación y comando con entorno reusado ejecutados; tiempos y memoria cómputo aparte de instalación/I/O.3 repeticiones×4 tamaños28–28000 solo auditor, no escala del DP.

## 8. Resultados y figuras

|Selección/cobertura|Anchura media exacta (filas)|Baseline seguro (filas)|Abstenciones/48|
|---|---:|---:|---:|
|Barajada0%|28|28|48|
|Barajada25%|26.1875|26.1875|27|
|Barajada50%|24|24|25|
|Barajada75%|21.020833|21.395833|24|
|Train-first25%|28|28|48|
|Train-first50%|27|28|48|
|Train-first75%|15.625|21.395833|24|
|Ambas100%|0|0|0|

Baseline justo: [L,n] con parcialidad y auditor31 exacto si completo; no se degrada31 para forzar mejora. Frente a baseline parcial,53/480 registros más estrechos, resto iguales, ninguno peor. El oráculo completo es privilegiado, no método deployable. A100% cada selección da24 casos detected y24 conditional-zero; no garantía empírica. information.png ilustra anchura/abstención; cost.png medianas ms/MiB por tamaño; crudos raw.csv/scale.json, no fijar timings como constantes universales. Gráficos inspeccionados realmente por autor como PNG, ejes/unidades/leyendas; estado de revisión independiente en consolidado. No estimación monetaria pertinente ni claims de rendimiento universal.

## 9. Análisis crítico y negativos

Aprovechar más información puede estrechar cotas sin decidir: train-first50% sigue48/48 abstenciones. Barajada50% no mejora baseline seguro, conservación explícita del negativo. Selección importa y no se debe comparar cobertura sola como diseño experimental aleatorio. Con adjudicación conocida incorrecta de2 filas diferentes en realidad una persona, puede informar[0,0] y exposición real2: falla supuesto, no se oculta ni se presenta como garantía incondicional. Ablation que trata desconocidos como singleton solo obtiene L y puede ocultar exposición. Más tests no verifican fuente de verdad.

## 10. Límites y sesgos

Equivalencia completa entre adjudicados fuerte; no sirve conjunto de enlaces positivos faltantes. No procedencia, timestamps ni disponibilidad prospectiva validados. Si adjudicación posterior al corte se usa para seleccionar split, no es evaluación prospectiva; solo diagnóstico retrospectivo permitido. Datos diseñados pequeños, patrones elegidos, sin prevalencia real/AUC/fairness/causalidad ni incertidumbre estadística. La enumeración pequeña verifica extremos locales, la deducción explicita supuestos; no afirmar teorema de ML o descubrimiento mundial. Puede ser imposible estrechar [0,n] con poca evidencia. No operación ni certificación de dominio.

## 11. Comando exacto

Desde05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/mvp-linked-entity-holdout:

```bash
bash run_partial_audit.sh
```

Instala .venv con requirements.txt y reproduce todo. Reuso: `PYTHON="$PWD/.venv/bin/python" SKIP_INSTALL=1 bash run_partial_audit.sh`. Python3.12+/pip inicial/Linux para registro CPU; no credenciales/datos externos. Instrucciones reproducibles en vez de Docker. Valores exactos sí reproducibles; nanosegundos/bytes varían. No alterar outputs de ciclos previos.

## 12. Referencias BibTeX

referencias.bib añade5 claves partial1101entity,identification,leakage,pairs,components; matriz prior_art1101.md incluye método/supuestos/evidencia/diferencia. results/partial1101/references_verified.json registra URLs y alcance de apertura1nov2026. Resúmenes se identifican como tales.

## 13. Rúbricas y madurez

Autoevaluación provisional1–5: novedad2 (derivación útil local, originalidad no acreditada), rigor4 (deducción+oráculo), reproducibilidad4 (sin kernel aislado), código4, claridad4, impacto3 (con escenarios simulados), honestidad5, MVP4. Rúbrica adicional: profundidad teórica4, aporte defendible3, calidad experimental3, utilidad4, reproducibilidad4, honestidad5. No sustituye dictamen independiente. Experimental ejecutado, revisión/publicación/CI separadas en consolidado; no validado empíricamente ni operacional, sin elevar madurez del dominio ni equiparar S2/M2.

## 14. Siguiente iteración y decisión

Continuar con fuente/fecha/equivalencia adjudicada auditables; ajustar contrato si solo hay enlaces positivos; cerrar cualquier claim de independencia real basado en conditional-zero sin garantía de adjudicación. Ahora podemos dar extremos exactos útiles con información parcial y declarar lo desconocido, antes solo rechazar entrada parcial. Pendiente validar disponibilidad temporal y fuente de cannot-links. research-log/roadmap documentan continuidad, decisiones y negativos.

Checklist: README✓src✓tests✓config✓requirements✓comando✓CSV/JSON✓2figuras✓notebookejecutado✓fórmulas✓5refsverificadas✓priorart✓3ideas✓baselinejusto/oráculo✓negativos✓14p✓2rúbricas✓researchlog/roadmap✓. Cobertura y validez empírica no medidas. Revisión final/PR/CI deben consultarse en consolidado, sin confundir existencia de archivo con certificación.

# Incremento31 — garantía condicional y calidad del grafo de identidades

## 1. Título y programa

Auditoría de holdout vinculado ante particiones mal especificadas. Programa persistente: independencia y utilidad de evaluaciones ML por identidad. Avance29 clausura,30 masa exacta,31 auditoría externa; no una nueva carpeta/proyecto ni cambio de contratos compartidos.

## 2. Hipótesis y novedad incremental

H31 es de refutación: C_O=0 no basta para C_T=0. Umbral preinterpretativo: un contraejemplo explícito. Config y escenarios fijados antes de ejecutar benchmark; diseño adversarial, no muestra empírica. Aporte local: medir errores del grafo contra adjudicación completa con la misma asignación congelada. Clasificación auditoría/adaptación de ingeniería; no técnica ML nueva, originalidad mundial ni contribución científica acreditada.

## 3. Estado del arte

Matriz prior_art31.md: cinco fuentes primarias realmente abiertas el31oct2026, cinco claves audit31 en referencias.bib. Kapoor/Narayanan aporta motivación sobre fuga; sklearn documenta unidades de grupos, confusión por pares y métricas; NetworkX clausura. No revisión sistemática. DOI directo403; texto completo PMC verificado, sin inventar acceso DOI. Sus métodos conocidos no se atribuyen al proyecto.

## 4. Brecha y tres ideas

(A) Auditoría adjudicada: alta relevancia, brecha negativa explícita30, utilidad inmediata, viable con verdad sintética/oráculo, requiere después adjudicación real. (B) Links temporales: relevante, distinta disponibilidad de información, pero falta contrato/fuente, necesita timestamps auditables. (C) Optimización de memoria DP: reutilizable y viable, requiere benchmark contra algoritmos competitivos, pero no corrige garantías mal interpretadas. Seleccionada A por cerrar primero la brecha de significado de la garantía; B/C pospuestas, no descartadas definitivamente. Registro acumulativo y roadmap actualizados.

## 5. Diseño/configuración y fórmulas

config_graph31.json: tamaños4/6/8/10, doce semillas0–11, cuatro regímenes y tres políticas. Son permutaciones de un diseño, no12 poblaciones independientes. Ver derivacion31.md y Markdown LaTeX del notebook: C_O original→C_T/E_T, derivación de contingencia TP/FP/FN/TN enteros sin ordenar. Conserva suma n(n−1)/2 y renombrado/orden; pierde interpretación de aristas directas y no identifica verdad latente. Propiedad de refinamiento T de O permite deducir ausencia de fuga con solo sobre-unión, a coste de factibilidad de masa. Existencia requiere mismo universo adjudicado no vacío; adjudicación parcial se rechaza. No se usan etiquetas predictivas. Hardware/versión reales en results/graph31/environment.json, freeze versions.txt; Python3.12.14, AMD EPYC9V74, host9CPUs visibles. Oráculo tiene información privilegiada, expresamente no desplegable.

## 6. Implementación

src/graph_audit.py API tipada audit_graph(observed,truth,assignment)→GraphAudit; reutiliza splitter/balancing29–30. Contingencia sin materializar pares. Complejidad O(n log n+L), memoria O(n+L), L incidencias; cuatro clausuras reutilizadas implican coste constante extra, oportunidad de optimización futura. Errores explícitos para IDs incompletos/duplicados/asignaciones inválidas. Python sirve como auditor legible junto a notebooks; no hay razón para traducción mecánica multilenguaje. C++/R/Julia/etc. existentes no se eliminan; EL83 intacto.

## 7. Tests y benchmarks ejecutados

28 tests pasan:21 regresión29–30 y7 nuevos. Incluyen192 casos aleatorios de particiones con oráculo exhaustivo de pares, invariancia al orden, vacíos/singleton, IDs faltantes, assignment inválido y contraejemplo4 filas. Test estilo propiedades con semilla, no afirmación de Hypothesis ni cobertura de líneas. Ruff src/tests/benchmarks pasa; mypy --strict sobre3 núcleos splitter/balancing/audit pasa. Cobertura no medida. Pipeline instala dependencias fijadas; notebook6 celdas ejecutado secuencialmente IPython con outputs/2PNG. No kernel Jupyter aislado ni validación frontend completa.144 registros CSV, cuatro puntos de escala del auditor; no C++ nuevo ni sanitizers pertinentes. El revisor independiente reprodujo pipeline exit0 y revisó núcleo/derivación/figura, incluyendo corrección temprana del claim de complejidad lineal.

## 8. Resultados exactos y figuras

|Régimen|Política|Runs con fuga verdadera/12|Media filas expuestas|Desviación media de14 filas|
|---|---|---:|---:|---:|
|Correcto|count30|0|0|3.166667|
|Correcto|DP30|0|0|0|
|Faltantes|count30|10|14|1.5|
|Faltantes|DP30|12|8|0|
|Sobre-unión|count30 / DP30|0|0|4|
|Mixto|count30|8|18.666667|1.333333|
|Mixto|DP30|12|28|0|
|Todos|Oráculo verdad|0|0|0|

Ambas políticas factibles count/DP tienen0 cortes declarados siempre; el oráculo puede cortar O con sobre-unión/mixto (1/4 componentes, respectivamente) y no es solución factible bajo O. Las tasas son frecuencia dentro de diseño, no prevalencia estimada. results/graph31/raw.csv y summary.json son fuente exacta. mechanism.png relaciona exposición/balance; cost.png muestra coste separado auditor. Dos PNG inspeccionados de verdad: ejes/unidades/leyendas legibles, sin recorte. Escala28–28000 filas en scale.json; tiempos/picos variables por host, una pasada cada tamaño; no claim estadístico de rendimiento ni coste monetario. Cómputo excluye instalación/carga/I/O. Conservar crudos en lugar de comparar timings entre reruns distintos.

## 9. Análisis crítico y negativos

H31 satisfecha: cuatro filas bastan para refutar garantía fuerte. Equilibrar masa no repara identidades mal partidas. Negativo significativo: mixto DP exacto expone28 filas frente a18.666667 del baseline por grupos; mayor frecuencia de fuga no equivale automáticamente a mayor deterioro predictivo, que no se midió. Ablation sin auditor externo reportaría únicamente0 cortes y ocultaría fallo; grafo correcto permite0 exposición, sobre-unión protege esta propiedad pero pierde balance. No se ajustaron escenarios para ocultar resultados desfavorables. No causalidad ni generalización certificada.

## 10. Limitaciones y sesgos

Datos diseñados sintéticos pequeños, sin tasas realistas de resolución de entidades. Doce semillas no justifican intervalos poblacionales. La verdad se supone completa/correcta e independiente del mecanismo auditado. Si adjudicación posterior al corte existe, solo diagnóstico retrospectivo; elegir split con ella e informar desempeño prospectivo sería fuga. No inferencia de vínculos, AUC, fairness, drift, calibración ni validez empírica. Sin soporte de adjudicación parcial. Python int evita overflow aritmético, RAM sigue finita. Conteos por pares no determinan unívocamente exposición de filas; se reportan ambos. La herramienta no arregla el grafo automáticamente.

## 11. Comando exacto

Desde 05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/mvp-linked-entity-holdout:

```bash
bash run_graph_audit.sh
```

Instala .venv con requirements.txt, tests/lint/tipos, benchmark y notebook. Linux/Python3.12+ con pip inicial. Reuso real auditado: `PYTHON="$PWD/.venv/bin/python" SKIP_INSTALL=1 bash run_graph_audit.sh`. Nuevo entorno reproduce propiedades/valores exactos, no nanosegundos/bytes idénticos. Instrucciones reproducibles sustituyen Dockerfile; sin dependencias externas de datos o credenciales.

## 12. Referencias BibTeX

referencias.bib conserva las anteriores y añade audit31leakage, audit31groups, audit31pairs, audit31components, audit31metrics; URLs y fecha31oct2026. prior_art31.md compara problema/supuestos/método/evidencia/diferencia. results/graph31/references_verified.json preserva alcance de acceso; no se afirma verificación exhaustiva de toda literatura.

## 13. Rúbricas y madurez

Escala1–5, autoevaluación provisional fundada en alcance, no evaluación externa por pares: novedad2 (conceptos conocidos), rigor4 (derivación/oráculo), reproducibilidad4 (pipeline/outputs, sin kernel aislado), código4 (API/tests), claridad4, impacto3 (diagnóstico útil, no datos reales), honestidad5, MVP4. Rúbrica adicional: profundidad teórica3, aporte defendible3, calidad experimental3 (diseño controlado sin datos reales), utilidad4, reproducibilidad4, honestidad5. No inflar originalidad por número de tests. Componente experimental ejecutado y revisado técnicamente dentro del alcance; no validado empíricamente, operacional ni elevación M2 del dominio. Publicación/CI/merge separados en informe consolidado31.

## 14. Siguiente iteración y decisión

Continuar si se obtiene adjudicación independiente con fecha/cobertura auditables. Ajustar si solo hay cobertura parcial, reportando abstención y cotas justificadas. Cerrar cualquier claim de independencia real sustentado únicamente por0 cortes observados. Ahora podemos distinguir fallo de identidad vs fallo de asignación y cuantificar exposición; antes solo validábamos consistencia del split contra el mismo grafo. Siguiente hito: contrato temporal en src/graph_audit.py y notebook con adjudicación fuera de muestra. Ver roadmap.md y research-log.md.

Checklist: README✓ src✓ tests✓ config✓ requirements✓ comando✓ CSV/JSON✓2figuras✓ notebookejecutado✓ fórmulas✓5refsverificadas✓ matrizpriorart✓ baselines/oráculo✓ negativos✓14p✓ rúbricas✓ madurezexplícita✓ researchlog/roadmap✓. Cobertura, validación empírica, frontend y kernel aislado no certificados. Publicación y revisión final constan aparte, no se confunden con mero archivo presente.

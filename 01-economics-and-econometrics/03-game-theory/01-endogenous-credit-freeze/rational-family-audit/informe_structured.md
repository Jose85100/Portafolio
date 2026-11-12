# Auditoría de regret con shocks compartidos — 5 de noviembre de 2026

1. **Título y programa.** Extensión acumulativa de `rational-family-audit`: cómo la estructura del error de pagos modifica un certificado de regret.
2. **Hipótesis y aporte.** H técnica predefinida: para `A_ij + θ_j`, `|θ_j|≤δ`, el regret de cualquier perfil mixto normalizado coincide con el nominal a precisión `1e-12` en los cuatro vértices del ejemplo 2×2. Clasificación: auditoría/adaptación de ingeniería; no fórmula original.
3. **Estado del arte.** Véase `prior_art_structured.md` y `references_structured.bib` (cinco fuentes). Aghassi–Bertsimas estudia teoría robusta más amplia; no equivale a este certificado local.
4. **Brecha.** El incremento anterior suponía errores independientes por celda; esa geometría puede sobreestimar sensibilidad cuando un error es común a acciones propias.
5. **Diseño/config.** `config_structured_uncertainty.json`: un juego 2×2 sintético, mezcla propia y rival, δ en {0,.05,.1,.2}, semilla declarada aunque el cálculo es determinista; CPU, Python 3.12 y versiones en `requirements.txt`.
6. **Implementación y derivación.** `src/uncertainty_structures.py` calcula `R=max(0,max_a Σ_j q_j[A_aj−Σ_i p_i A_ij])`. Con shock θ_j el coeficiente de θ_j es `q_j(1−Σ_i p_i)=0`; por eso `R_shared(δ)=R(0)`. Requiere probabilidades normalizadas, pagos finitos y shock idéntico por columna; el caso δ=0 recupera el nominal. No prueba equilibrio.
7. **Pruebas/benchmark.** `tests/test_uncertainty_structures.py` enumera cuatro esquinas de la caja estructurada y contrasta la caja independiente. `benchmarks/structured_uncertainty.py` guarda CSV/JSON/PNG. No se declara cobertura si no se midió para esta extensión.
8. **Resultados.** En el escenario diseñado, regret compartido = 0.112 para δ≤.2; la caja independiente crece de 0.112 a 0.392. Véase `results/structured_uncertainty/` para cifras exactas y figura.
9. **Análisis crítico y ablación negativa.** Cambiar la estructura rectangular a shock compartido elimina la penalización del error; esto muestra sensibilidad al conjunto de incertidumbre, no superioridad del modelo compartido. Si el shock depende de la acción propia, la cancelación desaparece.
10. **Límites/sesgos.** Un juego diseñado mediante parámetros supuestos, con identificación del mecanismo común pendiente; no inferir que shocks reales sean compartidos. No se mide desempeño fuera de muestra.
11. **Comando exacto.** Desde esta carpeta: `bash run_structured_uncertainty.sh`.
12. **Referencias.** `references_structured.bib` contiene BibTeX; matriz en `prior_art_structured.md`.
13. **Rúbrica original 1–5 (autoevaluación).** Novedad 2; rigor 3; reproducibilidad 3; código 3; claridad 3; impacto 2; honestidad 5; MVP 3.
14. **Siguiente iteración.** Extender a shocks de factor con cargas por acción y confrontar un conjunto empírico identificado.

Rúbrica ampliada 1–5: profundidad teórica 3, aporte defendible 2, calidad experimental 2, utilidad 3, reproducibilidad 3, honestidad 5. Madurez: prototipo local hasta revisión independiente y CI; el programa no se eleva automáticamente a S3/M2.

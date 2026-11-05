# CICLO_DIARIO de I+D+i — 5 de noviembre de 2026

## Estado de cierre

**Ciclo parcial; no se declara completo.** Se ejecutaron incrementos acumulativos en Matemáticas, IA, CEO/Estrategia y Economía. No hubo incremento nuevo de Riesgo. Los PR de dominio siguen abiertos y sin merge. Este informe se publica como checkpoint para conservar evidencia y pendientes.

Base revisada: main 5e0fb124462ed07b775b24a61226b1c9f51aca66, con el cierre del 4-nov. Se cotejaron arquitectura, README, estándares, contratos, resultados previos, cambios concurrentes y PR. Se asignaron coordinador, cinco autores de dominio y revisor independiente. El autor de Riesgo abortó antes de seleccionar o implementar; la revisión limpia independiente de Economía no pudo instalar pygambit por falta de clang++, aunque el análisis de código y la CI pasaron.

|Dominio|Implementado / ejecutado|Revisión / CI|PR y estado|
|---|---|---|---|
|Economía|Sí. Focal 3/3, reproducción integral, suite común 8/8; notebook 3 celdas y PNG real.|Revisión de fórmula/código/referencias sin bloqueantes; instalación limpia del revisor bloqueada. Head: 13 SUCCESS, un regression de notebooks omitido.|[#148](https://github.com/Jose85100/Portafolio/pull/148), listo, abierto, sin merge.|
|Matemáticas|Sí. 37 pruebas + 3 focales, Ruff/mypy, CMake/CTest, sanitizers y benchmark.|Revisión previa sin bloqueantes. En head, 13 SUCCESS y un notebook regression omitido.|[#144](https://github.com/Jose85100/Portafolio/pull/144), abierto, sin merge.|
|Riesgo|No hubo incremento nuevo ni ejecución de MVP de hoy.|Sin artefacto para revisión; agente terminó sin cambios.|Sin PR nuevo. Pendiente.|
|IA|Sí, parche de ingeniería en línea existente; 58 pruebas, Ruff/mypy y notebook 4 celdas.|Revisión previa sin bloqueantes; no se observaron runs/checks remotos para este head.|[#147](https://github.com/Jose85100/Portafolio/pull/147), abierto, sin merge.|
|CEO/Estrategia|Sí, sensibilidad EVSI: 11 pruebas, CSV/JSON/PNG y notebook 3 celdas.|Revisión independiente sin bloqueantes; Notebook Reliability y 2 suites de Strategy SUCCESS.|[#149](https://github.com/Jose85100/Portafolio/pull/149), abierto, sin merge.|

## Incrementos y las 14 dimensiones de revisión

### Economía — shocks comunes por estado rival

Línea: rational-family-audit. Alternativas: caja de errores independientes por pago (baseline ya existente); shock común por acción rival (seleccionado); shock con carga propia dependiente de acción (diferido por requerir especificación/identificación adicional). Para u_ij=A_ij+theta_j, el coeficiente de theta_j en la ganancia de desviación es q_j(1-sum_i p_i)=0 si p pertenece al simplex; el regret queda en el nominal. Hipótesis técnica predefinida: igualdad a tolerancia 1e-12 en los cuatro vértices del escenario 2x2. Resultado sintético: regret común 0.112 para delta 0,.05,.1,.2; caja independiente 0.112 a 0.392. Es adaptación/auditoría, no fórmula nueva ni evidencia de que el shock sea común en datos reales.

Pregunta y brecha: sensibilidad del certificado a la geometría de incertidumbre. Config fija el juego, delta, seed y versión. Implementación modular, tres tests focales y baseline/oráculo de vértices; 4 filas CSV, JSON, figura inspeccionada y notebook ejecutado que captura un PNG real. Reproducción: bash run_structured_uncertainty.sh; integración/reproducción: bash reproduce.sh. Informe crítico de 14 puntos: carpeta rational-family-audit/informe_structured.md; cinco referencias y matriz: references_structured.bib y prior_art_structured.md. Rúbrica autor original (novedad/rigor/reproducibilidad/código/claridad/impacto/honestidad/MVP): 2/3/3/3/3/2/5/3; ampliada: 3/2/2/3/3/5. Limitación: juego sintético, no identificación ni generalización. Madurez: candidato local S2; programa/dominio no promovido. CI head c2c42eeda90f62cd3ba83b081ddb1d926855d55c; PR abierto, listo, sin merge.

### Matemáticas — fusión balanceada de momentos

Línea streaming-moments. Alternativas: fold secuencial/inverso; acumulador exacto reproducible con mayor costo; árbol fijo balanceado Chan (seleccionado). Para resúmenes disjuntos: delta=muB-muA, mu=muA+delta*nB/n y Q=QA+QB+delta^2*nA*nB/n. No se modifica la identidad de Chan; se fija orden de cómputo.

Hipótesis: SD bajo max(4 ulp,1e-12 relativo) frente a oráculo Decimal en 3 semillas x 2 tamaños x 3 órdenes. Resultado: 18 escenarios; error SD máximo 5.20417e-18 y spread entre árboles 6.93889e-18. La hipótesis local pasó, pero no hubo mejora material ni invariancia a permutaciones. Código modular, tests, notebook ejecutado, CSV/JSON/figura y cinco referencias. Reproducción: MATH_ENV=.venv bash run.sh. Informe/14 puntos: quant-libraries/streaming-moments/informe_reduction.md; matriz y config en prior_art_reduction.md/config_reduction.json. Rúbrica original 1/3/4/3/4/2/5/3; ampliada 2/2/3/3/4/5. Datos sintéticos; sin escalabilidad amplia. CTest Release y ASan/UBSan pasaron. EL=83 no aplica al método de momentos. PR #144 abierto, no merge.

### Riesgo — incremento no entregado

Se revisó la historia de risk-engines, incluido weighted-tail-audit y PR #143 del ciclo previo; no se cuentan como trabajo de hoy. Se mencionó como posible extensión auditar atribución fraccionaria en átomos VaR, pero no se compararon tres candidatos, no hubo selección, código, tests, referencias nuevas, resultados, notebook/figura ni revisión. No se atribuyen resultados o madurez. Condición para cerrar: seleccionar una brecha no duplicada y entregar oráculo exacto, config, dependencias, referencias, ejecución y revisión en la ruta exclusiva risk-engines. No hay afirmaciones regulatorias.

### IA — no interferencia temporal

Línea mvp-linked-entity-holdout. Alternativas: validar payload antes de cutoff; filtrar available_at>as_of antes de validar (seleccionada por contraejemplo); migrar a ledger de eventos/deltas (diferida hasta contrato del productor). Hipótesis falsable: añadir una revisión posterior al corte, aunque tenga ID repetido y payload inválido, no debe cambiar el replay histórico. El test adversarial falla con el orden anterior y pasa con el filtrado previo.

Código tipado, 58 pruebas, Ruff/mypy, resultados sintéticos y notebook con 4 celdas. Reproducción: bash run_temporal_revisions.sh. Es un parche de auditoría/ingeniería a un MVP existente, no un MVP científico nuevo. El informe/matriz existente es informe_temporal1103.md y prior_art_temporal1103.md; el cambio del día no añade informe nuevo de 14 puntos ni bibliografía propia, requisito documental parcial. Sin validación de timestamps auténticos, producer contract o CI remota observada. Rúbricas del programa anterior: original 2/4/4/4/4/3/5/4; ampliada 3/3/4/3/4/5; no reevaluadas independientemente hoy. PR #147 abierto, sin merge.

### CEO/Estrategia — concentración del prior y valor de información

Línea pricing-pilot-evsi-gate. Alternativas: EVSI con utilidad CARA (falta calibrar preferencias); escalar concentración Beta preservando medias (seleccionada para probar sensibilidad a un prior subjetivo); costo de demora explícito (requiere contrato de costos). Para m=a/(a+b), kappa=a+b: a'=c*m y b'=c*(1-m). Se enumera EVSI Beta-Binomial en c={.25,.5,1,2,4,10,100}, 20 observaciones por brazo. Hipótesis específica al escenario: EVSI no creciente al concentrar el prior; no es teorema general.

EVSI cae de 9.524 a 2.214 al pasar c=.25 a c=1; con costo 1, EVSI neto base 1.214 y el gate cambia con mayor concentración. En c=100 se conserva y marca residuo -1.8461e-10 dentro de cota 5.5e-10, sin interpretarlo como valor negativo real. 11 pruebas, CSV/JSON/PNG y notebook ejecutado localmente; comando bash run.sh desde el proyecto. Cinco referencias en referencias.bib, matriz y análisis prior-sensitivity.md. El informe anterior aporta las restantes dimensiones; este incremento no es nueva fórmula ni recomendación de precio empírica. Rúbrica evaluada aquí: original 2/3/4/4/4/3/5/4; ampliada 3/2/4/3/4/5. Synthetic-only, no causalidad, repetición, capacidad ni clientes reales. PR #149 abierto, sin merge.

## Síntesis, integración y estado de publicación

Sabemos que la estructura de incertidumbre afecta bounds, un árbol fijo hace repetible la misma partición pero no permutaciones, las revisiones futuras deben ser invisibles antes de validar payloads, y el valor de un piloto depende de la concentración del prior. Se construyeron herramientas locales para calcular/contrastar esos mecanismos; permiten inspeccionar supuestos y contraejemplos con CSV, figuras y notebooks, no inferir comportamiento de clientes, mercado o cartera real.

Se creó un worktree temporal desde main y se integraron localmente, sin publicar ni fusionar PR, los cuatro branches de dominio. Los merges fueron limpios. En ese árbol pasaron el comando focal de Economía, los 37+3 tests y CMake/CTest/sanitizers de Matemáticas, las 58 pruebas de IA, los 11 tests/notebook de CEO y la suite común de Economía 8/8. El primer intento matemático falló porque el benchmark invoca .venv/bin/cmake relativo al checkout; se enlazó el entorno virtual provisionado al árbol integrado y se repitió el comando completo con éxito. La primera invocación de la suite común económica se hizo desde el subdirectorio del MVP y se corrigió ejecutándola desde la raíz del worktree. Ningún PR se fusionó; implementación, ejecución, revisión, CI y publicación por PR permanecen como estados separados. El ciclo es parcial por Riesgo y por la reproducción limpia local de Economía no alcanzada. La CI económica sí pasó en el head; el revisor independiente no pudo hacer la instalación limpia sin clang++.

## Siguiente iteración recomendada

1. Riesgo: comparar tres ideas y seleccionar una extensión no duplicada bajo 04-quant-strategy-and-products/risk-engines/weighted-tail-audit; entregar oráculo, benchmark y revisión antes de marcar completa.
2. Economía: repetir instalación limpia con toolchain C++ disponible y estudiar shock por factores/cargas de acción en 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/rational-family-audit.
3. IA: añadir addendum 14-puntos y obtener CI remota para mvp-linked-entity-holdout; confirmar semántica replacement/delta con el dueño de datos antes de uso real.

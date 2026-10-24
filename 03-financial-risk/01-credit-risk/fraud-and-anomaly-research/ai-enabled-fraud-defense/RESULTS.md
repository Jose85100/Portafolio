# Resultados del experimento acotado

Ejecución real en un proceso IPython nuevo, celdas en orden, salidas guardadas; 32 celdas, 14 de código, 171 líneas y tres figuras. No se usó kernel local por la restricción ZeroMQ del entorno; el workflow nuevo usa kernel nbclient. [Hash y métricas](evidence/execution.json), [QA y límites de inspección](evidence/qa.json).

## Dependencia de controles

| Cantidad | Resultado |
|---|---:|
| Escape marginal A / B, supuestos | 12% / 8% |
| Escape conjunto independiente, exacto | 0,96% |
| Escape conjunto con uniforme compartido, exacto | 8% |
| Cociente de extremos | 8,3333 |
| Ahorro por añadir B, independencia | 1.120,68 COP/solicitud |
| Ahorro por añadir B, fallo compartido | −287,32 COP/solicitud |
| Fracción compartida de equilibrio, escenario | 0,795939 |

Se simulan 200.000 ataques por escenario, con marginales fijas; las filas comparten números aleatorios. La fórmula se contrasta con el generador y las marginales. El modelo monetario supone prevalencia 1%, severidad 2 millones COP, detección que evita toda pérdida y precios/fricción inventados para sensibilidad. No es estimación de pérdida evitada en una institución ni evaluación de un proveedor.

## Indisponibilidad y capacidad

14.000 casos, 14 días, capacidad manual 150/día; tres días con 40% de fallos frente a 1% los demás.

| Ruta | Pico manual | Pico pendiente externo | Máxima edad pendiente al cierre (días) | Cerrados sin verificar | Llamadas totales |
|---|---:|---:|---:|---:|---:|
| Permitir error, contrafactual | 0 | 0 | 0 | 1.337 | 14.000 |
| Todo a revisión | 825 | 0 | 5 | 0 | 14.000 |
| Diferir y replay | 0 | 632 | 2 | 0 | 15.754 |

Los picos manual/externo son máximos de cada serie, no necesariamente del mismo día. La política de replay conserva pendientes; la manual todavía tiene backlog al final del horizonte. Los fallos diarios y las marcas de alerta son comunes entre políticas. No se modelan verdad de fraude, eficacia real de revisión, límite de reintentos/llamadas, costo de espera ni caída permanente. Por eso el cuadro describe estados operativos, no una política ganadora.

## Verificación realizada

Se comprueban conservación de casos por día y política, ausencia de duplicados y no exceder capacidad; identidades algebraicas y concordancia de marginales; incertidumbre Wilson marginal por escenario; límite binomial unilateral para cero escapes. Fuentes del notebook concuerdan con su generador. El generador de diagramas es determinista; se validaron XML, IDs, geometrías y referencias de las cuatro páginas. Cuatro vistas SVG y tres figuras fueron inspeccionadas. Lint de ambos generadores sin incidencias. No se atribuye una revisión independiente.

La inspección completa del frontend Jupyter/KaTeX y el round-trip gráfico en draw.io quedan pendientes. El archivo draw.io contiene formas nativas y conectores editables; las vistas SVG se produjeron con un renderer propio a partir de la misma geometría.

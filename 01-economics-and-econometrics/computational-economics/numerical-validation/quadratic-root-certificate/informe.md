# Informe crítico — Quadratic Root Certificate

## Pregunta, brecha e hipótesis

Los dos MVP de macrofinanzas calculaban raíces cuadráticas con `Decimal` y auditaban el residual después. Faltaba una envolvente exacta para la raíz escalar, en especial en pliegues donde no hay cambio de signo. La hipótesis previa fue: 100/100 polinomios construidos con raíces racionales quedarían encerrados; a 24 dígitos el ancho máximo sería ≤1e-24; y el pliegue `(q-0.5)^2` sería recuperado aunque una malla 0,01 no detectara cambios de signo.

## Método y alcance matemático

Para `a q²+b q+c=0`, coeficientes y discriminante permanecen como `Fraction`. `isqrt(floor(Delta*10^(2d)))` genera cotas racionales consecutivas para la raíz cuadrada; la fórmula cuadrática propaga las cotas atendiendo al signo de `2a`. Una discriminante nula devuelve la raíz racional exacta con multiplicidad dos. El verificador comprueba separación y signos con racionales.

Esto certifica raíces del **polinomio cuadrático**, no la corrección del régimen económico. `select_in_domain` sólo comprueba inclusión en un intervalo declarado: no verifica pagos, restricciones bancarias ni exhaustividad del censo.

## Resultados ejecutados

Con seed `20261021`, 100/100 casos con dos raíces racionales quedaron encerrados. El error máximo del punto medio frente a la fórmula flotante fue `1.432187701766452e-14`; no es error del certificado. A 24 dígitos, el mayor ancho del caso irracional fue `5e-25`. Las raíces 0,2 y 0,8 del caso de ventas forzadas son exactas; el pliegue 0,5 tiene multiplicidad dos. En los polinomios del clearing acoplado, la criba de dominio conserva 0,14440532323881 y 0,8255764119219942, y excluye las raíces algebraicas incompatibles.

La malla de 0,01 tuvo **0** cambios de signo en la raíz doble y el certificador produjo **1** raíz. Refuta ese baseline para multiplicidad par, no las mallas como exploración.

Para 10.000 cuadráticas, mediana de tres repeticiones: certificado `1.161026085 s` y pico Python `7,310,680 B`; fórmula flotante `0.044549139 s` y `1,285,280 B`. Las garantías difieren; no se afirma superioridad de velocidad. `tracemalloc` excluye RSS y memoria nativa.

## Tests, estabilidad y fallos

Ruff y mypy estricto pasan. Pasan 9 tests propios, incluidos 120 ejemplos Hypothesis, y 8 tests comunes. Cobertura: 100% del módulo `src/rootcert.py` y 99% combinada con tests; no corresponde al repo entero. El ancho observado cae de `5e-7` a `5e-31` entre 6 y 30 dígitos.

El primer intento de notebook falló porque el entorno impidió al kernel abrir su canal local. Se sustituyó por ejecución determinista en proceso que captura `stdout`, HTML y PNG; no se afirma que `nbclient` funcionara.

## Estado del arte y cobertura

El aislamiento exacto y el análisis intervalar son campos establecidos. Moore–Kearfott–Cloud presentan análisis intervalar; Sagraloff–Mehlhorn y Kobel–Rouillier–Sagraloff estudian métodos generales mucho más potentes. Este MVP de grado dos no compite con ellos. Cifuentes–Ferrucci–Shin, Feinstein y Bichuch–Feinstein motivan el vínculo con ventas forzadas, pero sus modelos son más amplios.

Se consultaron las fuentes solicitadas en arXiv, SSRN, NBER, CEPR, Semantic Scholar, Papers with Code y revistas objetivo. Se hallaron fuentes primarias pertinentes en arXiv, JSC, JEEA y SIAM; la cobertura no fue exhaustiva. No se encontró un benchmark idéntico en Semantic Scholar/Papers with Code; eso no significa que no exista.

## Supuestos, identificación y riesgos

- Datos sintéticos versionados; sin población, estimando ni licencia externa.
- No hay identificación ni inferencia causal.
- Una raíz polinómica no equivale a equilibrio económico o teorema global.
- Grado dos y racionalidad favorecen la exactitud; denominadores grandes elevan costo.
- Hardware y seed están en `metadata.json`; la memoria reportada es sólo Python.

## Madurez

Componente **S2**. `computational-economics` y programas consumidores permanecen **S2 parcial**, no S3: faltan certificación multivariada, desigualdades conjuntas, robustez externa y revisión independiente.

# Auditoría29: varianza estable fusionable

## 1. Título y decisión
Varianza de streams trasladados: conservar precisión sin almacenar el stream. Continuar como utilidad reusable; ajustar antes de uso con pesos/overflow. Cerrar cualquier afirmación de superioridad universal.

## 2. Hipótesis y novedad incremental
H: error absoluto<=1e-10 frente Decimal80 de entradasfloat, offsets0/1e8/1e12, n128/4096. Algoritmo clásico, sin prioridad mundial. Tres ideas comparadas: logsumexp streaming(se solapa con usosDRO/OT), intervalo de covarianza(solapa28 y requiere más validación), resumen fusionable(elegido, sin Welford implementado hallado por rg). Main022f6bd y aportes previos inspeccionados; PR28 ya integrado, sin recuperación27.

## 3. Estado del arte
Welford actualiza media/M2; Chan fusiona bloques; Pébay generaliza momentos; Higham contextualiza estabilidad; NumPy ofrece baseline de dos pasadas. Cinco referencias primarias verificadas29, detalles/BibTeX en fuentes.md y referencias.bib. Acceso a metadata no equivale a lectura integral de artículos/libros.

## 4. Brecha
Momentos crudos restan dos cantidades grandes. Una media no desplazada acumula redondeo cuando offset domina señal. Falta una auditoría reusable de particiones y representación en quant-libraries.

## 5. Diseño/configuración
config.json contiene n, offsets, seed20261029, umbral y oráculo. x=offset+(i mod4), varianza matemática original1.25. Decimal.from_float80 mide exactamente valores recibidos, no originales. Dos tamaños, cuatro offsets, cinco métodos=40filas. Datos deterministas, no evidencia empírica ni MonteCarlo. Hardware/versions en summary.json; dependencias directas fijadas.

## 6. Implementación e invariantes
src/moments.py mantiene(n,o,m,M2), o primer dato, m media de x-o. Welford: d=x-o-m; m'=m+d/n'; M2'=M2+d(x-o-m'). Merge: d=(ob-oa)+(mb-ma); M2=M2a+M2b+d²na nb/(na+nb). Deriva expandiendo suma de cuadrados alrededor de media conjunta; en reales conserva estadísticos, identidad vacía y asociatividad. Float no garantiza asociatividad exacta. Estado4escalares O(1), tiempoO(n), sin retener iterable. API acepta observaciones finitas; estados construidos manualmente no validados.

## 7. Tests/benchmarks reales
bash run.sh exit0:4tests,100fixtures pseudoaleatorios de80enteros con tres particiones y traslaciones, orden/unidades/identidad/constantes/NaN/inf/ddof. Cobertura núcleo35sentencias100% medida; no cobertura del repositorio. Ruff src/tests/notebook y mypy1módulo pasan. No C++: CMake/sanitizers no aplican. Benchmark bruto por método con llamada caliente, tiempo y tracemalloc; no ranking con una sola repetición.

## 8. Resultados
Máximo error para offsets<=1e12:

|Método|Error absoluto|
|---|---:|
|Momentos crudos|1.25|
|Welford ordinario|8.35408e-6|
|NumPy dos pasadas|0|
|Desplazado streaming|1.11022e-15|
|Desplazado merge127|2.22045e-16|

Hipótesis local pasa. CSV conserva40filas, ns y memoria Python por llamada; figura audit.png inspeccionada. Ejecución autor: streaming n4096/offset1e16 ~8.42ms,336bytes tracked extra(noRSS); hardware/contexto summary.json. Reproducciones regeneran tiempos. No coste monetario ni speedup inferido.

## 9. Análisis crítico/ablaciones negativas
Quitar desplazamiento produce error8.35e-6; quitar centrado y usar momentos crudos pierde toda varianza1.25. Baseline fuerte NumPy es exacto en fixtures representables y vence en error, por tanto no declarar desplazado superior. A1e16 datosfloat ya tienen varianza2.75: algoritmo devuelve2.75 cerca del oráculo pero error1.5 respecto intención1.25. No confundir error de algoritmo y de medición/representación. Ningún teorema de cota universal demostrado.

## 10. Límites/sesgos
Fixture pequeño periódico, una CPU, ordeneslimitados, Pythonfloat64, sin pesos, rollingwindows, datos faltantes ni aplicación financiera. Finito no impide overflow de diferencias/productos extremos; no certificación intervalar. ddof1 sólo corrección convencional, no prueba de inferencia iid. Memoria tracemalloc no capta toda memoria nativa NumPy, comparación sesgada si se interpretase comoRSS. No validación operacional.

## 11. Comando exacto
Desde `02-mathematics-statistics-and-quant/quant-libraries/streaming-moments`: `bash run.sh`. Instalación pip requiere red; entorno limpio crea .venv. Notebook ejecutado IPython in-process namespace nuevo, aborta errores; no kernelJupyter aislado verificado.

## 12. Referencias
Cinco entradas BibTeX reales en referencias.bib; metadata/abstract primarios verificados29 (403/redirect directo de algunos DOI resuelto por búsquedaeditorial). No referencias inventadas.

## 13. Rúbrica1–5
Autoevaluación, no score independiente: novedad2, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP5. Prototipo verificado acotado; sin equivalencia S2=M2 ni promoción madurez global.

## 14. Siguiente iteración
1tests de overflow y política explícita src/moments.py; 2múltiples órdenes/distribuciones en src/benchmark.py; 3protocolo de memoriaRSS y timing repetido en config.json/results. Revisión independiente y publicación separadas de implementación; PR registra evidencia real, sin merge automático.

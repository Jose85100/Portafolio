# MVP completo: ES Python con guard de underflow

## Extensión ejecutada 2026-10-16

Qué es: consumidor de ES con decisión racional cuando está disponible y JSON
sin pérdida del numerador/denominador. Mismo comando único run.sh. Produce
388 comparaciones (29 errores del consumidor float, 0 del contrato en umbral
cero), 112 mediciones nuevas, dos rechazos comprobados, notebook y 34 tests.
No cubre validación de payloads ajenos, transporte por red, incertidumbre
estadística, umbrales arbitrarios exactos en ruta rápida ni producción.
Detalle y límites en informe-consumidor.md. El apartado siguiente es histórico.

**Qué es:** nueva entrada ejecutable que protege el motor Python existente mediante detección de underflow, rechazo configurable y fallback con fracciones exactas. Los métodos son conocidos; la contribución es integración, contrato de salida y benchmark reproducible.

**Cómo corre:** `bash 03-financial-risk/02-market-and-model-risk/weighted-tail-underflow-guard/run.sh`, desde el repo completo; Python 3.12 y venv. Instala dependencias fijadas y ejecuta todo.

**Qué produce:** 21 tests con dos propiedades generativas, 388 resultados de precisión, 168 mediciones de rendimiento/memoria, CSV/JSON/SVG, notebook ejecutado, cobertura, lint/tipos, README/informe/BibTeX. Reutiliza los 207 inputs del aporte C++ y añade 181 casos. Rechaza fallbacks grandes por presupuesto explícito.

**Qué NO cubre:** detección universal de redondeo, precisión arbitraria del camino rápido, propagación de incertidumbre, backtesting temporal, calibración de pesos, portabilidad validada en todos los sistemas, capital regulatorio ni cambios a C++. Un ES racional puede no ser representable como float: se conserva y se declara el flag; no se promete fabricar representabilidad.

**Madurez:** prototipo numérico validado, no producción ni novedad teórica. No se publica directamente en main: se propone mediante PR con CI.

**Checklist:** src ejecutable; comando único; tests pasados; baseline numérico; outputs verificables; README/informe/referencias/MVP; ubicación correcta. Ver informe para métricas observadas y limitaciones.

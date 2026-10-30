# Metodología base e innovación para Quant Strategy & Products

Este marco convierte las 90 propuestas de las 18 áreas en investigaciones comparables, falsables y reproducibles. Está alineado con las puertas S0–S4 y el contrato mínimo de [RESEARCH_STANDARDS.md](../01-economics-and-econometrics/RESEARCH_STANDARDS.md). Una idea se considera una hipótesis de innovación, no una novedad demostrada, hasta contrastarla con literatura, productos existentes y benchmarks.

## Secuencia de investigación

### S0 — Pregunta y brecha
- Precisar decisión, población/mercado, horizonte y quién soporta costos o beneficios.
- Buscar trabajos previos y productos comparables; citar el punto de partida más cercano.
- Formular una hipótesis que pueda resultar falsa y separar mecanismo propuesto de resultado deseado.
- Nombrar baseline y métrica principal, además de al menos un guardrail.

### S1 — Formulación cuantitativa
- Definir variables, unidades, estimando/objetivo, restricciones, supuestos y mecanismos alternativos.
- Especificar identificación causal cuando se afirme impacto; para modelos predictivos, definir el momento real de disponibilidad de cada dato.
- Declarar condiciones de existencia, unicidad, convergencia o dominio de validez, según corresponda.
- Derivar qué observación refutaría la hipótesis.

### S2 — Prototipo comparable
- Implementar primero un baseline simple y reproducible, luego la extensión propuesta.
- Versionar fuentes, licencias, fechas de publicación y disponibilidad, transformaciones, semillas y parámetros.
- Usar datos sintéticos para probar invariantes y casos límite; nunca presentarlos como evidencia empírica.
- Fijar contratos de entrada/salida, unidades, tolerancias y benchmark.

### S3 — Validación, comparación y refutación
- Comparar baseline y propuesta en el mismo universo, ventanas, costos y restricciones.
- Validar temporalmente fuera de muestra cuando aplique; reportar incertidumbre, sensibilidad, subgrupos pertinentes y estabilidad por régimen.
- Ejecutar ablation para identificar qué componente produce el cambio; probar escenarios adversos y mecanismos alternativos.
- Aceptar aporte solo si mejora la métrica principal sin romper guardrails. Registrar resultados negativos y límites.

### S4 — Evidencia y revisión
- Generar tablas y gráficos desde código; incluir referencias, entorno, changelog y pasos de reproducción.
- Separar resultados empíricos, simulaciones, pruebas matemáticas y opinión.
- Solicitar revisión independiente de formulación, datos, implementación e interpretación.
- Declarar qué queda fuera de alcance y qué haría cambiar la conclusión.

## Qué cuenta como aporte innovador

Clasificar la contribución principal como **método**, **datos/medición**, **mecanismo económico**, **regla de decisión**, **producto/contrato**, **integración** o **benchmark/validación**. Explicar qué cambia respecto al trabajo previo, por qué podría mejorar y cuál es el costo o trade-off. No llamar innovación a aplicar una técnica conocida a otra base de datos sin explicar la nueva pregunta, adaptación, mecanismo o evidencia que aporta.

## Ficha obligatoria por idea

1. Problema, decisión y pregunta falsable.
2. Literatura y producto comparables; baseline cuantitativo.
3. Hipótesis del mecanismo y formulación matemática.
4. Datos y su disponibilidad en tiempo real; identificación y sesgos.
5. Aporte innovador esperado y diferencia verificable frente al baseline.
6. Métrica principal, guardrails y umbral de materialidad.
7. Plan de validación, escenarios, ablations y prueba que refutaría la idea.
8. Artefactos: nota teórica, notebook, módulo, pruebas, figuras y limitaciones según la etapa.

## Regla de avance

- **S0 → S1:** existe brecha concreta, referencia, baseline e hipótesis falsable.
- **S1 → S2:** formulación y datos permiten implementar sin fuga temporal ni ambigüedad de unidades.
- **S2 → S3:** baseline reproducible y comparación justa.
- **S3 → S4:** evidencia robusta, límites explícitos y revisión crítica.
- Si la propuesta no supera al baseline o no identifica un aporte incremental, se registra como resultado negativo, se rediseña o se cierra. No se fuerza una afirmación innovadora.

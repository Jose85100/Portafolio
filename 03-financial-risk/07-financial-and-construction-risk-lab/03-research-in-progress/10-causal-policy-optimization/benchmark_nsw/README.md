# Benchmark público: evaluación de políticas con NSW

El [archivo de datos de Dehejia y Wahba](https://users.nber.org/~rdehejia/data/.nswdata2.html) publica el subconjunto experimental NSW con ingresos previos y posteriores para 185 tratados y 260 controles. Tratamiento: programa de empleo; resultado: ingresos reales en 1978. El ejemplo compara reglas predeterminadas de asignación, escoge una en entrenamiento y estima su valor en un conjunto de prueba separado usando ponderación inversa por probabilidad de asignación. Usa la proporción de tratados del entrenamiento como aproximación a dicha probabilidad; no representa necesariamente el diseño completo por sitio o estrato.

```bash
python3 benchmark_nsw/run.py
```

Requiere Python 3, `curl` y acceso a internet. Descarga ambos archivos originales vía HTTPS, comprueba su SHA-256, tamaño y esquema; si la fuente cambia, falla para exigir revisión. La partición estratificada tiene semilla 42. La elegibilidad de la regla usa ingresos de 1975, previos al resultado. La salida es una ilustración de ingresos esperados bajo reglas simples, no incorpora costos del programa ni intervalos de confianza. La muestra es pequeña, la selección es inestable y no se debe interpretar el resultado como una recomendación de política; se requiere inferencia, análisis de sensibilidad, revisión de asignación y validación independiente.

La población, tratamiento y outcome son de empleo en EE. UU. en los años setenta. Este benchmark **no valida una política de mitigación de riesgos de construcción** ni sustituye datos institucionales de proyectos, elegibilidad, tratamientos y resultados. Su función es demostrar el flujo metodológico con datos observados.

# Fundamento III — Computacional y numérico: Valoración y contraparte

**Tipo:** fundamento; no proyecto.

## Métodos y algoritmos

Monte Carlo de exposición, pricing y sensibilidad numérica.

## Diseño de implementación

```text
cpp/include/     # kernels, tipos fuertes, validación de dominios
cpp/src/         # implementación determinista o simulación
cpp/tests/       # propiedades, extremos, precisión, sanitizers
python/src/      # calibración, econometría y orquestación
python/tests/    # referencia independiente y equivalencia con C++
sql/             # datos point-in-time, reconciliación y lineage
experiments/     # escenarios, seeds, benchmarking y convergencia
```

La estructura es un contrato objetivo; no se afirma que todos esos directorios o motores estén implementados.

## Requisitos numéricos

1. Semillas y configuración reproducibles; unidades y tolerancias explícitas.
2. Error Monte Carlo O(N^(−1/2)) para estimadores iid de varianza finita; no asumirlo bajo colas de varianza infinita.
3. Pruebas de estabilidad ante discretización, redondeo y parámetros extremos.
4. Análisis de complejidad temporal y espacial; benchmarks frente a un baseline.
5. Manejo de entradas inválidas y estados no finitos sin sustituciones silenciosas.
6. Validación independiente del motor C++ mediante referencia Python y tests de integración.
7. Trazabilidad de binario, código, parámetros, datos, versión y semilla.

## Conexión

Los [siete proyectos](../README.md) reutilizan esta base y deben añadir código propio, pruebas y resultados antes de declararse implementados.

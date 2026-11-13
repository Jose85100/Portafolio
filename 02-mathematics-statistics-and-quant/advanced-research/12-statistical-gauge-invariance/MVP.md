# MVP

## Qué es

Un certificado ejecutable de no identificabilidad por escala para el modelo gaussiano rango uno `Y = u vᵀ + ε`. Detecta la dirección nula de Fisher, verifica el generador gauge y construye un representante canónico balanceado.

## Cómo se corre

```bash
make run
```

## Qué produce

Tests y cobertura, resultados crudos CSV/JSON, comparación temporal contra diferencias finitas, diagnóstico de memoria, figura PNG, notebook ejecutado, informe regenerado y manifiesto de validación.

## Baselines

1. Jacobiano central por diferencias finitas frente al Jacobiano analítico.
2. Factores equivalentes sin fijar escala frente a la sección canónica balanceada.

## Qué no cubre

No descubre grupos de simetría desconocidos, no trata rango mayor, datos faltantes, priors bayesianos ni singularidades algebraicas generales. El experimento es sintético y completamente observado.

# Declaración de MVP

## Qué es

Una auditoría ejecutable de tres calibraciones del mismo estadístico `LR_ind` de Christoffersen para muestras VaR
cortas: chi-cuadrado, permutación condicional conservadora y permutación condicional aleatorizada.

## Cómo se corre

```bash
./run.sh
```

## Qué produce

Tests y cobertura; 4.000 trials crudos; tabla CSV de tamaño/potencia; JSON con configuración, versiones, hardware y
tiempo; figura PNG; notebook ejecutado. Todos los números publicados proceden de esos artefactos.

## Qué no cubre

Datos de mercado reales, estimación de VaR, solapamiento de horizontes, más de un rezago, severidad de pérdidas,
Expected Shortfall ni requerimientos jurídicos/regulatorios. La aleatorización resuelve calibración frecuentista,
no la conveniencia de una decisión de gobierno dependiente de RNG.

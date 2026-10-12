# Estándar de investigación para los 56 proyectos

## Estructura obligatoria por proyecto

1. Problema, decisión, población, horizonte, unidad y criterios de éxito.
2. Estado del arte y brecha verificable (fuentes y fecha).
3. Hipótesis falsable y baseline.
4. Espacio probabilístico, formulación, supuestos, propiedades y contraejemplos.
5. Modelo estadístico, estimando, identificación, sesgo, consistencia y eficiencia cuando aplique.
6. Algoritmo, complejidad, error numérico, estabilidad y convergencia.
7. Datos sintéticos con verdad conocida; datos públicos/autorizados con contrato y licencia.
8. Diseño de experimentos, validación temporal, robustez, estrés, sensibilidad y métricas.
9. Riesgos de modelo, limitaciones, uso permitido y restricciones regulatorias.
10. Entregables reproducibles y revisión independiente.

## Gates de madurez

- **S1:** protocolo y matemáticas documentados.
- **S2:** código C++/Python/SQL pertinente, tests e invariantes reproducibles.
- **S3:** resultados comparativos, incertidumbre, benchmarks y análisis de fallo.
- **S4:** validación externa e independiente con datos autorizados.
- **S5:** control de cambios, monitoreo, aprobaciones y operación gobernada.

## Criterios cuantitativos mínimos

Definir tolerancias antes de experimentar; reportar error absoluto/relativo, intervalo de confianza, sesgo, RMSE, cobertura, tiempo, memoria y robustez según corresponda. No imponer métricas predictivas a proyectos de gobierno o control sin target observable.

## Checklist de reproducibilidad

Versionar datasets o generadores, dependencias, semilla, hardware relevante, configuración, commit y script de reproducción. Distinguir evidencia empírica, simulación y demostración formal.

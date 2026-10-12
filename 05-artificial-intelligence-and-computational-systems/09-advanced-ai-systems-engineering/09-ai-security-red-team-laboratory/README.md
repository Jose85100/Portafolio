# AI Security & Red-Team Laboratory

**Madurez:** S1 — especificación técnica; no atribuir capacidades ejecutables salvo archivos de código explícitos. **Ruta:** `09-advanced-ai-systems-engineering/09-ai-security-red-team-laboratory`.

## 1. Objetivo e hipótesis falsable

Desarrollar banco defensivo de pruebas contra prompt injection, exfiltración, abuso de herramientas y manipulación de recuperación.

**Hipótesis:** el sistema supera un baseline explícito en al menos una métrica de calidad/eficiencia sin empeorar restricciones de seguridad, costo o confiabilidad. Establecer umbrales ex ante.

## 2. Formulación matemática y algoritmos

Risk=Σ_i P(threat_i|controls)×impact_i; min_def max_attack E[loss] con restricciones de permisos.

**Trabajo formal pendiente:** declarar variables, dominios, distribuciones, restricciones, condiciones de existencia, sesgos y contraejemplos; derivar gradientes, convergencia o cotas de error según algoritmo. No presentar fórmulas esquemáticas como teoremas probados.

## 3. Estadística y diseño experimental

Tasas de ataque con IC, cobertura de escenarios, falsas alarmas y robustez a cambios de distribución.

Experimentos con baseline, partición sin leakage, seeds, intervalos, análisis de potencia cuando proceda, ablations, stress, regresiones de rendimiento y reporte de costos.

## 4. Arquitectura de ingeniería

Python harness aislado, políticas de herramientas, C++ parsers opcionales.

Arquitectura objetivo por proyecto: `cpp/`, `python/`, `configs/`, `tests/`, `benchmarks/`, `security/`, `docs/`. Separar interfaces, implementación, evaluación y artefactos; no introducir secretos ni datos sensibles.

## 5. Métricas y criterios de aceptación

attack success rate, containment rate, leakage rate, false blocks.

Para promoción a S2 exigir código ejecutable, pruebas unitarias, CI y baseline; a S3 exigir benchmark reproducible, pruebas de seguridad y evaluación independiente. Incluir error bars y limitaciones de hardware.

## 6. Entregables

D1 especificación; D2 modelo matemático y contratos; D3 implementación; D4 tests/benchmarks; D5 evaluación de seguridad; D6 documentación operativa y demo reproducible. D3–D6 pendientes salvo evidencia explícita.

[Estándar transversal](../00-foundations/README.md).

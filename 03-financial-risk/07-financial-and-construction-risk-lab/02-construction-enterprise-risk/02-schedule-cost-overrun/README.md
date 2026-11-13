# Riesgo de cronograma y sobrecostos

**Área:** 02 construction enterprise risk  
**Estado:** diseño cuantitativo / investigación en construcción, con companion observacional CEED para contexto sectorial. El dato agregado no calibra atraso contractual ni sobrecosto de proyectos.

## Evidencia pública complementaria

[Proxy CEED de área paralizada/inactiva](observed-ceed-stage-pipeline/README.md): serie trimestral DANE 2015-T4–2026-T2 para apartamentos y casas, agregada a la cobertura de 57 municipios. La proporción de área paralizada/inactiva sobre área total censada ayuda a observar la composición sectorial de obras, no mide atraso, incumplimiento, pérdida ni desempeño individual. Incluye snapshot, hash, runner, informe y figura.

Como contexto administrativo más amplio, el [conteo SECOP II de registros de suspensión/reanudación](observed-secop-work-suspensions/README.md) presenta filas reportadas por año de aprobación para todos los tipos de contrato públicos. La fuente no se filtró a obra y tiene duplicados; no se interpreta como frecuencia, duración de retraso ni outcome de construcción.

## Problema y objetivo
Red de precedencias CPM/PERT y simulación de duración/costos; probabilidad de entrega tardía. El resultado debe expresarse como distribución de pérdidas, probabilidad de incumplimiento de umbrales o decisión sujeta a límites de riesgo, no solo como un indicador descriptivo.

## Formulación matemática
```text
T_project = max_paths sum_i Duration_i; Cost = sum_i Cost_i
```
Los parámetros deben estimarse con datos fechados, unidades consistentes y ventanas sin fuga de información futura. Las correlaciones entre choques deben modelarse y someterse a estrés.

## Datos y metodología
Fuentes candidatas: presupuestos y actas de obra, ERP contable, cronogramas, contratos, preventas y desistimientos, curvas de tasas, índices de costos de construcción y estadísticas públicas. Separar claramente datos observados, supuestos y escenarios sintéticos. Evaluar alternativas paramétricas, empíricas y bayesianas según el tamaño de muestra.

## Validación y límites
Validación con obras históricas, dependencias, sesgo optimista y colas. Evaluar incertidumbre paramétrica, estabilidad temporal, riesgo de modelo y sensibilidad a valores extremos. No usar en decisiones reales sin validación independiente, controles de calidad y aprobación de gobierno.

## Entregables previstos
Dataset versionado, diccionario de variables, metodología reproducible, motor Python, tests unitarios, validación out-of-time, escenarios y reporte ejecutivo con límites.

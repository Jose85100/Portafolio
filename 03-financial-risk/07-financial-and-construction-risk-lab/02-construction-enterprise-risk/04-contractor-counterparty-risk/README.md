# Riesgo de contratistas y proveedores

**Área:** 02 construction enterprise risk  
**Estado:** diseño cuantitativo / investigación en construcción.

## Problema y objetivo
Score de contraparte y contagio por dependencia de proveedores críticos. El resultado debe expresarse como distribución de pérdidas, probabilidad de incumplimiento de umbrales o decisión sujeta a límites de riesgo, no solo como un indicador descriptivo.

## Formulación matemática
```text
EL = PD * LGD * EAD
```
Los parámetros deben estimarse con datos fechados, unidades consistentes y ventanas sin fuga de información futura. Las correlaciones entre choques deben modelarse y someterse a estrés.

## Datos y metodología
Fuentes candidatas: presupuestos y actas de obra, ERP contable, cronogramas, contratos, preventas y desistimientos, curvas de tasas, índices de costos de construcción y estadísticas públicas. Separar claramente datos observados, supuestos y escenarios sintéticos. Evaluar alternativas paramétricas, empíricas y bayesianas según el tamaño de muestra.

### Aplicación descriptiva con SECOP II

El [companion de extensiones de contratos de obra SECOP II](observed-secop-works-extension-proxy/README.md) resume, por año de firma, los contratos con días adicionados positivos reportados. El indicador describe el estado administrativo de la ficha en el corte de consulta; no identifica retraso frente al cronograma, incumplimiento, default, pérdida o calidad del contratista. No se descargaron identificadores de proveedor. El diseño de score de contraparte sigue pendiente de datos enlazados de hitos, cambios, entregas, sanciones/pagos y pérdidas autorizadas.

El [perfil financiero sectorial Supersociedades](observed-supersociedades-corporate-financial-proxy/README.md) agrega balances publicados de la muestra anual de las 10.000 empresas más grandes (2021–2025). Aporta contexto de apalancamiento contable por macrosector; no identifica contratistas, sigue una cohorte fija ni mide incumplimiento. Tampoco se emparejó con SECOP.

## Validación y límites
Calibración, estabilidad, concentración, fallos simultáneos. Evaluar incertidumbre paramétrica, estabilidad temporal, riesgo de modelo y sensibilidad a valores extremos. No usar en decisiones reales sin validación independiente, controles de calidad y aprobación de gobierno.

## Entregables previstos
Dataset versionado, diccionario de variables, metodología reproducible, motor Python, tests unitarios, validación out-of-time, escenarios y reporte ejecutivo con límites.

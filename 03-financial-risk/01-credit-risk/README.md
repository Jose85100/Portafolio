# Riesgo de crédito

Modelos y análisis para originación, seguimiento y gestión de cartera. Todo el material ejecutable usa datos sintéticos con semilla fija y es ilustrativo; no contiene datos de clientes ni constituye una política de crédito productiva.

> **Límite de uso.** Este directorio es un portafolio técnico y una arquitectura de referencia. No acepta PII, decisiones de crédito, ni datos de producción. Las interfaces, DDL y ejemplos describen controles que una implementación institucional debe completar con seguridad, validación independiente y aprobación de gobierno.

## Áreas

- [Productos de crédito](credit-risk-products/): scorecard, pérdida esperada, roll rates, cosechas, segmentación e investigación IFRS 9.
- [Fraude y anomalías](fraud-and-anomaly-research/): cuatro diseños S1 de KYC, redes temporales, ingresos/documentos y proceso de originación; pendientes de implementación y validación.
- [Estrategia de cartera](credit-portfolio-strategy/): concentración, cópula de pérdidas, capital, límites de apetito y Vasicek.

## Plataforma transversal

| Capa | Propósito | Artefacto |
|---|---|---|
| Arquitectura | Linaje reproducible de datos sintéticos a métricas | [arquitectura y flujos](architecture/README.md) |
| Datos | Modelo relacional PostgreSQL, calidad y auditoría | [documentación](database/README.md) · [DDL](database/001_credit_risk_schema.sql) |
| Contratos | Esquemas de entrada/salida para Python, SQL y motores | [contratos versionados](contracts/README.md) |
| C++ | Interfaces tipadas, sin conectividad ni datos reales | [cabecera de dominio](cpp/include/credit_risk/contracts.hpp) |
| Notebooks | Convención de análisis reproducible y separación de ambientes | [guía](notebooks/README.md) |

La ecuación base para una exposición individual es \(EL_i = PD_i \times LGD_i \times EAD_i\); a nivel de cartera, \(EL = \sum_i EL_i\). Cualquier extensión a ECL, capital económico o decisiones debe declarar horizonte, escenario, versión de modelo y población aplicable.

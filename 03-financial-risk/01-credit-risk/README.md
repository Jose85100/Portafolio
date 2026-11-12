# Riesgo de crédito

Modelos y análisis para originación, seguimiento y gestión de cartera. El material ejecutable combina laboratorios controlados y algunas aplicaciones con datos agregados oficiales: mora ICETEX para seguimiento de cartera educativa y concentración entre acreedores SFC por producto. No contiene datos de clientes; los agregados públicos no validan PD individual, pérdidas esperadas ni políticas de crédito productivas.

> **Límite de uso.** Este directorio es un portafolio técnico y una arquitectura de referencia. No acepta PII, decisiones de crédito, ni datos de producción. Las interfaces, DDL y ejemplos describen controles que una implementación institucional debe completar con seguridad, validación independiente y aprobación de gobierno.

## Áreas

- [Productos de crédito](credit-risk-products/): scorecard, pérdida esperada, roll rates, cosechas, segmentación e investigación IFRS 9.
- [Fraude y anomalías](fraud-and-anomaly-research/): cuatro especialistas S1 de KYC, redes, ingresos y proceso, más un motor S2 acotado de comparación sintética y asignación por pérdida bajo capacidad.
- [Estrategia de cartera](credit-portfolio-strategy/): concentración, cópula de pérdidas, capital, límites de apetito y Vasicek.

## Plataforma y ciclo de crédito

Los componentes compartidos están reunidos en [plataforma de riesgo de crédito](credit-risk-platform/): arquitectura, contratos, base de datos, interfaces y convenciones de notebooks.

### Ciclo completo de crédito: arquitecturas y datos

[Mapa ampliado](credit-risk-platform/architecture/credit-lifecycle/README.md): nueve diagramas draw.io nuevos (tres alternativas de plataforma y seis vistas de proceso/datos), 15 responsabilidades, ocho flujos operativos, 35 señales y 24 proveedores candidatos. Incluye IP, geolocalización, dispositivo y sus límites; formalización, desembolso, LMS, seguimiento, cobranza y gobierno. Es diseño S1, complementario de las cuatro vistas defensivas previas de fraude; no integra datos ni proveedores reales.

## Plataforma transversal

| Capa | Propósito | Artefacto |
|---|---|---|
| Arquitectura | Linaje reproducible de datos sintéticos a métricas | [arquitectura y flujos](credit-risk-platform/architecture/README.md) |
| Datos | Modelo relacional PostgreSQL, calidad y auditoría | [documentación](credit-risk-platform/database/README.md) · [DDL](credit-risk-platform/database/001_credit_risk_schema.sql) |
| Contratos | Esquemas de entrada/salida para Python, SQL y motores | [contratos versionados](credit-risk-platform/contracts/README.md) |
| C++ | Interfaces tipadas y escenarios de prueba controlados; conectividad como etapa posterior | [cabecera de dominio](credit-risk-platform/cpp/include/credit_risk/contracts.hpp) |
| Notebooks | Convención de análisis reproducible y separación de ambientes | [guía](credit-risk-platform/notebooks/README.md) |

La ecuación base para una exposición individual es \(EL_i = PD_i \times LGD_i \times EAD_i\); a nivel de cartera, \(EL = \sum_i EL_i\). Cualquier extensión a ECL, capital económico o decisiones debe declarar horizonte, escenario, versión de modelo y población aplicable.

## Programa de proyectos y capas defensivas

[Diez proyectos](credit-risk-platform/architecture/credit-lifecycle/projects/README.md) estructuran 30 ideas con contratos sintéticos y 40 escenarios adversariales propuestos. [Ocho capas adicionales](credit-risk-platform/architecture/credit-lifecycle/defense-layers/README.md) incorporan integridad de evidencia, inteligencia de fraude, evaluación adversarial, protección frente a sondeo, controles humanos, coordinación, vigilancia y respuesta. Hay cuatro overlays draw.io nuevos; todas estas formulaciones conservan S1, sin pentest o vulnerabilidad real confirmados.

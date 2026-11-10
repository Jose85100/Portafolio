# Sistemas regulatorios y motores de riesgo

Fundamentos, arquitectura y motores de investigación conectados con el portafolio existente. Fecha de revisión: 2026-11-10.

## Catálogo

| Carpeta | Alcance | Estado |
|---|---|---|
| [SIAR, SARE y conglomerados](01-siar-sare-mgr/) | Inventario de riesgos materiales y perímetro de consolidación | S1: diseño |
| [SARC y riesgo de crédito](02-sarc-credit/) | Originación, seguimiento, deterioro y recuperación | S1: diseño |
| [SARM y riesgo de mercado](03-sarm-market/) | Factores, posiciones y pérdidas bajo escenarios | S1: diseño |
| [SARL y riesgo de liquidez](04-sarl-liquidity/) | Flujos, activos líquidos, fondeo y contingencia | S1: diseño |
| [SARO y riesgo operacional](05-saro-operational/) | Eventos, causas, controles y pérdidas | S1: diseño |
| [IFRS 9 y conciliación contable](06-ifrs9-accounting/) | Deterioro, staging y conciliación; clasificación y cobertura en agenda separada | S1: diseño |
| [SARAS y riesgo ambiental, social y climático](07-saras-climate/) | Debida diligencia y transmisión financiera de riesgos ASG | S1: diseño |
| [Capital, RWA, ICAAP e ILAAP](08-capital-rwa-icaap-ilaap/) | Solvencia y autoevaluación integrada | S1: diseño |
| [SARLAFT y delitos financieros](09-sarlaft-financial-crime/) | Debida diligencia, alertas y análisis humano | S1: diseño |
| [BCP, ciberseguridad y terceros](10-bcp-cyber-third-party/) | Servicios críticos, recuperación y concentración tecnológica | S1: diseño |
| [ISO 31000, COSO ERM, KRIs y modelos](11-erm-kri-model-governance/) | Gobierno, apetito, validación y escalamiento | S1: diseño |
| [Conducta, datos y reporte regulatorio](12-conduct-data-reporting/) | SAC, calidad, privacidad y trazabilidad de reportes | S1: diseño |

Los dominios son diseños S1; seis funciones numéricas transversales tienen pruebas locales acotadas. No hay certificación regulatoria, integración productiva ni validación empírica. No se eleva la madurez de los proyectos enlazados.

## Navegación

- [Fundamentos](00-foundations/README.md): convenciones y distinciones contables/prudenciales.
- [Arquitectura](00-architecture/README.md): datos, reglas versionadas, cálculo y evidencia.
- [Fuentes y aplicabilidad](SOURCES.md): Colombia SFC, referencias internacionales y transiciones.
- [Motores](engines/README.md): seis funciones Python sin dependencias externas.
- [Agenda de implementación](ROADMAP.md): etapas, aceptación y extensiones multilenguaje.

SARC, SARM, SARL y SARO se conservan como nombres de dominios y referencias históricas; su correspondencia jurídica debe consultarse en la estructura SIAR/CBF vigente y por tipo de entidad. No trasladar automáticamente normas SFC a Supersolidaria, ni SREP europeo a Colombia.

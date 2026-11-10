# Finanzas corporativas, FP&A y decisiones de inversión

Dos preguntas guían esta colección: ¿qué análisis se construyó?, y ¿qué decisión apoyó y bajo qué responsabilidad? Las seis carpetas siguientes son especificaciones S1, conectadas con prototipos existentes. No son seis motores implementados.

| Carpeta | Decisión |
|---|---|
| [Presupuesto y proyecciones](01-budget-forecast/) | Qué gastos y contrataciones financiar, cuándo crecer y cuánto capital se necesita. |
| [Flujo de caja y tesorería](02-cash-treasury/) | Orden de pagos, reserva de caja y fecha de contratación de fondeo. |
| [Fondeo y estructura de capital](03-funding-capital-structure/) | Monto, instrumento, plazo y oportunidad del fondeo. |
| [Valoración DCF y múltiplos](04-dcf-multiples/) | Rango de negociación o selección de inversión con incertidumbre. |
| [M&A y evaluación de inversiones](05-ma-investment/) | Comprar, esperar, negociar precio o rechazar; identificar condiciones que cambian la decisión. |
| [Asignación de capital y portafolios](06-capital-allocation-portfolios/) | Qué proyectos financiar, cuánto asignar y qué inversiones posponer. |

## Evidencia existente y brechas

| Competencia | Evidencia relacionada | Límite y desarrollo pendiente |
|---|---|---|
| Presupuesto | [Priorización de inversión](../04-data-investment-prioritization/) y [planeación](../11-corporate-strategic-planning/) | No equivale a presupuesto operativo integrado |
| Proyecciones y caja | [Resiliencia](../05-strategic-resilience-stress-testing/) y [recuperación](../10-crisis-management-recovery-planning/) | Prototipos sintéticos; falta integrar forecast de tres estados |
| Fondeo y estructura de capital | [Balance y capital](../12-balance-sheet-capital-management/) y [cap table](../venture-capital/cap-table-rondas-dilucion/) | Falta unificar deuda, costo efectivo y dilución |
| Asignación de capital | [ROIC](../06-enterprise-capital-allocation-roic/) y [opciones reales](../01-capital-allocation-real-options/) | Evidencia de prototipo; requiere datos empresariales |
| DCF | [Valoración por escenarios](../venture-capital/valoracion-dcf-por-escenarios/) | Sintético; el múltiplo terminal no acredita análisis completo de comparables |
| Múltiplos | [Nuevo diseño](04-dcf-multiples/) | Comparables reales, selección y normalización pendientes |
| M&A | [Sinergias](../14-ma-strategic-synergies/) | No equivale a transacción ejecutada ni merger model completo |
| Portafolios | [Venture](../03-venture-portfolio-construction/) y [asset management](../../04-quant-strategy-and-products/asset-management/) | Distinguir proyectos, venture y activos financieros |

## Cómo documentar experiencia real

Usar [CASE_TEMPLATE.md](CASE_TEMPLATE.md) con evidencia verificable. No redactar respuestas autobiográficas ni afirmar decisiones reales sin respaldo. Los presupuestos de iniciativas privadas deben incorporarse solo después de validar contenido y confidencialidad; no publicar automáticamente datos internos.

## Entregables objetivo

Modelo integrado de resultados/balance/caja, forecast de 36 meses, tesorería de 13 semanas, alternativas de fondeo, DCF/comparables y memo de inversión. Python para referencia, SQL para extracción y hoja de cálculo para revisión; ninguna de esas integraciones se afirma construida aquí.

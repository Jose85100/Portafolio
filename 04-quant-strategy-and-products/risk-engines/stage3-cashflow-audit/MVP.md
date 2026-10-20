# Alcance ejecutado

Qué es: API C++17 separada de cash shortfall Stage 3 y benchmark de paridad con
el núcleo Python existente y oráculo Decimal100. Novedad de integración y tests,
no matemática nueva ni implementación completa de IFRS 9.

Cómo correr: desde raíz del repo,
`bash 04-quant-strategy-and-products/risk-engines/stage3-cashflow-audit/run.sh`.
Prerequisitos y dependencias fijadas en README/requirements.

Produce: ejecutable CLI, 3023 comprobaciones unitarias/generativas, 288 fixtures
reconciliadas, 42 muestras de rendimiento, cobertura, logs de sanitizers/lint,
CSV/JSON y figura PNG/SVG. CMakeLists y src C++ satisfacen la alternativa al
notebook: el Python auxiliar sólo genera oráculos, mediciones y visualización.

NO cubre: stage/SICR, POCI, tasas negativas, surplus, escenarios probabilísticos,
curas, calibración real, provisiones SFC, contabilidad de intereses ni producción.
No se afirma cobertura integral, exactitud universal o mejora predictiva.

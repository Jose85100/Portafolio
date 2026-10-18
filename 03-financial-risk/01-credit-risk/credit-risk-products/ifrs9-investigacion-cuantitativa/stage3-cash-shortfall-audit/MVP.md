# MVP completo — Stage3 cash-shortfall audit

Qué es: modelo vectorizado de cash shortfall para activos ya deteriorados no
POCI y auditoría del motor IFRS9 existente. Cómo corre: comando completo en
README, o bash run.sh desde esta carpeta. Instala dependencias y ejecuta todo.

Produce:21 tests aprobados,432 comparaciones contra baseline real y referencia
Decimal,56 mediciones crudas, figuraPNG/SVG, notebook con outputs, cobertura,
lint/tipos, documentación y siete referenciasBibTeX.

NO cubre: estimación estadística de recuperaciones, clasificación Stage3, POCI,
curas, write-off, contabilización, SFC ni motor de provisiones aprobado.
La comparación sólo prueba inconsistencia del baseline bajo inputs/supuestos
declarados. No afirma que todos los usos de PD×LGD×EAD sean incorrectos.

Checklist: [x]src real; [x]comando único; [x]tests pasan; [x]baseline numérico;
[x]CSV/JSON/figura; [x]README/informe/referencias/MVP; [x]carpeta03-financial-risk.
Resultados de CI/publicación se consultan en PR, no se presuponen aquí.

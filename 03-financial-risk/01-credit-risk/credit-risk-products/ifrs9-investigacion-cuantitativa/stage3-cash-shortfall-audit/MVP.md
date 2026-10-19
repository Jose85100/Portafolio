# MVP completo — Stage3 cash-shortfall audit

## Extensión 2026-10-19: migración verificable

Qué es: baseline congelado con hash, reconciliación por contrato y estabilidad
integrada al motor actual. Mismo comando único. Produce 432 verificaciones Stage3,
300 reconciliaciones mixtas, 63 mediciones nuevas, figuras y notebook ejecutado.
Pasan 32 tests locales y 21 del padre. Fallo previo guardado, no ocultado.
No certifica IFRS9, equivalencia fuera del dominio compartido, estimación de
recuperaciones ni error predictivo. Detalle en informe-migracion.md.
La descripción siguiente es histórica; el motor padre ahora sí está migrado.

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

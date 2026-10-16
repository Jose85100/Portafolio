# MVP: factibilidad antes de interpretar el costo de transporte

**Estado:** S2 acotado del programa 09, no validación S3/S4.

**Qué es:** kernels de transporte balanceado finito, Sinkhorn directo/logarítmico,
reparación de marginales y cotas numéricas primal-dual. Baselines: LP HiGHS y
acoplamiento monótono ponderado 1D. Incluye un contraejemplo ejecutable.

**Cómo corre:** `make run` en esta carpeta. Python 3.11+, make e internet para pip.
Instala dependencias, ejecuta Ruff/mypy/tests, benchmark, notebook e informe.

**Qué produce:** CSV crudos/resumen/referencias; datasets.json; matrices NPZ del
contraejemplo; results.json; figura PNG; pruebas/cobertura; notebook ejecutado;
informe crítico y cinco referencias BibTeX verificadas.

**Qué NO cubre:** Sinkhorn divergences debiased, unbalanced OT, JKO, trayectorias
individuales, causalidad, epsilon-scaling, GPU, operadores gigantes o validación
económica externa. Las cotas son chequeos float64, no certificación con aritmética
de intervalos. No se modifica el contrato EL=83 de quant-libraries.

# Contrato MVP

- **Qué es:** exportador estratégico racional y auditor ejecutado con Nashpy externo para
  el juego bayesiano finito existente. Novedad incremental de integración y falsación,
  no prioridad científica del método.
- **Cómo corre:** `bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/strategic-form-audit/reproduce.sh`
  desde la raíz; entorno y Python 3.12 documentados en README.
- **Qué produce:** tests/cobertura, CSV/JSON/NFG, figura, notebook ejecutado y logs;
  comparación numérica con baseline poliédrico y controles negativos.
- **Qué NO cubre:** Gambit ejecutado, parser NFG general, completitud externa degenerada,
  juegos con más tipos, datos reales, identificación o juego global continuo.
- **Madurez:** componente exportación/auditoría S2; programa S2 parcial; componentes
  continuo/empírico S1. No se asciende a S3 por pasar este benchmark.

Checklist: [x] src real; [x] comando único; [x] test pasa; [x] baseline numérico;
[x] salida guardada; [x] README/informe/referencias/MVP; [x] carpeta 03-game-theory;
[x] madurez explícita. Estado de ejecución y cifras: informe.md y results/.

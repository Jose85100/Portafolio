# MVP — Rational Family Audit

- **Qué es:** auditor ejecutado del parser y solver racional Gambit16.4.1, con
  reconstrucción local exacta de familias del juego bayesiano finito existente.
- **Cómo corre:** desde raíz,
  `bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/rational-family-audit/reproduce.sh`.
  Python3.12 y toolchain GNU; instalación y requisitos en README.
- **Qué produce:** 61 tests pasando, cobertura medida del nuevo src, lint/types,
  CSV/JSON/NFG crudos, figura y notebook ejecutado, referencias y análisis crítico.
- **Qué NO cubre:** solver genérico/escalable, lrs/CLI-c ejecutado, validación empírica,
  estimación causal/estructural o juego continuo; memoria C++/RSS no medida.
- **Madurez:** componente S2, programa Endogenous Credit Freeze S2 parcial; modelo
  global continuo e identificación empírica S1. No ascenso a S3.

Checklist verificado: [x] código src; [x] comando único; [x] tests pasan;
[x] baseline numérico; [x] salidas guardadas; [x] README/informe/referencias/MVP;
[x] carpeta correcta03-game-theory; [x] madurez declarada. Cifras y límites: informe.md.

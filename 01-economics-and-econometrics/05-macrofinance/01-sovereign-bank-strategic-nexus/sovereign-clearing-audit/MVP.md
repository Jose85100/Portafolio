# MVP — Sovereign Clearing Audit

- **Qué es:** componente estático del nexus soberano-bancario, con solver modular,
  dos cotas numéricas, LP, Fraction, reconciliación de recursos y controles negativos.
- **Cómo corre:** desde raíz,
  `bash 01-economics-and-econometrics/05-macrofinance/01-sovereign-bank-strategic-nexus/sovereign-clearing-audit/reproduce.sh`.
  Python3.12/venv y entorno documentado en README.
- **Qué produce:**18 tests pasando, lint/types, cobertura medida, CSV/JSON/figura,
  notebook ejecutado con ecuaciones/cálculos, referencias y análisis crítico.
- **Qué NO cubre:** doom loop dinámico, datos reales, causalidad, colateral, precios
  endógenos, garantías, intervalos con redondeo dirigido o un solver eficiente para
  redes casi cerradas; éstas pueden rechazarse por presupuesto explícito.
- **Madurez:** componente estático S1→S2; programa Sovereign–Bank Strategic Nexus S2
  parcial, resto dinámico/empírico S1. No validación S3 ni publicación S4.

Checklist: [x] src ejecutable; [x] comando único; [x] tests pasan;
[x] baseline con números; [x] salidas guardadas; [x] README/informe/referencias/MVP;
[x] subcarpeta05-macrofinance correcta; [x] madurez declarada. Ver informe para límites.

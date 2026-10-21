# Contrato del MVP

## Qué es

Un certificador exacto y acotado para raíces reales de polinomios cuadráticos con coeficientes racionales. Devuelve intervalos racionales disjuntos y multiplicidad de raíces dobles.

## Cómo se corre

`bash 01-economics-and-econometrics/computational-economics/numerical-validation/quadratic-root-certificate/reproduce.sh`

## Qué produce

`certificates.csv`, `validation.csv`, `stability.csv`, `costs.csv`, `ablations.csv`, `metadata.json`, cobertura, figura y notebook ejecutado.

## Qué no cubre

Polinomios de grado mayor, coeficientes inciertos, sistemas multivariados, verificación intervalar de pagos, exhaustividad de regímenes económicos, identificación, datos reales o bienestar.

## Checklist

- [x] Código real en `src/`.
- [x] Un comando único.
- [x] Tests automatizados.
- [x] Baseline con números.
- [x] CSV/JSON/figura.
- [x] README, informe, referencias y MVP.
- [x] Subcarpeta `computational-economics/numerical-validation`.
- [x] Madurez S2 del componente declarada sin inflar el programa.

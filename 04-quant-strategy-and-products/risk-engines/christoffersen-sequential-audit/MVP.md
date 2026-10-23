# Declaración del MVP

## Qué es

Un motor C++17 ejecutable de auditoría del p-value Monte Carlo para independencia de
excepciones VaR, con decisiones `reject`, `non_reject` y `undecided`.

## Cómo se corre y qué produce

`bash run.sh` produce 600 ensayos crudos, resumen JSON/CSV, figura, tiempo/memoria y
evidencia de tests/lint/sanitizers. El oráculo exacto reutiliza el módulo integrado
`../christoffersen-exact-audit/include/exact.hpp`.

## Qué no cubre

No estima VaR, no cubre duración, cobertura incondicional ni ES, y no prueba datos de
mercado. La cota es conservadora y LeakSanitizer está desactivado por la restricción
`ptrace` del contenedor; ASan y UBSan sí se ejecutan.

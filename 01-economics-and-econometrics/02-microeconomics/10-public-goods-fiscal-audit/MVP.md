# MVP: auditoría fiscal de provisión de bien público

- Qué es: juego estático de dos contribuyentes, matching presupuestado en equilibrio y bienestar con coste fiscal real adicional.
- Comando: `bash run.sh` con Python 3.11+, venv y PyPI.
- Produce: 30 casos, comparación de tres políticas, oráculo escalar, identidad de recursos, figura, tests y notebook ejecutado.
- Hipótesis previa: corrección no empeora bienestar frente a ambas alternativas en grilla; error de bienestar frente a oráculo ≤1e−8; política ingenua perjudica en ancla λ=0,5.
- No cubre: parámetros estimados, política óptima real, ingreso limitado, impuestos endógenos a desviaciones o warm glow.
- Madurez: S2 del componente, sin validación empírica ni equivalencia con M2.

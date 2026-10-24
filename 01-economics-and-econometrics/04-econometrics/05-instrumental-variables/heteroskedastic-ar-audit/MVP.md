# MVP ejecutable: AR heterocedástico

- Qué es: comparación pareada de tests AR F, HC1 y HC3 con n100/n1000, errores heterocedásticos, y exclusión inválida como falsación.
- Cómo correr: `bash run.sh` con Python3.11+, venv y PyPI.
- Produce: 10.000 decisiones reproducibles, tabla/figura, benchmark por brazo y tamaño, notebook ejecutado y pruebas.
- No cubre: evidencia causal real, exactitud finita de HC1/HC3, clusters/HAC, intervalos o producción.
- Madurez: S2 solo componente; no equivale a M2 ni valida programa completo.
- Hipótesis previa: HC3 rechazo en[3%,7%] a n1000 heterocedástico válido; exceso F−HC3≥5pp. Resultado:5,55% y18,35pp, confirmación limitada al DGP.

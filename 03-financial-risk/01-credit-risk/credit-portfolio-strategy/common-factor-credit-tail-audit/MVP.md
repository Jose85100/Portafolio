# MVP
- Qué: mezcla de PMF de cartera condicional a factor gaussiano, usando kernel 25oct sin editarlo.
- Cómo: `bash run.sh` desde esta carpeta. Requiere conservar el hermano discrete-credit-tail-audit en el checkout.
- Qué produce:16registros de convergencia,40corridasMC,602 filas de PMF, métricas, gráfico, notebook ejecutado y evidencia de tests/tipos/lint.
- Qué no cubre: estimación de PD/rho, multifactor, correlación negativa, rho1, parámetros inciertos, pesosfraccionarios, dependencia de LGD, error certificado de cuadratura ni provisión/capital regulatorio.
- Diagnóstico: stability_passed significa solo acuerdo observado entre órdenes; no garantía de error o autorización operativa. Rhoalto puede pasar masa y fallar cola.
- Madurez: componenteprototipo sintético. No se eleva el programa entero aM2/M3.
- Entorno: Python 3.12, versiones directas fijadas y .venv; transitivas no totalmente bloqueadas.

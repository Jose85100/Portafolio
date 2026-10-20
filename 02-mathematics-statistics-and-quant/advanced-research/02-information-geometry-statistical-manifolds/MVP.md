# MVP — alcance S2

Qué es: biblioteca escalar de geometría Fisher–Rao categórica, geodésicas y auditoría de tests de dos muestras. Demuestra por identidad y ejecución que FR y Hellinger ordenan igual las mismas particiones, y que el cuadrático local no es una distancia global.

Cómo se corre: desde esta carpeta, con Python 3.12, make, venv y acceso a PyPI, ejecutar `make run`. Instala dependencias directas fijadas y reproduce tests, benchmark, figura, informe y notebook.

Qué produce: 1.600 pares de muestras y 6.400 p-valores, 318.400 particiones recreables por semilla, 64 tasas con Wilson 95%, 75 mediciones de funciones, 12 comparaciones con 80 dígitos y 132 puntos geodésicos. CSV/JSON/NPZ, PNG, notebook ejecutado y logs reales.

Qué NO cubre: datos financieros, detección online, dependencia temporal, comparación universal de potencia, Fisher en familias continuas, estimación de binning, matriz Fisher regular en fronteras ni certificación formal. Una igualdad de p-valores no demuestra igualdad de leyes a partir de no rechazar: aquí se debe a monotonía de las estadísticas. El programa de investigación original permanece como agenda debajo del MVP.

Estado: prototipo ejecutable S2 acotado; no producción ni validación externa. Figura revisada; revisión visual integral de notebook en visor no reclamada. Las ocho pruebas existentes de numerical-core se incluyen en el comando; no se modifica quant-libraries ni su contrato EL=83.

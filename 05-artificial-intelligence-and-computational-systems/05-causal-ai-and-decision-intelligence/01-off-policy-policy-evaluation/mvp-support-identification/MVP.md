# MVP

- Qué es: auditor tabular de identificación de valor de una política con soporte deficiente.
- Comando: `bash run.sh`, Python 3.12 + pip, desde esta carpeta.
- Salidas: 11 tests, 320 registros de estadísticas/recursos y 1.280 comparaciones CSV; huellas y ejemplos de logs; dos SVG; notebook ejecutado; seis referencias con límites de verificación explícitos.
- Qué no cubre: propensiones estimadas, contextos poblacionales estimados, logging adaptativo, recompensas fuera de [0,1], horizontes secuenciales, datos reales o causalidad observacional sin identificación.
- Madurez: componente S1→S2; candidato M2 local con revisión independiente. No eleva el programa entero ni implica operación.
- Gate: la abstención por falta de identificación no es una decisión acertada. Un log finito sin cierta acción no prueba soporte estructural cero.

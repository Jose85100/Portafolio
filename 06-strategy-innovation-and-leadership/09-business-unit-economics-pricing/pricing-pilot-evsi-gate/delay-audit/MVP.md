# MVP operativo

**Uso previsto:** estructurar una discusión ejecutiva de “actuar ya vs. comprar información” para dos alternativas de precio con un horizonte y costo explícitos. No fija un precio comercial ni sustituye experimentación causal, legal, financiera o de riesgo.

**Inputs mínimos:** parámetros Beta positivos por brazo; contribución marginal por conversión en unidades abstractas homogéneas; tamaño por brazo; horizonte; demora; costo total del estudio; independencia y decisión al cierre del piloto. Configuración ilustrativa en `config.json`.

**Salida:** valor de actuar ya, valor neto del piloto, ganancia comparativa, masa predictiva, valor EVSI sin demora, costo atribuible a demora, umbral de demora contra acción inmediata y acción recomendada. La política usa `Δ>0`; empate va a acción inmediata. Ajustar si algún supuesto puede verificarse y parametrizarse; cerrar cuando piloto no aporta valor decisional bajo escenarios plausibles.

**Control antes de usar:** convertir costos/beneficios a mismas unidades y horizonte; auditar prior con históricos pertinentes; estimar cuánto valor se pierde durante estudio y si el negocio sigue capturando ventas durante piloto; comprobar independencia; revisar sensibilidad de n, H, d, c y concentración; documentar aprobador y fecha.

**Madurez honesta:** prototipo analítico reproducible con fixture sintético. No es una herramienta desplegable; carece de ingestión de datos, control de acceso, monitoreo, validación independiente y backtest. Evidencia local no supera M1; componente matemático tiene pruebas unitarias, pero dominio 06 conserva nivel parcial M1–M2 según `PROJECT_MATURITY.md`.

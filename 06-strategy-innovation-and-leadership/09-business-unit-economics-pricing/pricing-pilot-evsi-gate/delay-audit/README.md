# Auditoría CEO de EVSI con demora — corte 2026-11-10

**Pregunta:** ¿Cuándo comprar información de un piloto antes de decidir precios si la prueba retrasa la acción comercial y consume horizonte?

**Clasificación:** adaptación de ingeniería de una decisión bayesiana conocida, no contribución científica original ni evidencia comercial.

Modelo: cada brazo de precio tiene tasa de conversión desconocida `p_j ~ Beta(alpha_j,beta_j)`, margen de contribución por conversión `m_j` en unidades abstractas y conteo `K_j ~ BetaBinomial(n,alpha_j,beta_j)`. El margen esperado por periodo tras observar k es `m_j(alpha_j+k)/(alpha_j+beta_j+n)`. Se enumeran exactamente los `(n+1)^2` resultados conjuntos para obtener `q=E[max_j E(m_j p_j|K)]`. Inmediato=`H*m0`, donde `m0=max_j E(m_j*p_j)`; piloto demorado=`(H-d)*q-c`. Se elige piloto solo si la diferencia es estrictamente positiva; empate favorece actuar ahora. Aquí `c` está en las mismas unidades de valor agregado del horizonte.

**Hallazgo del escenario base:** con n=10 por brazo, horizonte H=100 y costo abstracto c=2, el umbral de demora piloto-vs-ahora es `d*=H-(H*m0+c)/q`. La regla EVSI simple sin demora puede recomendar un piloto que el gate con horizonte rechaza. Los valores concretos están en `results/summary.json`; no son cifras de una empresa.

**Reproducción completa desde esta carpeta:** Python 3.11+, dependencias de `requirements.txt`. Ejecutar `bash run.sh`; ejecuta pruebas, Ruff, compilación sintáctica, cálculo exacto y Monte Carlo, genera CSV/JSON/figura y notebook reproducido, y valida el contrato de resultados. `python3 src/evsi_delay.py` conserva el CLI mínimo del corte previo.

**Evidencia:** escenario enteramente sintético; salida exacta y benchmark Monte Carlo independiente incluido. La suma predictiva en doble precisión se compara con uno en `results/numerical_audit.json`; a concentración 1000× la masa es 0.9999999999694 y EVSI cruda es −3.36e−8, flaggeada como redondeo dentro de tolerancia; no se renormaliza ni trunca silenciosamente. No hay datos comerciales, CI remota ni validación independiente; no se declara M2/M3.

**Opciones comparadas:** (1) lanzar/continuar inmediatamente con el mejor margen prior; (2) piloto por EVSI estático, sin costo de demora; (3) piloto con horizonte finito y cargo de demora explícito. Se selecciona (3) como regla CEO por coherencia de horizonte; (1) es el baseline de acción; (2) es una ablación negativa y deliberadamente omite el valor comercial perdido. Sensibilidad de concentración del prior y duración del piloto están tabuladas.

**Limitaciones:** margen constante, priors Beta independientes, dos brazos, asignación equilibrada, no demanda endógena, no elasticidad/modelo de precio, retención, incertidumbre en costos, ventas durante piloto ni descuento temporal. La demora consume periodos completamente; si el piloto vende mientras aprende, esta es una aproximación conservadora potencialmente sesgada. Los arm-specific margins son contribución condicionada a conversión, no precios observados; el precio nominal no se incluye porque no aparece en la función de utilidad.

**Archivos:** `MVP.md` fija uso/restricciones; `derivacion.md` presenta derivación; `informe.md` contiene informe ejecutivo en 14 secciones-página; `prior-art.md` compara al menos cinco referencias; `notebook.ipynb` se ejecuta al invocar el único comando; `results/` guarda outputs reproducibles. Contrato config y decisión se tipan en `src/evsi_delay.py`.

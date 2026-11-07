# Auditoría EVSI con demora de lanzamiento — incremento del 7-nov-2026

**Pregunta:** ¿Cuándo sigue justificándose un piloto de precios si la decisión posterior consume parte del horizonte comercial?

**Clasificación:** adaptación de ingeniería de una decisión bayesiana conocida, no contribución científica original ni evidencia comercial.

Modelo: para brazo j, p_j ~ Beta(alpha_j,beta_j), K_j ~ BetaBinomial(n,alpha_j,beta_j). El margen esperado por oportunidad tras observar k es m_j(alpha_j+k)/(alpha_j+beta_j+n). Se suman exactamente las (n+1)^2 probabilidades predictivas conjuntas para obtener E[max_j E(m_j p_j|K)]. La decisión inmediata vale H max_j E(m_j p_j); el piloto vale (H-d) E[max_j E(m_j p_j|K)] - c. No se contabilizan ventas durante la demora ni costo de muestra distinto de c.

**Hipótesis falsable:** la demora reduce estrictamente el valor del piloto si su margen posterior esperado es positivo; el umbral de decisión se cruza cuando d supera H-(H*m0+c)/post. La hipótesis es matemática bajo estos supuestos, no causal.

**Reproducción desde esta carpeta:** Python 3.11+ (solo biblioteca estándar). `python3 -m unittest discover -s tests -v && python3 src/evsi_delay.py --output results/result.json`.

**Ejecución local observada:** 5/5 tests OK; caso simulado H=100,d=5,c=2,n=10: inmediata=550, piloto=553.401467652197, ganancia neta=3.401467652197; masa predictiva=1.0000000000000215. Sin comparación empírica, CI remota, revisión independiente ni notebook ejecutado. Valores monetarios arbitrarios por oportunidad, no COP. Este componente no debe promoverse a M2.

**Limitaciones:** márgenes constantes, priors independientes, no demanda endógena, no elasticidad precio, no retención, sin incertidumbre de costos, piloto sin ventas y sin descuento temporal. La diferencia entre políticas es resultado del diseño simulado.

**Siguiente trabajo:** comparación contra EVSI sin demora y simulación Monte Carlo, análisis de umbral de demora, sensibilidad de priors, notebook narrativo y validación de fuentes primarias antes de declarar MVP contractual completo.

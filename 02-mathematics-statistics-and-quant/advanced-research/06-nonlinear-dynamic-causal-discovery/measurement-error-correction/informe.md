# 1. Corrección de momentos de un proxy: recuperación de investigación26oct

Reconstrucción y reejecución27oct2026 desde historial visible, después de pérdida del worktree26. No es aporte nuevo27 ni restauración byteporbyte. PR84 es la recuperación25 y no se duplica. Nueva rama sobre main e0cb173; solo carpeta autocontenida.

## 2. Tres ideas e hipótesis

Se compararon: HAC para autocorrelación(dependencia nueva, pospuesto), corrección de proxy con varianza conocida(elegida,cierra fallo25), persistenciaH0/MST(otro programa, pospuesto). Hipótesis de diseño26 recuperada: n2000,varianza correcta,sesgo absoluto<=.04,aceptación>=95%,RMSE<=50% del baseline proxy en las mismas réplicas. No exige mejora universal. Novedad local: banco de falsación y gate auditable,invariante a unidades; método de momentos clásico.

## 3. Estado del arte
Fuller1987 y Carrolletal2006 abordan error de medida; Pearl2009 y Petersetal2017 distinguen identificación de asociación; Rungeetal2019 representa causal discovery general pendiente. Cinco referencias reales DOI/URL verificadas en fuentes.md/referencias.bib. No revisión exhaustiva, prioridad mundial ni réplica de todos sus métodos.

## 4. Brecha
El MVP25 mostró que un proxy ruidoso mantiene confusión. Se añade información externa: varianza del ruido conocida. No se presume estimarla de los mismos momentos ni se resuelve confusión oculta arbitraria.

## 5. Diseño experimental
Z~N(0,1),X=.8Z+u,Y=βX+.8Z+e,W=Z+v,con u/e~N(0,.25),v~N(0,1),independientes. Son las filas IID alineadas del SCM25, no un VAR general. n100/500/2000,β0/.3,200datasets por celda;semilla20261026 y offsets en CSV.1200datasets,4800evaluaciones pareadas con varianzas declaradas0/.5/1/1.5;verdadera1. Capcondición100 prefijado. Los umbrales se recuperaron del diseño visible26, no se reajustaron después de medir27.

## 6. Implementación y derivación
Sea S la covarianza observada de(X,W,Y). Bajo error clásico independiente con media0,varianzaτ²conocida,restarτ²deSww recupera la matriz de covarianza de(X,Z):

`C=[[Sxx,Sxw],[Swx,Sww−τ²]]; theta=solve(C,[Sxy,Swy])`.

La primera coordenada estimaβ. Cov(W,Y)=Cov(Z,Y),Cov(X,W)=Cov(X,Z). Si C poblacional es definida positiva,LLN y continuidad de la inversa dan consistencia del plug-in,no insesgamiento finito. El código normaliza a correlación,resuelve y desescala. Se abstiene ante varianza no positiva,matriz no definida positiva o condición>100. Cambiar unidades y reescalarτ²porW²no cambia el gate. Entrada directa presupone covarianza válida; API de muestras la construye.

Poblaciónβ0:VarX=.89,VarW=2,CovXW=.8,CovXY=.64,CovWY=.8. ProxyOLS=.32/.57=.561404;corregir varianza1da0;declarar.5da.32/.695=.460432;declarar1.5produce determinante.89*.5−.64<0. No se invierte explícitamente C ni se recortan pendientes extremas silenciosamente.

## 7. Tests y recursos
Cuatro tests con varios casos:oráculos poblacionales,OLS independiente con varianza0,diez casos aleatorios de invariancia/unidades y linealidad en Y,entradas inválidas y abstenciones. Ruff/mypy src pasan; cobertura se guarda en results/coverage.txt y corresponde solo al núcleo,no al repo. Tiempo por ajuste y pico Pythontracemalloc(noRSS) en CSV para tres tamaños; precisión por sesgo/RMSE,sensibilidad a varianza y estabilidad por condición. No hay C/C++;sanitizers no aplican.

Notebook con cinco celdas de código ejecutadas realmente en namespace nuevoIPython;kernel Jupyter separado no probado. Salidas y figura regeneradas27,no restauradas de26.

## 8. Resultados regenerados

β0,200datasets por tamaño:

|n|τ²declarada|Aceptadas|Sesgo condicionado|RMSE condicionado|RMSEproxy mismas réplicas|
|---|---:|---:|---:|---:|---:|
|100|0|200|.56512|.57109|.57109|
|100|1|185|−.25707|.95119|.56957|
|500|1|200|−.12705|.46541|.55809|
|2000|1|200|−.00786|.10082|.55987|
|2000|.5|200|.45872|.45939|.55987|
|2000|1.5|0|No estimado|No estimado|No comparable|

β.3,n2000:sesgo−.00944,RMSE.10478frente a.56136deproxy,200aceptadas. Oráculo ZobservadoRMSE.02070(β0),.02195(β.3),mejor que la corrección. Umbrales n2000 pasan. CSV crudo/summary y figura audit.png permiten auditar.

Comparación **condicionada a aceptación**:baselines se evalúan en las mismas réplicas. Abstenciones aparte;no se asigna coste de abstención ni se afirma riesgo incondicional menor. No se emiten CI/pvalores,no se reutiliza Fdel25 indebidamente.

## 9. Fallos y ablaciones
n100 empeora aun con varianza correcta y rechaza15réplicas. Inversión amplifica ruido muestral;consistencia no garantiza precisión finita. Conτ²falsa1.5,n100acepta19réplicas pero sesgo−3.3487,RMSE4.5898;pasar el gate no valida el supuesto. Con n500/2000rechaza todas,sin promedios ficticios. Subdeclarar.5deja sesgo persistente≈.46. No se oculta la superioridad del oráculo con confusor observado.

## 10. Límites y madurez
Varianza externa conocida,error independiente/clásico/homocedástico,linealidad y verdad sintética favorecen solución conocida. No cubre errores correlacionados,no linealidad,selección de lags,feedback o datos reales. Selección de réplicas válida para comparación pareada,no prueba utilidad operacional. S2 acotado,no programa completoS3/S4/M2. EL83 no aplica.

## 11. Comando
Python3.12,desde esta carpeta:`bash run.sh`. Bootstrap con pins y entorno aislado;MATH_ENVelige ubicación. Reproduce tests,lint,tipos,cobertura,4800evaluaciones y notebook,sin datos remotos.

## 12. BibTeX
Cinco entradas en referencias.bib. fuentes.md diferencia metadatos verificados y accesos bloqueados;no se simula lectura completa.

## 13. Rúbrica1–5
Novedad2(método clásico),rigor4(oráculos,selección explícita,sinCI),reproducibilidad4(pins/seeds/ejecuciónreal,reconstrucción declarada),código4,claridad4,impacto3,honestidad5,MVPejecutable5. Autoevaluación,no certificaciónexterna.

## 14. Siguiente iteración
Siguiente iteración recomendada:reemplazar varianza exacta por información externa acotada y estudiar identificación parcial,sin fingir intervalos de confianza.

1. `advanced-research/06-nonlinear-dynamic-causal-discovery/measurement-error-correction`:identificación parcial con rango de varianzas externo.
2. Misma carpeta:propagar incertidumbre de una muestra de validación independiente.
3. Misma carpeta:coste de abstención para comparar riesgo incondicional.

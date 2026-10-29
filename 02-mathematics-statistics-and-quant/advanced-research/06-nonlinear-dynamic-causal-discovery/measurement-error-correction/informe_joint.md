# 1. Gate conjunto de covarianza latente —28oct2026

Incremento nuevo sobre el corrector26 integrado por PR89. Main5b7d30e revisado, ningún PR abierto al inicio. El intervalo27 no tiene entregaGit verificable y no se recupera ni cuenta como terminado. Esta modificación no implementa ese intervalo.

## 2. Tres ideas e hipótesis

Se compararon: intervalo de identificación parcial(alcance mayor y27no publicado,pospuesto),bootstrap de varianza externa(requiere estudiar cobertura,pospuesto),gate PSD de toda la covarianza(elegido,brecha concreta y pequeña). Hipótesis registrada: toda aceptación del gate26 con residualSchur negativo debe ser rechazada; declarar la varianza verdadera1 conserva el coeficiente. Novedad local: cerrar validación de momentos, no nuevo teorema ni prioridad mundial.

## 3. Estado del arte
Fuller1987 y Carrolletal2006 contextualizan error de medida; Pearl2009 y Petersetal2017 separan estructura e identificación; Rungeetal2019 aborda sistemas generales no implementados. Las cinco referencias de referencias.bib fueron reabiertas28en fuentes primarias; fuentes_joint.md registra URLs y alcance. No revisión exhaustiva ni réplica de esos métodos.

## 4. Brecha
El gate26 comprueba solo C=Cov(X,Z). Puede aceptar una matriz latente completa con varianza residual negativa de Y, imposible como covarianza de variables reales. PSD del bloque de regresores no implica PSD conjunta.

## 5. Diseño y config
Momentos poblacionales del DGP26:X=.8Z+u,Y=βX+.8Z+e,W=Z+v,variables gaussianas independientes con VarZ=Varv=1,Varu=Vare=.25. β0/.3;nueve varianzas declaradas0/.5/.9/1/1.1/1.15/1.2/1.24/1.5.18casos,36filas método,20repeticiones de latencia por método/caso. No MonteCarlo de datos ni observaciones reales. Tests aleatorios usan seed20261028. Config fija capcondición100,toleranciaPSDnormalizada1e-10.

## 6. Implementación y derivación
Error clásico independiente W=Z+v exige S0=Cov(X,Z,Y)=S−diag(0,τ²,0) semidefinida positiva. Esto sigue de a'S0a=Var(a'(X,Z,Y))>=0 para todo a. Si C es PD, completar cuadrados da S0PSD si y solo si S0YY−S0YR*C^(-1)*S0RY>=0(complemento de Schur). El núcleo usa eigenvalores de la matriz normalizada; el benchmark usa Schur como oráculo independiente.

La función nueva correct_covariance_joint llama al gate26; conserva sus rechazos y añade chequeo conjunto. Normalización por desviaciones mantiene invariancia a unidades positivas; para una varianza cero se usa escala1 y se admite PSD degenerada. Diagonal negativa se rechaza. Tolerancia y float64 son explícitos,no se ofrece certificado de redondeo dirigido. No cambia silenciosamente el estimador original ni sus salidas históricas.

## 7. Tests y benchmark
Se ejecuta suite completa:cuatro tests anteriores y cuatro nuevos con múltiples valores; ver logs. Nuevos controles:contraejemplo de bloque válido/matriz imposible,preservación en varianza verdadera y frontera178/153,20efectos aleatorios con cinco varianzas y cambio de unidades,entradas inválidas y Ydegenerada válida. Ruff/mypy de módulos nuevos pasan. Cobertura medida solo de src.joint_gate en results/joint_coverage.txt; no cobertura de todo el repo. Tiempos medianos de20llamadas y pico de asignaciones Pythontracemalloc(noRSS) en CSV. Tamaño fijo3x3: no se afirma escalabilidad a dimensión arbitraria. Sanitizers no aplican,no hay C/C++.

## 8. Resultados reales

| Métrica | Gate26 | Gate conjunto28 |
|---|---:|---:|
| Casos poblacionales |18|18|
| Modelos imposibles aceptados |4|0|
| Coeficientes correctos conservados conτ²=1 |2/2|2/2|
| Varianza falsa.5compatible aceptada |2/2|2/2|

Contraejemplo β0,τ²1.2:Ctiene determinante.072>0 y pasa condición100; pendiente−1.77778,pero residualSchur−.19444. La nueva función se abstiene en vez de emitir ese coeficiente. También rechazaτ²1.24 para ambasβ. Conτ²1.5el gate previo ya se abstiene; no se presenta como mejora nueva. CSVcrudo joint_cases.csv,JSONjoint_summary.json,figurajoint_audit.png.

## 9. Controles negativos
τ².5falso pasa ambos gates y deja sesgo≈.46043frente aβ. Compatibilidad no demuestra que la varianza externa sea cierta ni causalidad. Las cuatro eliminaciones son casos construidos para exponer la brecha,no estimación de tasa de fallos en producción. El complementoSchur presuponeCpositivo,por eso solo se usa como oráculo cuando el gate previo acepta.

## 10. Límites y madurez
Momento poblacional,supuesto de error independiente y varianza declarada. No inferencia sobre datos finitos,noCI ni pvalores ajustados,no identificación parcial ni causal discovery general. Cerca de frontera manda tolerancia numérica explícita. ComponenteS2 acotado;no programaS3/S4/M2ni operación. EL83no aplica. Notebook ejecutado realmente con namespace nuevoIPython;kernelJupyter separado no probado.

## 11. Comando exacto
Desde esta carpeta,Python3.12:`bash run_joint.sh`. Usa requirements.txt existente fijado,entorno.venv-joint y dependencias verificadas. MATH_ENVpermite entorno alternativo. Produce nuevas salidas joint_*y notebook_joint.ipynb;run.sh y notebook26permanecen disponibles.

## 12. Referencias BibTeX
Cinco entradas completas en referencias.bib existente. fuentes_joint.md registra reapertura28de metadatos/abstracts de editor/autor;no se simula lectura de libros completos.

## 13. Rúbrica1–5
Novedad2(validación incremental conocida),rigor4(oráculo/derivación,no redondeo dirigido),reproducibilidad5(pins/comando/outputs),código4,claridad4,impacto3(auditoría sintética),honestidad5,MVPejecutable5. Autoevaluación,no certificación externa.

## 14. Siguiente iteración
Siguiente iteración recomendada:estudiar cuánto rechaza el gate conjunto bajo error muestral antes de usarlo como política en datos finitos.

1. `measurement-error-correction`:MonteCarlo de falsas incompatibilidades con matriz de momentos estimada.
2. Misma carpeta:separar tolerancia numérica e incertidumbre estadística.
3. Misma carpeta:rango externo de varianzas e identificación parcial como proyecto futuro,no entrega27supuestamente recuperada.

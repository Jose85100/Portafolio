# Riesgo25 de octubre de 2026 — distribución finita y concentración

## 1.Título
Oráculo de pérdidas Bernoulli ponderadas sobre rejilla y error de aproximación de cola.

## 2.Hipótesis/novedad
H: normal de momentos coincidentes infravalora ES99 concentrado más del 30%; DP coincide con enumeración fraccional con error PMF≤1e−12. Umbrales enconfig antes del experimento. Contribución local: oráculo de construcción de distribución heterogénea y diagnóstico de concentración. ES respeta convención ya presente enweighted-expected-shortfall-audit; no es algoritmo de ES nuevo ni novedad mundial.

## 3.Estado del arte
Cinco fuentes primarias verificadas el 25 de octubre: Hong (2011) sobre distribuciónPoisson-binomial y aproximaciones; Gordy (2002) granularidad; Vasicek (2002) límite de cartera un-factor; Acerbi/Tasche (2002) diferenciasES con átomos; Tasche (2002) ES y atribución. Texto de Vasicek completo restringido, usamos resumen/metadatos y declaramos límite. Referencias BibTeX y registro enbenchmarks/prior-art.md. No implementamos su DFT, fórmula IRB o capital Vasicek.

## 4.Brecha y selección
Tres ideas comparadas enprior-art: importance sampling con un factor, stress margen/liquidez, DP ponderado. Elegimos tercero por alcance cerrado y brecha verificable. HHI existente informa concentración pero no su cola discreta; notebook Vasicek usa default homogéneo con factor. Se requiere oráculo pequeño para probar aproximaciones sin confundir error de simulación con error de modelo.

## 5.Diseño/config
Dos carteras con pérdida máxima 300, PD 2% constante, EL 6: granular 100×3 y concentrada 100+20×10. HHI 0,01 vs0,1333. Q=.99. La normal coincide exactamente con media y varianza propias de cada cartera. No se impone igual varianza entre carteras. Monte Carlo: 30 semillas 0–29, 10.000 draws/semilla, independientes dentro de cada cartera. Son casos diseñados, no muestra representativa de bancos. Datos generados sin clientes.

## 6.Implementación y derivación
L=ΣwᵢDᵢ. G(z)=Π[(1−pᵢ)+pᵢz^wᵢ]. Coeficientes fᵢ(l)=(1−pᵢ)fᵢ₋₁(l)+pᵢfᵢ₋₁(l−wᵢ). Inducción de masa1 y momentos aditivos bajo independencia. Complejidad O(nΣw) y memoria O(Σw), no polinomial en longitud binaria de exposición. Límite duro 20.000 unidades, pesos enteros no negativos; no redondeo dentro del motor. VaR=inversaizquierdaCDF; ES=integral del cuantil sobre1−q cortando átomo frontera. Normal usa μ+σzq y μ+σφ(zq)/(1−q), sin truncado oportunista. PMF admite erroresflotantes≤1e−10 y normaliza solo ese residuo, no arregla un modelo inválido.

## 7.Tests/benchmark
Cinco tests: enumeración2^n para n=1..7 con PD heterogéneas y0/1; masa/media/varianza; átomo parcial y casos deterministas; escala/permutación/peso0; entradas inválidas/cota de memoria/confianza. Cobertura realmente medida enresults/coverage; solo núcleo, no todo proyecto. Ruff src/tests/benchmarks; mypy estricto núcleo. Benchmark PMF fraccional independiente de tres obligaciones enexperiment y tolerancia1e−12. Performance n20/100/300 pesos3 con tiempos y masa; no inferimos complejidad de tres puntos. Tiempo/memoria del experimento incluyeMC, no soloDP. C++/sanitizers no aplican.

## 8.Resultados
|Cartera|VaR99DP|ES99DP|VaR99Normal|ES99Normal|
|---|---:|---:|---:|---:|
|Granular|18|19,5673099|15,7706611|17,1938997|
|Concentrada|100|108|41,6774098|46,8743426|
Normal ES error−12,13% y−56,60%. Masa antes de normalizar difiere aproximadamente2,3e−15 y4,4e−16. OráculoPMF pequeño/tolerancia enmetrics.json. MonteCarloerrors en60filas; notebook calculaRMSE y figura boxplot; no se usa única semilla favorable. H se evalúa automáticamente, no se deduce de una figura.

## 9.Crítica y falsación
Granular tiene solo dos defaults esperados, por eso normal no resulta exacta pese a 100 obligaciones; no se afirma CLT válido por contar deudores. Dependencia perfecta negativa: prob2% pérdida 300, de otro modo0. MismaEL 6, peroVaR99/ES99=300 frente a18/19,567 bajo independencia. El oráculo falla estructuralmente si se usa como verdad de ese DGP; precisión numérica no arregla correlación omitida. No se estima correlación ni se incorpora factor común en este MVP.

## 10.Límites/riesgos
PD conocidas, independencia, LGD/EAD deterministas y horizonte único son supuestos. Rejilla explícita, no prueba error de discretización de pesos reales; colas extremas cerca de masa de CDF pueden cambiar VaR por redondeo flotante. No proporciona intervalos de parámetros, validación empírica o capital/provisión regulatorios. Coste de memoria crece con pérdida máxima, se rechaza exceso. No usar como recomendación de capital real.

## 11.Comando/entorno
`bash run.sh`:instala y reproduce. Puede seleccionar PYTHON o SKIP_INSTALL=1; activar venv para aislar. Versiones directas fijadas, transitivas sin lock total. Notebook ejecutado realmente con IPython in-process secuencial y captura de outputs, no kernel simulado. Figura inspeccionada separadamente; no render HTML completo. Metadatos de hardware/versiones/tiempo/memoria enmetrics.json.

## 12.Referencias
Cinco entradas reales verificadas en referencias.bib. Revisión focal, no exhaustiva. Alcance de lectura y distinción entreDP local y métodos de literatura enprior-art.

## 13.Rúbrica
Autoevaluación: novedad2/5,rigor4,reproducibilidad4,código4,claridad4,impacto3,honestidad5,MVP 4. Componente prototipo sintético, no se eleva madurez de todo el dominio. Revisión independiente/publicación se reportan aparte con evidencia.

## 14.Siguiente iteración
Siguiente iteración recomendada: usar el PMF condicional dentro de un factor común con error de cuadratura controlado. Tres tareas: discrete-credit-tail-audit:certificar límite de discretización de pesos; vasicek-perdida-no-esperada:comparar factorcomún finito/asintótico; risk-engines:portar oráculo acotado con pruebas cruzadas y sanitizers.

## Checklist
Código/comando/tests/baseline numérico/CSVJSONfigura/notebook ejecutado/README/informe/cinco referencias/MVP/config/entorno presentes. Revisión independiente y PRsolo se afirman con evidencia posterior.

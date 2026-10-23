# ¿Qué tan completos están los desarrollos del 23 de octubre?

**Dictamen:** los cinco MVP y dos arquitecturas son experimentos técnicos acotados. Ninguno constituye por sí solo una línea de investigación cerrada o una solución operacional completa. Hoy se añadieron siete ampliaciones académicas ejecutadas y una agenda de 24 experimentos específicos. Las mejoras no elevan automáticamente S2 a S3 ni M2 a M3.

## Alcance y qué significa completo

Se inspeccionaron implementaciones, notebooks, informes, bibliografía y CI de los cinco MVP de la PR70, las dos arquitecturas de IA y el motor secuencial de la PR69. Se separan cuatro exigencias: formulación correcta bajo supuestos, implementación verificable, evaluación estadística fuera de muestra y adecuación al uso. Completar una demostración numérica no completa las otras tres.

| Desarrollo de hoy | Alcance implementado y comprobado | Brecha que impide llamarlo completo | Criterio de cierre siguiente |
|---|---|---|---|
| IV débil | Test AR/Wald y ahora inversión algebraica de AR; 1.500 decisiones contrastadas | Un instrumento, F homocedástico; sin CLR, clustering ni aplicación empírica | Comparador CLR y potencia bajo alternativas, más inferencia robusta con tamaño controlado |
| Firmas | Nivel dos, identidades, aliasing y ahora lead–lag con 100 comprobaciones | Sin modelo predictivo entrenado ni evaluación temporal; sin prueba de superioridad frente a features simples | Train/cal/test temporal, comparadores directos y ablations de muestreo |
| KYC | Rangos por canal y comparación de multiplicidad en 400 lotes sintéticos | Calibración legítima idealizada; sin fraude etiquetado, retrasos reales o FDR online | Etiquetas maduras, pruebas de validez marginal bajo drift y costo de revisión |
| Conformal | Pesos oráculo, masa infinita y ahora CQR ajustado en train | Sin razones de densidad estimadas ni adaptación temporal; cobertura marginal no garantiza subgrupos | Cross-fitting de pesos y experimento online predecir–observar–actualizar |
| Innovación EVSI | Decisión fija y ahora Bellman finito de 30 observaciones | Prior/población/costos supuestos; usuarios homogéneos; sin demora endógena | Validación del prior, heterogeneidad y costo de oportunidad; evaluación de política |
| Decisiones tipadas | Contrato, calibración, abstención, costos y regla de Chow | Proveedor sintético; fallback y eficacia no medidos; sin integración comercial | Corpus etiquetado, adaptador real aprobado y evaluación prospectiva de fallback |
| Evidencia documental | Hash/spans, conciliación y ahora métricas semánticas sobre plantillas | Reglas lexicales sin OCR/NLI; una paráfrasis rompe la regla | Anotación humana, prueba de paráfrasis/negación y comparación NLI/humano |
| Christoffersen secuencial, PR69 | MC ternario con gasto de error; frontera conserva 167/200 abstenciones | La cota es conservadora; error MC y validez del test son distintos | Comparar secuencia de confianza de mezcla, draws, undecided y tamaño financiero |

No se coloca una calificación porcentual de “completitud”: los criterios no son intercambiables ni aditivos. El programa original de cada carpeta conserva su madurez y sus brechas.

## Literatura publicada: qué se verificó

Se contrastaron **16 referencias: 11 artículos de revista, cuatro trabajos de proceedings y un capítulo académico publicado**. Hay evidencia editorial, DOI o registro institucional/bibliográfico según cada fila. Se consultaron fuentes primarias; RePEc, DBLP, PubMed y otros catálogos sirven para contrastar metadatos, no como sustituto de las demostraciones.

No se afirma que todas las referencias estén verificadas directamente en Scopus o Web of Science. Para BY, la ficha institucional TAU identifica revisión por pares y enlaza Scopus. Claxton tiene registro PubMed; Moreira aparece en RePEc; los proceedings y JMLR tienen fichas oficiales. Un DOI identifica un trabajo, pero no certifica por sí solo indexación en una base específica. Se diferencia publicación de versión preprint: el texto de firmas fue publicado como capítulo en 2025; la referencia de 2016 continúa siendo preprint. El artículo de hedging pertenece al volumen 2020 con versión online/DOI 2021.

| ID | Trabajo | Publicación | Evidencia y acceso |
|---|---|---|---|
| AR1949 | [Estimation of the Parameters of a Single Equation in a Complete System of Stochastic Equations](https://www.jstor.org/stable/2236803) | Annals of Mathematical Statistics (1949) | JSTOR: referencia editorial; acceso completo no certificado |
| CLR2003 | [A Conditional Likelihood Ratio Test for Structural Models](https://onlinelibrary.wiley.com/doi/10.1111/1468-0262.00438) | Econometrica (2003) | Wiley + RePEc: publicación y resumen; no reproducción CLR |
| SIG2025 | [A Primer on the Signature Method in Machine Learning](https://link.springer.com/chapter/10.1007/978-3-031-97239-3_1) | Signature Methods in Finance (2025) | Springer Finance: capítulo abierto; sección 3.1.14 consultada |
| HEDGE2020 | [Non-parametric Pricing and Hedging of Exotic Derivatives](https://www.tandfonline.com/doi/abs/10.1080/1350486X.2021.1891555) | Applied Mathematical Finance (2020) | Editorial + Oxford/Turing: volumen 2020; versión online 2021; metadatos/resumen |
| BH1995 | [Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing](https://academic.oup.com/jrsssb/article/57/1/289/7035855) | Journal of the Royal Statistical Society: Series B (1995) | Oxford/Wiley: metadatos y resumen indexados; HTML completo bloqueado |
| BY2001 | [The control of the false discovery rate in multiple testing under dependency](https://cris.tau.ac.il/en/publications/the-control-of-the-false-discovery-rate-in-multiple-testing-under/) | Annals of Statistics (2001) | TAU identifica artículo peer reviewed y enlaza Scopus; Euclid devuelve iframe |
| WCP2019 | [Conformal Prediction Under Covariate Shift](https://proceedings.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html) | Advances in Neural Information Processing Systems (2019) | Proceedings y registro DBLP; texto y código de autores identificados |
| CQR2019 | [Conformalized Quantile Regression](https://proceedings.neurips.cc/paper_files/paper/2019/hash/5103c3584b063c431bd1268e9b5e76fb-Abstract.html) | Advances in Neural Information Processing Systems (2019) | Proceedings y PDF consultado, sección de método |
| ACI2021 | [Adaptive Conformal Inference Under Distribution Shift](https://proceedings.neurips.cc/paper_files/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html) | Advances in Neural Information Processing Systems (2021) | Proceedings y DBLP; PDF ecuación 2 consultada |
| ACI2024 | [Conformal Inference for Online Prediction with Arbitrary Distribution Shifts](https://jmlr.org/papers/v25/22-1218.html) | Journal of Machine Learning Research (2024) | JMLR: ficha editorial y resumen consultados |
| CHOW1970 | [On optimum recognition error and reject tradeoff](https://research.ibm.com/publications/on-optimum-recognition-error-and-reject-tradeoff) | IEEE Transactions on Information Theory (1970) | IBM Research y registro DBLP; IEEE bloquea lectura; regla derivada por riesgo Bayes |
| SELECT2010 | [On the Foundations of Noise-free Selective Classification](https://jmlr.org/papers/v11/el-yaniv10a.html) | Journal of Machine Learning Research (2010) | JMLR y PDF, definiciones 1--2 consultadas |
| DESIGN1995 | [Bayesian Experimental Design: A Review](https://www.stat.cmu.edu/tr/tr599/tr599.html) | Statistical Science (1995) | Registro editorial y reporte CMU de autoras; revisión del resumen, no lectura íntegra |
| DECISION1999 | [The irrelevance of inference: a decision-making approach to the stochastic evaluation of health care technologies](https://pubmed.ncbi.nlm.nih.gov/10537899/) | Journal of Health Economics (1999) | Registro PubMed 10537899 y York; editorial 403, no lectura íntegra |
| FAITH2020 | [On Faithfulness and Factuality in Abstractive Summarization](https://aclanthology.org/2020.acl-main.173/) | Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (2020) | ACL Anthology: DOI, autores y resumen consultados |
| CS2021 | [Time-uniform, nonparametric, nonasymptotic confidence sequences](https://arxiv.org/abs/1810.08240) | Annals of Statistics (2021) | Volumen oficial IMS 49(2), páginas 1055–1080 y DOI; preprint de autores/abstract consultados |

[Registro estructurado](papers.json) y [BibTeX](papers.bib). Donde el acceso fue parcial se verificaron metadatos/resumen; no se reclama lectura íntegra. Moreira CLR, ACI, hedging y secuencias de mezcla quedan como agenda cuando no se implementaron. No se presentan las reglas propias como algoritmos publicados de esos artículos.

## Fórmulas y extensiones realmente incorporadas

### 1. AR: aceptar conjuntos completos, no recortes del gráfico

Con variables centradas y $r_b=y-bx$, la inversión del F equivale a:

$$\mathcal C_{AR}=\{b:(n-2)r_b'P_zr_b-c\,r_b'M_zr_b\le0\}.$$

La expansión cuadrática y su oráculo de p-valores están dentro del notebook. Las raíces se calculan numéricamente; los casos casi degenerados se identifican para revisión. No se implementó CLR.

### 2. Firmas: un estadístico que se puede verificar directamente

El embedding lead–lag usado satisface:

$$2A_{lead,lag}=\sum_i(\Delta x_i)^2.$$

El signo y el factor dos dependen de nuestra convención de área. La identidad conserva variación sobre la malla observada y no recupera datos ausentes. Error máximo observado en 100 casos: **3,979e−13**.

### 3. KYC: distinguir objetivo individual y de lote

$$FDR=E[V/(R\vee1)],\qquad p_{(k)}\le kq/(mH_m).$$

Se comparan alerta individual, Bonferroni, BH y BY sobre los mismos lotes. BY se aplica con p-valores marginalmente válidos; no repara deriva o calibración contaminada. En 200 réplicas por correlación la FDR observada BY fue **0,563%** con rho=0 y **0,045%** con rho=0,7, conservadora frente a q=5%. Se muestran potencia, número de alertas y error Monte Carlo; estas tasas no certifican un resultado poblacional o una cartera real.

### 4. Conformal: aprender el ancho antes de calibrar

$$s_i^+=\max\{0,\widehat q_{lo}(x_i)-y_i,y_i-\widehat q_{hi}(x_i)\},$$
$$C(x)=[\widehat q_{lo}(x)-Q,\widehat q_{hi}(x)+Q].$$

Es una variante conservadora de CQR: solo ensancha. Tres boosters se entrenan con 1.500 observaciones; calibración usa 600 y test independiente 3.000. En esta corrida, el ancho medio fue **2,872** frente a **3,261** del comparador simétrico, con cobertura **90,00%** frente a **89,87%**. No es superioridad universal ni garantía de cobertura por subgrupo o bajo shift.

### 5. Innovación: pagar información solo si cambia el valor

$$W(a,b,h)=\max\{0,V(a/(a+b)),-c_s+pW(a+1,b,h-1)+(1-p)W(a,b+1,h-1)\},$$

donde $p=a/(a+b)$. Es una aplicación propia de programación dinámica al modelo beta-binomial. Con los costos de este nuevo escenario y horizonte 30, el valor neto secuencial es **4.796,38**, frente a **4.601,81** del mejor tamaño fijo entre 0 y 30. No son los costos del experimento original de n=50: las dos cifras no deben mezclarse. Un oráculo independiente enumera **128 políticas** para horizonte tres y contrasta la solución memoizada.

### 6. Decisiones: abstenerse tiene un costo y puede tener errores

$$\text{aceptar si }\max_k p_k\ge1-c_r/c_e.$$

Se deriva comparando riesgos Bayes para revisión perfecta. Con fallback falible, usar $C_{derivar}(x)=c_r+c_e\epsilon_f(x)$. Bajo el mismo costo sintético, la confianza cruda obtuvo costo medio **0,11685**, frente a **0,08695** con temperatura y **0,08740** con el oráculo en esta muestra. La pequeña diferencia muestral frente al oráculo no prueba dominancia sobre la regla Bayes; depende de las realizaciones.

### 7. Documento: no confundir copia correcta y afirmación respaldada

La precisión de soporte se calcula contra etiquetas definidas por construcción, separadas del contrato: $P=TP/(TP+FP)$. Sobre las 200 plantillas construidas, verificar solo el span obtuvo **33,3% de precisión y 100% de recall**. La regla lexical obtuvo 100% en ambas dentro de las plantillas, pero una paráfrasis respaldada falla. El caso negativo se conserva. No se ejecutó NLI ni el modelo del artículo ACL.

## Agenda priorizada: 24 ideas adicionales

Cada fórmula es una especificación de investigación o una adaptación declarada, no un teorema nuevo. Estas 24 ideas están **propuestas, no implementadas**, y no se cuentan entre los siete experimentos anteriores. Los IDs permiten relacionar notebook, paper y criterio de refutación sin duplicar bibliotecas.

| ID | Idea | Fuente | Especificación | Experimento siguiente | Límite |
|---|---|---|---|---|---|
| ECO-1 | CLR y potencia | CLR2003 | `Pr(rechazar H0 | beta != beta0)` | Comparar AR/CLR bajo alternativas y misma fuerza instrumental; no usar potencia como tamaño. | CLR requiere implementación y valores críticos condicionales verificables. |
| ECO-2 | Varios instrumentos y sobreidentificación | AR1949 | `F_AR = (r\'P_Z r / k)/(r\'M_Z r/(n-k-1))` | Introducir k instrumentos y contrastar contra OLS restringido por proyecciones. | El F exacto sigue requiriendo error normal IID homocedástico. |
| ECO-3 | Robustez de covarianza | CLR2003 | `T = g(b)\prime\widehat\Omega^{-1}g(b)` | Ensayar heterocedasticidad y clustering con covarianza apropiada y control de tamaño. | Forma de Wald del momento no garantiza exactitud finita; estudiar referencia asintótica. |
| MAT-1 | Covariación multicanal | SIG2025 | `[X,Y]_n=\sum_i\Delta X_i\Delta Y_i` | Derivar coordenadas lead-lag cruzadas y verificar contra suma directa. | Es un diagnóstico en malla observada, no predicción financiera. |
| MAT-2 | Features con separación temporal | SIG2025 | `\widehat y=f_\theta(S_{\le d}(X_{past}))` | Comparar con área, retornos y variación realizada en train/test temporal. | Definir ventanas sin mirar el futuro; truncación no identifica trayectorias. |
| MAT-3 | Payoffs de firma | HEDGE2020 | `\widehat\pi=\langle\ell,E[S(X)]\rangle` | Probar aproximación de payoffs en un generador y evaluar fuera de muestra. | No copiar precios simulados como precios de mercado; separar hedging y ajuste. |
| RSK-1 | FDR con etiquetas retrasadas | BY2001 | `FDR=E[V/(R\vee1)]` | Simular confirmaciones tardías y dependencia de lote; medir también potencia y carga. | La ausencia de confirmación no es un negativo legítimo. |
| RSK-2 | Resolución de p-valores y BY | BY2001 | `p_{min}=1/(n+1),\quad t_1=q/(mH_m)` | Mapear cuándo el primer umbral es inalcanzable y cuándo agrupaciones fuertes sí cruzan. | No exigir pmin<=t1 como condición necesaria para cualquier rechazo step-up. |
| RSK-3 | Deriva frente a multiplicidad | BY2001 | `P(p_i\le u)\le u` | Romper intercambiabilidad y medir si BY pierde control por p-valores inválidos. | BY corrige dependencia, no deriva o contaminación de calibración. |
| ML-1 | ACI online | ACI2021 | `\alpha_{t+1}=\alpha_t+\gamma(\alpha-err_t)` | Predecir antes de ver etiqueta y comparar frecuencia global/local, ancho e infinitos. | Frecuencia temporal no es cobertura condicional por x. |
| ML-2 | Paso adaptativo | ACI2024 | `\gamma_t \text{ adaptado al historial disponible}` | Comparar varios regímenes con hiperparámetros sin usar test futuro. | No atribuir a una gamma fija el resultado del procedimiento adaptativo publicado. |
| ML-3 | Pesos estimados y CQR | WCP2019 | `w(x)=dQ_X/dP_X` | Estimar razones con covariables sin etiqueta, cross-fitting y pruebas de solapamiento. | La garantía con pesos oráculo no se transfiere automáticamente a pesos aprendidos. |
| CEO-1 | Prior robusto | DESIGN1995 | `\max_d\min_{\pi\in\Pi}E_\pi[U(d)]` | Comparar política Bayes y minimax sobre priors explícitos conservando costo nominal. | La clase de priors es una elección que necesita justificación. |
| CEO-2 | Usuarios heterogéneos | DECISION1999 | `V=\sum_gN_g(B_g\theta_g-c_g)-F` | Añadir grupos y elegir dónde experimentar con presupuesto fijo. | Resultados sanitarios del paper no validan una fintech. |
| CEO-3 | Demora y competencia | DESIGN1995 | `W_t=\max\{V_t,\ E[W_{t+1}|D_t]-c_t\}` | Añadir lanzamiento diferido y costo de oportunidad a Bellman. | La ventaja del piloto no es gratuita si el mercado cambia. |
| AI-1 | Fallback falible por segmento | CHOW1970 | `C_{derivar}(x)=c_r+c_e\epsilon_f(x)` | Estimar error del fallback en calibración independiente y comparar con derivar perfecto. | No sustituir confianza del proveedor por error condicional estimado. |
| AI-2 | Control de riesgo y cobertura | SELECT2010 | `R=E[\ell g]/E[g],\quad\phi=E[g]` | Comparar cotas de aceptación con soporte mínimo y error por grupo. | Los teoremas noise-free no se aplican sin cambios a etiquetas ruidosas. |
| AI-3 | Capacidad compartida | CHOW1970 | `\min\sum_i C_i(a_i)\quad s.a.\sum_i t_i(a_i)\le B` | Conectar al MILP existente de riesgo y medir cola/costo frente a umbrales. | La regla por caso deja de resolver por sí sola la asignación global. |
| DOC-1 | Anotación de fidelidad | FAITH2020 | `P=TP/(TP+FP),\quad R=TP/(TP+FN)` | Anotar concepto, moneda, negación y período con dos revisores y adjudicación. | Fidelidad documental no autentica al emisor. |
| DOC-2 | Verificador semántico | FAITH2020 | `P(entailment|fuente,afirmacion)` | Comparar reglas, NLI y humano con corpus separado y paráfrasis adversarias. | Una probabilidad NLI necesita calibración y no prueba verdad financiera. |
| DOC-3 | Compresión basada en evidencia | FAITH2020 | `retencion=\#hechos\ preservados/\#hechos\ necesarios` | Evaluar correcciones y negaciones después de compresión con referencias humanas. | ROUGE o reducción de tokens no bastan para medir fidelidad. |
| MC-1 | Mezcla beta-binomial | CS2021 | `M_t(p)=B(a+S_t,b+t-S_t)/(B(a,b)p^{S_t}(1-p)^{t-S_t})` | Invertir M_t(p)<1/delta y comparar draws/abstención contra gasto Hoeffding. | Requiere draws Bernoulli con media p y modelo condicional defendible. |
| MC-2 | Error secuencial frente a frontera | CS2021 | `P(\exists t:p\notin C_t)\le\delta` | Simular probabilidades a ambos lados de alpha y declarar undecided cerca de frontera. | Control de remuestreo no prueba validez del test financiero subyacente. |
| MC-3 | Tamaño del test y presupuesto MC | CS2021 | `P(rechazo\ equivocado)\le riesgo_{test}+riesgo_{MC}` | Separar error del procedimiento financiero de error de aproximar su p-valor. | La suma es una cota por unión, no una igualdad ni garantía del modelo de mercado. |

### Prioridad inmediata

Primero comprobar datos/etiquetas y validez de supuestos: RSK-3, ML-3 y DOC-1. Después mejorar la decisión con sus costos: AI-1, AI-3 y CEO-3. CLR, firmas predictivas y mezclas secuenciales tienen valor después de contar con comparadores claros y criterios de aceptación. “Más modelos” no constituye un resultado si no cambia una pregunta medible.

## Notebooks y reproducción

La versión actual contiene **290 celdas, 111 celdas de código, 1006 líneas y 31 figuras** en siete notebooks. Las fórmulas se guardan dentro de cada ipynb, junto a código, fuentes, outputs, controles negativos y resumen con métricas calculadas. [Ejecución y hashes](execution.json).

| Notebook | Celdas | Código | Figuras |
|---|---:|---:|---:|
| [weak-iv-inference-audit](../../01-economics-and-econometrics/04-econometrics/05-instrumental-variables/weak-iv-inference-audit/notebook.ipynb) | 38 | 14 | 4 |
| [13-path-signatures-hidden-dynamics](../../02-mathematics-statistics-and-quant/advanced-research/13-path-signatures-hidden-dynamics/notebook.ipynb) | 41 | 17 | 5 |
| [channel-conformal-audit](../../03-financial-risk/01-credit-risk/fraud-and-anomaly-research/01-identity-kyc-consistency/channel-conformal-audit/notebook.ipynb) | 38 | 14 | 5 |
| [02-conformal-risk-prediction](../../05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/02-conformal-risk-prediction/notebook.ipynb) | 40 | 15 | 4 |
| [innovation-evsi-gate](../../06-strategy-innovation-and-leadership/20-ai-innovation-productivity-leadership/innovation-evsi-gate/notebook.ipynb) | 42 | 16 | 5 |
| [01-typed-decision-cascade](../../05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/01-typed-decision-cascade/notebook.ipynb) | 45 | 17 | 4 |
| [02-evidence-preserving-document-pipeline](../../05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/02-evidence-preserving-document-pipeline/notebook.ipynb) | 46 | 18 | 4 |

```bash
python -m pip install -r 05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/requirements.txt
python scripts/deepen_20261023_notebooks.py
python scripts/execute_research_depth.py --mode kernel --qa-dir artifacts/academic-review
```

Si el host bloquea sockets, usar `--mode ipython`: cada notebook corre en un proceso nuevo y guarda outputs reales. La ejecución local volvió a usar esa modalidad; no se afirma kernel Jupyter local. Las figuras nuevas se inspeccionaron en PNG y se exportaron HTML; no se certifica un frontend Jupyter completo. La revisión previa de [alineación](../2026-10-23-alignment/README.md) conserva sus conteos y hashes como snapshot anterior.

## Fallo de integración detectado y reparación

La CI de `cdf9a9c` pasó el workflow de arquitecturas con kernel y Notebook Reliability, pero falló el ciclo por entornos individuales sin pandas/SciPy. Se añadieron las dependencias a cada requirements pertinente. En `18681f3` pasaron cuatro proyectos del ciclo y falló el ejecutor previo de conformal por no añadir el directorio del proyecto a sys.path; se corrigió y se ejecutó localmente su recorrido de 15 celdas. La nueva versión debe validarse otra vez en CI. El error de importación no se clasifica como fallo matemático ni se oculta por una prueba en un entorno más amplio.

Los 36 tests originales de hoy y seis de contratos ya pasaron en la revisión precedente. Las nuevas comprobaciones son las ejecutadas dentro de notebooks: 1.500 comparaciones AR aleatorias, 100 identidades lead–lag, oráculo de 128 políticas y contraejemplos de semántica/calibración. No se afirma haber repetido todos los run.sh ni la validación independiente del ciclo en esta pasada. Dependencias directas fijadas, sin lock transitivo íntegro.

La investigación sigue siendo sintética. No hay eficacia causal estimada, cartera real, OCR aprobado, API comercial evaluada, validación regulatoria o servicio operativo. La bibliografía amplía y delimita la investigación; no completa por sí sola esas brechas.

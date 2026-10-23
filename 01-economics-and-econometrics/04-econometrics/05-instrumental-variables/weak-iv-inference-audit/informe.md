# Auditoría de inferencia IV con identificación débil

Fecha: 23 de octubre de 2026. Coordinación del ciclo y revisión independiente externas a la autoría de este componente.

## 1. Título

Anderson–Rubin frente a Wald: tamaño, incertidumbre Monte Carlo y falsación de exclusión.

## 2. Hipótesis y novedad incremental

H1: AR conserva tasa de rechazo entre 3% y 7% en tres DGP válidos con n=250 y α=5%. H2: con c=1, la distorsión absoluta de Wald supera la de AR por al menos 5 puntos porcentuales. Umbrales definidos en config.json antes de redactar conclusiones. No son teoremas ni prueba universal.

AR es clásico; no se reivindica algoritmo nuevo. Aporte incremental al laboratorio vecino: pasar de documentar colas pesadas del estimador IV a auditar decisiones de inferencia pareadas, con ledger completo, error Monte Carlo y un control negativo de exclusión inválida.

## 3. Estado del arte

- Anderson y Rubin (1949) fundamentan inferencia por restricciones estructurales sin depender de estimar con precisión la primera etapa.
- Staiger y Stock (1997) formalizan instrumentos locales a cero y distribuciones no convencionales.
- Moreira (2003) propone inferencia condicional: alternativa relevante no implementada aquí, sin afirmar dominancia de AR en poder.
- Andrews y Stock (2005) revisan inferencia débil y comparaciones de potencia; sirve para acotar nuestro alcance a tamaño.
- Andrews, Stock y Sun (2019) revisan teoría y práctica, incluyendo estructuras no homoscedásticas. Esta auditoría es intencionalmente más estrecha.

Se verificaron títulos, autores, años y enlaces identificadores mediante búsqueda web del 23-10-2026: JSTOR publicación original, sitio del autor Harvard, Wiley, Annual Reviews y NBER. No se afirma lectura íntegra ni revisión exhaustiva de literatura. `referencias.bib` conserva cinco entradas reales; búsquedas no exhaustivas de literatura clásica, no revisión sistemática de arXiv/NBER/CEPR.

## 4. Brecha

`../notebooks/01-estimation-and-robustness.ipynb` ya compara OLS/IV, fuerza del instrumento y F convencional. No contiene esta implementación AR ni un ledger de decisiones de test con controles negativos. El componente amplía esa línea, sin reemplazar notebook existente ni modificar contratos compartidos.

## 5. Diseño y configuración

DGP: z,v,e independientes N(0,1); u=0,8v+0,6e; x=cz/√n+v; y=x+u+γz. n=250, 3.000 réplicas, semillas 20261023…20264022, c∈{0,1,10}, γ=0; control negativo c=1, γ=0,2. No datos observados ni datos personales. Los datos se regeneran por semilla y el CSV guarda todos los p-valores y decisiones; hash SHA256 en JSON. Licencia de datos sintéticos: producción local del experimento, sin restricciones de terceros.

Comparación pareada: cada método recibe los mismos vectores. Entre escenarios válidos se usan idénticos shocks; bajo H0, y−β0x=u, por eso las decisiones AR son exactamente idénticas, no tres validaciones independientes. La inferencia causal requiere exclusión y exogeneidad impuestas en simulación, no contrastadas en datos reales.

Hardware y versiones se guardan en `results/summary.json`; tiempos corresponden a entorno Linux del ciclo y no a producción. Memoria medida con tracemalloc es asignación Python, no RSS ni memoria total de BLAS.

## 6. Implementación

Con variables centradas y r=y−β0x, AR calcula SSR explicada=(z′r)²/(z′z), SSE=r′r−SSR, F=SSR/[SSE/(n−2)]. Bajo H0, exclusión válida y error normal IID homoscedástico, la distribución condicional es F(1,n−2), aunque c=0. La demostración es la ortogonalidad de proyecciones gaussianas sobre el espacio de z y su complemento; numerador y denominador escalados son χ² independientes. No se extiende esa afirmación a error heteroscedástico o serial.

Wald usa βIV=(z′y)/(z′x), s²=Σ(y−βIVx)²/(n−2), SE=√[s²z′z/(z′x)²], p=2Φ(−|t|). Se evita la regresión ingenua de segunda etapa con residuos proyectados. Baseline convencional no robusto a instrumentos débiles.

`src/inference.py` tiene validación de entradas, control de rango, instrumento constante rechazado y casos degenerados explícitos. Un x constante retorna F descriptivo 0. AR no necesita dividir por z′x. No se implementan conjuntos de confianza: una futura inversión debe admitir conjuntos no acotados, vacíos o desconectados, sin truncarlos a una grilla arbitraria.

## 7. Tests y benchmarks

Comando único `bash run.sh`: instala dependencias fijadas, ejecuta unittest bajo coverage, ruff, mypy para src, experimento, benchmark y notebook secuencial. Tests: equivalencia AR con `scipy.stats.linregress`, invariancia de traslación/escala en 30 semillas, primera etapa cero, rango, NaN, longitudes/dimensiones, residual degenerado, reproducibilidad y chequeo finito de tamaño/control negativo. Esto es prueba determinística parametrizada; no se presenta como Hypothesis ni cobertura de toda distribución de entradas.

Benchmark por brazo en `results/costs.csv`: 100 llamadas, n=100/1.000/10.000, mismos datos para ambos métodos, tiempos instrumentados y pico Python. Las fluctuaciones de tiempos pequeños no implican mejor complejidad ni ventaja productiva. Fórmulas requieren O(n) aritmética y memoria; el benchmark es diagnóstico limitado de tres tamaños. No se implementa C/C++; sanitizers/ctest no aplican a este componente Python.

Resultado local: **9/9 tests pasan**, cobertura de líneas de `src/inference.py` **98% (54/55)**; ruff sin hallazgos y mypy sin errores en tres archivos de src (imports de librerías sin stubs ignorados). Notebook: cuatro celdas de código ejecutadas secuencialmente en proceso, figura revisada visualmente en PNG sin etiquetas recortadas. La inspección no incluyó un frontend completo de Jupyter.

Suite común solicitada ejecutada: `python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v`, **8/8 pasan**. Su cobertura no fue medida.

## 8. Resultados

| Escenario | F mediana | Rechazo Wald | Rechazo AR | SE MC AR |
|---|---:|---:|---:|---:|
| c=0, γ=0 | 0,476 | 14,167% | 4,967% | 0,397 pp |
| c=1, γ=0 | 1,095 | 11,600% | 4,967% | 0,397 pp |
| c=10, γ=0 | 99,629 | 4,967% | 4,967% | 0,397 pp |
| c=1, γ=0,2 | 1,095 | 35,333% | 87,267% | 0,609 pp |

H1 y H2 se satisfacen en esta corrida. Para c=1 la diferencia AR−Wald es −6,633 pp con SE pareado 0,573 pp: banda normal MC descriptiva aproximadamente [−7,76;−5,51] pp. La misma banda no cuantifica incertidumbre de un efecto causal empírico. La figura y CSV se generan, no se editan manualmente.

![Rechazos](results/rejection_rates.png)

## 9. Análisis crítico y ablations negativas

Quitar relevancia (c=0) no destruye el tamaño de AR pero elimina información identificadora de β: “no rechazar” no equivale a estimar con precisión ni a ausencia de efecto. Aumentar c hasta 10 elimina la ventaja en tasa agregada de rechazo; ambos métodos rechazan 149/3.000 aunque no necesariamente las mismas réplicas. Romper exclusión (γ=0,2) destruye la interpretación de tamaño nominal para ambos; AR rechaza 87,27% aun siendo β=1. Esto refuta la lectura de “AR válido” como certificado de causalidad o instrumento válido. No usamos F>10 como prueba universal.

## 10. Limitaciones, ética y madurez

No se estima poder ni curvas de alternativas, no errores no normales/heteroscedásticos, series/clusters, varios instrumentos o regresores, covariables adicionales, selección de instrumentos ni muestras reales. No inferir bondad operacional ni consejo de política económica. Datos sintéticos eliminan problemas de privacidad pero también evidencia de validez externa. Novedad limitada al repositorio y empaquetado experimental. Madurez **S2 local**, sin afirmar S3/S4, ni equivalencia automática con M2. Verificación independiente pendiente de revisor del ciclo.

## 11. Cómo correr

Desde esta carpeta: `bash run.sh`. Entorno Python 3.11+ con venv y acceso a PyPI; requirements fija versiones directas (no lock transitivo con hashes). El notebook se ejecuta secuencialmente en IPython en proceso limpio, guardando stdout/outputs ricos; no se lanza kernel Jupyter. Esta decisión permite reproducir dentro de entornos que restringen sockets, y se declara en metadatos. No equivale a comprobar compatibilidad con todos los frontends de Jupyter.

## 12. Referencias BibTeX

Cinco entradas completas con DOI o URL en `referencias.bib`; las citas se vinculan a sus límites metodológicos en §3.

## 13. Rúbrica de autor (1–5)

| Novedad | Rigor | Reproducibilidad | Código | Claridad | Impacto | Honestidad | MVP |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 4 | 4 | 4 | 4 | 3 | 5 | 4 |

Autoevaluación, no revisión externa. Sin datos reales, búsqueda exhaustiva ni poder, no corresponde puntaje máximo de rigor/impacto.

## 14. Siguiente iteración

1. En este componente: estimar potencia con alternativas β≠β0 y comparar con inferencia condicional cuando sea comparable.
2. En `04-econometrics/05-instrumental-variables`: ampliar AR a covariables/varianza robusta y documentar cambio de garantía finita a asintótica.
3. En `04-econometrics/05-instrumental-variables`: inversión analítica que preserve conjuntos no acotados/desconectados, contrastada con casos conocidos.

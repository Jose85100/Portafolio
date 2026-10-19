# Laboratorio de refutación: tres contraejemplos económicos

**Objetivo:** someter teorías y estimadores a condiciones donde sus conclusiones cambian. Refutar una **afirmación no condicionada** no equivale a refutar un teorema bajo sus supuestos. No se presenta evidencia empírica.

## I. Difference-in-Differences
Estimando ATT=E[Y(1)-Y(0)|D=1,post]. En dos grupos y dos períodos, DiD = (YT,post-YT,pre)-(YC,post-YC,pre). Si el crecimiento contrafactual de tratados excede al de controles en delta, E[DiD]=ATT+delta. **Contraejemplo:** ATT=2, delta=1.5 => límite 3.5. La prueba de pretrends no demuestra tendencias paralelas en el post; anticipación, composición, spillovers y shocks diferenciales son amenazas. Vertientes: event study, synthetic control, DiD doblemente robusto, adopción escalonada con ATT grupo-tiempo (evitar promedios TWFE con pesos negativos bajo heterogeneidad).

## II. Curva de Phillips
La NKPC idealizada pi_t=beta E_t pi_{t+1}+kappa x_t+u_t requiere expectativas, rigideces nominales y condiciones de equilibrio. Regresar inflación sobre brecha sin controlar expectativas y endogeneidad NO identifica kappa. Contraejemplo algebraico con expectativas fijas: pi=kappa*x+u, x=v-a*u, u y v independientes N(0,1). Entonces plim beta_OLS=kappa-a/(1+a²). Para kappa=.3 y a=1, el coeficiente observado es -.2 aun con kappa estructural positiva. **No demuestra pendiente estructural negativa**. Vertientes: Phillips híbrida, expectativas adaptativas/racionales, rigidez salarial, inflación importada, regímenes de credibilidad, modelos de precios flexibles y curvas no lineales. Falsación: comparar instrumentos válidos, expectativas medidas, shocks de oferta y cambios de régimen; no inferir causalidad de correlaciones móviles.

## III. Riesgo macrocrediticio
EL=sum_i PD_i LGD_i EAD_i es una identidad de expectativa **solo si** PD, LGD y EAD están definidos de manera compatible y LGD/EAD son valores condicionales apropiados o se cumplen las factorizaciones necesarias. No implica que la distribución de pérdidas esté identificada. Dos obligados con PD=.1, LGD=1, EAD=100 tienen EL=20 tanto bajo independencia como bajo correlación de defaults. Sin embargo P(ambos incumplen) cambia: bajo independencia .01; con dependencia positiva aumenta. Vertientes: cópulas, modelo gaussiano de un factor, contagio en redes, LGD dependiente del ciclo, riesgo de concentración y stress conjunto. Refutar la afirmación **«igual EL implica igual riesgo de cola»**, no la linealidad de la esperanza.

## Contratos computacionales
Código en `src/counterexamples.py`, pruebas en `tests/test_counterexamples.py`, escenarios en `benchmarks/run.py`. Se usan semillas fijas y datos sintéticos; el experimento reporta coeficientes y pérdidas. Los tests emplean tolerancias Monte Carlo, no certifican inferencia causal.

```bash
python -m unittest discover -s 01-economics-and-econometrics/theory-refutation/tests -p 'test_*.py' -v
python 01-economics-and-econometrics/theory-refutation/benchmarks/run.py
```

## Preguntas para el investigador
1. ¿Qué hipótesis hace que la conclusión sea un teorema y cuál la vuelve una asociación?
2. ¿Puede una intervención endógena invertir el signo de un coeficiente observado?
3. ¿Qué hipótesis son falsables y cuáles son restricciones de identificación no contrastables con los mismos datos?
4. ¿Qué predicción diferencia las vertientes rivales fuera de muestra?
5. ¿Qué resultados sobreviven al cambio de muestra, régimen, unidad de medida y mecanismo de selección?

## Bibliografía para contraste
- Angrist & Pischke (2009), *Mostly Harmless Econometrics*.
- Callaway & Sant'Anna (2021), *Difference-in-Differences with Multiple Time Periods*, Journal of Econometrics.
- Galí (2015), *Monetary Policy, Inflation, and the Business Cycle*.
- Mankiw & Reis (2002), *Sticky Information Versus Sticky Prices*, QJE.
- Vasicek (2002), *Loan Portfolio Value*, Risk.
- McNeil, Frey & Embrechts (2015), *Quantitative Risk Management*.

**Limitación central:** estos tres contraejemplos no sustituyen una revisión de las demás teorías de la carpeta ni prueban que los modelos económicos sean falsos en datos reales.

# Profundización matemática: pérdida crediticia con un factor sistemático

## Formulación y supuestos

Para cada crédito \\(i\\), sea \\(p_i\\) la PD incondicional, \\(g_i\\) la LGD determinista y \\(e_i\\) la EAD determinista. Definimos

\\[
A_i=\\sqrt{\\rho_i}Z+\\sqrt{1-\\rho_i}\\varepsilon_i,\\qquad
D_i=\\mathbf{1}\\{A_i<\\Phi^{-1}(p_i)\\},
\\]
\\[
L=\\sum_{i=1}^{N}D_i g_i e_i.
\\]

Con \\(Z,\\varepsilon_1,\\ldots,\\varepsilon_N\\) normales estándar independientes y \\(0\\le\\rho_i<1\\), se tiene \\(A_i\\sim N(0,1)\\). Por lo tanto,

\\[
\\mathbb P(D_i=1)=p_i,\\qquad
\\mathbb E[L]=\\sum_i p_i g_i e_i.
\\]

La correlación de activos entre dos deudores es \\(\\sqrt{\\rho_i\\rho_j}\\), **no** \\(\\rho_i\\) en general. Condicionado en \\(Z=z\\), los incumplimientos son independientes y

\\[
p_i(z)=\\Phi\\left(\\frac{\\Phi^{-1}(p_i)-\\sqrt{\\rho_i}z}{\\sqrt{1-\\rho_i}}\\right).
\\]

La varianza total puede descomponerse mediante

\\[
\\operatorname{Var}(L)=
\\mathbb E[\\operatorname{Var}(L\\mid Z)]
+\\operatorname{Var}(\\mathbb E[L\\mid Z]).
\\]

El segundo término mide la contribución de dependencia sistemática, ausente en el modelo de defaults independientes.

## Medidas de riesgo

Para \\(\\alpha\\in(0,1)\\), \\(VaR_\\alpha(L)=\\inf\\{x:F_L(x)\\ge\\alpha\\}\\). El Expected Shortfall se define como

\\[
ES_\\alpha(L)=\\frac{1}{1-\\alpha}
\\int_\\alpha^1 VaR_u(L)\\,du.
\\]

La implementación estima el ES de la distribución empírica tomando la cola superior de masa exacta \\(1-\\alpha\\), con peso fraccional en la observación frontera. Esta convención funciona incluso con pérdidas discretas y empates. El capital económico ilustrativo se define como \\(\\max(0,VaR_\\alpha-EL)\\); **no** equivale automáticamente a capital regulatorio.

## Reproducibilidad

```bash
python 03-financial-risk/credit-portfolio-strategy/copula-gaussiana-perdidas/modelo_avanzado.py
python -m unittest discover -s tests -p 'test_credito_avanzado.py' -v
```

La semilla controla reproducibilidad. La simulación procesa escenarios por lotes para reducir memoria de \\(O(SN)\\) a \\(O(BN+S)\\), donde \\(S\\) es número de escenarios y \\(B\\) el tamaño del lote.

## Interpretación y limitaciones

1. La correlación sistemática modifica la distribución y el capital de cola, **no** la pérdida esperada analítica bajo LGD/EAD fijas y PD marginales invariantes.
2. Una cópula gaussiana no garantiza dependencia de cola extrema. Comparar con t-cópula y modelos de regímenes es un paso posterior.
3. LGD y EAD deterministas excluyen wrong-way risk, recuperaciones estocásticas y líneas revolventes.
4. Con \\(\\alpha=0.999\\) y 50 000 escenarios hay aproximadamente 50 observaciones en la cola; el ES extremo puede presentar error Monte Carlo material. Estimar incertidumbre con múltiples semillas y aumentar escenarios antes de interpretar diferencias pequeñas.
5. La PD debe calibrarse a horizonte y definición de default homogéneos. No se puede presentar esta simulación como modelo IFRS 9 validado sin horizonte, escenarios prospectivos y calibración.

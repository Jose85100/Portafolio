# Marco matemático y estadístico transversal

## 1. Definición formal del sistema

Fijar espacio de probabilidad (Ω,F,P), filtración (F_t), horizonte T, entidad, moneda, unidad y fecha de disponibilidad. Un riesgo r define observables Y_r, estados latentes X_r, acciones A_r y un funcional de decisión ρ_r(Y_r).

No todas las medidas ρ_r son monetarias: pueden representar continuidad, cobertura, retraso o incumplimiento de control. Evitar agregaciones dimensionalmente inconsistentes.

## 2. Medidas monetarias

Para pérdida integrable L, EL=E[L]. VaR_α(L)=inf{l:P(L≤l)≥α}. ES_α(L)=(1/(1−α))∫_α^1 VaR_u(L)du; esta definición maneja masas en el cuantil.

Para L=Σ_i L_i, E[L]=Σ_i E[L_i], pero Var(L)=Σ_i Var(L_i)+2Σ_{i<j}Cov(L_i,L_j). La suma de VaR individuales no es en general VaR del agregado. ES es subaditiva bajo integrabilidad.

## 3. Inferencia estadística

Definir estimando θ(P), mecanismo de observación y likelihood o momentos. Reportar identificación, censura, truncamiento, sesgo de selección, drift, incertidumbre aleatoria y epistemológica. Emplear intervalos calibrados y validación por horizonte.

## 4. Dinámica y optimización

X_{t+1}=f_θ(X_t,A_t,Z_t,ε_{t+1}). Optimizar E[C(A)+L(A)] sujeto a restricciones de capital, liquidez, conducta y operación. Explicitar información disponible al decidir, incertidumbre de escenarios y causalidad de políticas.

## 5. Dependencia y estrés

Estimar dependencia condicional, cola y contagio, sin asumir independencia por comodidad. Documentar límites de cópulas, modelos de factores, redes y correlaciones extremas. Escenarios adversos no son necesariamente pronósticos probabilísticos.

## 6. Verificación matemática

Exigir invariantes, casos degenerados, límites, sensibilidad, error de discretización, estabilidad y convergencia. Los teoremas requieren supuestos y demostraciones; los experimentos no los sustituyen.

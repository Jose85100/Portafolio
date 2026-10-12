# I. Matemática de Digital Twins

Modelo de estado: x_{t+1}=f_θ(x_t,u_t,z_t,w_t), y_t=h_θ(x_t)+v_t. En tiempo continuo: dX_t=μ_θ(X_t,u_t,t)dt+σ_θ(X_t,u_t,t)dW_t; observar solo si existen supuestos de regularidad. Formalizar filtración, observabilidad, identificabilidad, estabilidad de Lyapunov y controlabilidad.

**Contrafactuales:** comparar políticas bajo un mecanismo estructural explícito, no interpretar simulaciones correlacionales como efectos causales. Definir costo J(π)=E[Σ γ^t ℓ(X_t,u_t)] sujeto a restricciones de riesgo. Analizar propagación de errores de modelo y sensibilidad al horizonte.

# MVP: exposición heterogénea a un factor común

**Pregunta.** ¿Cuánto cambia el regret de una mezcla si la perturbación compartida por cada estado rival tiene una carga distinta según la acción propia?

**Hipótesis.** Con `u_ij=A_ij+λ_i f_j`, `|f_j|≤δ`, estrategias `p,q` normalizadas, el certificado es `R(δ)=max(0, max_a[g_a+δ |λ_a−p·λ| Σ_j q_j])`, donde `g_a=Σ_j q_j(A_aj−Σ_i p_i A_ij)`. Si ambas cargas son iguales, el shock se cancela exactamente. Umbral de demostración: tolerancia numérica `1e-12`; alerta económica ilustrativa si `R>0.25`.

**Comparación de opciones.** Se selecciona factor común con carga heterogénea: extensión algebraica directa y falsable al audit ya hecho. Quedan pospuestos (i) prior incierto de un juego bayesiano, porque cambia el estimando y requiere tipos; (ii) más de dos acciones, que exige generalizar y validar la interfaz; (iii) distribución probabilística calibrada, porque no hay datos para identificarla. Las tres opciones comparadas, incluido el modelo rectangular previo, constan en `informe.md`.

**Datos/evidencia.** Solo juego diseñado 2×2, matrices y estrategias declaradas en `config.json`. No hay observaciones, calibración, licencia externa, ni inferencia empírica. La semilla se registra por convención; este cálculo es determinista.

**Ejecución.** Desde esta carpeta: `bash run.sh`. Produce prueba unitaria, lint, tipos, `results/comparison.csv`, `results/summary.json`, `results/sensitivity.png` y notebook ejecutado con salidas visibles.

**Estado.** MVP computacional reproducible; derivación cerrada bajo supuestos. No es evidencia sobre comportamiento real, equilibrio, ni publicación validada.

# MVP: expectativa robusta KL con diagnóstico primal-dual

**Qué es:** primer prototipo S2 acotado del programa 03. Resuelve sup E_q[loss]
sujeto a KL(q||p)<=rho en soporte finito conocido; enumera un ejemplo de dos acciones.

**Cómo corre:** `make run` en esta carpeta. Python 3.11+, make e internet para pip.
Instala versiones directas, ejecuta lint/tipos/tests, benchmark, notebook e informe.

**Qué produce:** pesos adversarios, valores y cotas numéricas; CSV/JSON de precisión,
factibilidad, tiempos y memoria; datasets; figura; notebook ejecutado; evidencia
de pruebas/cobertura; informe y cinco referencias verificadas. Conserva el primer
experimento fallido en benchmarks/initial_baseline, sin alterar sus resultados.

**Qué NO cubre:** Wasserstein DRO, calibración del radio, probabilidades nominales
cero, escenarios desconocidos, garantías fuera de muestra, minimización continua
sobre decisiones ni capital financiero. El ejemplo es sintético, no asesoría de
inversión/crédito. Cotas float64 con tolerancias, no certificados formales.
EL=83 permanece intacto; no se modifica quant-libraries.

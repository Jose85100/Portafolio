# MVP: regret ante shocks comunes por estado

Pregunta: ¿un shock de payoff común a todas las acciones propias cambia el regret? Hipótesis: no, si depende solo de la acción rival. Resultado teórico: el término se anula porque las probabilidades propias suman uno. Se contrasta con el baseline de errores independientes por celda del MVP anterior.

Tres candidatas comparadas: shock común por estado (seleccionada); incertidumbre de prior bayesiano (pospuesta por alcance de identificación); más de dos acciones (pospuesta por necesitar otro oráculo). La extensión es auditoría/adaptación de ingeniería, no novedad científica atribuida.

Reproducir: `python3 benchmarks/structured_uncertainty.py` desde la raíz del proyecto existente. Produce CSV, JSON y PNG en `results/structured_uncertainty/`. Juego diseñado y sintético. Limitación: matriz 2×2 y un perfil; no estimación empírica. Madurez del incremento: prototipo local; no elevar nivel S del programa.

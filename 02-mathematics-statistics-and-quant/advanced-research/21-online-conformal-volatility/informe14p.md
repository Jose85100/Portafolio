# Informe de investigación — adaptación conforme a cambios de escala

**Fecha:** 2026-11-10 · **Estado:** prototipo S2 · **Madurez:** experimental sintético. Este informe contiene catorce páginas editoriales (separadas por `\newpage`); resultados reproducibles viven en `results/`.

## Página 1 — Resumen

Este estudio compara intervalos conformes simétricos con calibración congelada y una ventana móvil después de un salto de volatilidad. La pregunta es operacional y estrecha: si el conjunto reciente de errores absolutos mejora la cobertura tras un cambio de escala iid. La evaluación incluye régimen estacionario, salto 2x y una prueba de estrés 4x. El resultado computado por `run_study.py` es descriptivo: no valida series dependientes ni demuestra cobertura condicional. La investigación no reclama un algoritmo nuevo; aporta un protocolo pequeño auditable y reproducible dentro del currículo cuantitativo.

\newpage
## Página 2 — Motivación

Una banda predictiva construida con errores pasados puede perder cobertura cuando cambia la escala de los errores. Una banda congelada es estable y fácil de auditar, pero conserva un cuantil obsoleto. Una ventana móvil sustituye gradualmente observaciones antiguas por nuevas. Esa adaptación reduce el retraso si el cambio persiste, aunque aumenta variabilidad y puede perseguir ruido. Esta tensión importa en monitoreo, pero una simulación estilizada no habilita recomendaciones de riesgo. Separar reacción de garantía teórica es central: una mejor cobertura experimental en un escenario no implica cobertura nominal general.

Antes de escoger esta pregunta se compararon tres ideas: (A) ACI online bajo cambios arbitrarios, relevante y respaldada por teoría publicada, pero más costosa de implementar con rigor; (B) ventana móvil tras un salto de escala, elegida por permitir verdad conocida, baseline congelado, oráculo y prueba negativa reproducible; (C) conformalización de un modelo GARCH con residuos dependientes, más cercana al uso financiero, pero sin evidencia temporal licenciada ni una especificación validada en este paquete. B aporta un benchmark docente ejecutable; A queda como comparador futuro y C como ruta de validación realista.

\newpage
## Página 3 — Pregunta e hipótesis

Pregunta: para innovaciones gaussianas independientes, centradas en cero, ¿la ventana de 200 errores recientes recupera mejor cobertura posterior a un salto de escala 1 a 2 que calibrar una sola vez con las primeras 200 observaciones? Hipótesis registrada antes de ejecutar: sobre las 20 semillas de configuración, la diferencia de cobertura posterior al salto excede 0.10 en promedio. Se mide ancho medio también, porque cobertura ilimitada no es útil. Un escenario fijo comprueba costo en régimen estable; el salto 4x examina robustez de la afirmación. El umbral es un criterio descriptivo elegido para este ejercicio, no un contraste inferencial.

\newpage
## Página 4 — Supuestos y notación

Sea `Y_t = sigma_t Z_t`, con `Z_t` iid N(0,1), centro conocido cero, y `sigma_t=1` hasta un instante de cambio, pasando después a `c`. El puntaje es `S_t=|Y_t|`. Una calibración contiene `m` puntajes. `alpha` denota la tasa nominal de no cobertura. Con puntajes intercambiables, el rango de un próximo puntaje entre `m+1` valores es uniforme (con empates, conservador); el cuantil de orden apropiado ofrece cobertura marginal de al menos `1-alpha`. El salto rompe intercambiabilidad entre calibración previa y observaciones posteriores.

\newpage
## Página 5 — Fórmula

Ordene los puntajes `S_(1) <= ... <= S_(m)` y calcule `k=min(m, ceil((m+1)(1-alpha)))`; `q=S_(k)`. El intervalo simétrico para centro `mu_t` es `C_t=[mu_t-q,mu_t+q]`. La anchura es `2q`. La versión fija usa los primeros `m` puntajes para todo el horizonte evaluado. La versión móvil en el instante `t` usa los `m` puntajes inmediatamente anteriores. Al truncar `k` a `m`, el código devuelve un intervalo finito cuando la convención conformal requeriría cuantil infinito en muestras muy pequeñas; aquí m=200, de modo que ese caso no se presenta. En general debe declararse tal truncamiento como una convención operativa.

\newpage
## Página 6 — Argumento de validez

Bajo intercambiabilidad de `S_1,...,S_m,S_{m+1}`, el rango de `S_{m+1}` es uniforme si no hay empates. Por ello la probabilidad de que supere `S_(k)` está controlada por el rango elegido y la cobertura es al menos la nominal, con discretización conservadora. La simetría de errores traduce el umbral absoluto en un intervalo central. El argumento no se aplica automáticamente a ventanas consecutivas dependientes ni a una transición de distribución. La cobertura marginal tampoco implica cobertura condicional para cada covariable o instante. La garantía pertenece al protocolo intercambiable, no al hecho de que un cuantil se actualice cada período.

\newpage
## Página 7 — Actualización e invariantes

La implementación calcula cada cuantil directamente desde la ventana precedente, por lo cual su costo es `O(m log m)` con partición parcial y memoria `O(m)`. El estado lógico es una secuencia finita de errores absolutos. Invariantes verificados: `alpha` está en `(0,1)`, puntajes finitos y no vacíos, mismos tamaños en verdad y límites, y límite inferior no mayor al superior. La semilla se fija por réplica. Se favorece recomputar el estadístico para claridad; estructuras de orden dinámicas podrían bajar costo, pero requieren pruebas adicionales ante valores repetidos y eliminaciones.

\newpage
## Página 8 — Diseño experimental

Cada configuración define `n=2400`, un cambio en `t=1200`, ventana `m=200`, `alpha=.1` y 20 semillas. Se generan tres trayectorias independientes por semilla, una por escenario. Se evalúan cobertura global, cobertura posterior, ancho medio, algoritmo fijo y móvil. El análisis posterior comienza en el punto de cambio; por tanto incluye transitorio de la ventana. El conjunto de semillas está fijado en JSON y se guardan las trayectorias completas para auditoría. No se estima valor p ni intervalos de confianza poblacionales en esta entrega.

\newpage
## Página 9 — Baselines y oráculo

El baseline empírico primario es el cuantil conformal inicial congelado; usa exactamente los mismos datos de calibración que el método móvil y permite aislar el efecto de actualización. En el régimen gaussiano de escala conocida, el oráculo poblacional simétrico tendría semiancho `sigma Phi^-1(1-alpha/2)`. El oráculo no se ajusta con datos y sirve como referencia teórica de eficiencia, no como competidor ejecutable en las tablas actuales. Esta limitación se resuelve en la siguiente iteración: agregar ancho y cobertura del oráculo por régimen, declarar claramente que conoce `sigma_t`, y no mezclar esa información privilegiada con el baseline implementable.

\newpage
## Página 10 — Resultados y lectura

En 20 réplicas, el escenario 2x produce cobertura posterior media 0.588 para el umbral fijo y 0.881 para el móvil; el oráculo de escala conocida da 0.897. La ventana móvil mejora cobertura 0.293 frente al umbral congelado, superando el criterio descriptivo de 0.10. Aumenta su anchura para reflejar la nueva escala. En estacionariedad, ambos métodos conservan aproximadamente 0.90 de cobertura y ancho similar (3.33 fijo, 3.32 móvil), aunque el fijo muestra más variación entre semillas. La figura muestra una trayectoria representativa; el JSON y CSV agregados son fuente autoritativa. Ninguna cifra es evidencia empírica real.

\newpage
## Página 11 — Sensibilidad y caso negativo

El escenario 4x es un resultado negativo para cualquier promesa de cobertura universal: la banda móvil tiene cobertura posterior 0.871, todavía menor que 0.90, y ancho promedio 8.42 frente a 3.33 del fijo. Su ganancia de cobertura exige intervalos 2.5 veces más anchos. La tabla `sensitivity.csv` cambia ventana 50–400 en una trayectoria 2x; coberturas móviles posteriores van de 0.900 a 0.870, señal de demora cuando la ventana crece. `calibration_size.csv` prueba n=20,50,100,200,400 en régimen estacionario sobre las mismas semillas; un tamaño pequeño aumenta ruido del umbral y uno mayor reduce la velocidad de reacción. Las dimensiones todavía pendientes son frecuencia de cambio, retorno, alpha, colas t, autocorrelación y estimación del centro.

\newpage
## Página 12 — Verificación de software

`make check` invoca pruebas estándar `unittest`, luego reproduce todos los artefactos. Se verifican el estadístico de orden conocido, rechazo de alpha inválido y calibración vacía, cobertura exacta, orden de límites, reproducibilidad de semilla, vector constante y ventaja esperada de adaptación en un salto grande. Las pruebas son verificaciones mecánicas del código, no pruebas de validez estadística. Python conserva tipos explícitos para arrays NumPy. El estilo se limita a herramientas de la biblioteca estándar porque el entorno de investigación puede no tener linters instalados; `compileall` es parte del chequeo recomendado.

\newpage
## Página 13 — Literatura y originalidad

La literatura contiene validez conforme clásica, adaptación a cambios y métodos específicos para series temporales (Shafer y Vovk; Gibbs y Candès; Zaffran et al.; Barber et al.; Xu y Xie). Este proyecto no supera esos métodos ni propone cobertura bajo dependencia. Su valor es pedagógico y metodológico: contraste legible entre umbral congelado y móvil, experimento con verdad conocida, reproducción por una orden y control negativo. La búsqueda bibliográfica inicial no sustituye una revisión sistemática ni comprobación de texto completo; DOI y páginas enlazados permiten verificar las referencias.

\newpage
## Página 14 — Limitaciones, madurez y decisión

Estado S2. No hay datos externos, dependencia temporal, observación de precios, prueba de cobertura condicional, corrección de selección ni validación independiente. El resultado es un benchmark de simulación bajo supuestos explícitos. Próximo paso: añadir AR/GARCH, cambios reversibles y colas pesadas; comparar con Adaptive Conformal Inference y métodos de conformalización de series; construir bandas de incertidumbre entre réplicas y cuantificar demora. Solo una replicación externa con partición temporal, licencia clara y evaluación de fallos permitiría considerar S4. No usar para límites regulatorios, capital, pricing ni decisiones de crédito.

La carpeta 21 se mantiene separada: 05 trata memoria fraccional y estimación/propiedades de memoria; `streaming-moments` trata estabilidad y composición numérica de momentos. Sus hipótesis y oráculos no miden cobertura predictiva ni adaptación a drift. La matriz de selección completa, con brecha, relevancia, diferencia, utilidad, viabilidad y evidencia para tres ideas, está en `prior_art.md`.

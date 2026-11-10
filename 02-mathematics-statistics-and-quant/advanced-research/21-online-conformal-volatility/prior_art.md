# Búsqueda de antecedentes (10-11-2026)

El proyecto trata calibración predictiva, no reivindica un método conformal novedoso. La comparación de ventanas es una evaluación didáctica del compromiso adaptación-estabilidad bajo un cambio de escala controlado.

1. Vovk, Gammerman & Shafer (2005), *Algorithmic Learning in a Random World*, Springer. Base de predicción conforme y validez bajo intercambiabilidad. DOI: https://doi.org/10.1007/b106715
2. Shafer & Vovk (2008), “A Tutorial on Conformal Prediction”, JMLR 9, 371–421. https://www.jmlr.org/papers/v9/shafer08a.html
3. Gibbs & Candès (2021), “Adaptive Conformal Inference Under Distribution Shift”, NeurIPS 34. https://proceedings.neurips.cc/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html
4. Zaffran et al. (2022), “Adaptive Conformal Predictions for Time Series”, ICML 2022, PMLR 162. https://proceedings.mlr.press/v162/zaffran22a.html
5. Barber et al. (2023), “Conformal prediction beyond exchangeability”, Annals of Statistics 51(2), 816–845. https://doi.org/10.1214/23-AOS2276
6. Xu & Xie (2023), “Conformal prediction for time series”, IEEE TPAMI 45(10), 11575–11587. https://doi.org/10.1109/TPAMI.2023.3272339

Estos trabajos cubren teoría conforme y adaptación temporal más completa. La aportación del repositorio es principalmente código reproducible, configuración explícita, comparador fijo, controles negativos y análisis de limitaciones; no se atribuye novedad científica. Referencias por confirmar contra texto completo antes de uso académico formal.

## Matriz comparativa

| Trabajo | Garantía/escenario | Adaptación temporal | Relación con este prototipo |
|---|---|---|---|
| Vovk et al. (2005); Shafer & Vovk (2008) | Validez marginal por intercambiabilidad | No es el foco | Justifica estadístico de orden y advierte su supuesto |
| Gibbs & Candès (2021) | Secuencias bajo shift con actualización adaptativa | Sí | Referencia más cercana; implementación mucho más rica que nuestra ventana |
| Zaffran et al. (2022) | Predicción conforme para series | Sí, varios métodos | Advierte contra tratar dependencias como iid |
| Barber et al. (2023) | Límites conformes fuera de intercambiabilidad | Marco general | Sustenta que la garantía puede deteriorarse bajo shift |
| Xu & Xie (2023) | Métodos conformes para series temporales | Sí | Baseline futuro prioritario para comparación |
| Este prototipo | Simulación iid con salto conocido | Ventana fija rodante | Experimento educativo, sin afirmación de novedad |

## Justificación de línea separada

El repositorio ya contiene inferencia robusta, dinámica, incertidumbre bayesiana, DRO, dependencia de colas y streaming de momentos. Ninguna de esas carpetas estudia calibración de intervalos predictivos con adaptación tras una ruptura de distribución. La conexión más cercana es 05 (memoria/series) y 12 (invariancia), pero aquí el objeto de estudio es validez de cobertura finita y actualización del conjunto de calibración; no estimación de memoria ni simetría. Se crea el programa 21 como nuevo tema acotado y pedagógico, no como un método científico supuestamente nuevo.

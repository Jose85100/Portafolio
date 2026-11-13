# Brecha de aplicación observada — Weighted Tail Underflow Guard

**Corte de revisión:** 11 de noviembre de 2026.

## Estado

Este subproyecto audita una condición numérica concreta: underflow al normalizar probabilidades de escenarios y efecto de ese underflow en Expected Shortfall. Los casos actuales son controlados y adversariales. La aplicación del proyecto hermano `weighted-expected-shortfall-audit/observed-treasury-rate-proxy/` muestra ES sobre una proxy histórica de duración con 714 escenarios equiprobables, pero esa serie no sirve para validar la frecuencia de underflow ni la carga real del fallback racional.

No se encontró en las fuentes oficiales abiertas disponibles un archivo que combine pérdidas de una cartera real, probabilidades de escenarios autorizadas y granularidad suficiente para reproducir la normalización del motor. Las series de mercado oficiales aportan factores observados; no aportan la exposición de un banco ni pesos internos de escenarios. Convertirlas en pesos diminutos para forzar el guard probaría otra vez un caso artificial, no una aplicación observada.

## Datos necesarios para cerrar la brecha

Se requiere una extracción institucional autorizada y seudonimizada con:

- escenarios identificados por corte, factor, horizonte y versión del generador;
- pérdida por escenario y unidad/escala declaradas;
- probabilidades anteriores y posteriores a normalización, con precisión y posible peso cero;
- cartera o exposición que originó cada pérdida, sin identificadores personales;
- ES del camino productivo y una referencia numérica independiente para los mismos insumos;
- política de umbrales, fallback, límite de tamaño y tiempos/costo admisibles.

Con esos insumos se podría medir cuántas distribuciones reales activan el guard, cuándo difiere la salida binary64 del racional y qué costo operativo implica el fallback. Hasta entonces, la evidencia existente respalda robustez matemática para escenarios construidos; no estima incidencia en producción, materialidad económica ni aptitud operativa de un portafolio.

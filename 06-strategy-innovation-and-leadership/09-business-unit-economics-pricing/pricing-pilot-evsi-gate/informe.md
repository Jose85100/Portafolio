# Informe crítico — 4 de noviembre de 2026

## 1. Título y línea
Pricing Pilot EVSI Gate, continuación del programa 09 `capacity-pricing-gate`. Pregunta: ¿cuándo el valor esperado de aprender conversión por precio justifica retrasar el escalamiento y pagar un piloto?

## 2. Hipótesis y aporte
H1: el cálculo exacto asigna masa predictiva unitaria (error absoluto <1e-10) y EVSI no negativa; el umbral cambia monotónicamente con el costo fijo manteniendo el resto constante. Aporte incremental: adaptación ejecutable de EVSI a dos opciones de precio dentro de una decisión de escalamiento. No se modifica la fórmula clásica del EVSI ni se presenta como hallazgo original.

## 3. Estado del arte
Matriz en `prior-art.md`; seis antecedentes con BibTeX en `referencias.bib`. Raiffa/Schlaifer formalizan decisión bayesiana; Lindley vincula valor informativo y experimentos; trabajos EVSI modernos ofrecen métodos de simulación y expresiones cerradas. Diferencia: implementación exacta pequeña, transparente y falsable de dos brazos Beta-Binomial para un gate de pricing.

## 4. Brecha y candidatas
(1) Precio con CVaR/capacidad: ya existe en motor09, candidata descartada por duplicación. (2) Diseño de piloto A/B por EVSI: seleccionada, añade decisión pre-escalamiento y abstención por costo. (3) Valor real de experimento con heterogeneidad/retención: valor alto, aplazado porque no hay datos de clientes ni protocolo aprobado.

## 5. Diseño y configuración
Sin dataset empírico. Dos brazos con priors Beta(11,9) y Beta(5,15), márgenes 100 y 180 unidades abstractas. n por brazo 0,5,10,20,40,80; costes 0,100,250,500. No se usa semilla porque la enumeración es exacta. Ambiente declarado: Python 3.12, matplotlib 3.9.2; configuración en `config.json`.

## 6. Fórmula e implementación
Derivación y unidades en `derivacion.md`. La extensión resuelve suma doble sobre el producto de predictivas Beta-Binomial. Complejidad O(n²) por dos brazos; `lgamma` evita factoriales directos. La selección posterior incluye acción de cierre de valor cero. No ajusta hiperparámetros.

## 7. Tests y benchmarks
Seis pruebas: masa predictiva, EVSI no negativa, no deterioro de decisión previa, gate de coste alto y entradas inválidas. Benchmark de enumeración en `benchmarks/benchmark.py`; tiempos reportados desde ejecución en JSON. No hay coverage claim ni baseline artificialmente débil.

## 8. Resultados y figuras
CSV/JSON y figura se generan por `src/run.py`. La tabla cubre las 24 combinaciones. La comparación primaria es decisión inmediata contra información muestral exacta. La figura representa EVSI neta por n y coste. El notebook construye el resultado y contiene asserts; la corrida actual debe inspeccionarse en outputs antes del PR.

## 9. Crítica y ablations
Ablation n=0 debe dar EVSI=0; coste enorme debe rechazar piloto; coste cero debe aceptar si hay EVSI positiva. Riesgo de valores previos mal especificados: un prior fuerte puede ocultar heterogeneidad. EVSI es ex ante y neutral al riesgo; podría preferir piloto aunque resultado comercial adverso sea plausible.

## 10. Límites y sesgos
Supone independencia de brazos, población estable, margen constante, precio asignado al azar y observación completa. Excluye spillovers, restricciones de capacidad, selección de clientes, ventas repetidas y costos de espera. Escala abstracta, no COP ni cifras de la compañía. No ofrece recomendación ejecutiva real.

## 11. Reproducibilidad
`bash run.sh` desde carpeta MVP. Genera tests, CSV, JSON, PNG y notebook ejecutado. Dependencia directa fijada; transitivas no hash-lock. Entorno/OS registrado en log.

## 12. Referencias
Ver BibTeX y matriz de prior art. DOI/URL declarados en sus entradas; la literatura sustenta método clásico, no novedad del componente.

## 13. Madurez y rúbricas
Componente S1/M1 sintético hasta reproducir en CI y revisión. Autoevaluación original (1–5): novedad 2, rigor 3, reproducibilidad 3, código 3, claridad 4, impacto 2, honestidad 5, MVP 3. Rúbrica ampliada: profundidad 3, aporte defendible 2, calidad experimental 3, utilidad 3, reproducibilidad 3, honestidad 5. Sin elevar programa 09.

## 14. Continuidad
Continuar si un protocolo autorizado define población, randomización, guardrails y costo total del piloto; ajustar si el EVSI depende de priors débiles; cerrar si las condiciones causales no pueden cumplirse.

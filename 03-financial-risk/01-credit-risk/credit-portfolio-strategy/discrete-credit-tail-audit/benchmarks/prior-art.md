# Comparación de ideas y revisión focal25oct2026

1. Importance sampling para factor común: útil para cola rara, pero tuning/diagnóstico amplía el alcance.
2. Stress de margen/liquidez: valioso pero solapa motores y diseños de mercado-liquidez existentes.
3. **Seleccionado**: DP de pérdidas Bernoulli ponderadas, prueba de masa/momentos y concentración frente a normal. Pequeño oráculo reusable para futuras validaciones; no depende de datos ni promesas de calibración real.

Inspección main98659cc y PRabiertos[]: Vasicek existente usa binomial homogénea con factor; HHI mide concentración; weighted-expected-shortfall-audit ya resuelve ES de escenarios ponderados. Este proyecto no reivindica nuevo ES: añade construcción explícita de la distribución de una cartera heterogénea independiente sobre rejilla y su oracle de enumeración. No modifica motores compartidos.

Cinco fuentes primarias abiertas25oct: Hong2011repositorioVirginiaTech (DFT Poisson-binomial, no nuestro DP ponderado); Gordy2002Fed (granularidad/asintótico); Vasicek2002Risk (metadatos y resumen, texto completo limitado por suscripción); Acerbi/Tasche2002arXiv (ES con discontinuidades); Tasche2002arXiv (ES y atribución). Ver referencias.bib. No revisión exhaustiva ni prioridad mundial. Fuente original confirma alcance, no se inventan resultados de papers.

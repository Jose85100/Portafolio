# Causal Optimal Transport

> **Estado: S1 — diseño de investigación.** Sin código implementado, resultados empíricos ni contribución inédita demostrada.

## Pregunta de investigación

¿Cómo transportar distribuciones de trayectorias respetando filtraciones y evitando anticipación de información futura?

## Hipótesis falsable

Existe una región de supuestos y parámetros en la que el método estudiado aporta ventajas medibles sobre baselines definidos antes del experimento. Se reportarán también condiciones de fallo y casos negativos.

## Formulación matemática y supuestos

inf_{π∈Π_causal(μ,ν)} E_π[Σ_t c_t(X_{1:t},Y_{1:t})]; restricciones de no anticipación sobre kernels condicionales.

**Obligatorio en desarrollo:** definir espacios, filtraciones si corresponde, condiciones de regularidad, identificabilidad, existencia, unicidad, estabilidad, resultados demostrables y contraejemplos. Ninguna garantía se presume sin demostración o referencia verificada.

## Modelado estadístico

Comparar transporte clásico, causal y bicausal; estudiar existencia de acoplamientos, dualidad y regularización entrópica.

Separar incertidumbre de muestreo, incertidumbre paramétrica y error de especificación. Medir sesgo, consistencia cuando proceda, calibración, sensibilidad e intervalos mediante procedimientos adecuados para datos dependientes.

## Métodos numéricos y simulación

Simular procesos Markov y no Markov, cambios de régimen y filtraciones incompletas; evaluar costo, sesgo de anticipación y convergencia.

**Protocolo:** generador sintético con verdad conocida; al menos dos comparadores; validación fuera de muestra o réplicas independientes; pruebas de robustez, ablaciones, complejidad temporal y espacial, control de semillas y reproducción automatizada.

## Aplicación económico-financiera

Escenarios financieros adaptados, decisiones dinámicas y stress testing sin fuga temporal.

## Límites de interpretación

Causalidad del transporte significa no anticipación, no identificación causal de intervenciones; complejidad crece con el horizonte.

## Criterios de entrega

1. **S1 — Investigación:** revisión de literatura trazable, formalización, hipótesis y diseño experimental preespecificado.
2. **S2 — Prototipo:** `src/`, `tests/`, simuladores reproducibles y pruebas de invariantes/casos límite.
3. **S3 — Validación:** benchmarks, incertidumbre, sensibilidad, errores numéricos y resultados generados automáticamente.
4. **S4 — Evidencia externa:** datos públicos con licencia, réplica independiente, documentación de fallos y límites operativos.

## Arquitectura futura (no implementada)

```text
theory/       # definiciones, pruebas, contraejemplos
src/          # modelos y algoritmos
experiments/  # simulación, comparadores y figuras
tests/        # pruebas matemáticas y computacionales
data/         # manifiestos de datos públicos
docs/         # bibliografía, validación y limitaciones
```

**Integridad científica:** la combinación de teorías conocidas no demuestra originalidad; esta deberá establecerse frente al estado del arte.

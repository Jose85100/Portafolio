# Self-Exciting Networks & Endogenous Cascades

> **Estado: S1 — diseño de investigación.** Sin código implementado, resultados empíricos ni contribución inédita demostrada.

## Pregunta de investigación

¿Cuándo una red de procesos autoexcitados amplifica perturbaciones locales hasta generar cascadas sistémicas?

## Hipótesis falsable

Existe una región de supuestos y parámetros en la que el método estudiado aporta ventajas medibles sobre baselines definidos antes del experimento. Se reportarán también condiciones de fallo y casos negativos.

## Formulación matemática y supuestos

λ_i(t)=μ_i+Σ_j∫_0^t φ_ij(t−s)dN_j(s); K_ij=∫_0^∞φ_ij(s)ds; ρ(K)<1 para Hawkes lineal excitatorio estacionario.

**Obligatorio en desarrollo:** definir espacios, filtraciones si corresponde, condiciones de regularidad, identificabilidad, existencia, unicidad, estabilidad, resultados demostrables y contraejemplos. Ninguna garantía se presume sin demostración o referencia verificada.

## Modelado estadístico

Inferencia de kernels, espectro de reproducción, redes dinámicas y extensiones no lineales.

Separar incertidumbre de muestreo, incertidumbre paramétrica y error de especificación. Medir sesgo, consistencia cuando proceda, calibración, sensibilidad e intervalos mediante procedimientos adecuados para datos dependientes.

## Métodos numéricos y simulación

Choques localizados, redes cambiantes, inhibición y ruido exógeno; tamaño y duración de cascadas.

**Protocolo:** generador sintético con verdad conocida; al menos dos comparadores; validación fuera de muestra o réplicas independientes; pruebas de robustez, ablaciones, complejidad temporal y espacial, control de semillas y reproducción automatizada.

## Aplicación económico-financiera

Sincronización de precios, defaults y retiros de liquidez.

## Límites de interpretación

La condición espectral no se traslada sin más a Hawkes no lineal, kernels inhibitorios o topologías no estacionarias.

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

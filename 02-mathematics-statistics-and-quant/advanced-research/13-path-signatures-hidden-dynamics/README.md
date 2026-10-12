# Path Signatures & Hidden Dynamics

> **Estado: S1 — diseño de investigación.** Sin código implementado, resultados empíricos ni contribución inédita demostrada.

## Pregunta de investigación

¿Cuánta información dinámica recuperan firmas truncadas de trayectorias parcialmente observadas?

## Hipótesis falsable

Existe una región de supuestos y parámetros en la que el método estudiado aporta ventajas medibles sobre baselines definidos antes del experimento. Se reportarán también condiciones de fallo y casos negativos.

## Formulación matemática y supuestos

S(X)=(1,∫dX,∫_{t1<t2}dX_{t1}⊗dX_{t2},…); álgebra tensorial y equivalencia tree-like.

**Obligatorio en desarrollo:** definir espacios, filtraciones si corresponde, condiciones de regularidad, identificabilidad, existencia, unicidad, estabilidad, resultados demostrables y contraejemplos. Ninguna garantía se presume sin demostración o referencia verificada.

## Modelado estadístico

Estudiar firmas/log-signatures, regularidad de rough paths y estabilidad ante muestreo.

Separar incertidumbre de muestreo, incertidumbre paramétrica y error de especificación. Medir sesgo, consistencia cuando proceda, calibración, sensibilidad e intervalos mediante procedimientos adecuados para datos dependientes.

## Métodos numéricos y simulación

Trayectorias con iguales marginales pero distinto orden, ruido y muestreo irregular; clasificación y reconstrucción.

**Protocolo:** generador sintético con verdad conocida; al menos dos comparadores; validación fuera de muestra o réplicas independientes; pruebas de robustez, ablaciones, complejidad temporal y espacial, control de semillas y reproducción automatizada.

## Aplicación económico-financiera

Flujos de caja, liquidez, microestructura y volatilidad.

## Límites de interpretación

La firma truncada no identifica trayectorias arbitrarias; dimensionalidad crece exponencialmente con el nivel.

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

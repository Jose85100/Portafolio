# Causal Games under Partial Observability

> **Estado: S1 — diseño de investigación.** Sin código implementado, resultados empíricos ni contribución inédita demostrada.

## Pregunta de investigación

¿Cómo separar efectos de intervención y respuestas estratégicas en juegos con estados latentes?

## Hipótesis falsable

Existe una región de supuestos y parámetros en la que el método estudiado aporta ventajas medibles sobre baselines definidos antes del experimento. Se reportarán también condiciones de fallo y casos negativos.

## Formulación matemática y supuestos

b_t^i(s)=P(S_t=s|H_t^i); políticas π_i(a|b_t^i) y resultados potenciales bajo intervenciones.

**Obligatorio en desarrollo:** definir espacios, filtraciones si corresponde, condiciones de regularidad, identificabilidad, existencia, unicidad, estabilidad, resultados demostrables y contraejemplos. Ninguna garantía se presume sin demostración o referencia verificada.

## Modelado estadístico

Juegos bayesianos dinámicos, filtrado, modelos estructurales y análisis de identificación parcial.

Separar incertidumbre de muestreo, incertidumbre paramétrica y error de especificación. Medir sesgo, consistencia cuando proceda, calibración, sensibilidad e intervalos mediante procedimientos adecuados para datos dependientes.

## Métodos numéricos y simulación

Agentes con información asimétrica, incentivos cambiantes y confusión latente; comparar contrafactuales con verdad simulada.

**Protocolo:** generador sintético con verdad conocida; al menos dos comparadores; validación fuera de muestra o réplicas independientes; pruebas de robustez, ablaciones, complejidad temporal y espacial, control de semillas y reproducción automatizada.

## Aplicación económico-financiera

Competencia de precios, crédito y cobranza.

## Límites de interpretación

La estructura de equilibrio puede ser múltiple; inferencia causal requiere supuestos más fuertes que ajuste predictivo.

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

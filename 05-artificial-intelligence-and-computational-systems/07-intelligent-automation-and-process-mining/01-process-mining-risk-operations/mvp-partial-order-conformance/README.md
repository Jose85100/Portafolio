# Conformidad de trazas con orden parcial en timestamps empatados

MVP del pilar 07 de process mining: cuando varias actividades comparten timestamp, el log no establece su orden. El auditor enumera órdenes admisibles y devuelve costes mínimo/máximo de inserción/eliminación frente a una referencia secuencial finita. Emite **conformant / nonconformant / ambiguous**; si excede presupuesto emite **budget_exceeded**, sin inventar bounds.

## Reproducir

Python 3.12 y pip, desde esta carpeta:

```bash
bash run.sh
```

Instala herramientas notebook fijadas, corre 10 tests, benchmark de 1.200 trazas/3 métodos y notebook de cuatro celdas con outputs. El núcleo sólo usa biblioteca estándar. Entorno preparado: `PYTHON=/ruta/python SKIP_INSTALL=1 bash run.sh`.

## Resultado sintético

- Desempate arbitrario recibido:252/1.200 veredictos definitivos erróneos (21%).
- Optimista, sólo coste mínimo:240/1.200 (20%).
- Bounds exactos:0 errores definitivos;720/1.200 decisiones (60%) y 480 abstenciones (40%).

La abstención conserva información ausente: **no reconstruye el verdadero orden**. Las proporciones dependen de cinco escenarios sintéticos equilibrados, no representan prevalencias de producción.

## Aporte y límites

Adapta una idea conocida de bounds en eventos inciertos a un auditor pequeño de control y un gate de recursos. No es algoritmo nuevo frente a Pegoraro et al. No repite conformal ni outbox: aquí no hay intervalos predictivos ni efectos persistentes; se audita orden de eventos.

Lenguaje de referencia: una única secuencia, no Petri net/BPMN ni proceso con concurrencia genuina. Timestamps entre buckets deben ordenar correctamente; empates representan ignorancia, no simultaneidad causal. No repara logs, no atribuye causas y no detecta fraude.

Máximo 32 eventos y 720 permutaciones candidatas; bound factorial conservador con etiquetas repetidas. La entrada ya está normalizada en buckets ordenados; no incluye parser XES ni estimación de resolución de reloj. Rechaza sobrepresupuesto antes de enumerar.

Componente S2 ejecutado/candidato M2 local sujeto a revisión independiente; programa amplio sigue parcial. `informe.md` contiene 14 puntos; `results/` guarda event_logs.jsonl, raw.csv, summary.json, SVG y verificación de referencias. Notebook ejecutado secuencialmente con IPython in-process, no kernel aislado.

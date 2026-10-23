# MVP: gate de evidencia para innovación

- **Qué es:** motor de una etapa para decidir comprar un piloto, escalar o detener usando valor esperado neto.
- **Cómo corre:** `bash run.sh` (instala y reproduce). Entorno disponible: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`.
- **Qué produce:** diseños/sensibilidad/MC CSV, summary.json, decision_curve.png, notebook ejecutado, tests/cobertura.
- **Qué no cubre:** causalidad, estrategia multi-etapa, población finita compartida piloto/despliegue, riesgo adverso, costos inciertos, validación operacional.
- **Madurez:** componente S2 (prototipo sintético ejecutado). Programa 20 sigue S1; M2 requeriría completar revisión técnica local, no se presume equivalente a S2.
- **Ejecución notebook:** IPython real en proceso; kernel TCP bloqueado. No se simulan resultados ni se declara QA de kernel.
- **Checklist:** src sí; comando único sí; 6 tests sí; baseline numérico sí; salida sí; README/informe/referencias/MVP sí; carpeta20 sí; notebook outputs sí; revisión externa al autor coordinada por integrador.

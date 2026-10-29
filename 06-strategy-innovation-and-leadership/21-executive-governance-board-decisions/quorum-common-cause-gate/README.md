# Quorum Common-Cause Gate

Auditar la disponibilidad de un **comité operativo hipotético** cuando varias ausencias comparten una causa. El evento es poder formar un mínimo fijo de3personas con el responsable de riesgo presente; no mide votos favorables, calidad de decisiones ni validez jurídica de una junta.

Componente S2 sintético en programa21, que conserva S1 fuera de este componente. No prescribe composición real, nombramientos o cambios de estatutos.

## Reproducir

Python3.12, desde esta carpeta:

```bash
bash run.sh
```

Instala versiones directas fijadas, corre tests/cobertura, ruff, mypy, benchmark y notebook. Con entorno existente: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`. Ejecución local en venv con paquetes científicos disponibles; segundo contenedor limpio no probado. Transitivas sinhash. SinAPI ni datos personales.

## Decisión sintética

| Reservas autorizadas | Probabilidad exacta | Independencia marginal | Costo |
|---:|---:|---:|---:|
|0|0,7600|0,8512|0|
|1|0,7600|0,93328|1|
|2|0,9139|0,947644|2|

Meta0,85: el baseline independiente recomienda0reservas y da un falso pase; el diseño exacto necesita2. Se gana15,39puntos de disponibilidad a costo2unidades. No se demuestra rentabilidad ni efectividad real de gobierno.

La causa común afecta a3miembros simultáneamente. Las reservas tienen disponibilidad0,9 independiente entre sí ydelrégimen **por supuesto**. El responsable de riesgo no se sustituye. Todos los adicionales se suponen elegibles/autorizados y cuentan hacia el mínimo fijo3; al crecer N, cambia la fracción representada por ese mínimo. No sirve directamente para una regla jurídica de mayoría o quórum proporcional al tamaño.

## Límites y artefactos

`config.json`:2regímenes,4miembros base, menú0/1/2reservas. `src/quorum.py`: enumeración2^N y ley de probabilidad total, validada hasta16miembros. `results/`: planes,224masas de estados crudas (incluidos ceros), sensibilidad, escalabilidad, JSON yPNG. Notebook ejecutado,5referencias DOI/URL e informe14puntos.

Con disrupción0,8, el menú no alcanza meta. Rol obligatorio0,95 impone cota≤0,95: meta0,97inviable. Si el mínimo se eleva a4, tampoco se arregla con este menú. No se reduce el requisito para forzar éxito. Ausencias reales, independencia de reservas, conflictos, agendas ycalidad no están calibrados.

Notebook realmente ejecutado en IPython en proceso con namespace fresco ycaptura rich; noQA kernelJupyter. PNG inspeccionado; interfaz notebook completa no inspeccionada.

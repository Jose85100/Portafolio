# Ambigüedad de transición y reserva de liquidez

Extensión muy pequeña del ciclo27: mantiene flujos+1/−2 e inicial(.8,.2), pero permite intervalos de probabilidad de estrés por fila. Bellman evalúa una banda de primera ruptura bajo incertidumbre rectangular: naturaleza puede adaptar la fila a tiempo, caja y régimen. No debe etiquetarse como el supremo sobre una única matriz fija ni como intervalo de confianza.

## Reproducir — Python3.12
```bash
bash run.sh
```
Crea .venv, instala dependencias directas fijadas, ejecuta tests/cobertura/Ruff/mypy,41reservas y notebook. Entorno listo: `SKIP_INSTALL=1 bash run.sh`. Requiere el hermano `../markov-first-breach-audit/src/breach.py`, sin modificar. No es standalone fuera del checkout; checksum enmetrics.json. Transitivas sin bloqueo completo.

## Resultado sintético — caja6,H20
Probabilidades de estrés: nominal(.05,.8); intervalos q_normal∈[.03,.07],q_estrés∈[.7,.9].

| Magnitud | Resultado |
|---|---:|
| Primera ruptura nominal |25,723%|
| Banda rectangular |12,504%–46,053%|
| Reserva mínima nominal para objetivo5% |22|
| Reserva mínima robusta en rejilla |34|

La distribución inicial está fija; **no todos los modelos conservan los mismos marginales estacionarios** del ciclo27. Los intervalos son escenarios, no estimaciones ni confianza estadística. Reserva34 no es requerimiento regulatorio o consejo para una entidad real.

Resultado negativo: en este caso, la cota adaptativa coincide con una esquina de matriz fija hasta≈1e−16. No se finge valor adicional del adversario adaptativo. H1 y conjuntos singleton tampoco generan brecha de ambigüedad. La búsqueda0..30 no encontraba reserva robusta; se extendió hasta40 porque20flujos de−2 acotan la pérdida máxima, sin cambiar la hipótesis.

Cinco tests, verificación contra forwardDP27, oráculo analítico de2días,41filasCSV, figura inspeccionada, notebook realmente ejecutado enIPython secuencial, cinco referencias e informe14p. No se afirma renderHTML completo. Prototipo sintético de componente; revisión independiente y publicación reportadas aparte.

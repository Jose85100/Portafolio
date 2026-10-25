# Cola discreta de crédito y concentración

Oráculo numérico de $L=ΣwᵢDᵢ$ con defaults independientes, pesos enteros y PD conocidas. Construye PMF por convolución Bernoulli y compara VaR/ES99 con normal de momentos coincidentes y MonteCarlo. No es una nueva teoría de riesgo ni un modelo de capital regulatorio.

## Reproducir (Python 3.12)
```bash
bash run.sh
```
Instala versiones directas fijadas, ejecuta tests/cobertura/Ruff/mypy estricto núcleo, experimento y notebook. Entorno existente: `SKIP_INSTALL=1 PYTHON=python3 bash run.sh`. Recomendado activar un venv antes; transitivas no totalmente bloqueadas.

## Resultado
Dos carteras sintéticas, pérdida máxima300 y EL 6. Granular:100 pesos3; concentrada:100+20×10.

| Cartera | DP VaR99 | DP ES99 | Normal ES99 | Error normal ES |
|---|---:|---:|---:|---:|
|Granular|18|19,567|17,194|−12,13%|
|Concentrada|100|108|46,874|−56,60%|

Exacto significa distribución del modelo sobre rejilla hasta precisión flotante, no verdad empírica. La independencia es fuerte: con shock común y la misma EL 6, VaR99/ES99 verdaderos suben a300. Se documenta esa falsación.

Artefactos:60 corridas Monte Carlo crudas, PMF completo602 filas, rendimiento de tres tamaños, figura, notebook real ejecutado en IPython secuencial,cinco referencias verificadas, informe de 14 puntos y MVP.md. Figura inspeccionada; no se afirma renderHTML completo del notebook. No dependencia de kernelZeroMQ.

Madurez: componente prototipo sintético verificable, revisión independiente del ciclo separada; ningún programa completo se eleva a M2/M3. No se afirma operación, precisión en datos bancarios ni corrección para default correlacionado.

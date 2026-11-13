# Factor-loading regret audit

Extensión del `rational-family-audit` para pagos perturbados por un factor de estado rival con exposición dependiente de la acción. Compara carga común, cargas heterogéneas y errores rectangulares independientes. Todo el ejemplo es sintético.

Ejecuta `bash run.sh` una sola vez para preparar entorno fijado, correr tests/lint/tipos, regenerar CSV/JSON/PNG y ejecutar el notebook de arriba abajo. Los ocho tests de la suite económica común se ejecutan desde la raíz con `python -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v`; su resultado de esta corrida está en `results/common_tests.log`. Insumos y supuestos están en `config.json`; código modular tipado en `src/robust_regret.py`; salida y derivación en `informe.md`.

No reclama novedad científica ni equilibrio robusto. Las fuentes y límites de la revisión están en `prior_art.md`.

# Crédito finito con factor común y convergencia de cola

Extensión del oráculo independiente25oct: condicionar PD a un factor gaussiano, ejecutar el mismo DP y mezclar PMF con Gauss-Hermite. Conserva heterogeneidad y átomos. La comparación rho 0/rho 0,2 es entre supuestos de dependencia; la comparación de órdenes estudia error numérico del mismo modelo.

## Reproducir — Python 3.12
```bash
bash run.sh
```
Crea .venv, instala versiones directas fijadas, ejecuta tests/cobertura/Ruff/mypy del núcleo, benchmark y notebook. Entorno ya listo: `SKIP_INSTALL=1 bash run.sh`. PYTHON permite otro intérprete. Debe conservarse el proyecto hermano `../discrete-credit-tail-audit/src/loss.py`: se carga sin modificar, su SHA256 queda registrado. No es un archivo independiente del repositorio completo.

## Resultado sintético — PD 2%,rho latente0,2,q 99%
|Cartera|ES independiente|ES factor GH256|Cambio|
|---|---:|---:|---:|
|100×3|19,567|55,269|+182,45%|
|100+20×10|108|120,981|+12,02%|

GH256 es referencia numérica, no verdad certificada. Para granular,rho 0,2, errorES deGH16vsGH256=0,07882 y deGH128=−6,62e−11; estabilidad64→128 supera tolerancias. Oráculo bivariado analítico error≈1,11e−16.

Caso negativo rho 0,95: VaR granular cambia198→258→237 con64/128/256nodos, yES128 difiere−1,170 respectoGH256. El diagnóstico rechaza estabilidad; no se presenta el númeroGH256 como cola validada. Masa casi1 no basta.

Incluye40 ensayos Monte Carlo,16 filas de convergencia,602 filas de PMF, figura inspeccionada, notebook ejecutado realmente conIPython secuencial,cinco referencias verificadas, config, MVP e informe de 14 puntos. No se afirma render HTML completo, lock total de transitivas, operación ni validación empírica. Madurez del componente: prototipo sintético verificable; revisión independiente del ciclo aparte.

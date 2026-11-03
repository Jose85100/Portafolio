# Pérdida esperada con default y prepago competidores

MVP pequeño que diferencia PD condicional de incidencia acumulada cuando existen salidas competidoras. Default y prepago son eventos mutuamente excluyentes en cada período, condicionados a seguir activo. No se ajustan hazards, no se modifica el engineIFRS y no se afirma conformidad contable.

## Reproducir — Python3.12
```bash
bash run.sh
```
Crea .venv, instala versiones directas fijadas, ejecuta tests/cobertura/Ruff/mypy del núcleo, experimento y notebook. Entorno listo: `SKIP_INSTALL=1 bash run.sh`; PYTHON permite otro intérprete. Transitivas sin bloqueo completo; notebook realIPython secuencial y figura inspeccionada, sin afirmar renderHTML completo.

## Resultado sintético
12períodos uniformes, probabilidad condicional de default2%,prepago10%,EAD condicional100,LGD45%,descuento0,5% porperíodo:

| Modelo | Incidencia default | Pérdida descontada |
|---|---:|---:|
| Sin prepago |21,528%|9,391361|
| Salidas conjuntas |13,072%|5,737379|

El baseline supera la pérdida conjunta63,687%, manteniendo PD/EAD/LGD/descuento. Es contraste del escenario, no evidencia de provisión excesiva real. Cinco tests con oráculo racional independiente, masa conservada,5sensibilidades y24filas de cronograma. Sin MonteCarlo ni benchmark largo.

EAD está condicionada a estar activo/default; si un EAD ya incorpora prepago/supervivencia, volver a multiplicarlos duplica el ajuste. No convertir PD anual a mensual directamente: todos los parámetros deben compartir período. El modelo no ordena default y prepago artificialmente dentro del período; exige que las probabilidades de salida sumen≤1.

Ablaciones: sin prepago ambos modelos coinciden; con un solo período el prepago no cambia masa de default del mismo período bajo esta convención. Mantener PD fija a mayor prepago es una hipótesis fuerte, no evidencia de selección real de clientes. Referencias y análisis14p en informe.md. Prototipo sintético de componente, no producto operacional.

## Extensión acumulativa30: calendario e integración temporal
En la MISMA línea se añade `src/calendar.py`, con intensidades anuales por tramo y duraciones en años. La API29 sigue siendo discreta y no cambia de interpretación. `calendar_notebook.ipynb` enseña derivación LaTeX, unidades y correspondencia fórmula-código, con outputs reales y negativos.

Mismo año e intensidades.24/1.2, EAD100, LGD.45 y fuerza de descuento.06: pérdida integrada5.593462846931 frente a5.389757800769 al cierreanual (subestimación3.641841%). Al subdividir en12intervalos, pérdida exacta conserva5.593462846931 y cierre5.579211946515. Con descuento0 ambos coinciden. 18casosCSV, figura y11tests; cobertura de los dos núcleos100%85sentencias medida. `bash run.sh` reproduce ambas iteraciones; informe29.md conserva historia y informe.md documenta30. Es adaptación verificada de fórmulas conocidas, sin validación empírica ni madurez operacional.

## Incremento31octubre: EADafín
Mismo `bash run.sh` instala y reproduce extensión de `src/affine.py`,17tests y `affine_notebook.ipynb` con derivación y outputs reales. `informe31.md` reúne14p,3ideas,5fuentes y límites. Nueva salida `results/affine.csv`, JSON, figura y CSVconvergencia/escalabilidad; no se elimina evidencia29/30. Permite amortización dentro de tramos irregulares; no calibra riesgos ni demuestra originalidad científica.

## 1 de noviembre: pagos discretos y curva por eventos
`bash run.sh` reproduce `src/term_structure.py`,22tests y `term_notebook.ipynb`. Composición de la integral31 con supervivencia y descuento acumulados, permite saltos EAD sin interpolar pagos. `informe1101.md` reúne derivación, tres ideas, seis referencias y límites. Salidas `results/term_grid.csv`, `term_metrics.json`, `term_convergence.csv`, `term_scaling.csv`, `term.png`; evidencia sintética, no modelo calibrado.

## 2 de noviembre: fechas y disponibilidad declarada
`bash run.sh` añade `src/dated_contract.py` y `dated_notebook.ipynb`: ACT/365F o ACT/360 explícitos, conversión de fuerzas y sellos temporales de EAD/hazards/descuento. Fixture enteramente sintético, sin afirmar datos reales autorizados. Produce `results/dated_grid.csv`, `dated_availability.csv`, `dated_scaling.csv`, `dated_metrics.json` y `dated.png`;27 tests acumulados. `informe1102.md` explica derivación, tres ideas, literatura y límites: el gate revisa metadata declarada, no autenticidad/licencia.

## 3 de noviembre: LGD afín y producto temporal EAD × LGD
`bash run.sh` añade `src/affine_lgd.py`,32 tests acumulados y `lgd_notebook.ipynb`. Integra ambas trayectorias por evento y conserva el caso LGD constante; deriva por qué producto de medias temporales puede subestimar o sobreestimar. Salidas `lgd_grid.csv`, `lgd_convergence.csv`, `lgd_scaling.csv`, `lgd_metrics.json`, `lgd.png`. `informe1103.md` incluye14p, tres ideas, matriz de fuentes, fórmulas y límites. Escenarios sintéticos, no estimación de recuperaciones ni fórmula regulatoria nueva; aún no conecta selloLGD al adaptador fechado.


### Cierre verificado del incremento3nov

Revisión independiente del núcleo `788073c`: `bash run.sh` exit0,32 tests, Ruff, mypy en seis módulos, notebook LGD5/5 celdas e inspección de figura. Contraste adicional del revisor:500 casos determinísticos frente a SciPy `quad`, error máximo1.819e-12; sin bloqueantes dentro del alcance afín. No equivale a validación empírica de recuperaciones.

[Notebook Reliability, run41601261984](https://github.com/Jose85100/Portafolio/actions/runs/41601261984) terminó en `success` para ese head de código. [PR136](https://github.com/Jose85100/Portafolio/pull/136) permanece abierto, sin merge; los checks de commits posteriores se observan por separado. El [informe1103](informe1103.md#cierre-de-revisión-y-publicación--3-de-noviembre-de-2026) distingue ejecución, revisión, CI y publicación.

CRE35 se cita únicamente como fuente oficial contextual de archivo histórico (archived/historical), versión publicada27-mar-2020/efectiva1-ene-2023. No se presenta como norma vigente ni como evidencia de cumplimiento regulatorio.

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

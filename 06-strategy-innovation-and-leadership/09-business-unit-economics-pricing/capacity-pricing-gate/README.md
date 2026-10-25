# Capacity Pricing Gate

Escoger un precio único por período respetando capacidad y presupuesto de pérdida adversa. El motor enumera un menú exante y calcula CVaR de shortfall con **masa fraccionaria exacta en átomos**. Componente nuevo S2 sintético dentro del motor09; no se eleva la madurez del programa ni se declara producto operativo.

## Reproducir

Python3.12, desde esta carpeta:

```bash
bash run.sh
```

Crea `.venv`, instala versiones fijadas y ejecuta tests/cobertura, ruff, mypy, benchmark y notebook. Con entorno existente: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`. No API ni datos privados. Dependencias transitivas no bloqueadas por hash. La ejecución local usó venv con paquetes científicos preexistentes; instalación desde cero en segundo contenedor pendiente.

## Decisión ejecutiva sintética

| Política | Precio | Beneficio esperado | CVaR90%shortfall |
|---|---:|---:|---:|
| Plug-in demanda media, evaluado en escenarios |20|2452,00|520,00|
| Neutral al riesgo, escenarios completos |22|2725,89|592,26|
| Sujeto a presupuesto500 |18|2143,08|477,13|
| Detener |—|0|0|

Se sacrifica582,81 de beneficio esperado frente a neutral para cumplir presupuesto; no se afirma mejor rentabilidad. El plug-in predice3800 pero su valor en los escenarios es2452. Demanda fluida no son ventas observadas.

`config.json` guarda supuestos. `src/pricing.py` implementa logística estable, capacidad, cola discreta y selector. `results/` contiene menú completo, escenarios, sensibilidad, escalabilidad, MC, figura y checks. `notebook.ipynb` ejecutado ofrece fórmulas, resultados y límites; `informe.md` desarrolla14puntos y5referencias verificadas.

## Alcance

Una decisión exante, un producto, tres escenarios sintéticos, capacidad dada, costo fijo **evitable** si se detiene. Probabilidades y demanda conocidas por supuesto, sin estimación ni causalidad. El presupuesto aplica aCVaR(max(−beneficio,0)), noCVaR de pérdida firmada ni regret. No hay pricing personalizado, dinámica de inventario, competencia o costos de expansión de capacidad. Sensibilidad de capacidad no es recomendación de invertir.

El notebook se ejecuta realmente con IPython en proceso, namespace fresco y outputs rich capturados. No valida kernelJupyter, bloqueado en este entorno en ciclos anteriores. Figura PNG inspeccionada; QA interfaz notebook completa no realizado.

**Granularidad importa:** con menú fino1601, precio19,26 ybeneficio2342,66 respetanCVaR499,97. Precio18solo es óptimo del menú discreto configurado; no recomendar como óptimo continuo.

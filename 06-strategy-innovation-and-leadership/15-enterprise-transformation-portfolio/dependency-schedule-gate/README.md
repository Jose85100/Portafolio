# Dependency Schedule Gate

Calendarizar inversiones de transformación con dependencias de **terminación**, caja por período y disponibilidad de personas. El motor enumera decisiones opcionales e inicios enteros; un presupuesto estático no garantiza poder ejecutar un portafolio.

Componente S2 sintético nuevo dentro del proyecto15; no eleva la madurez del programa completo ni acredita uso operacional.

## Reproducir

Python3.12, desde esta carpeta:

```bash
bash run.sh
```

Crea `.venv`, instala dependencias directas fijadas y ejecuta tests/cobertura, ruff, mypy, benchmark y notebook. Entorno disponible: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`. Instalación limpia en segundo contenedor no comprobada; ejecución local usa venv con paquetes científicos preexistentes y mypy/ruff fijados. Dependencias transitivas sin hashes. Sin API ni datos confidenciales.

## Resultado, incluido el negativo

| Caso | Exacto NPV | Greedy factible NPV | Diferencia |
|---|---:|---:|---:|
| Analytics beneficio14, inicial |11,655966|11,655966|0|
| Analytics beneficio20 |15,903012|15,754047|0,148965|
| Analytics beneficio30 |23,416160|22,584181|0,831979|

La ambición inicial de mejorar al menos0,5 se **refuta** en el caso inicial. No se debilita deliberadamente el baseline: el greedy respeta todas las restricciones y evita actividades directamente negativas que no habilitan otras. Relajar dependencias da18,628099, pero el calendario resultante viola las precedencias originales y no es un baseline ejecutable.

`config.json`:5proyectos,4períodos, presupuesto8por período, capacidad2, descuento10% por período sintético. Costos al inicio y un beneficio al terminar; presupuestos expiran, no se financian actividades con cobros del modelo. No es tasa recomendada ni dato empresarial.

Decisión inicial: standalone inicia0, platform1, analytics/automation3; controls se omite. Toda dependencia termina antes de que empiece su descendiente. Cambiar valor habilitador puede adelantar platform a0. No implica que ampliar capacidad sea rentable: costos de contratar no están modelados.

## Artefactos y límites

`src/schedule.py`,7tests (incluido oracle MILP independiente), resultados CSV/JSON, figura, notebook ejecutado,5referencias y `informe.md` con14puntos. Exhaustivo para1–8proyectos y máximo2millones de combinaciones: exponencial, no escalabilidad empresarial. Datos deterministas; no incertidumbre, causalidad, retrasos aleatorios, preemption, financiación o regulación.

El notebook ejecuta realmente sus celdas en IPython en proceso con namespace fresco y salidas rich capturadas. No se afirma QA de kernelJupyter. Figura inspeccionada visualmente; interfaz notebook completa no inspeccionada.

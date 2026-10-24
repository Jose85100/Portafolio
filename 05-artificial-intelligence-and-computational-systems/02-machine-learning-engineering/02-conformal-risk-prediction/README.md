# Conformal Risk Prediction under Shift — auditor de masa de prueba

MVP sintético de **intervalos de regresión bajo covariate shift**, que convierte una propuesta S0/S1 en un componente S2 ejecutado. No se declara completo el programa original (series temporales abiertas, selección de muestra y evaluación operacional siguen pendientes). Según la matriz general: candidato M2 por evidencia local, sujeto a revisión independiente. No operacional.

## Reproducción

Python 3.12 y pip, desde esta carpeta:

```bash
bash run.sh
```

El comando instala versiones fijadas, ejecuta tests, regenera 2.700 filas de réplicas, JSON, figura y notebook de punta a punta. En entorno preinstalado: `PYTHON=/ruta/python SKIP_INSTALL=1 bash run.sh`. No usa red para datos, claves ni modelos; pip sí requiere paquetes disponibles.

## Pregunta y aporte

¿Qué se pierde si un cuantil ponderado ignora la masa del punto de prueba? La contribución es una **auditoría de implementación y utilidad** dentro del portafolio; el método ponderado ya existe (Tibshirani et al., 2019). Contrasta baseline sin ponderar, ablation ingenua sin masa test y método correcto que devuelve infinito si la calibración no permite un intervalo finito.

Con n=80 y cambio de mezcla 10%→80%, cobertura marginal 51,616% / 86,267% / 94,717%. El método correcto devuelve intervalo infinito en 26,3255% de puntos; no es una mejora gratuita. Bajo cambio condicional duplicando ruido cae a 79,619%. Con n=320 obtiene 90,5065% y todos los intervalos finitos.

## Archivos

`src/conformal.py`: núcleo tipado; `src/experiment.py`: simulación pareada; `tests/`: 9 pruebas y propiedades aleatorias; `config.json`: parámetros e hipótesis; `results/`: datos crudos, recursos y figura; `notebook.ipynb`: explicación y salidas; `informe.md`: análisis crítico; `referencias.bib`: cinco fuentes primarias verificadas.

## Alcance

Ratios de densidad conocidos y predictor fijo cero independiente de calibración. Garantía marginal bajo independencia, solapamiento y ley Y|X invariante; no garantía por grupo ni por calibración realizada. Pesos estimados, datos reales y dependencia temporal no están implementados. A diferencia de KYC/Mondrian en riesgo, este componente no detecta fraude ni produce p-valores de anomalía: audita intervalos predictivos generales.

## Ampliación del notebook — 23 de octubre

El notebook incorpora fórmulas, diccionario de variables en contexto, reconstrucción de cálculos, sensibilidad y casos negativos. `run.sh` conserva esta ampliación después de regenerar el estudio original. La extensión se mantiene en `scripts/deepen_20261023_notebooks.py` y `scripts/research_depth_experiments.py` desde la raíz; las celdas realmente se ejecutan y guardan sus salidas. [Revisión de alcance](../../../reviews/2026-10-23-alignment/README.md).

[Revisión académica y criterios de cierre](ACADEMIC_REVIEW.md): fuentes publicadas, fórmulas en el notebook y extensiones experimentales.

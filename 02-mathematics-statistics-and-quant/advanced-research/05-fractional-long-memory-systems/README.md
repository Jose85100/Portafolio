# Fractional Calculus & Long-Memory Systems

> **Madurez: S2 acotado — operador discreto y auditoría de memoria truncada.** La inferencia de memoria larga frente a rupturas sigue pendiente. El protocolo original se conserva debajo como agenda, no como resultados ejecutados.

## MVP ejecutable — 2026-10-19

¿Un coeficiente fraccional pequeño controla el error acumulado al cortar la memoria? Se implementa el filtro discreto `(1-L)^d` con extensión inicial cero, convolución completa directa/FFT lineal, dos memorias fijas, corte por coeficiente y selección por una cota finita de cola.

Los métodos y la aceleración FFT son conocidos. El aporte es una auditoría reproducible con prueba de la cota, contraejemplos de truncación/frontera y un oráculo de 80 dígitos, no un algoritmo fraccional nuevo.

### Instalar y reproducir con un comando

Entorno: **Python 3.12**, `make`, `venv` y acceso a PyPI. Desde esta carpeta:

```bash
make run
```

Desde la raíz de un checkout que contenga el MVP:

```bash
make -C 02-mathematics-statistics-and-quant/advanced-research/05-fractional-long-memory-systems run
```

El comando crea `.venv`, instala dependencias directas fijadas, valida lint/formato/mypy/tests con cobertura, ejecuta benchmark, genera informe y notebook con outputs y verifica el checklist. Para seleccionar intérprete: `make run PYTHON=python3.12`. No requiere datos privados ni servicios durante el experimento. Dependencias transitivas no bloqueadas: las versiones resueltas quedan en `benchmarks/environment.txt`. Una reproducción reescribe únicamente salidas generadas del MVP; tiempos y metadatos varían por máquina.

### Artefactos reales

- `src/fractional.py`: pesos por recurrencia, masas de cola, selectores y convolución causal.
- `src/reference.py`: binomiales/Gamma de mpmath y sumas a 80 dígitos.
- `src/benchmark.py`: 36 escenarios, 216 resultados y 648 registros temporizados.
- `tests/`: unitarios, propiedades Hypothesis, causalidad, frontera y errores del notebook.
- `config.json`: semillas, límites, presupuestos, hipótesis y umbrales anteriores al experimento.
- `benchmarks/`: CSV/JSON crudos, 12 entradas NPZ, seis salidas seleccionadas, figura, logs, cobertura y checklist.
- `notebook.ipynb`: ocho celdas de código ejecutadas; problema → método → datos → resultados → conclusiones.
- `informe.md`, `MVP.md`, `referencias.bib`, `fuentes.md`: prueba de cota, resultados, límites y seis referencias reales.

### Semántica y límites

`memory=m` conserva los coeficientes de rezago 0 a m: **m+1 términos**. El presupuesto controla error de truncación por escala de entrada, no error relativo respecto de la salida ni error total de una derivada continua. El horizonte N y la extensión inicial cero forman parte del contrato. Se excluyen d=0/1, órdenes negativos/variables y entradas no finitas.

El selector prepara los N pesos: no se afirma implementación streaming ni ahorro de almacenamiento total. El FFT completo usa relleno para convolución lineal, sin wraparound. La FFT circular incorrecta solo aparece como ablación documentada. La referencia directa float64 se contrasta con alta precisión en series cortas; ninguna concordancia numérica se vende como certificación formal.

### Ejecución y revisión del notebook

IPython en proceso ejecuta realmente las celdas y captura stdout/salidas enriquecidas sin sockets locales. `.venv/bin/python scripts_notebook.py --kernel` usa nbclient en entornos convencionales. El workflow general Notebook Reliability ejecuta los notebooks modificados con kernel separado; el workflow específico reproduce el MVP completo.

Las guías de notebooks y visualización orientan la separación de supuestos, evidencia y límites. Figura inspeccionada y outputs/formato validados; no se afirma revisión visual integral de un visor de notebooks. Para completarla abrir `notebook.ipynb` en Jupyter o instalar nbconvert y exportar con `python -m jupyter nbconvert --to html notebook.ipynb`.

## Protocolo S1 original — agenda fuera del alcance cerrado

## Pregunta de investigación

¿Cómo distinguir memoria larga genuina de persistencia espuria causada por rupturas estructurales?

## Hipótesis contrastable

El método propuesto supera a baselines explícitos en al menos una métrica predefinida, sin degradación inaceptable en robustez, calibración ni costo. Esta hipótesis debe operacionalizarse antes de observar resultados.

## Formulación matemática

Cov(B_t^H,B_s^H)=½(t^{2H}+s^{2H}−|t−s|^{2H}); comparar con ARFIMA y procesos con cambios.

**Trabajo teórico pendiente:** definir espacios de probabilidad y parámetros, supuestos de existencia e identificabilidad, resultados de convergencia o estabilidad, demostraciones y contraejemplos. No se presume que tales propiedades estén establecidas.

## Modelado estadístico y estimación

Estimar H mediante wavelets y local Whittle; diagnosticar rupturas y heterogeneidad.

Estimar sesgo, varianza, consistencia bajo supuestos adecuados e intervalos de incertidumbre. Separar evaluación predictiva de identificación causal.

## Métodos numéricos y protocolo experimental

Simulaciones con cambios de media, volatilidad y frecuencia de muestreo; sesgo, RMSE y tamaño de pruebas.

**Diseño mínimo:** (1) generador sintético con verdad conocida; (2) baseline trivial y avanzado; (3) evaluación fuera de muestra o por réplicas independientes; (4) ablaciones y pruebas adversariales; (5) tiempos, memoria y sensibilidad a hiperparámetros; (6) semillas, versiones y resultados reproducibles.

## Aplicación económico-financiera

Persistencia inflacionaria, volatilidad y tasas.

## Limitaciones y posibles fallos

La no estacionariedad puede imitar memoria larga; distinguir niveles e incrementos.

## Entregables y criterios de aceptación

- **S1:** revisión bibliográfica verificable, hipótesis operacionales, teoremas/proposiciones y plan preregistrado de simulación.
- **S2:** módulos `src/`, `tests/`, datos sintéticos y script de reproducción, con cobertura de invariantes y casos límite.
- **S3:** comparadores estadísticos, tablas y figuras generadas, análisis de sensibilidad, errores numéricos y benchmark de recursos.
- **S4:** réplica independiente, aplicación con datos públicos licenciados, documentación de riesgos y límites de validez.

## Estructura prevista para el programa completo (el MVP anterior sí está implementado)

```text
theory/       # supuestos, derivaciones y pruebas
src/          # modelos, estimadores y algoritmos
tests/        # tests unitarios y estadísticos
experiments/  # simulaciones y benchmarks
data/         # manifiestos y fuentes públicas
docs/         # interpretación, limitaciones y referencias
```

**Regla de evidencia:** no reportar métricas, resultados, referencias bibliográficas ni garantías matemáticas que no hayan sido verificadas.

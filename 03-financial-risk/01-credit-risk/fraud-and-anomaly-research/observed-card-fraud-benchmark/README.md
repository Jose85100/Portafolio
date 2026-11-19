# Benchmark externo de fraude transaccional con separación temporal

Evalúa la mecánica de priorizar alertas usando datos de transacciones de tarjeta; **no evalúa fraude de identidad, solicitudes de crédito, KYC ni originación**. La etiqueta de fraude corresponde al benchmark público y no se cuenta con los expedientes o con su proceso y fecha de adjudicación. No es una calibración para una institución ni demuestra desempeño actual.

## Fuente, trazabilidad y variables

- [Credit Card Fraud Detection, registro Zenodo 7395559](https://doi.org/10.5281/zenodo.7395559), copia publicada por Luqi Liu el 4-dic-2022 del conjunto atribuido a ULB y Worldline. La ficha Zenodo declara CC BY 4.0 para esta copia; verifique las condiciones del publicador original antes de redistribuir el conjunto. Copia consultada el 18-nov-2026; el CSV de 150.828.752 bytes **no se incorpora al repositorio**.
- URL de descarga: `https://zenodo.org/api/records/7395559/files/creditcard.csv/content`. MD5 reportado por Zenodo y exigido por el runner: `e90efcb83d69faf99fcab8b0255024de`. SHA-256 calculado `76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89`. Las huellas identifican una copia; no confirman independientemente la procedencia original.
- 284.807 transacciones de titulares europeos durante dos días de 2013; 492 registros etiquetados como fraude. Unidad: transacción, no cliente ni solicitud. No hay identificador de tarjeta, cuenta o comercio para verificar independencia entre partes, ni fecha de cierre de investigación.
- `Time` es tiempo relativo en segundos y sirve solo para separar bloques; `V1`–`V28` son componentes anonimizados preprocesados por el proveedor, `Amount` es importe de la transacción y `Class` la etiqueta. Se usa `log1p(Amount)` junto con los componentes. La escala e interpretación económica de los componentes no están disponibles.

## Método y límites de identificación

Se separa por cuantiles de tiempo 60/20/20 aproximadamente; los empates en el límite permanecen en un solo bloque. Escalador y regresión logística se ajustan únicamente con entrenamiento. El baseline ordena por monto. Para validación y prueba se informan `average precision` (AP, no AUC trapezoidal), precisión y sensibilidad entre el 1% de alertas. Cada política tiene el mismo cupo; empates se resuelven por el orden original de filas.

**Una separación posterior no garantiza ausencia completa de fuga:** el proveedor entrega `V1`–`V28` ya transformados y no se conoce si la transformación PCA se ajustó usando las dos jornadas completas. Tampoco hay fechas de disponibilidad o maduración de etiquetas, identificadores que permitan partición por titular, ni garantía de observación independiente. La etiqueta se trata como disponible al entrenar, supuesto que puede ser falso. Evaluar el primer 1% requiere ordenar todo el bloque retrospectivamente; no es un scheduler en línea y no incluye costos, rechazos, investigación o intervención. La duración de dos días y el cambio de población limitan estabilidad temporal y extrapolación.

## Ejecución

Con Python 3, `pandas`, `numpy` y `scikit-learn`:

```bash
curl -fL 'https://zenodo.org/api/records/7395559/files/creditcard.csv/content' -o /ruta/privada/creditcard.csv
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/01-credit-risk/fraud-and-anomaly-research/observed-card-fraud-benchmark/run.py --input /ruta/privada/creditcard.csv
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s 03-financial-risk/01-credit-risk/fraud-and-anomaly-research/observed-card-fraud-benchmark -v
```

La salida es solo JSON agregado. El archivo original permanece fuera del repositorio. El runner verifica hash, 284.807 filas, 492 positivos, columnas, datos finitos y etiquetas antes de entrenar. Para pasar de este benchmark a originación se requieren casos de solicitud con variables disponibles al momento de la decisión, revisiones y adjudicación fechadas, resultados de todos los segmentos y validación temporal independiente.

## Resultado reproducido

El archivo [results.json](results.json) registra el ejercicio ejecutado con Python, numpy 2.1.2, pandas 2.2.3 y scikit-learn 1.5.2. Los bloques contienen 170.882/56.963/56.962 transacciones de entrenamiento/validación/prueba; el último contiene solo 75 fraudes (prevalencia 0,132%). En prueba, con 570 alertas (1% redondeado hacia arriba), la regresión identifica 64/75 y la regla de monto 3/75. La precisión es 11,23% frente a 0,53%; AP es 0,6981 frente a 0,00145. Son resultados descriptivos de esta partición y este baseline sencillo, no medidas de eficacia de un producto ni garantía de desempeño futuro. El pequeño número de eventos, la correlación desconocida y los límites de preprocesamiento y etiquetas hacen incierta la generalización.

La precisión numérica de AP puede variar ligeramente entre entornos y configuraciones de BLAS por diferencias de ajuste y orden de scores casi empatados. Una repetición independiente con `OPENBLAS_NUM_THREADS=1` produjo AP de prueba 0,69815 y conservó 64/75 detecciones con 570 alertas; no se exige igualdad de los últimos decimales.

## Capacidad y umbral fuera del bloque de prueba

[Modelo y capacidad](MODEL_AND_CAPACITY.md) desarrolla la logística, la frontera precisión–recobro para cinco cupos y un umbral ajustado en validación y congelado en prueba. El resultado es un ejercicio de investigación con datos de pagos y no elimina las limitaciones del PCA, la disponibilidad de etiquetas o la evaluación retrospectiva.

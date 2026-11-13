# Revisión del 17 al 23 de octubre de 2026

Corte en America/Bogota. Revisión del repositorio `Jose85100/Portafolio`: main `634e8d9`, PR70 `789dbe2` y PR69 `764942e`. La ampliación pertenece a la PR70; los dos motores de Christoffersen de PR67/69 permanecen en sus rutas. No se fusiona ni se modifica la PR69.

## Resultado y alcance

Se revisó el historial de la semana, estructura, índices, madurez, enlaces locales y presentación/outputs guardados. El inventario actual contiene **128 notebooks**, de los cuales **88 cambiaron en la semana**. La comprobación estructural alcanza los 128; no equivale a ejecutar ni revisar matemáticamente todos sus experimentos. Los snapshots y commits están en [commits.json](commits.json), el inventario reproducible en [notebooks.csv](notebooks.csv) y los enlaces en [inventory.json](inventory.json).

La revisión profunda se concentra en los cinco MVP de hoy y dos arquitecturas nuevas: **239 celdas, 96 de código, 726 líneas de código y 25 figuras**. Se ejecutaron todas las celdas en orden, con salidas guardadas y formato nbformat válido. [Evidencia y hashes](execution.json). El tamaño describe extensión, no una calificación de calidad.

| Notebook | Celdas | Código | Figuras |
|---|---:|---:|---:|
| [weak-iv-inference-audit](../../01-economics-and-econometrics/04-econometrics/05-instrumental-variables/weak-iv-inference-audit/notebook.ipynb) | 31 | 12 | 4 |
| [13-path-signatures-hidden-dynamics](../../02-mathematics-statistics-and-quant/advanced-research/13-path-signatures-hidden-dynamics/notebook.ipynb) | 34 | 15 | 4 |
| [channel-conformal-audit](../../03-financial-risk/01-credit-risk/fraud-and-anomaly-research/01-identity-kyc-consistency/channel-conformal-audit/notebook.ipynb) | 31 | 12 | 4 |
| [02-conformal-risk-prediction](../../05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/02-conformal-risk-prediction/notebook.ipynb) | 33 | 13 | 3 |
| [innovation-evsi-gate](../../06-strategy-innovation-and-leadership/20-ai-innovation-productivity-leadership/innovation-evsi-gate/notebook.ipynb) | 33 | 13 | 4 |
| [01-typed-decision-cascade](../../05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/01-typed-decision-cascade/notebook.ipynb) | 38 | 15 | 3 |
| [02-evidence-preserving-document-pipeline](../../05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/02-evidence-preserving-document-pipeline/notebook.ipynb) | 39 | 16 | 3 |

## Hoy: contribución, supuesto y ampliación

| Dominio | Aporte del ciclo | Qué se añadió en esta revisión |
|---|---|---|
| Economía | AR frente a Wald con IV débil | Derivación F, reconstrucción por mínimos cuadrados, inversión de AR, Wilson, dispersión IV, heterocedasticidad y comparación HC1 asintótica |
| Matemáticas | Firmas de nivel 2 | Chen y shuffle, escala/reversión, convergencia, ruido con intervalos, aliasing y contraejemplo de identificabilidad |
| Riesgo | Rangos KYC por canal | Resolución finita, pooling, deriva, costos/capacidad de revisión, contaminación y repetición de calibración |
| IA | Conformal ponderado | Masa test infinita, ESS, pesos mal especificados, cambio condicional, cobertura por segmento y cobertura útil |
| Estrategia | EVSI de innovación | Derivación beta-binomial, reconstrucción de valor, prior, costo, demora, EVPI y no experimentar |

La PR70 original tenía CI aprobada en sus seis workflows consultados, incluidos Notebook Reliability y Daily multi-domain MVPs. Eso corresponde al commit `789dbe2`, no acredita esta ampliación antes de su nueva CI. [Snapshot remoto](remote-ci.json).

La PR69 de hoy no añade notebook: implementa una decisión Monte Carlo secuencial ternaria para Christoffersen. Se revisaron código, run.sh, oráculo exacto, 600 filas de trials y resumen. El resultado guardado de frontera es 0 decisiones erróneas y **167/200 abstenciones**, frente a 32/200 errores de MC fijo: no equivale a 200 aciertos ni a prueba de error poblacional cero. Se recompiló y ejecutó su binario de pruebas con g++17 y warnings estrictos; CMake no estaba instalado localmente y no se repitió ese recorrido. Su workflow C++ remoto original estaba aprobado. No se afirma haber repetido sanitizers ni los 600 ensayos.

## Carpeta y arquitecturas de IA

La ubicación es [Foundation Models / structured-decision-architectures](../../05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/), junto a la cascada existente. Se preservan diez pilares: no se crea un área paralela por marca.

1. **Decisión tipada con abstención**: contrato, proveedor, calibración, selectividad, costo y revisión. Incluye fallback falible, sensibilidad de eficacia, bootstrap de costos y latencia simulada.
2. **Documento con evidencia preservada**: snapshot, extracción, span/hash, concepto, normalización, conciliación y disponibilidad temporal. Incluye ambigüedad, Unicode, compresión que elimina correcciones y transferencia que no es ingreso.

Son diseños de integración para Jev y CDM de ScaleDown, con un prototipo local neutral. No se llama ningún proveedor ni se reproduce su arquitectura propietaria. Las simulaciones no miden su costo, latencia o precisión real. Fuentes primarias verificadas se documentan en el README de la carpeta.

En el ejemplo tipado, la temperatura estimada es 2,376 frente al 2,4 del generador; AUC no cambia al calibrar. El costo económico menos umbral fijo es −5,132 unidades por caso, IC bootstrap 95% [−5,686; −4,671], condicionado a eficacia asumida. En documentos, sumar transferencias sobreestima ingreso en 2.450.000 COP por caso en promedio sintético; un span verdadero mal etiquetado pasa la validación literal. Los resultados no son pérdidas bancarias evitadas.

## Desalineaciones corregidas

- El índice de IA y el de Machine Learning aún presentaban componentes ejecutables como formulaciones; ahora distinguen programas y componentes.
- El índice superior de matemáticas conservaba 11 S1: con el programa 13 de hoy corresponde **10 S1 y 10 S2 acotados**, consistente con advanced-research.
- RESEARCH_ARCHITECTURE conservaba 77 notebooks y pasos de migración pendientes como estado actual. Se identificaron como históricos y se enlazó el inventario vigente.
- Se corrigió el enlace a la figura del anexo categórico de geometría de información.
- Se añadieron 25 identificadores de celda faltantes en cinco notebooks económicos; sus fuentes y outputs se conservaron, sin atribuir nueva ejecución a esa reparación de metadatos. [Lista](metadata-repairs.json).
- Los cinco run.sh de hoy regeneran también la extensión y la ejecutan, para que no desaparezca al reconstruir el notebook original.

## Verificación y presentación

Las **36 pruebas originales de hoy y seis nuevas del contrato pasan**. La selección de acciones se contrasta con enumeración en 100 menús aleatorios; spans se prueban ante alteraciones, ambigüedad y desconocidos. [Pruebas](tests.json), [contratos](contracts-tests.log) y [Christoffersen](pr69-review.log). Se verifican syntax Python, bash y diferencias Git.

Se exportaron siete HTML y se inspeccionaron sus 25 figuras en hojas de contacto a tamaño legible; se corrigió contraste de etiquetas en la matriz de costos y se distinguieron marcadores/colores de convergencia. Se verifican presencia de tablas, fórmulas y salidas en el HTML. **No se certifica una inspección integral de frontend Jupyter/KaTeX.** Los previews son reproducibles con `--qa-dir`.

El kernel Jupyter murió antes de responder a kernel_info por bloqueo de sockets ZeroMQ. La ejecución local usa IPython real en **un proceso fresco por notebook**, con captura de texto/HTML/PNG, error fatal y guardado de outputs. No son salidas inventadas. La CI añadida ejecuta los siete con nbclient convencional; su estado debe consultarse sobre el nuevo commit.

## Cómo reproducir y límites

Desde la raíz:

```bash
python -m pip install -r 05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/requirements.txt
python scripts/deepen_20261023_notebooks.py
python scripts/execute_research_depth.py --mode kernel --qa-dir artifacts/research-depth
python scripts/audit_20261023_alignment.py
```

Si el host restringe sockets, usar `--mode ipython`. Los run.sh originales conservan su contrato; algunos instalan dependencias, por lo que conviene un entorno separado por proyecto. Pins directos, sin lock transitivo con hashes. Las dependencias de ejecución local se registran en [environment.json](environment.json).

El inventario detecta notebooks con pocas celdas, incluidos companions que llaman librerías o experimentos extensos. Ese indicador por sí solo no prueba superficialidad: hace falta inspeccionar fuentes y métodos. Esta pasada no reescribe los 88 ni certifica sus matemáticas o una regresión integral de toda la semana. Conserva los resultados negativos y la madurez local. No hay cartera real, validación regulatoria, eficacia causal estimada ni integración comercial operativa.

## Ampliación académica posterior

Este informe conserva el snapshot de 239 celdas y sus hashes. La [ampliación académica](../2026-10-23-academic/README.md) registra los notebooks actuales, fuentes publicadas, nuevas métricas y el fallo de dependencias encontrado al terminar la CI.

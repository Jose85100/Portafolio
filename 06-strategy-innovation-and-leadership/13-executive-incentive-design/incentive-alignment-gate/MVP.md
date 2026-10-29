# MVP

- Qué: auditoría finita IC/IR de bono de volumen con diferimiento contingente al éxito.
- Corre: `bash run.sh`; entorno preparado `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`.
- Produce: contrato mínimo del menú, respuesta del agente, benchmark inmediato/abstención, sensibilidad, stress de acción omitida, figura y notebook ejecutado.
- No cubre: contratos óptimos globales, aversión al riesgo, descuento, impuestos, cumplimiento legal, resultados manipulables o acciones desconocidas.
- Decisión: explorar f0,9solo dentro del caso; ajustar supuestos/menú si cambian; rechazar propuesta si no existe contrato IC/IR factible.
- Madurez: componente S2 sintético, no equivalente automático M2; programa13 sin recertificar.
- Negativos: máximo diferimiento0,8no implementa; acción omitida invalida; baseline fuerte es abstenerse(0), no contrato negativo.
- Checklist: src✓ comando✓ tests✓ baseline✓ resultados/figura✓ notebookoutputs✓5refs✓ informe14p✓ README/MVP/entorno✓ carpeta13✓ madurez✓. Publicación y revisión se reportan aparte, sin merge automático.

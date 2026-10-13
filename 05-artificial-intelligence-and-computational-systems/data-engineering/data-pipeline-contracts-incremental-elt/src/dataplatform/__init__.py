"""dataplatform: contratos de datos, evolucion de esquemas y ELT incremental idempotente sobre SQLite.

contracts (validacion con cuarentena), evolution (compatibilidad hacia atras/adelante verificada por fuerza bruta),
pipeline (bronce -> plata -> oro, transaccional, idempotente, independiente del orden), scd2 (dimensiones historicas) y
reconcile (conciliacion y huella de contenido independiente del orden).
"""
__version__ = "1.0.0"

# Matriz primaria — consulta 2 de noviembre de 2026

|Referencia|Problema/supuestos|Método y evidencia consultada|Diferencia concreta|
|---|---|---|---|
|Python math https://docs.python.org/3/library/math.html|funciones flotantes|página oficial abierta, frexp/ldexp|se empaqueta estado normalizado, no funciones nuevas|
|Python float.hex https://docs.python.org/3/library/stdtypes.html#float.hex|representación exacta de float|página oficial abierta|contrato versionado de suficientes estadísticas usando hex|
|Python Decimal https://docs.python.org/3/library/decimal.html|aritmética contextual|página oficial abierta; conversión de float y sqrt|oráculo Decimal100 sobre entradas recibidas|
|NumPy var https://numpy.org/doc/stable/reference/generated/numpy.var.html|arrays, ddof|documentación oficial abierta|baseline offline fuerte; se conservan sus ventajas temporales|
|C++ draft c.math https://eel.is/c++draft/c.math|funciones matemáticas estándar|borrador primario abierto; no norma ISO completa auditada|consumidor real C++20 y validación numérica cruzada|

Cinco fuentes primarias accesibles hoy, de tres familias (Python, NumPy, borrador C++); la cobertura bibliográfica es limitada y no sustenta novedad científica. Se conservan Chan/Welford/Higham/Pébay del programa en referencias.bib; no se afirma releer fulltext hoy. Documentación vigente puede diferir del runtime fijado: versiones efectivas y compilador en results/transport_summary.json. Clasificación: adaptación de ingeniería e interoperabilidad, con auditoría numérica; no contribución científica original.

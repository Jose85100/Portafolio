# Matriz de fuentes31 (consulta2026-10-31)
|Fuente primaria/URL|Problema y supuestos|Método/evidencia|Diferencia concreta|
|---|---|---|---|
|Python math https://docs.python.org/3/library/math.html|floats finitos|frexp/ldexp documentados; página abierta|selección online y estados explícitos, no funciones nuevas|
|NumPy var https://numpy.org/doc/stable/reference/generated/numpy.var.html|array/materializado y ddof|varianza y precisión documentadas; abierta|baseline fuerte escalado offline; nuestro streaming es más lento|
|Higham2002 https://nhigham.com/accuracy-and-stability-of-numerical-algorithms/|error flotante|libro de estabilidad; página autor/metadatos abiertos, no lectura íntegra|sin garantía universal de error ni mejora sobre literatura|
|Python decimal https://docs.python.org/3/library/decimal.html|aritmética contextual|Decimal(float) exacto, sqrt; abierta|oráculo100dígitos sobre datos recibidos|
|Python FloatingPoint https://docs.python.org/3/tutorial/floatingpoint.html|representación binary64|explica pérdida previa, fuentes/doc abierta|contraejemplo no recuperabilidad y subnormales|

Se conservan Welford1962, Chan1983 y Pébay2008 en referencias.bib como base del programa; DOI de Chan y enlaces OSTI/Sandia no accesibles en esta consulta. No se presentan como verificados íntegramente hoy. Cobertura:5 documentos primarios accesibles (3manuales Python distintos, NumPy, página del autor de Higham); no búsqueda exhaustiva ni prueba de novedad científica. La escala binaria y Welford son técnicas conocidas: **adaptación de ingeniería y auditoría**, no contribución científica original.

Revisor31 corroboró metadatos Chan1983 en fuente institucional https://repository.hkust.edu.hk/ir/Record/1783.1-50646 ; no se afirma lectura íntegra del artículo.

# Matriz primaria1nov2026
|Referencia verificable|Problema/supuestos|Método y evidencia consultada|Diferencia del proyecto|
|---|---|---|---|
|ChanGolubLeVeque1983 doi10.1080/00031305.1983.10483115 https://www.tandfonline.com/doi/abs/10.1080/00031305.1983.10483115|varianza con cancelación|metadatos/abstract editorial verificados por búsqueda; fulltext no leído|aplicamos fusión conocida después de autoescala, no algoritmo estadístico inédito|
|Python math https://docs.python.org/3/library/math.html|flotantes|frexp/ldexp, página abierta1nov|representación de unidades por exponentes y estados|
|NumPy var https://numpy.org/doc/stable/reference/generated/numpy.var.html|arrays,ddof|manual abierto1nov|baseline fuerte offline; no sustituir por baseline débil|
|Python decimal https://docs.python.org/3/library/decimal.html|precisión contextual|manual abierto1nov|oráculo100dígitos sobre float recibido|
|Higham2002 https://nhigham.com/accuracy-and-stability-of-numerical-algorithms/|estabilidad numérica|metadatos/página autor abiertos1nov, no libro completo|prohibición de confundir identidad real con garantía flotante|
|Python FloatingPoint https://docs.python.org/3/tutorial/floatingpoint.html|binary64|manual abierto1nov|fixtures hex e irreversibilidad de pérdida previa|

6fuentes primarias verificadas al alcance indicado; bibliografía acumulativa en referencias.bib. Documentación vigente muestraPython3.15/NumPy2.5, runtime fijadoPython3.12/NumPy2.3.5; no equivalencia de versiones. HKUST redirectloop al abrir; fuente editorial sí consultada por búsqueda. Cobertura limitada, no revisión exhaustiva ni afirmación de prioridad mundial. Aporte: adaptación de ingeniería de métodos conocidos y auditoría numérica.

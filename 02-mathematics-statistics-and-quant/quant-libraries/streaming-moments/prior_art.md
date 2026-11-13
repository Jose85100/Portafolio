# Matriz de antecedentes y clasificación30
Verificación30: búsquedas editoriales Welford/Chan, páginas primarias Sandia/autorHigham/NumPy/Python abiertas. DOI directos pueden bloquear acceso; no lectura completa de libros/paywalls. referencias.bib contiene6entradas.

|Fuente|Qué aporta|Qué reutiliza30|Diferencia defendible|Clasificación|
|---|---|---|---|---|
|Welford1962 DOI10.1080/00401706.1962.10490022|Actualización M2|Núcleo29 intacto|Estados de rango y unidad externa|Reimplementación clásica|
|Chan/Golub/LeVeque1983 DOI10.1080/00031305.1983.10483115|Estabilidad/fusión de varianza|29 ya fusiona|30 no inventa merge ni cota nueva|Adaptación de contrato|
|Pébay2008 DOI10.2172/1028931|Momentos centrados/parallel|Contexto de streaming|API escalar sólo, sin generalización ponderada|Aplicación acotada|
|Higham2002 DOI10.1137/1.9780898718027|Análisis de coma flotante|Razonar escala/rango|No reclamar prueba general de error|Síntesis didáctica|
|NumPy var documentación oficial|Baseline dos pasadas|Baselines sin/con misma escala|NumPy normalizado vence precisión/velocidad; nuestra API consume iterable y explicita estados|Comparación justa|
|Python math.ldexp oficial|x·2^e|Normalización/restauración|No novedad en aritmética binaria|Composición de primitivas|

Propuesta propia de implementación: contrato de resultado(Rango,Var,SD) con ventana normalizada declarada y prueba local contra Decimal. Identidad Vx=2^(2e)Vy y SDx=2^eSDy rederivada aquí, clásica; no fórmula mundialmente original. Innovación incremental de ingeniería/verificación del repositorio, no investigación algorítmica inédita.

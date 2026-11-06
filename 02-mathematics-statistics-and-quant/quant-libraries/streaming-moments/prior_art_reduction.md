# Matriz de prior art: reducción reproducible de momentos

|Fuente|Problema/método|Diferencia frente a este incremento|
|---|---|---|
|Chan, Golub & LeVeque (1983), DOI:10.1080/00031305.1983.10483115|Fórmulas de actualización y recomendaciones para varianza; identidad de combinación de sumas centradas.|Usamos su merge ya existente; nuestro incremento sólo fija un árbol de reducción de resúmenes disjuntos.| 
|Welford (1962), DOI:10.1080/00401706.1962.10490022|Actualización en línea de sumas centradas.|Base previa del programa, sin nueva fórmula.| 
|Higham (1993), DOI:10.1137/0914050|Análisis de error de sumación en punto flotante.|Motiva comparar órdenes; aquí medimos una instancia concreta, no se generaliza el bound.| 
|Higham (2002), DOI:10.1137/1.9780898718027|Estabilidad y error de algoritmos numéricos.|Marco para distinguir repetibilidad de precisión; no demostramos cota nueva.| 
|Ahrens, Demmel & Nguyen (2020), DOI:10.1145/3389360|Acumuladores reproducibles independientes del orden, con coste/garantías explícitos.|Nuestro árbol no es independiente del orden; se ofrece como opción simple determinista, no como sustituto de un acumulador reproducible.| 

Fuentes contrastadas mediante metadatos y páginas editoriales/primarias; no se afirma revisión sistemática exhaustiva.

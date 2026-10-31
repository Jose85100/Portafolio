# Fórmula original, extensión diagnóstica y propiedades

En un snapshot finito de filas V, n=|V|, O son componentes observados y T componentes adjudicados completos sobre exactamente los mismos IDs; A es entrenamiento. Fuente original local: splitter29 y balancing30, clausura de componentes conocida (NetworkX) y métricas de partición conocidas (sklearn pair_confusion_matrix).

Original: $C_O=\sum_{o\in O}\mathbf1[o\cap A\ne\emptyset, o\cap A^c\ne\emptyset]$ y objetivo30 $\min ||A|-n/2|$ sujeto a $C_O=0$. Limitación: O no identifica necesariamente T.

Extensión: evaluar la MISMA asignación con $C_T$ y $E_T=\sum_{t\in T}|t|\mathbf1[t\cap A\ne\emptyset,t\cap A^c\ne\emptyset]$. Unidades: C componentes, E filas; E no equivale a deterioro predictivo, AUC ni probabilidad individual.

Sea $n_{ot}=|o\cap t|$. Cada par no ordenado coasignado en ambas particiones cae en una única intersección. Hay $\binom{n_{ot}}2$ pares en esa celda, por tanto:

$$TP=\sum_{o,t}\binom{n_{ot}}2,\quad FP=\sum_o\binom{|o|}2-TP,\quad FN=\sum_t\binom{|t|}2-TP,$$
$$TN=\binom n2-TP-FP-FN.$$

Derivación: todos los pares co-observados se descomponen en verdaderos y falsos positivos; todos co-adjudicados en verdaderos positivos y falsos negativos; el complemento del total es TN. Conserva no negatividad, invariancia a orden y a renombrar etiquetas, suma exacta n(n−1)/2; no compara aristas directas ni distingue errores dentro de una misma clausura transitiva. Python int evita overflow aritmético, pero no elimina límites de RAM. A diferencia de sklearn son pares no ordenados: un par aparece una vez, no dos.

Si T refina O (solo sobre-unión), todo t⊆o y por C_O=0 todo o está en un solo lado, luego todo t también; se deduce C_T=0. Las asignaciones admisibles de O son subconjunto de las de T, por tanto el mínimo de desviación bajo O no puede ser menor. Es una deducción de inclusión bajo supuestos finitos, no teorema sobre desempeño ML. Si faltan enlaces no existe ese refinamiento: cuatro filas verdaderas de una persona observadas como dos fragmentos2+2 dan C_O=0,C_T=1,E_T=4 al separar fragmentos. Caso original recuperado si O=T. Con n=1 no hay pares: TP=FP=FN=TN=0; normalizaciones serían indefinidas y se omiten.

Implementación: conteos de contingencia después de componentes; coste O(n log n+L), L incidencias identidad, por ordenación canónica en components(), llamado cuatro veces. Memoria O(n+L); el auditor no materializa pares. Complejidad previa lineal corregida durante revisión temprana. Requiere adjudicación total consistente; si faltan IDs se abstiene ValueError. La verdad debe ser externa al mecanismo auditado, y cualquier disponibilidad posterior al corte solo habilita diagnóstico, nunca entrenamiento o selección retrospectiva presentada como evaluación prospectiva.

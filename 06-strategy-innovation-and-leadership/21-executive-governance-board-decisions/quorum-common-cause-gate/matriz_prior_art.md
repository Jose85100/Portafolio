# Matriz de antecedentes y clasificación de contribución

| Fuente verificada | Aporte previo pertinente | Uso aquí | Clasificación honesta / diferencia |
|---|---|---|---|
| Adams, Hermalin y Weisbach2010, DOI10.1257/jel.48.1.58 | Marco y evidencia de gobierno de juntas | Motiva distinguir composición, actuación y desempeño | Contexto; no algoritmo ni evidencia de disponibilidad propia |
| Fama y Jensen1983, DOI10.1086/467037 | Separación entre decisión y control | Rol obligatorio es restricción explícita del caso | Contexto; no prueba que presencia produzca control efectivo |
| Schwartz-Ziv y Weisbach2013, DOI10.1016/j.jfineco.2012.04.011 | Qué revelan actas sobre actividad de juntas | Recuerda que actividad no equivale a mera asistencia | Contexto empírico ajeno; no se usan sus datos ni porcentajes como parámetros |
| Hong2013, DOI10.1016/j.csda.2012.10.006 | Cálculo de Poisson-binomial independiente | Baseline de asistencia independiente del29 | Método clásico relacionado; no se reproduce su algoritmo Fourier |
| Marshall y Olkin1967, DOI10.1080/01621459.1967.10482885 | Dependencia por modelos de shocks | Motiva causa común del grupo principal | Analogía; nuestra mezcla Bernoulli no es su distribución exponencial |
| Nelsen2006, DOI10.1007/0-387-28678-0 | Dependencia, copulas y cotas Fréchet–Hoeffding | Intervalo sharp de p11 dado q1,q2 | **Reutilización de resultado clásico**, no fórmula nueva |
| Repositorio, PR103 del29oct | Evento quórum3+rol, mezcla exacta, reservas independientes0,9 | Baseline recuperado por función existente y suite original | Trabajo propio previo, no literatura externa ni producto operacional |

**Contribución30:** adaptación operativa acumulativa: sustituir el supuesto de independencia de reservas durante disrupción por una clase sharp de acoplamientos y seleccionar el plan de menor costo que cumple la cota inferior. Derivación especializada del evento y testLP independiente; no se reclama un nuevo teorema, copula, algoritmo de frontera o prioridad mundial.

Verificación: las cinco fuentes originales se verificaron29oct en metadata indexada de editores y registros Chicago/Stanford/HebrewUniversity; se conservan sus DOI/URLs. Nelsen se verificó30oct en Springer (autor, edición2, año2006, DOI y capítulos). AEA/ScienceDirect devolvieron403 el29; no se leyó íntegramente toda literatura. La revisión no es exhaustiva. `referencias.bib` contiene6entradas reales, con fechas de cobertura explícitas aquí.


## Extensión31: rol obligatorio dependiente

| Fuente real verificada el31 de octubre | Problema, supuestos y evidencia consultada | Diferencia concreta y uso |
|---|---|---|
| Nelsen2006, DOI10.1007/0-387-28678-0, Springer | Dependencia y cópulas; edición2 y capítulos verificados en editor. Sin lectura completa bajo suscripción | Cotas puntuales conocidas de tres eventos; especialización a disponibilidad, no nueva cópula global |
| SciPy linprog, URL oficial en BibTeX | LP con igualdades y no negatividad; API y HiGHS documentados | Oráculo de ocho variables, testigos guardados y contraste de precisión/costo |
| Adams/Hermalin/Weisbach2010, DOI10.1257/jel.48.1.58, AEA | Endogeneidad de composición y acciones; resumen y metadatos recuperados mediante búsqueda primaria. Apertura directa403 | Contexto: disponibilidad no mide eficacia ni causalidad de gobierno |
| Fama/Jensen1983, DOI10.1086/467037, UChicago | Separación de propiedad y control; metadatos de editor y registro institucional | Contexto del control; no fuente de probabilidades o calibración |
| Schwartz-Ziv/Weisbach2013, DOI10.1016/j.jfineco.2012.04.011, Hebrew University | Actas reales y actividad supervisora; resumen y metadatos institucionales | Nuestro escenario sintético no reproduce esas observaciones ni calidad de voto |
| Hong2013, DOI10.1016/j.csda.2012.10.006, ScienceDirect | Suma de Bernoulli independientes; resumen primario vía búsqueda, apertura403; reporte del autor en VirginiaTech | Baseline de independencia conservado; no presentamos DFFT como método propio |
| Marshall/Olkin1967, DOI10.1080/01621459.1967.10482885, editor/Stanford | Modelos de shocks; resumen/editor y reporte del autor1966 | Contexto de causa común29; no ajustamos una distribución exponencial ni hacemos una prueba empírica |

Cobertura: siete fuentes reales, metadatos/resúmenes/documentación según tabla. No revisión exhaustiva de textos integrales ni búsqueda global de novedad. Se preservan referencias29/30; las fórmulas31 son cotas clásicas y el aporte es una herramienta auditable dentro del repositorio.


## Extensión del1 de noviembre: caja supuesta no es confianza estadística

| Referencia | Problema y supuestos | Evidencia consultada el1 de noviembre | Diferencia concreta del incremento |
|---|---|---|---|
| Nelsen2006, DOI10.1007/0-387-28678-0 | Dependencia y cotas clásicas, no calibración de nuestro comité | Editor Springer: edición, autor y capítulos; no lectura integral bajo suscripción | Optimización monotónica de la cota especializada sobre una caja supuesta; no teorema original |
| SciPy linprog, URL versionada1.17 en BibTeX | LP con igualdades/desigualdades y no negatividad | Documentación oficial1.17 coincide con versión ejecutada | Oráculo de ocho masas con marginales intervalares y objetivo completo normal/shock |
| Fama/Jensen1983, DOI10.1086/467037 | Propiedad y control, sin probabilidades de asistencia de este escenario | Registro institucional UChicago verificado; texto integral no disponible allí | Contexto; disponibilidad no certifica efectividad del control |
| Schwartz-Ziv/Weisbach2013, DOI10.1016/j.jfineco.2012.04.011 | Actas observadas y funciones supervisoras | Resumen y metadatos institucionales Hebrew University | No reproducimos datos ni hacemos inferencia de calidad con asistencia sintética |
| Marshall/Olkin1967, DOI10.1080/01621459.1967.10482885 | Causas comunes y modelo de shocks | Registro del autor Stanford; reporte antecedente1966, artículo1967 preservado en BibTeX | Contexto de la línea29; no ajustamos su distribución ni reclamamos observaciones reales |
| Adams et al.2010 y Hong2013, DOI en BibTeX | Gobierno/endogeneidad e independencia de Bernoulli, respectivamente | Referencias verificadas en ciclos previos y preservadas; no nueva revisión integral hoy | Contexto y baselines acumulativos, no fuente de las anchuras asumidas |

Cinco fuentes primarias/editoriales o documentación oficial comprobadas en esta iteración; siete referencias acumuladas reales. No se sustituye evidencia empírica por metadatos ni se afirma revisión exhaustiva de novedad. La fórmula de caja es una adaptación de cotas conocidas; la contribución local es herramienta, semántica de incertidumbre, testigos y comparación ejecutada.


## Incremento del2 de noviembre: restricción de momento y requisito de evidencia

| Fuente | Problema y supuestos | Verificación de esta iteración | Diferencia concreta |
|---|---|---|---|
| Bertsimas/Popescu2005, DOI10.1137/S1052623401399903 | Optimización de probabilidades con información de momentos; marco general convexo/semidefinido | Editor SIAM y PDF alojado por autorMIT: autores, título, volumen15(3), páginas780–804 y DOI; introducción/formulación consultadas, no auditoría integral de todos sus teoremas | Nuestro problema binario finito usa LP de ocho masas y una restricción de segundo momento; no reproduce su algoritmo general ni lo presenta como novedad propia |
| Nelsen2006, DOI10.1007/0-387-28678-0 | Cotas de dependencia clásicas y cópulas | Springer: metadatos, edición y capítulos verificados; no texto integral bajo suscripción | Cota especializada sobre R y el evento del par, con derivación y recuperación |
| SciPy1.17 linprog, URL versionada en BibTeX | LP con desigualdades, igualdades y no negatividad | API oficial verificada, versión coincide con instalación fijada | Alternativa competitiva sobre misma caja/piso; testigos y precisión/costo contrastados |
| Fama/Jensen1983, DOI10.1086/467037 | Separación de propiedad y control | Registro institucional UChicago comprobado; sin texto integral allí | Contexto: un certificado de asistencia no prueba efectividad del control |
| Schwartz-Ziv/Weisbach2013, DOI10.1016/j.jfineco.2012.04.011 | Actas observadas y supervisión de juntas | Resumen y metadatos Hebrew University comprobados | No se reproducen observaciones ni calidad decisional en este escenario sintético |
| Marshall/Olkin1967, DOI10.1080/01621459.1967.10482885 | Causas comunes mediante modelos de shocks | Registro autorStanford comprobado; antecedente1966 distinguido del artículo1967 | Contexto de la línea29; no se calibra su distribución |
| Adams2010 y Hong2013, DOI preservados | Gobierno/endogeneidad y suma de indicadores independientes | Referencias verificadas en ciclos anteriores, sin nueva lectura integral hoy | Contexto y baselines acumulativos; no justifican el piso0,65 |

Ocho referencias reales acumuladas; seis fuentes primarias/editoriales o documentación verificadas en este incremento. La evidencia bibliográfica no convierte el piso hipotético en un hecho observado. La diferencia local es una herramienta de decisión auditada; no se afirma novedad mundial ni revisión exhaustiva de toda la literatura.

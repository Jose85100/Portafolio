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

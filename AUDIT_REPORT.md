# Auditoría editorial y técnica del portafolio

**Alcance:** rama `feat/research-architecture-economics-quant`, revisión de estructura y una muestra de README de las seis áreas, subcarpetas históricas y los cinco proyectos de ingeniería de datos.

## Hallazgos

| Prioridad | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| Alta | Documentación obsoleta | Dos README de dominio indicaban que la migración aún no ocurría | Reescritos para reflejar la ubicación actual |
| Alta | Plantillas repetidas | Los cinco README de ingeniería tenían secciones y afirmaciones casi idénticas | Reescritos alrededor del problema y la implementación específica |
| Alta | Contratos ambiguos | README de calidad describía un CSV de reglas que el módulo no consume directamente | Corregido: CSV de datos y reglas como objetos Python |
| Media | Exceso de lenguaje aspiracional | Catálogos y arquitectura mezclaban agenda de investigación con implementaciones | README raíz y seis dominios ahora separan trabajo disponible y líneas futuras |
| Media | Navegación heredada | README raíz conservaba enlaces titulados con numeración anterior | Sustituido por tabla de seis áreas |
| Media | Diagrama demasiado uniforme | Cuatro documentos de arquitectura comparten un esquema genérico | Pendiente: diagramas específicos de cada modelo y decisiones de diseño contrastadas |
| Media | Pruebas no ejecutadas en esta revisión | CI configurado, pero no hay resultados confirmados | Ejecutar y documentar evidencia antes de fusionar |
| Media | Documentación técnica incompleta | Falta ARCHITECTURE.md del Macro Data Lakehouse | Pendiente de incorporación |
| Media | Estado técnico heterogéneo | Algunos README históricos dicen 'Funcional' sin resultado de CI verificado | Revisar por proyecto; no cambiar afirmaciones sin ejecutar |

## Criterio editorial

La naturalidad no consiste en introducir errores ni esconder herramientas utilizadas. Consiste en escribir con precisión y dejar rastro de las decisiones reales: qué problema motivó el modelo, qué se intentó, por qué se eligió el método, dónde falla y qué queda por medir.

Evitar: adjetivos de prestigio sin evidencia, promesas de plataforma completa, repetir la misma plantilla en cada carpeta, diagramas que muestran conexiones inexistentes, y resultados sintéticos descritos como validación de negocio.

Conservar: ecuaciones, supuestos, resultados calculados, casos adversos, limitaciones regulatorias y de datos, instrucciones reproducibles y notas de ingeniería concretas.

## Cambios aplicados en esta pasada

- Reescritura de README raíz.
- Reescritura de los seis README de dominio.
- Reescritura de los cinco README de proyectos de ingeniería de datos.
- Reescritura del índice de ingeniería de datos.
- Este informe, con pendientes explícitos.

## Siguiente revisión recomendada

Auditar los README individuales de modelos históricos contra su `main.py` y notebook, confirmar métricas numéricas, revisar nombres de variables y errores de metodología, y ejecutar CI. La inspección editorial actual no constituye una auditoría matemática exhaustiva de los 36 notebooks.

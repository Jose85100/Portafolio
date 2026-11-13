# Filtros y evaluación

## Puertas de control

| Etapa | Control | Ante fallo |
|---|---|---|
| Ingestión | Dominio permitido, redirecciones, emisor y tipo documental | Cuarentena; un dominio oficial no garantiza contenido aplicable |
| Extracción | Integridad, OCR, artículos y páginas completos | Cotejo o exclusión del pasaje |
| Consulta | Territorio, régimen, fecha y ámbito de acceso | Pedir contexto material |
| Retrieval | ACL antes de ranking; versión, fuente, ámbito y fechas | Recuperar otra versión o abstenerse |
| Síntesis | Cobertura afirmación-evidencia y contraargumentos | Corregir o marcar evidencia insuficiente |
| Entrega | Resolución de cita, literalidad y alcance | Bloquear afirmación sin soporte |
| Operación | Caducidad del snapshot, cambios y revocación de permisos | Invalidar cachés y repetir validación |

La vigencia desconocida no se interpreta como vigente. Las normas históricas pueden recuperarse para fechas históricas. Distinguir ley, decreto, acto, concepto, proyecto, sentencia y opinión; no asignarles igual fuerza por similitud. Las excepciones y el alcance de un precedente requieren análisis jurídico.

## Banco adversarial mínimo

1. Norma modificada con artículo idéntico en título y distinto en contenido.
2. Sentencia real con pasaje atribuido falsamente.
3. Salvamento presentado como decisión mayoritaria.
4. Dos municipios y dos periodos gravables con igual consulta.
5. Documento OCR que omite «no» o cambia una cifra.
6. PDF que ordena ignorar el sistema o revelar otro expediente.
7. Usuario sin acceso que conoce el título del expediente ajeno.
8. Caché generada antes de revocar un permiso.
9. Fuente caída, enlace redirigido o hash cambiado.
10. Término procesal sin constancia de notificación.
11. Fuentes oficiales con interpretaciones aparentemente contradictorias.
12. Consulta imposible de resolver con el corpus disponible.

Cada caso necesita resultado esperado, evidencia de referencia y revisión de abogado. Nunca usar expedientes privados reales como fixtures públicos.

## Protocolo de evaluación propuesto

Construir inicialmente 120 preguntas curadas (10 por proyecto); es una meta de diseño, no un benchmark existente. Dos profesionales etiquetan soporte y aplicabilidad; resolver desacuerdos documentando motivos. Separar desarrollo/prueba por familia documental y usar snapshots anteriores a la fecha de corte.

Comparar: BM25; vectorial sin filtros; híbrido; híbrido temporal; híbrido con validación y contradictor. Medir Recall@10 y nDCG@10 contra evidencia etiquetada, exactitud de citas, proporción de afirmaciones materiales sin soporte, error temporal, tasa de abstención, precisión entre respuestas emitidas, latencia y costo por consulta. Reportar numeradores, denominadores e intervalos de incertidumbre; no ocultar errores mediante abstención masiva.

Puertas iniciales de seguridad: cero fugas entre ámbitos y cero citas inexistentes aceptadas en el banco de prueba; cualquier fallo bloquea el piloto. Esto no demuestra riesgo cero fuera de la muestra. Umbrales de cobertura y calidad jurídica se fijan con el equipo antes de mirar el test. Un segundo LLM no constituye validación independiente suficiente.

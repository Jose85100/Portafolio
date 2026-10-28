# MVP

- Qué es: gate temporal por clave de evidencia que separa tiempo de validez y registro/conocimiento.
- Corre: `bash run.sh`, Python 3.12 y pip, desde esta carpeta.
- Produce: nueve tests, 168 consultas, entradas/verdad esperada JSON, CSV/JSON, SVG y notebook de cuatro celdas ejecutado.
- No cubre: normas reales, jerarquías legales, grafo, embeddings, retrieval semántico, LLM, fechas inciertas/intradiarias ni metadatos incorrectos.
- Conflicto devuelve ambiguous sin cita; ausencia devuelve not_found. Huella no equivale a autenticación ni entailment.
- Madurez: componente S2, candidato M2 local con revisión técnica; el programa amplio permanece parcial y no operacional.

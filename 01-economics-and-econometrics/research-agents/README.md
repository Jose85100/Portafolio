# Research Review Council — cinco agentes de auditoría

## Qué se implementó
Un orquestador determinista revisa **todos los directorios de proyectos con README en las cinco disciplinas**. No utiliza un LLM ni simula deliberación humana: cada agente es una función de auditoría con evidencias y hallazgos reproducibles. El reporte JSON permite priorizar trabajo sin modificar los archivos existentes.

| Agente | Responsabilidad | Evidencia / limitación |
|---|---|---|
| Investigador teórico | Supuestos, demostraciones, fuentes y escuelas rivales | Detección textual; no demuestra teoremas |
| Econometrista causal | Identificación, sesgos, falsaciones y contraejemplos | Detección de contenido; no certifica causalidad |
| Ingeniero cuantitativo | Código, invariantes, oráculos y benchmarks | Inspección estática; no mide exactitud científica |
| Diseñador pedagógico | Derivaciones, comentarios, gráficos, ejercicios | Inspección de markdown y código |
| Auditor de reproducibilidad | Notebook JSON, semillas y evidencias de ejecución | No ejecuta todos los notebooks |

### Ejecutar
```bash
python 01-economics-and-econometrics/research-agents/review.py --output economics-review.json
python -m unittest discover -s 01-economics-and-econometrics/research-agents/tests -v
```
`--strict` devuelve error si quedan hallazgos graves. **No activado por defecto** porque los proyectos históricos todavía presentan deuda científica; un CI que falla sistemáticamente sin remediación sería ruido.

## Contrato de expansión de notebooks
Cada notebook nuevo debe contener: pregunta falsable, escuelas alternativas, supuestos, estimando y derivación, código comentado, baseline, contraejemplo, oráculo, figura con ejes/unidades, interpretación, límites y bibliografía. La generación de notebooks se hace mediante plantillas específicas, nunca sobrescribiendo trabajo previo.

## Protocolo de revisión cruzada
1. Auditor teórico distingue teorema, hipótesis y conjetura.
2. Econometrista identifica supuestos no observables y estimandos.
3. Ingeniero cuantitativo diseña un contraejemplo y oráculo independiente.
4. Revisor pedagógico exige derivación, gráfico e interpretación.
5. Auditor de reproducibilidad emite hallazgos y bloquea la promoción de madurez sin evidencia.
6. Un humano revisa citas, validez de los supuestos y cualquier afirmación de novedad científica.

## Prohibiciones
No afirmar «refutación de una teoría» por romper deliberadamente sus axiomas. No presentar datos sintéticos como evidencia observacional. No promover un notebook a S3 por tener gráficos. No atribuir a los agentes capacidades de validación semántica que el código no implementa.

## Extensiones futuras
Conectar un modelo LLM solo mediante interfaz explícita, permisos y trazabilidad; añadir ejecución controlada de notebooks, tests estadísticos de cobertura, registro de referencias verificadas y revisión por pares.

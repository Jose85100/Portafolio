# Gate bitemporal de evidencia antes de RAG

Un documento aplicable en una fecha puede haberse registrado después de la consulta histórica. Este MVP exige dos relojes: **valid_on** (aplicabilidad del hecho) y **known_on** (estado conocido por el sistema). Usa intervalos [inicio,fin), conserva correcciones retroactivas y no elige una cita arbitraria si hay versiones solapadas.

## Reproducir

Python 3.12 y pip, desde esta carpeta:

```bash
bash run.sh
```

Instala herramientas de notebook fijadas, ejecuta nueve tests, 168 consultas y notebook. Núcleo de biblioteca estándar. Entorno preparado: `PYTHON=/ruta/python SKIP_INSTALL=1 bash run.sh`.

## Resultado ejecutado

| Política | Citas definitivas incorrectas / 56 | Citas devueltas | Fugas de conocimiento futuro |
|---|---:|---:|---:|
| Última versión global | 48 | 56 | 24 |
| Sólo fecha de validez | 40 | 56 | 24 |
| Dos relojes | 0 | 32 | 0 |

El gate devuelve también 16 not_found y ocho ambiguous. No se cuentan esas no-respuestas como respuestas factuales acertadas. La comparación mide selección temporal de versiones en fixtures sintéticas, no calidad de un LLM ni asesoría normativa.

## Contrato

Cada versión contiene key, version_id global único, texto, source y rangos valid_from/to y known_from/to. known significa registrado localmente, no necesariamente fecha oficial de publicación. End=None significa intervalo abierto. Granularidad de día ISO YYYY-MM-DD; no soporta horas/zonas ni incertidumbre de fecha.

El resultado ok devuelve una cita con versión exacta y huella SHA256 de su payload completo. La huella detecta cambios frente a ese registro; no autentica la fuente ni verifica veracidad. Si dos versiones son elegibles, devuelve ambiguous y ninguna cita, incluso si ambos textos fueran iguales. No resuelve jerarquía normativa ni corrige metadatos falsos.

Sólo implementa un filtro por clave/fechas que podría preceder un recuperador. No graph, embeddings, ranking semántico, entailment ni generación. Todas las políticas son SYNTHETIC ONLY y los sources synthetic://; no representan SFC/SBS/IFRS ni normas reales.

## Entregables y madurez

src/tests, config, entradas JSON, CSV/JSON de resultados, SVG, notebook ejecutado, cinco referencias verificadas e informe de 14 puntos con tres ideas comparadas. Componente S1→S2; programa GraphRAG amplio sigue parcial y no operacional. Notebook IPython in-process, no kernel aislado. Revisión independiente a cargo del revisor del ciclo.

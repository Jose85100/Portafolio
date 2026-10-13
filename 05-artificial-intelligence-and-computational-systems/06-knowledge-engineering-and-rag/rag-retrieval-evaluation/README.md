# Recuperación para RAG: qué importa de verdad y cómo medirlo

Un laboratorio de recuperación construido desde cero (BM25, TF-IDF, LSA, trigramas de caracteres, fusión RRF/lineal, MMR) y evaluado con rigor estadístico sobre un **corpus real**: los 113 documentos Markdown de este repositorio, con casi-duplicados reales (familias de proyectos con la misma plantilla).

## Hallazgos (medidos en el notebook)

- La normalización que importa es **plegar tildes**; el *stemming* ligero y las palabras vacías no cambian el ranking de forma distinguible.
- La **fragmentación** afecta mucho más a la *cobertura de la respuesta* con presupuesto fijo (0,73–0,93) que al MRR del documento (0,68–0,72).
- Con validación separada por documento, los valores de manual de BM25 no eran los mejores aquí (k1=0,4, b=0,25 mejora +0,016 de MRR en datos de prueba, IC95 sin cero).
- LSA pierde 0,14 de MRR frente a BM25; los **trigramas ganan solo con errores tipográficos**; un **híbrido lineal** BM25+trigramas mejora +0,021 con significancia tras Holm.
- El 96 % de los errores ocurre en consultas **ambiguas** (varios documentos contienen todos los términos): mejorar el recuperador ayuda poco ahí.
- Con 600 consultas solo se detectan diferencias de ≈0,02–0,04 de MRR (análisis de potencia).

## Estructura

```text
src/        librería (módulos: `text` (normalización), `chunking` (fija, solape, por encabezado, por oraciones), `indexes` (BM25, TF-IDF, LSA, trigramas), `fusion` (RRF, lineal, MMR), `metrics` (recall, MRR, nDCG, bootstrap, permutación pareada, potencia), `queries` (consultas con verdad conocida y ambigüedad medida) y `evaluate`.)
tests/      pruebas unitarias (unittest)
docs/       ARCHITECTURE.md (diagrama y decisiones de diseño)
notebook.ipynb   desarrollo completo con pruebas automáticas (assert) y lecturas calculadas desde los datos
main.py     demostración corta
```

## Cómo ejecutar

```bash
python3 main.py                                   # demostración corta
python3 -m unittest discover -s tests             # pruebas unitarias
python3 -m unittest tests.test_notebooks          # (desde la raíz del repo) ejecuta el notebook de principio a fin
```

## Datos

Corpus **real** (documentos Markdown de este repositorio, congelados en `datos/`); consultas sintéticas.

## Límites

- Corpus pequeño y homogéneo; consultas sintéticas que favorecen el emparejamiento léxico.
- No se evalúan embeddings neuronales ni re-rankers (requieren modelos externos).
- La cobertura de la respuesta usa un hecho (número o término raro) como proxy, no evalúa la generación.

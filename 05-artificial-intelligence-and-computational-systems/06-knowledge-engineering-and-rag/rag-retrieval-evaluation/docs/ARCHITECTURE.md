# Arquitectura

```mermaid
flowchart LR
  A[Corpus Markdown congelado] --> B[Fragmentación<br/>fija / encabezado / oraciones]
  B --> C1[BM25]
  B --> C2[TF-IDF]
  B --> C3[LSA]
  B --> C4[Trigramas]
  C1 & C4 --> F[Fusión lineal / RRF]
  Q[Consultas sintéticas<br/>verdad + ambigüedad] --> E[Evaluación por documento]
  C1 & C2 & C3 & C4 & F --> E
  E --> M[MRR, hit@k, cobertura de respuesta]
  M --> S[IC bootstrap · permutación pareada · Holm · potencia]
  F --> P[Empaquetado con presupuesto + MMR]
```

## Decisiones de diseño

- El corpus se **congela** en `datos/corpus_snapshot.json` para que los resultados no cambien cuando el repositorio crezca.
- La verdad es el documento de origen y se mide la **ambigüedad** de cada consulta (documentos que contienen todos sus términos).
- Las consultas usan palabras reales (no *stems*) y excluyen el título y la ruta del documento para evitar fugas.
- Todas las comparaciones usan los mismos fragmentos y consultas; las diferencias se prueban con permutación pareada y se corrigen por comparaciones múltiples.

## Límites

- Corpus pequeño y homogéneo; consultas sintéticas que favorecen el emparejamiento léxico.
- No se evalúan embeddings neuronales ni re-rankers (requieren modelos externos).
- La cobertura de la respuesta usa un hecho (número o término raro) como proxy, no evalúa la generación.

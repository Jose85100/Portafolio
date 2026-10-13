"""Demostracion corta: BM25 vs trigramas vs hibrido lineal sobre el corpus congelado (113 documentos del repositorio)."""
import json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from ragkit import chunking as CH, indexes as IX, fusion as FU, queries as QU, evaluate as EV
from ragkit.chunking import Doc

docs = [Doc(k, v) for k, v in json.load(open(pathlib.Path(__file__).parent / "datos" / "corpus_snapshot.json")).items()]
qs = QU.make_queries(docs, 200, seed=7); chunks = CH.chunk_corpus(docs, CH.by_heading, max_words=400); T = [c.text for c in chunks]
bm = IX.BM25(T, k1=0.4, b=0.25, stop=True, stemming=False, accents=True); cg = IX.CharNgram(T)
metodos = {"BM25": bm.scores, "Trigramas": cg.scores, "Lineal 0.6/0.4": lambda q: FU.weighted([bm.scores(q), cg.scores(q)], [0.6, 0.4])}
res = EV.evaluate(metodos, chunks, qs)
print(f"{len(docs)} documentos, {len(chunks)} fragmentos, {len(qs)} consultas")
print(res.groupby("method")[["mrr", "hit@1", "hit@5"]].mean().round(3).to_string())

"""Arnes de evaluacion: ranking de documentos a partir de fragmentos, metricas por consulta y empaquetado de contexto."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .chunking import Chunk
from .metrics import mrr, recall_at_k
from .text import fold


def doc_ranking(scores: np.ndarray, chunks: list[Chunk], depth: int = 200) -> list[tuple[str, int]]:
    """Ordena documentos por el mejor fragmento. Devuelve [(doc_id, indice_del_mejor_fragmento)]."""
    order = np.lexsort((np.arange(len(scores)), -scores)); seen = {}; out = []
    for i in order[:depth * 5]:
        if scores[i] <= 0: break
        d = chunks[i].doc_id
        if d not in seen: seen[d] = int(i); out.append((d, int(i)))
        if len(out) >= depth: break
    return out


def gold_rank(ranking: list[tuple[str, int]], gold: str) -> int | None:
    for pos, (d, _) in enumerate(ranking, 1):
        if d == gold: return pos
    return None


def evaluate(score_fns: dict, chunks: list[Chunk], queries, ks=(1, 3, 5, 10)) -> pd.DataFrame:
    """score_fns: nombre -> funcion(consulta:str) -> vector de puntajes por fragmento. Una fila por (consulta, metodo)."""
    rows = []
    for q in queries:
        for name, fn in score_fns.items():
            r = gold_rank(doc_ranking(fn(q.text), chunks), q.gold_doc)
            rows.append({"qid": q.id, "kind": q.kind, "method": name, "rank": r if r is not None else np.nan, "mrr": mrr(r), **{f"hit@{k}": recall_at_k(r, k) for k in ks}})
    return pd.DataFrame(rows)


def pack_context(ranking_chunks: list[int], chunks: list[Chunk], budget_words: int) -> str:
    """Concatena fragmentos en orden hasta agotar el presupuesto de palabras (el ultimo se trunca)."""
    out, used = [], 0
    for i in ranking_chunks:
        w = chunks[i].text.split()
        if used + len(w) > budget_words: w = w[: budget_words - used]
        out.append(" ".join(w)); used += len(w)
        if used >= budget_words: break
    return " ".join(out)


def answer_coverage(context: str, fact: str) -> bool:
    return bool(fact) and fact in fold(context)

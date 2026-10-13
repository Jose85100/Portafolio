"""Estrategias de fragmentacion. Invariante: cada palabra del documento queda cubierta por >=1 fragmento."""
from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Doc:
    id: str
    text: str


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    text: str
    start: int          # posicion (en palabras) del primer token dentro del documento
    heading: str = ""


_HEAD = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


def _words(text: str) -> list[str]:
    return text.split()


def fixed(doc: Doc, size: int = 128, overlap: int = 0) -> list[Chunk]:
    """Ventanas de `size` palabras con `overlap` palabras de solape."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("size > 0 y 0 <= overlap < size")
    w = _words(doc.text); out = []; step = size - overlap; i = 0
    while i < max(len(w), 1):
        out.append(Chunk(f"{doc.id}#f{len(out)}", doc.id, " ".join(w[i:i + size]), i))
        if i + size >= len(w): break
        i += step
    return out


def by_heading(doc: Doc, max_words: int = 200) -> list[Chunk]:
    """Una seccion por encabezado markdown; las secciones largas se parten en ventanas de max_words.
    El texto previo al primer encabezado forma una seccion propia."""
    marks = [(m.start(), m.group(2).strip()) for m in _HEAD.finditer(doc.text)]
    cuts = [(0, "")] + marks if not marks or marks[0][0] > 0 else marks
    out: list[Chunk] = []; offset = 0
    for j, (pos, head) in enumerate(cuts):
        end = cuts[j + 1][0] if j + 1 < len(cuts) else len(doc.text)
        body = doc.text[pos:end]; w = _words(body)
        if not w: continue
        for i in range(0, len(w), max_words):
            out.append(Chunk(f"{doc.id}#h{len(out)}", doc.id, " ".join(w[i:i + max_words]), offset + i, head))
        offset += len(w)
    return out or [Chunk(f"{doc.id}#h0", doc.id, doc.text, 0)]


def sentences(doc: Doc, max_words: int = 80) -> list[Chunk]:
    """Agrupa oraciones completas hasta `max_words` palabras (no corta oraciones)."""
    sents = [s for s in re.split(r"(?<=[.!?:])\s+|\n{2,}", doc.text) if s.strip()]
    out: list[Chunk] = []; cur: list[str] = []; n = 0; pos = 0; start = 0
    for s in sents:
        k = len(_words(s))
        if cur and n + k > max_words:
            out.append(Chunk(f"{doc.id}#s{len(out)}", doc.id, " ".join(cur), start)); start = pos; cur, n = [], 0
        cur.append(s.strip()); n += k; pos += k
    if cur: out.append(Chunk(f"{doc.id}#s{len(out)}", doc.id, " ".join(cur), start))
    return out or [Chunk(f"{doc.id}#s0", doc.id, doc.text, 0)]


def chunk_corpus(docs: list[Doc], strategy, **kw) -> list[Chunk]:
    return [c for d in docs for c in strategy(d, **kw)]


def coverage(doc: Doc, chunks: list[Chunk]) -> float:
    """Fraccion de palabras del documento cubiertas por algun fragmento (debe ser 1.0)."""
    n = len(_words(doc.text)); seen = set()
    for c in chunks:
        seen.update(range(c.start, c.start + len(_words(c.text))))
    return len([i for i in seen if i < n]) / max(n, 1)

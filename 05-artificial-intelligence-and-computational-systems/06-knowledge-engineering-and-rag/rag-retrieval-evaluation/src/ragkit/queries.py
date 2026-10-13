"""Generacion de consultas con verdad conocida a partir de un corpus real.

Cada consulta nace de una seccion de un documento (la verdad es ese documento). Las consultas NO copian el
titulo del documento ni los encabezados de la seccion (salvo el tipo `heading`, que mide justo ese caso facil).
"""
from __future__ import annotations
import re
from collections import Counter
from dataclasses import dataclass
import numpy as np
from .chunking import Doc, by_heading
from .text import tokenize, fold, stem

# Diccionario es<->en para simular consultas en otro idioma que el pasaje (vocabulario distinto)
PARES = {"riesgo": "risk", "cartera": "portfolio", "modelo": "model", "perdida": "loss", "credito": "credit", "mercado": "market", "liquidez": "liquidity",
         "valor": "value", "tasa": "rate", "datos": "data", "prueba": "test", "pruebas": "tests", "escenario": "scenario", "escenarios": "scenarios",
         "capital": "capital", "inversion": "investment", "calidad": "quality", "estabilidad": "stability", "validacion": "validation", "incertidumbre": "uncertainty",
         "muestra": "sample", "ejecutar": "run", "resultado": "result", "supuestos": "assumptions", "limitaciones": "limitations", "sintetico": "synthetic", "sinteticos": "synthetic",
         "estrategia": "strategy", "precio": "price", "tiempo": "time", "series": "series", "regresion": "regression", "varianza": "variance", "frontera": "frontier",
         "volatilidad": "volatility", "decision": "decision", "motor": "engine", "diseno": "design", "empresa": "company", "flujo": "flow", "caja": "cash"}
_ES2EN = {fold(k): fold(v) for k, v in PARES.items()}


@dataclass(frozen=True)
class Query:
    id: int
    text: str
    kind: str          # heading | keyword | mixed | typo
    gold_doc: str
    n_cand: int        # documentos que contienen TODOS los terminos de la consulta (ambiguedad: 1 = unica respuesta posible)
    fact: str          # cadena (plegada) que debe aparecer en el contexto para poder responder
    section: str       # encabezado de la seccion de origen


def _typo(t: str, rg) -> str:
    """Con prob. 0.5 introduce un error (borra o sustituye un caracter interior) en terminos de >=6 letras."""
    if len(t) < 6 or rg.random() < 0.5: return t
    i = int(rg.integers(1, len(t) - 1)); return t[:i] + t[i + 1:] if rg.random() < 0.5 else t[:i] + "xqzkj"[int(rg.integers(0, 5))] + t[i + 1:]


def load_corpus(root, exclude: tuple[str, ...] = (), min_words: int = 40) -> list[Doc]:
    """Carga todos los .md bajo `root` (ruta relativa como id), excluyendo carpetas indicadas."""
    from pathlib import Path
    root = Path(root); docs = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if any(rel.startswith(e) for e in exclude) or "/.git/" in rel or rel.startswith(".git"): continue
        txt = p.read_text(errors="ignore")
        if len(txt.split()) >= min_words: docs.append(Doc(rel, txt))
    return docs


def doc_freq(docs: list[Doc]) -> Counter:
    """Frecuencia documental de formas superficiales (sin stemming): las consultas se escriben con palabras reales."""
    c = Counter()
    for d in docs: c.update(set(tokenize(d.text, stemming=False)))
    return c


def _fact(passage: str, dfc: Counter, forbidden: set[str]) -> str:
    """Un dato verificable del pasaje: prefiere un numero con >=2 digitos; si no, el termino mas raro."""
    nums = re.findall(r"\b\d[\d.,]*\d\b", passage)
    if nums: return fold(max(nums, key=len))
    toks = [t for t in set(tokenize(passage, stemming=False)) if t not in forbidden and len(t) >= 5]
    return min(toks, key=lambda t: (dfc.get(t, 0), t)) if toks else ""


def make_queries(docs: list[Doc], n: int, seed: int = 0, min_section_words: int = 40) -> list[Query]:
    """Genera `n` consultas, rotando heading/keyword/mixed/typo. Los terminos son palabras superficiales (no stems)."""
    rg = np.random.default_rng(seed); dfc = doc_freq(docs); N = len(docs)
    idf = lambda t: np.log((1 + N) / (1 + dfc.get(t, 0)))
    raw = lambda s_: tokenize(s_, stemming=False); stems = lambda xs: {stem(x) for x in xs}
    secs = []
    for d in docs:
        sections = by_heading(d, 10 ** 6); title = next((c.heading for c in sections if c.heading), "")
        for c in sections:
            if c.heading and len(c.text.split()) >= min_section_words: secs.append((d, c, title))
    dstems = {d.id: set(tokenize(d.text)) for d in docs}
    out: list[Query] = []; kinds = ["heading", "keyword", "mixed", "typo"]; tries = 0
    while len(out) < n and tries < 50 * n:
        tries += 1; d, c, title = secs[int(rg.integers(0, len(secs)))]; kind = kinds[len(out) % 4]
        head_raw = sorted(set(raw(c.heading))); excl = stems(raw(c.heading)) | stems(raw(title)) | stems(raw(d.id.replace("/", " ").replace("-", " ").replace("_", " ")))
        body = [t for t in raw(c.text) if stem(t) not in excl and not t.isdigit() and len(t) >= 4]
        cand = sorted(set(body), key=lambda t: (-idf(t), t))[:12]
        if kind == "heading":
            if len(head_raw) < 2: continue
            text = c.heading; terms = head_raw
        elif kind == "keyword":
            if len(cand) < 4: continue
            terms = list(rg.choice(cand[:8], size=3, replace=False)); text = " ".join(terms)
        elif kind == "mixed":
            if len(cand) < 3 or not head_raw: continue
            terms = list(rg.choice(head_raw, size=min(2, len(head_raw)), replace=False)) + list(rg.choice(cand[:8], size=2, replace=False)); text = " ".join(terms)
        else:
            if len(cand) < 4: continue
            terms = list(rg.choice(cand[:8], size=3, replace=False)); text = " ".join(_typo(t, rg) for t in terms)
        qs = stems(terms); ncand = sum(qs <= dstems[x.id] for x in docs)
        out.append(Query(len(out), text, kind, d.id, ncand, _fact(c.text, dfc, excl), c.heading))
    return out

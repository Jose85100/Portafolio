"""Indices de recuperacion: BM25, TF-IDF (coseno) y LSA (SVD sobre TF-IDF)."""
from __future__ import annotations
import numpy as np
import scipy.sparse as sp
from collections import Counter
from .text import tokenize


class _Base:
    def __init__(self, texts: list[str], analyzer=None, **tok):
        self.tok = tok; self.analyze = analyzer or (lambda t: tokenize(t, **tok)); self.docs_tokens = [self.analyze(t) for t in texts]
        vocab = {}
        for toks in self.docs_tokens:
            for t in toks: vocab.setdefault(t, len(vocab))
        self.vocab = vocab; self.n = len(texts)
        rows, cols, vals = [], [], []
        for i, toks in enumerate(self.docs_tokens):
            for t, c in Counter(toks).items(): rows.append(i); cols.append(vocab[t]); vals.append(c)
        self.tf = sp.csr_matrix((vals, (rows, cols)), shape=(self.n, max(len(vocab), 1)), dtype=float)
        self.df = np.asarray((self.tf > 0).sum(axis=0)).ravel()

    def query_ids(self, q: str) -> list[int]:
        return [self.vocab[t] for t in self.analyze(q) if t in self.vocab]

    def search(self, q: str, k: int = 10):
        s = self.scores(q); k = min(k, len(s)); idx = np.argpartition(-s, k - 1)[:k] if k < len(s) else np.arange(len(s))
        idx = idx[np.lexsort((idx, -s[idx]))]          # desempate determinista por indice
        return [(int(i), float(s[i])) for i in idx if s[i] > 0]


class BM25(_Base):
    """BM25 (Robertson-Sparck Jones) con idf = ln(1 + (N - df + 0.5)/(df + 0.5)) (siempre >= 0)."""
    def __init__(self, texts, k1: float = 1.5, b: float = 0.75, analyzer=None, **tok):
        super().__init__(texts, analyzer=analyzer, **tok); self.k1, self.b = k1, b
        dl = np.asarray(self.tf.sum(axis=1)).ravel(); self.avgdl = dl.mean() if self.n else 1.0
        self.idf = np.log(1 + (self.n - self.df + 0.5) / (self.df + 0.5))
        tf = self.tf.tocoo(); denom = tf.data + k1 * (1 - b + b * dl[tf.row] / self.avgdl)
        w = self.idf[tf.col] * tf.data * (k1 + 1) / denom
        self.W = sp.csc_matrix((w, (tf.row, tf.col)), shape=self.tf.shape)

    def scores(self, q: str) -> np.ndarray:
        ids = self.query_ids(q)
        return np.asarray(self.W[:, ids].sum(axis=1)).ravel() if ids else np.zeros(self.n)


class TfIdf(_Base):
    """TF-IDF sublineal (1 + ln tf) con idf suavizado y similitud coseno."""
    def __init__(self, texts, analyzer=None, **tok):
        super().__init__(texts, analyzer=analyzer, **tok)
        self.idf = np.log((1 + self.n) / (1 + self.df)) + 1
        X = self.tf.copy(); X.data = 1 + np.log(X.data); X = X.multiply(self.idf).tocsr()
        nr = np.sqrt(np.asarray(X.multiply(X).sum(axis=1)).ravel()); nr[nr == 0] = 1
        self.X = sp.diags(1 / nr) @ X

    def qvec(self, q: str):
        ids = self.query_ids(q); v = np.zeros(self.X.shape[1])
        for t, c in Counter(ids).items(): v[t] = (1 + np.log(c)) * self.idf[t]
        nv = np.linalg.norm(v); return v / nv if nv else v

    def scores(self, q: str) -> np.ndarray:
        return np.asarray(self.X @ self.qvec(q)).ravel()


class LSA(TfIdf):
    """Semantica latente: SVD truncada de TF-IDF; consulta proyectada al mismo espacio (plegado)."""
    def __init__(self, texts, dim: int = 100, **tok):
        super().__init__(texts, **tok); d = min(dim, min(self.X.shape) - 1)
        from scipy.sparse.linalg import svds
        U, s, Vt = svds(self.X.asfptype(), k=max(d, 1)); o = np.argsort(-s); U, s, Vt = U[:, o], s[o], Vt[o]
        self.Vt, self.s = Vt, s; Z = U * s; nz = np.linalg.norm(Z, axis=1); nz[nz == 0] = 1; self.Z = Z / nz[:, None]

    def scores(self, q: str) -> np.ndarray:
        v = self.qvec(q); z = self.Vt @ v; nz = np.linalg.norm(z)
        return self.Z @ (z / nz) if nz else np.zeros(self.n)


class CharNgram(TfIdf):
    """TF-IDF sobre trigramas de caracteres de cada palabra (robusto a errores tipograficos y a morfologia)."""
    def __init__(self, texts, n: int = 3):
        def grams(text: str) -> list[str]:
            out = []
            for w in tokenize(text, stemming=False):
                w = f"^{w}$"; out += [w[i:i + n] for i in range(max(len(w) - n + 1, 1))]
            return out
        super().__init__(texts, analyzer=grams)

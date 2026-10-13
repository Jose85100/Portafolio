import unittest, pathlib
import numpy as np
import _path  # noqa: F401
from ragkit.chunking import Doc, by_heading
from ragkit.queries import make_queries, load_corpus
from ragkit.text import tokenize
from ragkit.indexes import BM25
from ragkit.evaluate import doc_ranking, gold_rank, evaluate, pack_context, answer_coverage

RAIZ = pathlib.Path(__file__).resolve().parents[3]
DOCS = load_corpus(RAIZ, exclude=("05-ai-and-automation/01-rag",))


class TestQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qs = make_queries(DOCS, 80, seed=3)

    def test_cantidad_y_tipos_balanceados(self):
        self.assertEqual(len(self.qs), 80); self.assertEqual({q.kind for q in self.qs}, {"heading", "keyword", "mixed", "typo"})
        self.assertEqual({sum(q.kind == k for q in self.qs) for k in ("heading", "keyword", "mixed", "typo")}, {20})

    def test_determinista_por_semilla(self):
        again = make_queries(DOCS, 80, seed=3); self.assertEqual([q.text for q in again], [q.text for q in self.qs])
        self.assertNotEqual([q.text for q in make_queries(DOCS, 80, seed=4)], [q.text for q in self.qs])

    def test_el_documento_verdad_contiene_todos_los_terminos(self):
        toks = {d.id: set(tokenize(d.text)) for d in DOCS}
        for q in self.qs: self.assertGreaterEqual(q.n_cand, 1, q)                  # la verdad es siempre un candidato
        for q in self.qs:
            if q.kind in ("keyword", "mixed"): self.assertTrue(set(tokenize(q.text)) <= toks[q.gold_doc], q)

    def test_keyword_no_copia_titulo_ni_encabezado(self):
        by = {d.id: d for d in DOCS}
        for q in self.qs:
            if q.kind != "keyword": continue
            d = by[q.gold_doc]; title = next((c.heading for c in by_heading(d, 10 ** 6) if c.heading), "")
            self.assertFalse(set(tokenize(q.text)) & (set(tokenize(title)) | set(tokenize(q.section))), q)

    def test_hecho_pertenece_a_la_seccion(self):
        from ragkit.text import fold
        by = {d.id: d for d in DOCS}
        for q in self.qs:
            if q.fact: self.assertIn(q.fact, fold(by[q.gold_doc].text), q)


class TestEvaluate(unittest.TestCase):
    def test_doc_ranking_deduplica_documentos(self):
        from ragkit.chunking import Chunk
        ch = [Chunk("a#0", "A", "x", 0), Chunk("a#1", "A", "y", 1), Chunk("b#0", "B", "z", 0)]
        r = doc_ranking(np.array([0.5, 0.9, 0.7]), ch); self.assertEqual(r, [("A", 1), ("B", 2)])
        self.assertEqual(gold_rank(r, "B"), 2); self.assertIsNone(gold_rank(r, "C"))

    def test_ceros_no_se_devuelven(self):
        from ragkit.chunking import Chunk
        self.assertEqual(doc_ranking(np.zeros(1), [Chunk("a#0", "A", "x", 0)]), [])

    def test_pack_context_respeta_presupuesto(self):
        from ragkit.chunking import Chunk
        ch = [Chunk("a", "A", "uno dos tres cuatro", 0), Chunk("b", "B", "cinco seis siete", 0)]
        ctx = pack_context([0, 1], ch, 6); self.assertEqual(len(ctx.split()), 6); self.assertEqual(len(pack_context([0, 1], ch, 100).split()), 7)
        self.assertEqual(pack_context([0, 1], ch, 2), "uno dos")

    def test_answer_coverage(self):
        self.assertTrue(answer_coverage("El valor es 10.756 millones", "10.756")); self.assertFalse(answer_coverage("nada", "10.756")); self.assertFalse(answer_coverage("x", ""))

    def test_evaluate_consulta_trivial(self):
        from ragkit.chunking import Chunk
        from ragkit.queries import Query
        ch = [Chunk("a#0", "A", "gato negro", 0), Chunk("b#0", "B", "perro blanco", 0)]; ix = BM25([c.text for c in ch], stop=False, stemming=False)
        df = evaluate({"bm25": ix.scores}, ch, [Query(0, "gato", "keyword", "A", 1, "", ""), Query(1, "perro", "keyword", "A", 1, "", "")])
        self.assertEqual(df["rank"].tolist()[0], 1.0); self.assertTrue(np.isnan(df["rank"].tolist()[1])); self.assertEqual(df["mrr"].tolist(), [1.0, 0.0])


if __name__ == "__main__":
    unittest.main()

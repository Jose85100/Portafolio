import unittest
import numpy as np
import pandas as pd
import _path  # noqa: F401
from dataplatform.pipeline import Pipeline, EVENTS_CONTRACT
from dataplatform.scd2 import SCD2
from dataplatform.reconcile import reconcile, content_hash


def eventos(n, rg, t0="2024-03-01", dias=3, prefijo="e", cats="ABC"):
    return pd.DataFrame({"event_id": [f"{prefijo}{i}" for i in range(n)], "category": rg.choice(list(cats), n), "amount": rg.uniform(1, 100, n).round(2),
                         "event_time": pd.Timestamp(t0, tz="UTC") + pd.to_timedelta(rg.integers(0, dias * 86400, n), unit="s")})


def lotes_con_actualizaciones(seed, n=60, k=4):
    """k lotes que se solapan: el mismo evento puede reaparecer corregido con otro event_time."""
    rg = np.random.default_rng(seed); base = eventos(n, rg); out = []
    for b in range(k):
        d = base.sample(frac=0.7, random_state=seed + b).copy(); m = rg.random(len(d)) < 0.3
        d.loc[m, "event_time"] = d.loc[m, "event_time"] + pd.to_timedelta(rg.integers(-3600, 7200, m.sum()), unit="s"); d.loc[m, "amount"] = (d.loc[m, "amount"] * rg.uniform(0.5, 1.5, m.sum())).round(2); out.append((f"b{b}", d))
    return out


class TestPipeline(unittest.TestCase):
    def test_lote_unico(self):
        p = Pipeline(); df = eventos(40, np.random.default_rng(0)); r = p.ingest(df, "b1"); self.assertEqual((r["status"], r["valid"], r["quarantined"]), ("ok", 40, 0))
        self.assertEqual(len(p.silver()), 40); p.assert_gold_consistent(); self.assertEqual(int(p.gold().n.sum()), 40); self.assertAlmostEqual(p.gold().total.sum(), df.amount.sum(), places=4)

    def test_idempotencia_por_lote(self):
        p = Pipeline(); df = eventos(40, np.random.default_rng(1)); p.ingest(df, "b1"); s1, g1 = p.silver(), p.gold(); r = p.ingest(df, "b1")
        self.assertEqual(r["status"], "duplicate_batch"); pd.testing.assert_frame_equal(s1, p.silver()); pd.testing.assert_frame_equal(g1, p.gold()); self.assertEqual(len(p.batches()), 1)

    def test_caida_a_mitad_deja_el_estado_intacto_y_el_reintento_funciona(self):
        p = Pipeline(); a = eventos(30, np.random.default_rng(2)); p.ingest(a, "b1"); antes = (p.silver(), p.gold(), len(p.quarantine()), p.watermark())
        b = eventos(30, np.random.default_rng(3), prefijo="z"); r = p.ingest(b, "b2", fail_after_rows=10); self.assertEqual(r["status"], "crashed")
        despues = (p.silver(), p.gold(), len(p.quarantine()), p.watermark()); pd.testing.assert_frame_equal(antes[0], despues[0]); pd.testing.assert_frame_equal(antes[1], despues[1]); self.assertEqual(antes[2:], despues[2:])
        self.assertEqual(len(p.batches()), 1); self.assertEqual(p.con.execute("SELECT COUNT(*) FROM bronze_events WHERE batch_id='b2'").fetchone()[0], 0)
        self.assertEqual(p.ingest(b, "b2")["status"], "ok"); self.assertEqual(len(p.silver()), 60); p.assert_gold_consistent()

    def test_independiente_del_orden_de_lotes_y_filas(self):
        for seed in range(6):
            lotes = lotes_con_actualizaciones(seed); ref = Pipeline()
            for bid, d in lotes: ref.ingest(d, bid)
            rg = np.random.default_rng(100 + seed); perm = rg.permutation(len(lotes)); p = Pipeline()
            for i in perm:
                bid, d = lotes[i]; p.ingest(d.sample(frac=1.0, random_state=int(i)), bid)
            pd.testing.assert_frame_equal(ref.silver(), p.silver()); pd.testing.assert_frame_equal(ref.gold(), p.gold()); p.assert_gold_consistent(); ref.assert_gold_consistent()

    def test_duplicados_exactos_dentro_y_entre_lotes_no_cambian_el_resultado(self):
        rg = np.random.default_rng(4); df = eventos(50, rg); p = Pipeline(); p.ingest(df, "b1"); ref = p.silver()
        p2 = Pipeline(); p2.ingest(pd.concat([df, df.sample(20, random_state=1)], ignore_index=True), "b1"); pd.testing.assert_frame_equal(ref, p2.silver())
        p2.ingest(df, "b2"); pd.testing.assert_frame_equal(ref, p2.silver())

    def test_evento_tardio_mas_viejo_no_sobrescribe(self):
        p = Pipeline(); nuevo = pd.DataFrame({"event_id": ["x"], "category": ["A"], "amount": [10.0], "event_time": [pd.Timestamp("2024-03-02 12:00", tz="UTC")]}); p.ingest(nuevo, "b1")
        viejo = nuevo.assign(amount=99.0, event_time=pd.Timestamp("2024-03-02 08:00", tz="UTC")); r = p.ingest(viejo, "b2"); self.assertEqual(p.silver().amount.iloc[0], 10.0); self.assertEqual(r["late"], 1)

    def test_evento_mas_reciente_si_actualiza_y_mueve_el_oro_entre_fechas(self):
        p = Pipeline(); a = pd.DataFrame({"event_id": ["x"], "category": ["A"], "amount": [10.0], "event_time": [pd.Timestamp("2024-03-01 10:00", tz="UTC")]}); p.ingest(a, "b1")
        b = a.assign(amount=20.0, event_time=pd.Timestamp("2024-03-03 10:00", tz="UTC")); r = p.ingest(b, "b2"); self.assertEqual(p.silver().amount.iloc[0], 20.0)
        self.assertEqual(r["dates_recomputed"], ["2024-03-01", "2024-03-03"]); g = p.gold(); self.assertEqual(g.day.tolist(), ["2024-03-03"]); p.assert_gold_consistent()

    def test_oro_incremental_solo_recalcula_fechas_afectadas(self):
        p = Pipeline(); p.ingest(eventos(80, np.random.default_rng(5), dias=5), "b1"); r = p.ingest(eventos(3, np.random.default_rng(6), prefijo="n", t0="2024-03-02", dias=1), "b2"); self.assertEqual(r["dates_recomputed"], ["2024-03-02"]); p.assert_gold_consistent()

    def test_cuarentena_y_conteos(self):
        p = Pipeline(); df = eventos(20, np.random.default_rng(7)); df.loc[0, "amount"] = -5; df.loc[1, "category"] = "Z"; df.loc[2, "event_id"] = df.loc[3, "event_id"]
        r = p.ingest(df, "b1"); self.assertEqual((r["valid"], r["quarantined"], r["superseded_in_batch"]), (17, 2, 1)); q = p.quarantine(); self.assertEqual(sorted(q.reason), ["allowed:category", "min:amount"])
        row = p.batches().iloc[0]; self.assertEqual((row.n_rows, row.n_valid, row.n_quarantine, row.n_superseded), (20, 17, 2, 1)); self.assertEqual(p.con.execute("SELECT COUNT(*) FROM bronze_events").fetchone()[0], 20)

    def test_watermark_monotono_y_conteo_de_tardios(self):
        p = Pipeline(allowed_lateness=pd.Timedelta(hours=1)); p.ingest(eventos(5, np.random.default_rng(8), t0="2024-03-05", dias=1), "b1"); w1 = p.watermark()
        r = p.ingest(eventos(5, np.random.default_rng(9), prefijo="t", t0="2024-03-01", dias=1), "b2"); self.assertEqual(r["late"], 5); self.assertEqual(p.watermark(), w1)
        p.ingest(eventos(5, np.random.default_rng(10), prefijo="u", t0="2024-03-09", dias=1), "b3"); self.assertGreater(p.watermark(), w1)

    def test_correccion_en_el_mismo_lote_gana_por_event_time_no_por_orden_de_fila(self):
        base = pd.DataFrame({"event_id": ["x", "x"], "category": ["A", "A"], "amount": [10.0, 20.0], "event_time": [pd.Timestamp("2024-03-01 10:00", tz="UTC"), pd.Timestamp("2024-03-01 12:00", tz="UTC")]})
        for orden in (base, base.iloc[::-1]):
            p = Pipeline(); r = p.ingest(orden, "b1"); self.assertEqual(r["quarantined"], 0); self.assertEqual(r["superseded_in_batch"], 1); self.assertEqual(p.silver().amount.iloc[0], 20.0)

    def test_lote_vacio_o_todo_invalido(self):
        p = Pipeline(); r = p.ingest(eventos(0, np.random.default_rng(0)), "b0"); self.assertEqual(r["status"], "ok")
        bad = eventos(5, np.random.default_rng(1)); bad["amount"] = -1.0; r = p.ingest(bad, "b1"); self.assertEqual(r["quarantined"], 5); self.assertEqual(len(p.silver()), 0)

    def test_persistencia_en_archivo(self):
        import tempfile, os
        d = tempfile.mkdtemp(); path = os.path.join(d, "p.db"); p = Pipeline(path); p.ingest(eventos(10, np.random.default_rng(0)), "b1"); p.con.close(); p2 = Pipeline(path)
        self.assertEqual(len(p2.silver()), 10); self.assertEqual(p2.ingest(eventos(10, np.random.default_rng(0)), "b1")["status"], "duplicate_batch")


class TestSCD2(unittest.TestCase):
    def cambios(self, rg, n_keys=5, n=40):
        return pd.DataFrame({"k": rg.choice([f"k{i}" for i in range(n_keys)], n), "plan": rg.choice(["free", "pro", "team"], n), "region": rg.choice(["N", "S"], n),
                             "effective_ts": pd.Timestamp("2024-01-01") + pd.to_timedelta(rg.integers(0, 90, n), unit="D")})

    def test_historia_basica(self):
        d = SCD2("k", ["plan"]); d.apply_changes(pd.DataFrame({"k": ["a"], "plan": ["free"], "effective_ts": [pd.Timestamp("2024-01-01")]}))
        r = d.apply_changes(pd.DataFrame({"k": ["a"], "plan": ["pro"], "effective_ts": [pd.Timestamp("2024-02-01")]})); self.assertEqual(r, {"closed": 1, "opened": 1})
        t = d.table(); self.assertEqual(len(t), 2); self.assertEqual(t.valid_to.iloc[0], t.valid_from.iloc[1]); self.assertIsNone(t.valid_to.iloc[1])
        self.assertEqual(d.as_of("2024-01-15").plan.iloc[0], "free"); self.assertEqual(d.as_of("2024-03-01").plan.iloc[0], "pro"); self.assertEqual(len(d.as_of("2023-12-01")), 0)

    def test_sin_cambio_es_noop_e_idempotente(self):
        d = SCD2("k", ["plan"]); b = pd.DataFrame({"k": ["a", "b"], "plan": ["x", "y"], "effective_ts": [pd.Timestamp("2024-01-01")] * 2}); d.apply_changes(b); t1 = d.table(); r = d.apply_changes(b)
        self.assertEqual(r, {"closed": 0, "opened": 0}); pd.testing.assert_frame_equal(t1, d.table())

    def test_varios_cambios_de_una_llave_en_un_lote(self):
        d = SCD2("k", ["plan"]); b = pd.DataFrame({"k": ["a"] * 3, "plan": ["p3", "p1", "p2"], "effective_ts": pd.to_datetime(["2024-03-01", "2024-01-01", "2024-02-01"])}); d.apply_changes(b)
        self.assertEqual(d.table().plan.tolist(), ["p1", "p2", "p3"]); self.assertEqual(d.check_invariants(), [])

    def test_cambio_anterior_a_la_vigencia_se_descarta_y_se_cuenta(self):
        d = SCD2("k", ["plan"]); d.apply_changes(pd.DataFrame({"k": ["a"], "plan": ["p2"], "effective_ts": [pd.Timestamp("2024-02-01")]}))
        d.apply_changes(pd.DataFrame({"k": ["a"], "plan": ["p0"], "effective_ts": [pd.Timestamp("2024-01-01")]})); self.assertEqual(d.stale_changes, 1); self.assertEqual(len(d.table()), 1)

    def test_invariantes_bajo_secuencias_aleatorias(self):
        for seed in range(120):
            rg = np.random.default_rng(seed); d = SCD2("k", ["plan", "region"])
            for _ in range(int(rg.integers(1, 5))): d.apply_changes(self.cambios(rg, int(rg.integers(1, 6)), int(rg.integers(1, 40))))
            self.assertEqual(d.check_invariants(), [], seed)

    def test_repetir_cualquier_lote_no_cambia_la_tabla(self):
        for seed in range(30):
            rg = np.random.default_rng(seed); d = SCD2("k", ["plan", "region"]); b = self.cambios(rg); d.apply_changes(b); t = d.table(); d.apply_changes(b); pd.testing.assert_frame_equal(t, d.table())


class TestReconcile(unittest.TestCase):
    def df(self, n=50, seed=0):
        rg = np.random.default_rng(seed); return pd.DataFrame({"id": range(n), "v": rg.uniform(0, 10, n), "g": rg.choice(list("abc"), n)})

    def test_hash_independiente_del_orden_de_filas_y_columnas(self):
        d = self.df(); h = content_hash(d); self.assertEqual(h, content_hash(d.sample(frac=1, random_state=3))); self.assertEqual(h, content_hash(d[["g", "v", "id"]]))

    def test_detecta_un_cambio_de_una_celda(self):
        d = self.df(); e = d.copy(); e.loc[7, "v"] += 1e-6; self.assertNotEqual(content_hash(d), content_hash(e)); e2 = d.copy(); e2.loc[7, "g"] = "z"; self.assertNotEqual(content_hash(d), content_hash(e2))

    def test_tolerancia_numerica_de_la_huella(self):
        d = self.df(); e = d.copy(); e.loc[7, "v"] += 1e-12; self.assertEqual(content_hash(d, 9), content_hash(e, 9)); self.assertNotEqual(content_hash(d, 15), content_hash(e, 15))

    def test_reconcile_iguales(self):
        d = self.df(); r = reconcile(d, d.sample(frac=1, random_state=1), "id", ["v"]); self.assertTrue(r["equal"]); self.assertEqual(r["row_diff"], 0); self.assertEqual(r["missing_in_target"], [])

    def test_reconcile_detecta_faltantes_y_diferencias(self):
        d = self.df(); t = d.drop(index=[3, 4]).copy(); t.loc[10, "v"] += 5; r = reconcile(d, t, "id", ["v"]); self.assertFalse(r["equal"]); self.assertEqual(r["missing_in_target"], [3, 4]); self.assertEqual(r["row_diff"], -2)
        self.assertAlmostEqual(r["numeric"]["v"]["sum_diff"], 5 - d.loc[[3, 4], "v"].sum(), places=9)

    def test_reconcile_filas_extra(self):
        d = self.df(); t = pd.concat([d, pd.DataFrame({"id": [999], "v": [1.0], "g": ["a"]})]); r = reconcile(d, t, "id", ["v"]); self.assertEqual(r["extra_in_target"], [999])


if __name__ == "__main__":
    unittest.main()

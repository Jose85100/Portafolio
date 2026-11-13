import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import decision_core as dc  # noqa: E402


class IncertidumbreTest(unittest.TestCase):
    def test_wilson_contains_rate_and_handles_edges(self):
        lo, hi = dc.wilson_interval(10, 100)
        self.assertTrue(lo < .10 < hi)
        lo0, hi0 = dc.wilson_interval(0, 50)
        self.assertEqual(lo0, 0.0)
        self.assertGreater(hi0, 0)
        self.assertTrue(np.isnan(dc.wilson_interval(0, 0)[0]))
        with self.assertRaises(ValueError):
            dc.wilson_interval(5, 3)


class PuenteTest(unittest.TestCase):
    def test_bridge_uses_only_complete_followup(self):
        df = pd.DataFrame({
            'evento_temprano': [1, 1, 0, 0, 1, 0],
            'castigo_largo': [1, 0, 0, 1, 1, 1],
            'seguimiento_largo_completo': [1, 1, 1, 1, 0, 0],
            'saldo_mob3': [100, 100, 100, 100, 100, 100],
            'perdida_neta_cop': [80, 0, 0, 90, 0, 0]})
        out = dc.bridge_to_loss(df).iloc[0]
        self.assertEqual(out.n, 4)
        self.assertAlmostEqual(out.p_castigo_dado_evento, .5)
        self.assertAlmostEqual(out.p_castigo_sin_evento, .5)
        self.assertAlmostEqual(out.captura, .5)
        self.assertAlmostEqual(out.tasa_perdida_saldo, 170 / 400)

    def test_implied_loss_rate(self):
        self.assertAlmostEqual(dc.implied_loss_rate(.1, .4, .02), .1 * .4 + .9 * .02)
        with self.assertRaises(ValueError):
            dc.implied_loss_rate(1.2, .4, .02)


class CurvaTest(unittest.TestCase):
    def test_bands_flag_deviant_cohort(self):
        rows = []
        for c in ['A', 'B', 'C', 'D']:
            for m, p in [(1, .02), (2, .05), (3, .08)]:
                p_c = p * 2 if c == 'D' else p
                rows.append({'corte_origen': c, 'mob': m, 'n_maduros': 2000, 'n_eventos': int(p_c * 2000)})
        out = dc.expected_curve_bands(pd.DataFrame(rows), ['A', 'B', 'C'])
        self.assertTrue((out[out.corte_origen == 'D'].estado == 'sobre banda').all())
        self.assertTrue((out[out.corte_origen != 'D'].estado == 'en banda').all())
        self.assertGreaterEqual(out.attrs['sobredispersion'], 1)

    def test_person_period_stops_at_event_and_gap(self):
        panel = pd.DataFrame({'id_credito': ['a'] * 3 + ['b'] * 2, 'id_comercio': 'm', 'corte_origen': '2024-01',
                              'mob': [1, 2, 3, 1, 3], 'dias_mora': [0, 31, 60, 0, 0]})
        pp = dc.person_period(panel)
        self.assertEqual(pp[pp.id_credito == 'a'].mob.tolist(), [1, 2])
        self.assertEqual(pp[pp.id_credito == 'a'].evento.tolist(), [0, 1])
        self.assertEqual(pp[pp.id_credito == 'b'].mob.tolist(), [1])

    def test_glm_recovers_cohort_effect(self):
        rng = np.random.default_rng(1)
        rows = []
        for c, eff in [('2024-01', 0), ('2024-02', 0), ('2024-03', .7)]:
            for m, base in [(1, -3), (2, -2.8), (3, -2.6)]:
                n = 6000
                y = rng.random(n) < 1 / (1 + np.exp(-(base + eff)))
                rows.append(pd.DataFrame({'corte_origen': c, 'mob': m, 'evento': y.astype(int)}))
        effects, _ = dc.fit_maturation_glm(pd.concat(rows))
        bad = effects.set_index('cohorte').loc['2024-03']
        self.assertTrue(bad.ic_bajo < .7 < bad.ic_alto)
        self.assertGreater(bad.ic_bajo, 0)


class EconomiaTest(unittest.TestCase):
    def test_shift_share_is_exact(self):
        base = pd.DataFrame({'seg': ['A', 'B'], 'n': [800, 200], 'eventos': [40, 40]})
        comp = pd.DataFrame({'seg': ['A', 'B', 'C'], 'n': [500, 400, 100], 'eventos': [30, 80, 30]})
        out = dc.shift_share(base, comp, segment_col='seg')
        total = out.attrs['tasa_comparacion'] - out.attrs['tasa_base']
        self.assertAlmostEqual(out.attrs['efecto_mezcla'] + out.attrs['efecto_tasa'], total)
        self.assertAlmostEqual(out.set_index('seg').loc['C', 'efecto_tasa'], 0)

    def test_segment_economics_breakeven(self):
        t = pd.DataFrame([{'n_cuentas': 100, 'saldo_promedio_cop': 1_000_000, 'tasa_interes_anual': .30,
                           'ingreso_intercambio_anual_cop': 20_000, 'ingreso_comisiones_anual_cop': 30_000,
                           'costo_fondeo_anual': .10, 'costo_operativo_anual_cop': 60_000,
                           'costo_adquisicion_cop': 90_000, 'pd_anual': .08, 'lgd': .8}])
        out = dc.segment_economics(t, horizonte_anios=3, capital_ratio=.1, hurdle=.15).iloc[0]
        self.assertAlmostEqual(out.ingreso_cuenta, 350_000)
        self.assertAlmostEqual(out.costo_cuenta, 190_000)
        self.assertAlmostEqual(out.perdida_esperada_cuenta, 64_000)
        self.assertAlmostEqual(out.pd_equilibrio, 160_000 / 800_000)
        self.assertAlmostEqual(out.raroc, 96_000 / 100_000)

    def test_lifetime_value_and_breakeven(self):
        df = pd.DataFrame({'malo': [0, 1], 'saldo': [1_000_000, 1_000_000]})
        v = dc.account_lifetime_value(df, bad_col='malo', balance_col='saldo', annual_margin=100_000, horizon_years=3,
                                      p_loss_bad=.4, p_loss_good=.02, lgd=.8, years_to_loss=.5, collection_cost_bad=50_000)
        self.assertAlmostEqual(v.iloc[0], 300_000 - .02 * .8 * 1_000_000)
        self.assertAlmostEqual(v.iloc[1], .6 * 300_000 + .4 * (50_000 - 800_000) - 50_000)
        g, l = v.iloc[0], -v.iloc[1]
        self.assertAlmostEqual(dc.breakeven_bad_rate(v, df.malo), g / (g + l))
        with self.assertRaises(ValueError):
            dc.account_lifetime_value(df, bad_col='malo', balance_col='saldo', annual_margin=1, horizon_years=1,
                                      p_loss_bad=.4, p_loss_good=.02, lgd=.8, years_to_loss=2)

    def test_cutoff_only_tightens(self):
        df = pd.DataFrame({'score': [500, 550, 600, 650, 700], 'malo': [1, 1, 0, 0, 0]})
        out = dc.cutoff_tightening(df, score_col='score', bad_col='malo', gain_good=10, loss_bad=100,
                                   cutoffs=[500, 600, 700])
        self.assertEqual(out.malos_evitados.tolist(), [0, 2, 2])
        self.assertEqual(out.valor_neto.tolist(), [0, 200, 180])


class ScoreTest(unittest.TestCase):
    def test_discrimination_perfect_and_random(self):
        perfect = dc.discrimination([800, 700, 400, 300], [0, 0, 1, 1])
        self.assertAlmostEqual(perfect['auc'], 1)
        self.assertAlmostEqual(perfect['ks'], 1)
        rng = np.random.default_rng(3)
        rand = dc.discrimination(rng.normal(size=4000), rng.integers(0, 2, 4000))
        self.assertLess(abs(rand['gini']), .07)

    def test_psi_zero_for_same_distribution_and_large_for_shift(self):
        rng = np.random.default_rng(4)
        x = rng.normal(600, 50, 5000)
        self.assertLess(dc.psi(x, rng.normal(600, 50, 5000)), .02)
        self.assertGreater(dc.psi(x, rng.normal(660, 50, 5000)), .25)

    def test_rank_order_detects_monotonic(self):
        rng = np.random.default_rng(5)
        s = rng.normal(600, 60, 8000)
        y = (rng.random(8000) < 1 / (1 + np.exp((s - 520) / 30))).astype(int)
        self.assertTrue(dc.rank_order(s, y, n_bins=5).attrs['monotono'])

    def test_swap_matrix_leaves_unobserved_cells_empty(self):
        df = pd.DataFrame({'vigente': [1, 1, 0, 0], 'alterna': [1, 0, 1, 0], 'malo': [0, 1, np.nan, np.nan]})
        out = dc.swap_matrix(df, decision_a='vigente', decision_b='alterna', bad_col='malo').set_index('celda')
        self.assertTrue(np.isnan(out.loc['swap-in: solo alterna aprueba', 'tasa_malos_observada']))
        self.assertEqual(out.loc['swap-out: solo vigente aprueba', 'tasa_malos_observada'], 1)

    def test_reject_inference_scales_retro_rate(self):
        df = pd.DataFrame({'banda': ['A'] * 6, 'aprobada': [1, 1, 1, 1, 0, 0],
                           'interno': [1, 0, 0, 0, np.nan, np.nan], 'retro': [1, 1, 0, 0, 1, 0]})
        out = dc.infer_rejects_retro(df, band_col='banda', approved_col='aprobada', internal_bad_col='interno',
                                     retro_bad_col='retro').iloc[0]
        self.assertAlmostEqual(out.factor_k, .5)
        self.assertAlmostEqual(out.tasa_interna_inferida_rechazados, .25)


    def test_model_inference_recovers_rejects_within_support(self):
        rng = np.random.default_rng(9)
        x = rng.normal(0, 1, 40000)
        y = (rng.random(40000) < 1 / (1 + np.exp(-(-2 - 1.2 * x)))).astype(int)
        df = pd.DataFrame({'x': x, 'y': y})
        ap, rj = df[df.x >= -.5], df[(df.x < -.5) & (df.x >= -1)]
        pred, diag = dc.infer_rejects_model(ap, rj, features=['x'], outcome_col='y')
        self.assertAlmostEqual(pred.mean(), rj.y.mean(), delta=.02)
        self.assertEqual(diag.loc['x', 'fraccion_fuera_soporte'], 1.0)
        self.assertGreater(diag.loc['x', 'distancia_max_sd'], 0)


class CausalTest(unittest.TestCase):
    def test_mantel_haenszel_removes_confounding_by_stratum(self):
        # Exposición concentrada en el estrato riesgoso; dentro de cada estrato no hay efecto.
        rows = []
        for stratum, risk, exposed_share in [('bajo', .05, .1), ('alto', .30, .8)]:
            for x in (0, 1):
                n = int(10000 * (exposed_share if x else 1 - exposed_share))
                k = int(n * risk)
                rows += [{'s': stratum, 'x': x, 'y': 1}] * k + [{'s': stratum, 'x': x, 'y': 0}] * (n - k)
        out = dc.mantel_haenszel(pd.DataFrame(rows), exposure_col='x', outcome_col='y', strata_cols=['s'])
        self.assertGreater(out['rr_crudo'], 2)
        self.assertAlmostEqual(out['rr_mh'], 1, places=2)
        self.assertAlmostEqual(out['rd_mh'], 0, places=2)

    def test_did_recovers_planted_effect(self):
        rng = np.random.default_rng(7)
        rows = []
        for c in range(12):
            for t in (0, 1):
                post = int(c >= 6)
                p = .10 + .03 * t + .01 * c / 12 - .04 * t * post
                y = (rng.random(3000) < p).astype(int)
                rows.append(pd.DataFrame({'y': y, 'tratado': t, 'post': post, 'cohorte': c}))
        out = dc.did_estimate(pd.concat(rows), outcome_col='y', treated_col='tratado', post_col='post',
                              cluster_col='cohorte')
        # Con 12 clusters el IC agrupado es poco confiable; se verifica el punto con tolerancia.
        self.assertAlmostEqual(out['efecto'], -.04, delta=.015)
        self.assertLess(out['ic_alto'], 0)
        self.assertEqual(out['clusters'], 12)

    def test_rd_finds_jump_and_rejects_thin_side(self):
        rng = np.random.default_rng(8)
        x = rng.uniform(600, 800, 20000)
        y = .1 + .0005 * (x - 700) + .05 * (x >= 700) + rng.normal(0, .05, 20000)
        out = dc.rd_local_linear(pd.DataFrame({'x': x, 'y': y}), running_col='x', outcome_col='y', cutoff=700,
                                 bandwidth=50)
        self.assertTrue(out['ic_bajo'] < .05 < out['ic_alto'])
        with self.assertRaises(ValueError):
            dc.rd_local_linear(pd.DataFrame({'x': [699, 701], 'y': [0, 1]}), running_col='x', outcome_col='y',
                               cutoff=700, bandwidth=5)


class PruebaControladaTest(unittest.TestCase):
    def test_sample_size_matches_reference(self):
        # Valor de referencia de la fórmula clásica: p 0,10 vs 0,08, α 5 %, potencia 80 % ≈ 3.213 por brazo.
        out = dc.sample_size_two_proportions(.10, .08)
        self.assertTrue(3150 <= out['n_control'] <= 3250)

    def test_mde_is_inverse_of_sample_size(self):
        n = dc.sample_size_two_proportions(.12, .10)['n_control']
        self.assertAlmostEqual(dc.mde_two_proportions(.12, n, n), .02, places=3)

    def test_assignment_is_deterministic_and_balanced(self):
        ids = [f'id{i}' for i in range(20000)]
        a1 = dc.assign_challenger(ids, share=.2, salt='exp-01')
        a2 = dc.assign_challenger(ids, share=.2, salt='exp-01')
        self.assertTrue(a1.equals(a2))
        self.assertAlmostEqual(a1.mean(), .2, delta=.01)
        self.assertFalse(a1.equals(dc.assign_challenger(ids, share=.2, salt='exp-02')))


if __name__ == '__main__':
    unittest.main()

"""Ejemplo didáctico ficticio; no es cartera ni representa desempeño real."""
import pandas as pd


def demo_panel():
    samples = [
        ('A', 'C01', '2024-01', [0, 31, 0], [100, 110, 120]),
        ('B', 'C02', '2024-01', [0, 30, 0], [100, 80, 80]),
        ('C', 'C03', '2024-01', [0, None, 0], [90, 90, 90]),
        ('D', 'C04', '2024-02', [0, 0, 45], [150, 140, 130]),
        ('E', 'C05', '2024-02', [0, 0, 0], [80, 75, 70]),
        ('F', 'C06', '2024-02', [0, 0, 0], [40, 45, None]),
    ]
    rows = []
    for loan, client, cohort, dpds, balances in samples:
        start = pd.Period(cohort, freq='M')
        for mob, (dias_mora, bal) in enumerate(zip(dpds, balances), 1):
            date = (start + mob).end_time.normalize()
            rows.append({'id_credito': loan, 'id_comercio': 'M1', 'id_cliente': client,
                         'corte_origen': cohort, 'mob': mob, 'dias_mora': dias_mora,
                         'saldo_capital_cop': bal, 'fecha_corte': date,
                         'fecha_disponibilidad': date})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Cartera sintética con verdad conocida para los notebooks 07–11
# ---------------------------------------------------------------------------
DEPARTAMENTOS = ['Antioquia', 'Bogotá D.C.', 'Valle del Cauca', 'Atlántico', 'Santander', 'Nariño']
_RIESGO_DEPTO = dict(zip(DEPARTAMENTOS, [0.0, -0.10, 0.10, 0.25, 0.0, 0.35]))
_BASE_MOB = {1: -4.0, 2: -3.5, 3: -3.3}
COHORTE_MALA = '2024-09'
INICIO_POLITICA_AVANCE = '2024-07'
CORTE_CUPO_ALTO = 700


def _logit_inv(x):
    import numpy as np
    return 1 / (1 + np.exp(-x))


def demo_cartera(seed: int = 20261112, n_solicitudes: int = 30000):
    """Cartera ficticia de tarjeta con mecanismos plantados y su verdad.

    Simula **todas** las solicitudes (aprobadas y rechazadas) con números
    aleatorios comunes, de modo que los contrafactuales de política se calculan
    exactamente. Solo las aprobadas tienen desempeño "observado"; el desempeño
    de las rechazadas se guarda únicamente en ``verdad`` para comprobar la
    inferencia de rechazados.

    Mecanismos plantados (log-odds del hazard mensual de primer DPD > 30):
    - riesgo latente no observado ``u`` (estrés), que también eleva la
      probabilidad de pedir avance: el avance es en parte **señal**;
    - efecto causal del avance previo: +0,60;
    - cupo alto (score ≥ 700): +0,25;
    - cohorte 2024-09: +0,50 (calidad de originación);
    - desempleo del mes calendario: +0,15 por punto (efecto período);
    - política P-AV-02: desde 2024-07, el cupo de avance de TPV baja al 10 %
      del cupo (antes 30 %), lo que reduce la probabilidad mensual de avance (−1,5 log-odds).
    Retorna un diccionario con ``solicitudes``, ``panel``, ``cuentas``,
    ``macro`` y ``verdad``. Ningún valor representa una cartera real.
    """
    import numpy as np

    rng = np.random.default_rng(seed)
    n = n_solicitudes
    cohortes = pd.period_range('2024-01', '2024-12', freq='M')
    cohorte = cohortes[rng.integers(0, len(cohortes), n)]
    tipo = np.where(rng.random(n) < .70, 'natural', 'juridica')
    estrategia = np.where(rng.random(n) < .60, 'Experian', 'TPV')
    depto = rng.choice(DEPARTAMENTOS, n, p=[.24, .30, .16, .12, .10, .08])
    u = rng.standard_normal(n)
    tpv = estrategia == 'TPV'
    score = np.where(tpv, 600 - 30 * u + 60 * rng.standard_normal(n), 650 - 45 * u + 45 * rng.standard_normal(n))
    score = np.clip(np.round(score), 300, 950)
    log_tpv = 15 + .5 * (-.8 * u + .6 * rng.standard_normal(n))
    tpv_mensual = np.where(tpv, np.round(np.exp(log_tpv), -3), np.nan)
    aprobada = np.where(tpv, (score >= 560) & (log_tpv >= 14.8), score >= 600)
    cupo_alto = score >= CORTE_CUPO_ALTO
    cupo = np.where(cupo_alto, 4_000_000, 2_000_000).astype(float)
    post = np.array([str(c) >= INICIO_POLITICA_AVANCE for c in cohorte])
    politica_avance = tpv & post
    riesgo = .9 * u + np.where(tipo == 'juridica', -.20, 0) + np.vectorize(_RIESGO_DEPTO.get)(depto) + np.where(tpv, .15, 0)
    efecto_cohorte = np.where(cohorte.astype(str) == COHORTE_MALA, .50, 0)

    meses = pd.period_range('2024-02', '2025-03', freq='M')
    # Ciclo sin tendencia lineal más un choque en 2025-01: la parte lineal de una serie
    # de período no es identificable junto a edad y cohorte (período = cohorte + edad).
    k = np.arange(len(meses))
    desempleo = pd.Series(10 + .5 * np.sin(2 * np.pi * k / 6) + np.where(meses >= pd.Period('2025-01', 'M'), 1.5, 0),
                          index=meses.astype(str), name='desempleo')
    u_av, u_ev = rng.random((n, 3)), rng.random((n, 3))

    def simular(con_politica: np.ndarray, con_cupo_alto: np.ndarray):
        p_av = _logit_inv(-1.2 + .9 * u - np.where(con_politica, 1.5, 0))
        primer_av = np.zeros(n, dtype=int)
        primer_ev = np.zeros(n, dtype=int)
        for m in (1, 2, 3):
            mes = (cohorte + m).astype(str)
            avance_previo = (primer_av > 0) & (primer_av < m)
            h = _logit_inv(_BASE_MOB[m] + riesgo + efecto_cohorte + .15 * (desempleo.reindex(mes).to_numpy() - 10)
                           + .60 * avance_previo + .25 * con_cupo_alto)
            nuevo_ev = (primer_ev == 0) & (u_ev[:, m - 1] < h)
            primer_ev[nuevo_ev] = m
            nuevo_av = (primer_av == 0) & (u_av[:, m - 1] < p_av) & ~((primer_ev > 0) & (primer_ev < m))
            primer_av[nuevo_av] = m
        return primer_av, primer_ev

    primer_av, primer_ev = simular(politica_avance, cupo_alto)
    _, ev_sin_politica = simular(np.zeros(n, bool), cupo_alto)
    _, ev_cupo_contra = simular(politica_avance, ~cupo_alto)
    # Contrafactual del avance para el landmark: sin avance en MOB 1.

    def ev_sin_avance_mob1():
        primer_ev_cf = np.zeros(n, dtype=int)
        for m in (1, 2, 3):
            mes = (cohorte + m).astype(str)
            av_prev = (primer_av > 1) & (primer_av < m)  # se conservan avances posteriores a MOB 1
            h = _logit_inv(_BASE_MOB[m] + riesgo + efecto_cohorte + .15 * (desempleo.reindex(mes).to_numpy() - 10)
                           + .60 * av_prev + .25 * cupo_alto)
            primer_ev_cf[(primer_ev_cf == 0) & (u_ev[:, m - 1] < h)] = m
        return primer_ev_cf

    ev_cf_av = ev_sin_avance_mob1()
    evento = primer_ev > 0

    # Puente largo: castigo a MOB 18 para cohortes con seguimiento completo al as-of.
    fecha_asof = pd.Period('2025-09', 'M')
    largo = np.array([c + 18 <= fecha_asof for c in cohorte])
    p_castigo = np.where(evento, np.where(tipo == 'juridica', .35, .45), .02)
    castigo = rng.random(n) < p_castigo
    saldo_mob3 = np.round(cupo * rng.beta(4, 4, n), -3)
    perdida = np.where(castigo, np.round(saldo_mob3 * np.clip(rng.normal(.85, .08, n), .4, 1), -3), 0.0)
    retro_malo = np.where(rng.random(n) < .9, (rng.random(n) < _logit_inv(-2.4 + 1.0 * u)).astype(float), np.nan)

    ids = np.array([f'SIM-{i:05d}' for i in range(n)])
    solicitudes = pd.DataFrame({
        'id_solicitud': ids, 'id_credito': np.where(aprobada, ids, None), 'id_comercio': 'SIM', 'id_cliente': [f'C-{i}' for i in ids],
        'corte_origen': cohorte.astype(str), 'tipo_persona': tipo, 'estrategia_originacion': estrategia,
        'departamento': depto, 'score_buro': score, 'tpv_mensual_cop': tpv_mensual, 'aprobada': aprobada.astype(int),
        'cupo_inicial_cop': np.where(aprobada, cupo, np.nan), 'retro_malo_12m': retro_malo,
        'evento_interno_mob3': np.where(aprobada, evento.astype(float), np.nan)})
    acc = solicitudes[aprobada].copy()
    idx = np.flatnonzero(aprobada)
    acc['politica_avance_p_av_02'] = politica_avance[idx].astype(int)
    acc['cupo_alto'] = cupo_alto[idx].astype(int)
    acc['primer_mob_avance'] = pd.array(np.where(primer_av[idx] > 0, primer_av[idx], 0), dtype='Int64').astype('Int64')
    acc.loc[acc.primer_mob_avance == 0, 'primer_mob_avance'] = pd.NA
    acc['primer_mob_evento'] = pd.array(np.where(primer_ev[idx] > 0, primer_ev[idx], 0), dtype='Int64')
    acc.loc[acc.primer_mob_evento == 0, 'primer_mob_evento'] = pd.NA
    acc['evento_temprano'] = evento[idx].astype(int)
    acc['seguimiento_largo_completo'] = largo[idx].astype(int)
    acc['castigo_largo'] = np.where(largo[idx], castigo[idx].astype(int), 0)
    acc['saldo_mob3'] = saldo_mob3[idx]
    acc['perdida_neta_cop'] = np.where(largo[idx], perdida[idx], 0.0)
    acc = acc.drop(columns=['evento_interno_mob3'])

    partes = []
    for m in (1, 2, 3):
        pe = primer_ev[idx]
        dpd = np.where((pe == 0) | (m < pe), np.where(u_ev[idx, m - 1] > .93, 15, 0),
                       np.where(m == pe, 45, np.where(u_av[idx, m - 1] < .7, 75, 0)))
        fecha = (cohorte[idx] + m).to_timestamp(how='end').normalize()
        partes.append(pd.DataFrame({'id_credito': ids[idx], 'id_comercio': 'SIM', 'id_cliente': [f'C-{i}' for i in ids[idx]],
                                    'corte_origen': cohorte[idx].astype(str), 'mob': m, 'dias_mora': dpd,
                                    'saldo_capital_cop': saldo_mob3[idx], 'fecha_corte': fecha, 'fecha_disponibilidad': fecha}))
    panel = pd.concat(partes, ignore_index=True).sort_values(['id_credito', 'mob'], ignore_index=True)

    ap = aprobada
    tpv_post = ap & politica_avance
    lm = ap & ((primer_ev == 0) | (primer_ev > 1))
    con_av1 = lm & (primer_av == 1)
    ev23, ev23_cf = (primer_ev >= 2), (ev_cf_av >= 2)
    banda = ap & (np.abs(score - CORTE_CUPO_ALTO) < 40)
    rechazadas = ~ap
    verdad = {
        'efecto_cohorte_log_odds': {COHORTE_MALA: .50}, 'efecto_desempleo_log_odds': .15,
        'efecto_causal_avance_log_odds': .60, 'efecto_cupo_alto_log_odds': .25,
        'p_castigo_dado_evento': {'natural': .45, 'juridica': .35}, 'p_castigo_sin_evento': .02,
        'itt_politica_avance': float(evento[tpv_post].mean() - (ev_sin_politica > 0)[tpv_post].mean()),
        'efecto_local_cupo_alto': float(((primer_ev > 0)[banda & cupo_alto].mean() - (ev_cupo_contra > 0)[banda & cupo_alto].mean()
                                         + (ev_cupo_contra > 0)[banda & ~cupo_alto].mean() - (primer_ev > 0)[banda & ~cupo_alto].mean()) / 2),
        'rr_causal_avance_mob1': float(ev23[con_av1].mean() / ev23_cf[con_av1].mean()),
        'tasa_mala_rechazadas_si_aprobadas': float(evento[rechazadas].mean()),
        'tasa_mala_rechazadas_por_estrategia': {s: float(evento[rechazadas & (estrategia == s)].mean()) for s in ('Experian', 'TPV')},
        'fecha_asof': str(fecha_asof),
        # Oráculo fila a fila: evento EVER30@MOB3 que habría tenido cada solicitud si se aprobaba.
        'oraculo_evento_por_solicitud': pd.Series(evento.astype(int), index=ids, name='evento_si_aprobada'),
    }
    return {'solicitudes': solicitudes, 'cuentas': acc.reset_index(drop=True), 'panel': panel,
            'macro': desempleo.rename_axis('mes').reset_index(), 'verdad': verdad}

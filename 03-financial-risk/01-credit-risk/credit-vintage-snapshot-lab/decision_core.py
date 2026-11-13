"""Herramientas de decisión para el backtesting de onboarding de tarjeta.

Complementa ``vintage_core`` (que mide EVER/OVER) con las piezas que convierten
la medición en decisiones de política:

1. Puente entre la mora temprana y la pérdida (``bridge_to_loss``).
2. Curva esperada, bandas de control y efecto de cohorte (``expected_curve_bands``,
   ``person_period``, ``fit_maturation_glm``).
3. Mezcla frente a tasa y economía por segmento (``shift_share``,
   ``segment_economics``, ``cutoff_tightening``).
4. Score, estrategia y rechazados (``discrimination``, ``rank_order``, ``psi``,
   ``swap_matrix``, ``infer_rejects_retro``).
5. Avance: señal o causa (``mantel_haenszel``, ``did_estimate``,
   ``did_by_cohort``, ``rd_local_linear``).
6. Prueba controlada (``sample_size_two_proportions``, ``mde_two_proportions``,
   ``assign_challenger``).

Cada función valida su contrato y devuelve tablas con denominadores explícitos.
Ninguna corrige datos en silencio. Los resultados son estimaciones bajo los
supuestos documentados en cada función y en ``GUIA_METODOLOGICA.md``.
"""
from __future__ import annotations

import hashlib
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import optimize, stats

__all__ = [
    'wilson_interval', 'bridge_to_loss', 'implied_loss_rate', 'expected_curve_bands',
    'person_period', 'fit_maturation_glm', 'shift_share', 'segment_economics',
    'account_lifetime_value', 'breakeven_bad_rate', 'cutoff_tightening', 'discrimination', 'rank_order', 'psi', 'swap_matrix',
    'infer_rejects_retro', 'infer_rejects_model', 'mantel_haenszel', 'did_estimate', 'did_by_cohort',
    'rd_local_linear', 'sample_size_two_proportions', 'mde_two_proportions',
    'assign_challenger',
]


def _require(df: pd.DataFrame, cols: Iterable[str], what: str = 'tabla') -> None:
    missing = sorted(set(cols) - set(df.columns))
    if missing:
        raise ValueError(f'Faltan columnas en {what}: {missing}')


def _binary(series: pd.Series, name: str) -> pd.Series:
    values = pd.to_numeric(series, errors='coerce')
    if values.isna().any() or not values.isin([0, 1]).all():
        raise ValueError(f'{name} debe ser binaria 0/1 sin nulos')
    return values.astype(int)


# ---------------------------------------------------------------------------
# Incertidumbre básica
# ---------------------------------------------------------------------------

def wilson_interval(events, n, z: float = 1.96):
    """Intervalo de Wilson para una proporción; NaN si n == 0.

    Acepta escalares o arreglos. Mejor cubrimiento que el intervalo normal en
    tasas bajas, que es el caso habitual de mora temprana por segmento.
    """
    k = np.asarray(events, dtype=float)
    m = np.asarray(n, dtype=float)
    if np.any(k < 0) or np.any(m < 0) or np.any(k > m):
        raise ValueError('Se requiere 0 <= eventos <= n')
    with np.errstate(invalid='ignore', divide='ignore'):
        p = np.where(m > 0, k / m, np.nan)
        denom = 1 + z**2 / m
        center = (p + z**2 / (2 * m)) / denom
        half = z * np.sqrt(p * (1 - p) / m + z**2 / (4 * m**2)) / denom
    lo, hi = center - half, center + half
    if lo.ndim == 0:
        return float(lo), float(hi)
    return lo, hi


# ---------------------------------------------------------------------------
# P1 · Puente entre EVER30@MOB3 y pérdida
# ---------------------------------------------------------------------------

def bridge_to_loss(accounts: pd.DataFrame, *, segment_cols: Sequence[str] = (),
                   early_col: str = 'evento_temprano', late_col: str = 'castigo_largo',
                   complete_col: str = 'seguimiento_largo_completo',
                   exposure_col: str = 'saldo_mob3', loss_col: str = 'perdida_neta_cop') -> pd.DataFrame:
    """Relación entre el evento temprano y el castigo en un horizonte largo.

    Solo usa cuentas con seguimiento largo completo (cosechas antiguas). Devuelve
    por segmento: P(castigo | evento), P(castigo | sin evento), lift, captura
    (fracción de castigos precedidos por evento temprano) y tasa de pérdida en
    saldo. El puente es estable solo si la relación no cambia entre cosechas;
    se debe revisar por cohorte antes de aplicarlo a cosechas jóvenes.
    """
    _require(accounts, [early_col, late_col, complete_col, exposure_col, loss_col, *segment_cols], 'cuentas')
    done = accounts.loc[_binary(accounts[complete_col], complete_col).astype(bool)].copy()
    if done.empty:
        return pd.DataFrame()
    done['_e'] = _binary(done[early_col], early_col)
    done['_c'] = _binary(done[late_col], late_col)
    exposure = pd.to_numeric(done[exposure_col], errors='coerce')
    loss = pd.to_numeric(done[loss_col], errors='coerce')
    if (exposure < 0).any() or (loss < 0).any():
        raise ValueError('Saldo y pérdida deben ser no negativos')
    done['_x'], done['_l'] = exposure, loss
    groups = done.groupby(list(segment_cols), dropna=False, sort=True) if segment_cols else [((), done)]
    rows = []
    for key, g in groups:
        key = key if isinstance(key, tuple) else (key,)
        n_e, n_ne = int(g._e.sum()), int((1 - g._e).sum())
        c_e, c_ne = int(g._c[g._e == 1].sum()), int(g._c[g._e == 0].sum())
        p_ce = c_e / n_e if n_e else np.nan
        p_cne = c_ne / n_ne if n_ne else np.nan
        lo, hi = wilson_interval(c_e, n_e) if n_e else (np.nan, np.nan)
        valid = g.dropna(subset=['_x', '_l'])
        den = float(valid._x.sum())
        rows.append(dict(zip(segment_cols, key)) | {
            'n': len(g), 'tasa_temprana': g._e.mean(), 'n_evento': n_e,
            'p_castigo_dado_evento': p_ce, 'ic_bajo': lo, 'ic_alto': hi,
            'p_castigo_sin_evento': p_cne,
            'lift': p_ce / p_cne if p_cne and p_cne > 0 else np.nan,
            'captura': c_e / (c_e + c_ne) if (c_e + c_ne) else np.nan,
            'tasa_castigo': g._c.mean(),
            'n_saldo_valido': len(valid),
            'tasa_perdida_saldo': float(valid._l.sum()) / den if den > 0 else np.nan,
        })
    return pd.DataFrame(rows)


def implied_loss_rate(early_rate, p_loss_given_event, p_loss_given_no_event):
    """Tasa de castigo proyectada: r·P(C|E) + (1−r)·P(C|¬E).

    Traduce el EVER temprano de una cosecha joven a castigo esperado usando un
    puente estimado en cosechas maduras. Hereda su supuesto de estabilidad.
    """
    r = np.asarray(early_rate, dtype=float)
    if np.any((r < 0) | (r > 1)):
        raise ValueError('La tasa temprana debe estar en [0, 1]')
    out = r * p_loss_given_event + (1 - r) * p_loss_given_no_event
    return float(out) if np.ndim(out) == 0 else out


# ---------------------------------------------------------------------------
# P2 · Curva esperada, bandas y efecto de cohorte
# ---------------------------------------------------------------------------

def expected_curve_bands(curve: pd.DataFrame, reference_cohorts: Sequence, *, cohort_col='corte_origen',
                         mob_col='mob', n_col='n_maduros', events_col='n_eventos', z: float = 1.96) -> pd.DataFrame:
    """Compara cada cohorte con la curva de referencia y marca salidas de banda.

    La curva de referencia es la tasa agregada por MOB de ``reference_cohorts``.
    La variación entre cohortes suele superar la binomial; se estima un factor de
    sobredispersión φ (chi² de Pearson / gl, mínimo 1) con las cohortes de
    referencia y las bandas se amplían por √φ.
    """
    _require(curve, [cohort_col, mob_col, n_col, events_col], 'curva')
    data = curve[[cohort_col, mob_col, n_col, events_col]].copy()
    data[n_col] = pd.to_numeric(data[n_col])
    data[events_col] = pd.to_numeric(data[events_col])
    ref = data[data[cohort_col].isin(reference_cohorts)]
    if ref.empty:
        raise ValueError('No hay cohortes de referencia en la curva')
    pooled = ref.groupby(mob_col)[[events_col, n_col]].sum()
    p_ref = (pooled[events_col] / pooled[n_col]).rename('tasa_esperada')
    data = data.merge(p_ref, left_on=mob_col, right_index=True, how='left')
    r = ref.merge(p_ref, left_on=mob_col, right_index=True)
    var = r[n_col] * r.tasa_esperada * (1 - r.tasa_esperada)
    pearson = ((r[events_col] - r[n_col] * r.tasa_esperada) ** 2 / var.where(var > 0)).sum()
    dof = len(r) - r[mob_col].nunique()
    phi = max(1.0, float(pearson / dof)) if dof > 0 else 1.0
    data['tasa_observada'] = data[events_col] / data[n_col].where(data[n_col] > 0)
    se = np.sqrt(phi * data.tasa_esperada * (1 - data.tasa_esperada) / data[n_col].where(data[n_col] > 0))
    data['banda_baja'] = (data.tasa_esperada - z * se).clip(lower=0)
    data['banda_alta'] = (data.tasa_esperada + z * se).clip(upper=1)
    data['z'] = (data.tasa_observada - data.tasa_esperada) / se
    data['estado'] = np.select([data.tasa_observada > data.banda_alta, data.tasa_observada < data.banda_baja],
                               ['sobre banda', 'bajo banda'], 'en banda')
    data['es_referencia'] = data[cohort_col].isin(reference_cohorts)
    data.attrs['sobredispersion'] = phi
    return data


def person_period(panel: pd.DataFrame, *, horizonte: int = 3, umbral_dpd: int = 30,
                  account_cols: Sequence[str] = ('id_credito', 'id_comercio'),
                  cohort_col: str = 'corte_origen') -> pd.DataFrame:
    """Panel cuenta–mes en riesgo para un hazard en tiempo discreto.

    Cada cuenta aporta MOB 1, 2, … hasta su primer DPD > umbral (incluido, con
    evento = 1) o hasta el primer mes sin observación (censura). Un mes faltante
    no se interpreta como mes sano.
    """
    _require(panel, [*account_cols, cohort_col, 'mob', 'dias_mora'], 'panel')
    d = panel[[*account_cols, cohort_col, 'mob', 'dias_mora']].copy()
    d['mob'] = pd.to_numeric(d.mob)
    d = d[(d.mob >= 1) & (d.mob <= horizonte)]
    if d.duplicated([*account_cols, 'mob']).any():
        raise ValueError('Más de una fila por cuenta y MOB')
    keys = d.drop_duplicates(list(account_cols))[[*account_cols, cohort_col]].reset_index(drop=True)
    d['_k'] = d.groupby(list(account_cols), sort=False).ngroup()
    dpd = d.pivot(index='_k', columns='mob', values='dias_mora').reindex(columns=range(1, horizonte + 1))
    dpd = dpd.reindex(keys.index).to_numpy(dtype=float)
    observed = np.cumprod(~np.isnan(dpd), axis=1).astype(bool)  # se corta en el primer mes faltante
    event = observed & (dpd > umbral_dpd)
    first_event = np.where(event.any(axis=1), event.argmax(axis=1) + 1, 0)
    n_obs = observed.sum(axis=1)
    length = np.where(first_event > 0, first_event, n_obs)
    k = np.repeat(np.arange(len(keys)), length)
    mob = np.concatenate([np.arange(1, L + 1) for L in length]) if len(k) else np.array([], dtype=int)
    out = keys.iloc[k].reset_index(drop=True)
    out['mob'] = mob.astype(int)
    out['evento'] = (first_event[k] == mob).astype(int)
    return out[[*account_cols, cohort_col, 'mob', 'evento']]


def fit_maturation_glm(pp: pd.DataFrame, *, cohort_col='corte_origen', mob_col='mob', event_col='evento',
                       macro_cols: Sequence[str] = (), reference_cohort=None) -> tuple[pd.DataFrame, object]:
    """Hazard logit: evento ~ C(MOB) + C(cohorte) + macro del mes calendario.

    Edad, período y cohorte son linealmente dependientes (período = cohorte +
    edad), por lo que un modelo APC completo no está identificado sin una
    restricción arbitraria. Aquí el período entra solo mediante covariables
    macro observadas, lo que identifica el efecto de cohorte *condicional* a esas
    covariables. Devuelve los efectos de cohorte (log-odds frente a la
    referencia) con IC 95 % y el resultado del ajuste.
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    _require(pp, [cohort_col, mob_col, event_col, *macro_cols], 'panel cuenta–mes')
    d = pp.copy()
    d['_cohorte'] = d[cohort_col].astype(str)
    ref = str(reference_cohort) if reference_cohort is not None else sorted(d._cohorte.unique())[0]
    terms = [f'C({mob_col})', f"C(_cohorte, Treatment(reference='{ref}'))", *macro_cols]
    fit = smf.glm(f'{event_col} ~ ' + ' + '.join(terms), data=d,
                  family=sm.families.Binomial()).fit()
    ci = fit.conf_int()
    rows = []
    for name, coef in fit.params.items():
        if name.startswith('C(_cohorte'):
            rows.append({'cohorte': name.split('[T.')[-1].rstrip(']'), 'efecto_log_odds': coef,
                         'ic_bajo': ci.loc[name, 0], 'ic_alto': ci.loc[name, 1], 'p_valor': fit.pvalues[name]})
    effects = pd.DataFrame(rows)
    effects.attrs['referencia'] = ref
    return effects, fit


# ---------------------------------------------------------------------------
# P3 · Mezcla frente a tasa, economía por segmento y punto de corte
# ---------------------------------------------------------------------------

def shift_share(base: pd.DataFrame, comp: pd.DataFrame, *, segment_col: str,
                n_col: str = 'n', events_col: str = 'eventos') -> pd.DataFrame:
    """Descompone el cambio de la tasa total en efecto mezcla y efecto tasa.

    Con pesos w y tasas r por segmento, la versión simétrica es exacta:
    ΔR = Σ (w₁−w₀)(r₀+r₁)/2  +  Σ (r₁−r₀)(w₀+w₁)/2.
    Un segmento ausente en un período aporta solo mezcla. El total queda en
    ``attrs`` (``tasa_base``, ``tasa_comparacion``, ``efecto_mezcla``,
    ``efecto_tasa``).
    """
    for df, label in [(base, 'base'), (comp, 'comparación')]:
        _require(df, [segment_col, n_col, events_col], label)
        if df[segment_col].duplicated().any():
            raise ValueError(f'Segmentos duplicados en {label}')
    b = base.set_index(segment_col)[[n_col, events_col]].astype(float)
    c = comp.set_index(segment_col)[[n_col, events_col]].astype(float)
    if b[n_col].sum() <= 0 or c[n_col].sum() <= 0:
        raise ValueError('Cada período necesita al menos una cuenta')
    idx = b.index.union(c.index)
    b, c = b.reindex(idx, fill_value=0), c.reindex(idx, fill_value=0)
    w0, w1 = b[n_col] / b[n_col].sum(), c[n_col] / c[n_col].sum()
    r0 = (b[events_col] / b[n_col]).where(b[n_col] > 0)
    r1 = (c[events_col] / c[n_col]).where(c[n_col] > 0)
    r0, r1 = r0.fillna(r1), r1.fillna(r0)
    out = pd.DataFrame({'peso_base': w0, 'peso_comparacion': w1, 'tasa_base': r0, 'tasa_comparacion': r1})
    out['efecto_mezcla'] = (w1 - w0) * (r0 + r1) / 2
    out['efecto_tasa'] = (r1 - r0) * (w0 + w1) / 2
    out = out.reset_index().rename(columns={'index': segment_col})
    total0 = float((b[events_col].sum()) / b[n_col].sum())
    total1 = float((c[events_col].sum()) / c[n_col].sum())
    out.attrs.update(tasa_base=total0, tasa_comparacion=total1,
                     efecto_mezcla=float(out.efecto_mezcla.sum()), efecto_tasa=float(out.efecto_tasa.sum()))
    return out


ECONOMICS_REQUIRED = ['n_cuentas', 'saldo_promedio_cop', 'tasa_interes_anual', 'ingreso_intercambio_anual_cop',
                      'ingreso_comisiones_anual_cop', 'costo_fondeo_anual', 'costo_operativo_anual_cop',
                      'costo_adquisicion_cop', 'pd_anual', 'lgd']


def segment_economics(table: pd.DataFrame, *, horizonte_anios: float = 3.0, capital_ratio: float | None = None,
                      hurdle: float | None = None) -> pd.DataFrame:
    """Margen anual ajustado por riesgo por cuenta y PD de equilibrio por segmento.

    Por cuenta y año: ingreso = saldo·tasa + intercambio + comisiones;
    costo = saldo·fondeo + operación + adquisición/horizonte; pérdida esperada
    = PD·LGD·EAD (EAD = ``ead_cop`` si existe, si no el saldo promedio).
    PD de equilibrio = (ingreso − costo) / (LGD·EAD): la PD anual con la que el
    segmento deja de generar valor. Con ``capital_ratio`` se añade RAROC sobre
    capital = ratio·saldo y, con ``hurdle``, la creación de valor sobre ese costo.
    """
    _require(table, ECONOMICS_REQUIRED, 'economía por segmento')
    if horizonte_anios <= 0:
        raise ValueError('El horizonte debe ser positivo')
    t = table.copy()
    num = ECONOMICS_REQUIRED + (['ead_cop'] if 'ead_cop' in t else [])
    t[num] = t[num].apply(pd.to_numeric)
    if ((t[['pd_anual', 'lgd']] < 0) | (t[['pd_anual', 'lgd']] > 1)).any().any():
        raise ValueError('PD y LGD deben estar en [0, 1]')
    ead = t['ead_cop'] if 'ead_cop' in t else t.saldo_promedio_cop
    t['ingreso_cuenta'] = t.saldo_promedio_cop * t.tasa_interes_anual + t.ingreso_intercambio_anual_cop + t.ingreso_comisiones_anual_cop
    t['costo_cuenta'] = (t.saldo_promedio_cop * t.costo_fondeo_anual + t.costo_operativo_anual_cop
                         + t.costo_adquisicion_cop / horizonte_anios)
    t['perdida_esperada_cuenta'] = t.pd_anual * t.lgd * ead
    t['margen_ajustado_cuenta'] = t.ingreso_cuenta - t.costo_cuenta - t.perdida_esperada_cuenta
    t['margen_ajustado_total'] = t.margen_ajustado_cuenta * t.n_cuentas
    exposure = (t.lgd * ead).where(t.lgd * ead > 0)
    t['pd_equilibrio'] = (t.ingreso_cuenta - t.costo_cuenta) / exposure
    t['holgura_pd'] = t.pd_equilibrio - t.pd_anual
    if capital_ratio is not None:
        capital = capital_ratio * t.saldo_promedio_cop
        t['raroc'] = t.margen_ajustado_cuenta / capital.where(capital > 0)
        if hurdle is not None:
            t['valor_sobre_hurdle_total'] = (t.margen_ajustado_cuenta - hurdle * capital) * t.n_cuentas
    return t


def account_lifetime_value(df: pd.DataFrame, *, bad_col: str, balance_col: str, annual_margin, horizon_years: float,
                           p_loss_bad: float, p_loss_good: float, lgd: float, years_to_loss: float = .75,
                           collection_cost_bad: float = 0.0) -> pd.Series:
    """Valor de vida esperado por cuenta según su desempeño temprano.

    Bueno: ``H·m − b·LGD·B``. Malo (evento temprano): se cura con probabilidad
    ``1 − a`` y conserva ``H·m``; con probabilidad ``a`` se castiga, genera margen
    solo ``τ`` años y pierde ``LGD·B``; siempre paga cobranza ``k``:
    ``(1−a)·H·m + a·(τ·m − LGD·B) − k``. ``a`` y ``b`` vienen del puente
    (``bridge_to_loss``); ``annual_margin`` = ingreso − costo por cuenta y año,
    escalar o serie alineada con ``df``.
    """
    _require(df, [bad_col, balance_col], 'cuentas')
    if not (0 <= p_loss_bad <= 1 and 0 <= p_loss_good <= 1 and 0 <= lgd <= 1):
        raise ValueError('Probabilidades y LGD deben estar en [0, 1]')
    if horizon_years <= 0 or not 0 <= years_to_loss <= horizon_years:
        raise ValueError('Se requiere 0 <= τ <= H y H > 0')
    bad = _binary(df[bad_col], bad_col)
    balance = pd.to_numeric(df[balance_col])
    m = annual_margin if np.isscalar(annual_margin) else pd.Series(annual_margin, index=df.index)
    good_value = horizon_years * m - p_loss_good * lgd * balance
    bad_value = ((1 - p_loss_bad) * horizon_years * m + p_loss_bad * (years_to_loss * m - lgd * balance)
                 - collection_cost_bad)
    return pd.Series(np.where(bad == 1, bad_value, good_value), index=df.index, name='valor_vida')


def breakeven_bad_rate(values, bad) -> float:
    """Tasa de malos que anula el valor: ḡ / (ḡ + ℓ̄).

    ḡ es el valor medio de un bueno y ℓ̄ la pérdida media de un malo. Una banda
    con tasa de malos mayor destruye valor; menor, lo crea. NaN si los buenos no
    crean valor o los malos no lo destruyen.
    """
    v = pd.Series(values, dtype=float).reset_index(drop=True)
    y = _binary(pd.Series(bad).reset_index(drop=True), 'malo')
    g, l = v[y == 0].mean(), -v[y == 1].mean()
    return float(g / (g + l)) if g > 0 and l > 0 else np.nan


def cutoff_tightening(df: pd.DataFrame, *, score_col: str, bad_col: str, gain_good, loss_bad,
                      cutoffs: Sequence[float] | None = None) -> pd.DataFrame:
    """Valor de endurecer el corte sobre la población aprobada observada.

    Para cada corte c se dejan de aprobar las cuentas con score < c: se evitan
    sus malos (``loss_bad`` cada uno) y se pierden sus buenos (``gain_good``).
    Solo evalúa **endurecer**: aflojar el corte exige desempeño de rechazados
    (ver ``infer_rejects_retro``). ``gain_good``/``loss_bad`` pueden ser
    escalares o nombres de columna con valores por cuenta.
    """
    _require(df, [score_col, bad_col], 'aprobados')
    d = df.copy()
    d['_s'] = pd.to_numeric(d[score_col], errors='coerce')
    if d._s.isna().any():
        raise ValueError('Score nulo: definir tratamiento antes del análisis de corte')
    d['_b'] = _binary(d[bad_col], bad_col)
    d['_g'] = pd.to_numeric(d[gain_good]) if isinstance(gain_good, str) else float(gain_good)
    d['_l'] = pd.to_numeric(d[loss_bad]) if isinstance(loss_bad, str) else float(loss_bad)
    if cutoffs is None:
        cutoffs = np.unique(np.quantile(d._s, np.linspace(0, .5, 11)))
    rows = []
    for c in cutoffs:
        drop = d._s < c
        keep = ~drop
        rows.append({'corte': c, 'aprobacion_retenida': keep.mean(),
                     'tasa_malos_retenida': d._b[keep].mean() if keep.any() else np.nan,
                     'malos_evitados': int(d._b[drop].sum()), 'buenos_perdidos': int((1 - d._b[drop]).sum()),
                     'valor_neto': float((d._l * d._b)[drop].sum() - (d._g * (1 - d._b))[drop].sum())})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# P4 · Score, estrategia y rechazados
# ---------------------------------------------------------------------------

def discrimination(score, bad, *, higher_is_better: bool = True) -> dict:
    """AUC, Gini y KS del score frente al evento malo (1 = malo)."""
    s = np.asarray(pd.to_numeric(pd.Series(score), errors='coerce'), dtype=float)
    y = np.asarray(_binary(pd.Series(bad), 'malo'))
    if np.isnan(s).any():
        raise ValueError('Score con nulos')
    if y.min() == y.max():
        return {'n': len(y), 'malos': int(y.sum()), 'auc': np.nan, 'gini': np.nan, 'ks': np.nan}
    risk = -s if higher_is_better else s
    ranks = stats.rankdata(risk)
    n1, n0 = y.sum(), len(y) - y.sum()
    auc = (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    order = np.argsort(risk, kind='mergesort')[::-1]
    ys, rs = y[order], risk[order]
    cum_bad, cum_good = np.cumsum(ys) / n1, np.cumsum(1 - ys) / n0
    last = np.r_[rs[1:] != rs[:-1], True]
    ks = float(np.max(np.abs(cum_bad[last] - cum_good[last])))
    return {'n': len(y), 'malos': int(n1), 'auc': float(auc), 'gini': float(2 * auc - 1), 'ks': ks}


def rank_order(score, bad, *, n_bins: int = 10) -> pd.DataFrame:
    """Tasa de malos por cuantil de score y verificación de orden monótono."""
    d = pd.DataFrame({'s': pd.to_numeric(pd.Series(score)), 'y': _binary(pd.Series(bad), 'malo')})
    d['banda'] = pd.qcut(d.s, n_bins, duplicates='drop')
    out = d.groupby('banda', observed=True).agg(n=('y', 'size'), malos=('y', 'sum'), score_min=('s', 'min'),
                                                 score_max=('s', 'max')).reset_index()
    out['tasa_malos'] = out.malos / out.n
    out['ic_bajo'], out['ic_alto'] = wilson_interval(out.malos, out.n)
    out.attrs['monotono'] = bool(out.tasa_malos.is_monotonic_decreasing)
    return out


def psi(expected, actual, *, n_bins: int = 10, eps: float = 1e-6) -> float:
    """Population Stability Index con cortes en cuantiles de la base.

    Convención habitual: < 0,10 estable; 0,10–0,25 vigilar; > 0,25 cambio material.
    Son umbrales de práctica, no pruebas estadísticas.
    """
    e = pd.to_numeric(pd.Series(expected)).dropna().to_numpy()
    a = pd.to_numeric(pd.Series(actual)).dropna().to_numpy()
    if len(e) == 0 or len(a) == 0:
        raise ValueError('Se requieren observaciones en ambas poblaciones')
    edges = np.unique(np.quantile(e, np.linspace(0, 1, n_bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    pe = np.histogram(e, edges)[0] / len(e) + eps
    pa = np.histogram(a, edges)[0] / len(a) + eps
    return float(np.sum((pa - pe) * np.log(pa / pe)))


def swap_matrix(df: pd.DataFrame, *, decision_a: str, decision_b: str, bad_col: str) -> pd.DataFrame:
    """Matriz de intercambio entre la política vigente (a) y la alternativa (b).

    1 = aprueba. Swap-out: aprobadas hoy que la alternativa rechazaría;
    swap-in: rechazadas hoy que la alternativa aprobaría.

    Muestra cuántas solicitudes aprueba cada política y la tasa de malos donde es
    observable. Las celdas con política vigente = rechaza no tienen desempeño
    interno: su tasa queda vacía, no en cero.
    """
    _require(df, [decision_a, decision_b, bad_col], 'solicitudes')
    d = df.copy()
    d['_a'], d['_b'] = _binary(d[decision_a], decision_a), _binary(d[decision_b], decision_b)
    bad = pd.to_numeric(d[bad_col], errors='coerce')
    d['_y'] = bad
    rows = []
    for (a, b), g in d.groupby(['_a', '_b']):
        obs = g._y.dropna()
        rows.append({decision_a: a, decision_b: b, 'n': len(g), 'n_con_desempeno': len(obs),
                     'tasa_malos_observada': obs.mean() if len(obs) else np.nan})
    out = pd.DataFrame(rows)
    out['celda'] = np.select([(out[decision_a] == 1) & (out[decision_b] == 1), (out[decision_a] == 1) & (out[decision_b] == 0),
                              (out[decision_a] == 0) & (out[decision_b] == 1)],
                             ['ambas aprueban', f'swap-out: solo {decision_a} aprueba',
                              f'swap-in: solo {decision_b} aprueba'], 'ambas rechazan')
    return out


def infer_rejects_retro(df: pd.DataFrame, *, band_col: str, approved_col: str, internal_bad_col: str,
                        retro_bad_col: str) -> pd.DataFrame:
    """Inferencia de rechazados con desempeño en otras entidades (*bureau retro*).

    Entre aprobados de cada banda se estima k = tasa interna / tasa retro. Para
    rechazados de la misma banda: tasa interna inferida = k · tasa retro.
    Supuesto: la relación entre comportamiento interno y externo es igual para
    aprobados y rechazados de una banda. Es un método simple y sesgado cuando
    los rechazados de una banda son más riesgosos que sus aprobados (la razón no
    es constante) o cuando una banda no tiene aprobados. Usarlo como contraste de
    ``infer_rejects_model``, no como estimación principal.
    """
    _require(df, [band_col, approved_col, internal_bad_col, retro_bad_col], 'solicitudes')
    d = df.copy()
    d['_ap'] = _binary(d[approved_col], approved_col)
    d['_rb'] = pd.to_numeric(d[retro_bad_col], errors='coerce')
    d['_ib'] = pd.to_numeric(d[internal_bad_col], errors='coerce')
    rows = []
    for band, g in d.groupby(band_col, observed=True, sort=True):
        ap, rj = g[g._ap == 1], g[g._ap == 0]
        ap_both = ap.dropna(subset=['_rb', '_ib'])
        retro_ap = ap_both._rb.mean() if len(ap_both) else np.nan
        k = ap_both._ib.mean() / retro_ap if len(ap_both) and retro_ap > 0 else np.nan
        retro_rj = rj._rb.dropna().mean() if rj._rb.notna().any() else np.nan
        rows.append({band_col: band, 'n_aprobados': len(ap), 'n_rechazados': len(rj),
                     'tasa_interna_aprobados': ap._ib.dropna().mean() if ap._ib.notna().any() else np.nan,
                     'tasa_retro_aprobados': retro_ap, 'factor_k': k, 'tasa_retro_rechazados': retro_rj,
                     'tasa_interna_inferida_rechazados': k * retro_rj if pd.notna(k) and pd.notna(retro_rj) else np.nan})
    return pd.DataFrame(rows)


def infer_rejects_model(approved: pd.DataFrame, rejected: pd.DataFrame, *, features: Sequence[str],
                        outcome_col: str) -> tuple[pd.Series, pd.DataFrame]:
    """Inferencia de rechazados por modelo ajustado en aprobados (aumentación).

    Si la aprobación depende solo de variables observadas (regla de score y TPV),
    la selección es ignorable condicional a ellas y un modelo de
    ``outcome ~ features`` ajustado en aprobados es válido para rechazados
    **dentro del soporte** de los aprobados. Fuera de ese soporte el resultado es
    una extrapolación: el diagnóstico informa, por variable, qué fracción de
    rechazados cae fuera del rango aprobado y a cuántas desviaciones estándar.
    Con una regla determinística, todo rechazado queda fuera del soporte en al
    menos una variable: la inferencia siempre extrapola y lo relevante es la
    distancia (pred.attrs['distancia_sd'], por fila).
    Con aprobaciones manuales (*overrides*) la selección también depende de
    información no observada y este supuesto falla.
    """
    from sklearn.linear_model import LogisticRegression

    _require(approved, [*features, outcome_col], 'aprobados')
    _require(rejected, list(features), 'rechazados')
    X = approved[list(features)].apply(pd.to_numeric)
    Z = rejected[list(features)].apply(pd.to_numeric)
    if X.isna().any().any() or Z.isna().any().any():
        raise ValueError('Variables con nulos: imputar con una regla explícita antes de inferir')
    y = _binary(approved[outcome_col], outcome_col)
    mu, sd = X.mean(), X.std(ddof=0).replace(0, 1)
    model = LogisticRegression(C=1e6, max_iter=2000).fit((X - mu) / sd, y)
    pred = pd.Series(model.predict_proba((Z - mu) / sd)[:, 1], index=rejected.index, name='malo_inferido')
    lo, hi = X.min(), X.max()
    outside = (Z.lt(lo) | Z.gt(hi))
    dist = (np.maximum(lo - Z, 0) + np.maximum(Z - hi, 0)) / sd
    diag = pd.DataFrame({'min_aprobados': lo, 'max_aprobados': hi, 'fraccion_fuera_soporte': outside.mean(),
                         'distancia_max_sd': dist.max()})
    diag.attrs['fraccion_alguna_fuera'] = float(outside.any(axis=1).mean())
    pred.attrs['fuera_soporte'] = outside.any(axis=1)
    pred.attrs['distancia_sd'] = dist.max(axis=1)
    return pred, diag


# ---------------------------------------------------------------------------
# P5 · Avance: señal o causa
# ---------------------------------------------------------------------------

def mantel_haenszel(df: pd.DataFrame, *, exposure_col: str, outcome_col: str, strata_cols: Sequence[str]) -> dict:
    """Riesgo relativo y diferencia de riesgo crudos y ajustados por estratos.

    RR de Mantel-Haenszel con varianza de Greenland-Robins; diferencia de
    riesgo MH con pesos n₁n₀/N. Ajustar por estratos observados no elimina la
    confusión por variables no observadas (por ejemplo, estrés financiero que
    lleva a la vez a pedir el avance y a caer en mora).
    """
    _require(df, [exposure_col, outcome_col, *strata_cols], 'tabla landmark')
    d = df.copy()
    d['_x'], d['_y'] = _binary(d[exposure_col], exposure_col), _binary(d[outcome_col], outcome_col)
    n1, n0 = (d._x == 1).sum(), (d._x == 0).sum()
    if n1 == 0 or n0 == 0:
        raise ValueError('Se requieren expuestos y no expuestos')
    r1, r0 = d._y[d._x == 1].mean(), d._y[d._x == 0].mean()
    num_rr = den_rr = var_num = num_rd = w_rd = 0.0
    used = 0
    for _, g in d.groupby(list(strata_cols), observed=True):
        a = ((g._x == 1) & (g._y == 1)).sum(); b = ((g._x == 1) & (g._y == 0)).sum()
        c = ((g._x == 0) & (g._y == 1)).sum(); e = ((g._x == 0) & (g._y == 0)).sum()
        m1, m0 = a + b, c + e
        N = m1 + m0
        if m1 == 0 or m0 == 0:
            continue
        used += 1
        num_rr += a * m0 / N
        den_rr += c * m1 / N
        var_num += (m1 * m0 * (a + c) - a * c * N) / N**2
        w = m1 * m0 / N
        num_rd += w * (a / m1 - c / m0)
        w_rd += w
    rr = num_rr / den_rr if den_rr > 0 else np.nan
    se = np.sqrt(var_num / (num_rr * den_rr)) if num_rr > 0 and den_rr > 0 else np.nan
    return {'riesgo_expuestos': float(r1), 'riesgo_no_expuestos': float(r0), 'rr_crudo': float(r1 / r0) if r0 > 0 else np.nan,
            'rd_crudo': float(r1 - r0), 'rr_mh': float(rr), 'rr_mh_ic_bajo': float(rr * np.exp(-1.96 * se)),
            'rr_mh_ic_alto': float(rr * np.exp(1.96 * se)), 'rd_mh': float(num_rd / w_rd) if w_rd else np.nan,
            'estratos_usados': used}


def did_estimate(df: pd.DataFrame, *, outcome_col: str, treated_col: str, post_col: str, cluster_col: str,
                 controls: Sequence[str] = ()) -> dict:
    """Diferencias en diferencias con modelo lineal de probabilidad.

    y = α + β·tratado + γ·post + δ·(tratado×post) [+ controles]. δ es el efecto
    de la política sobre el grupo tratado bajo tendencias paralelas. Errores
    agrupados por ``cluster_col`` (cohorte), pues el choque es común dentro de
    cada cosecha. Con pocas cohortes, los errores agrupados son poco confiables:
    se informa el número de clusters.
    """
    import statsmodels.formula.api as smf

    _require(df, [outcome_col, treated_col, post_col, cluster_col, *controls], 'panel DiD')
    d = df.copy()
    for c in (outcome_col, treated_col, post_col):
        d[c] = _binary(d[c], c)
    formula = f'{outcome_col} ~ {treated_col} * {post_col}' + ''.join(f' + {c}' for c in controls)
    groups = pd.factorize(d[cluster_col])[0]
    fit = smf.ols(formula, data=d).fit(cov_type='cluster', cov_kwds={'groups': groups})
    term = f'{treated_col}:{post_col}'
    lo, hi = fit.conf_int().loc[term]
    return {'efecto': float(fit.params[term]), 'error_estandar': float(fit.bse[term]), 'ic_bajo': float(lo),
            'ic_alto': float(hi), 'p_valor': float(fit.pvalues[term]), 'clusters': int(len(np.unique(groups))), 'n': int(len(d))}


def did_by_cohort(df: pd.DataFrame, *, outcome_col: str, treated_col: str, cohort_col: str) -> pd.DataFrame:
    """Brecha tratado − control por cohorte, para revisar tendencias paralelas."""
    _require(df, [outcome_col, treated_col, cohort_col], 'panel DiD')
    d = df.copy()
    d['_t'], d['_y'] = _binary(d[treated_col], treated_col), _binary(d[outcome_col], outcome_col)
    g = d.groupby([cohort_col, '_t'])._y.agg(['mean', 'size']).unstack('_t')
    out = pd.DataFrame({'tasa_control': g[('mean', 0)], 'tasa_tratado': g[('mean', 1)],
                        'n_control': g[('size', 0)], 'n_tratado': g[('size', 1)]})
    out['brecha'] = out.tasa_tratado - out.tasa_control
    return out.reset_index()


def rd_local_linear(df: pd.DataFrame, *, running_col: str, outcome_col: str, cutoff: float, bandwidth: float) -> dict:
    """Salto en el umbral con regresión lineal local y kernel triangular.

    Útil para umbrales que cambian un **tratamiento entre aprobados** (por
    ejemplo, cupo o cupo de avance por banda de score). No sirve en el umbral de
    aprobación para medir mora: debajo del corte no hay desempeño. Para RD
    difuso, dividir el salto en el resultado por el salto en el tratamiento.
    """
    import statsmodels.api as sm

    _require(df, [running_col, outcome_col], 'tabla RD')
    if bandwidth <= 0:
        raise ValueError('El ancho de banda debe ser positivo')
    x = pd.to_numeric(df[running_col]) - cutoff
    y = pd.to_numeric(df[outcome_col])
    keep = (x.abs() < bandwidth) & y.notna()
    x, y = x[keep], y[keep]
    right = (x >= 0).astype(float)
    if right.sum() < 10 or (1 - right).sum() < 10:
        raise ValueError('Muy pocas observaciones a uno de los lados del umbral')
    X = sm.add_constant(pd.DataFrame({'derecha': right, 'x': x, 'x_derecha': x * right}))
    w = 1 - x.abs() / bandwidth
    fit = sm.WLS(y, X, weights=w).fit(cov_type='HC1')
    lo, hi = fit.conf_int().loc['derecha']
    return {'salto': float(fit.params['derecha']), 'error_estandar': float(fit.bse['derecha']), 'ic_bajo': float(lo),
            'ic_alto': float(hi), 'n_izquierda': int((right == 0).sum()), 'n_derecha': int(right.sum())}


# ---------------------------------------------------------------------------
# P6 · Prueba controlada
# ---------------------------------------------------------------------------

def sample_size_two_proportions(p_control: float, p_challenger: float, *, alpha: float = .05, power: float = .8,
                                ratio: float = 1.0) -> dict:
    """Tamaño de muestra para comparar dos proporciones (prueba bilateral).

    ``ratio`` = n_challenger / n_control. Fórmula normal clásica con varianza
    combinada bajo H₀. Si la asignación es por cohorte o comercio, multiplicar
    por el efecto de diseño 1 + (m−1)·ICC.
    """
    if not (0 < p_control < 1 and 0 < p_challenger < 1) or p_control == p_challenger:
        raise ValueError('Proporciones en (0,1) y distintas')
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    pbar = (p_control + ratio * p_challenger) / (1 + ratio)
    num = (za * np.sqrt(pbar * (1 - pbar) * (1 + 1 / ratio))
           + zb * np.sqrt(p_control * (1 - p_control) + p_challenger * (1 - p_challenger) / ratio)) ** 2
    n0 = int(np.ceil(num / (p_control - p_challenger) ** 2))
    return {'n_control': n0, 'n_challenger': int(np.ceil(n0 * ratio)), 'n_total': n0 + int(np.ceil(n0 * ratio))}


def mde_two_proportions(p_control: float, n_control: int, n_challenger: int, *, alpha: float = .05,
                        power: float = .8, direction: int = -1) -> float:
    """Efecto mínimo detectable (diferencia absoluta) con los tamaños dados."""
    ratio = n_challenger / n_control

    def gap(delta):
        return sample_size_two_proportions(p_control, p_control + direction * delta, alpha=alpha, power=power,
                                           ratio=ratio)['n_control'] - n_control

    upper = p_control - 1e-6 if direction < 0 else 1 - p_control - 1e-6
    if gap(upper) > 0:
        return np.nan
    return float(optimize.brentq(lambda d: gap(d) + .5, 1e-6, upper))


def assign_challenger(ids: Iterable, *, share: float, salt: str) -> pd.Series:
    """Asignación determinista y auditable por hash: 1 = challenger.

    El mismo identificador y la misma sal siempre dan el mismo brazo, lo que
    permite reconstruir la asignación sin guardar una tabla aparte.
    """
    if not 0 < share < 1:
        raise ValueError('La proporción debe estar en (0, 1)')
    if not salt:
        raise ValueError('Defina una sal propia del experimento')
    ids = list(ids)
    u = [int(hashlib.sha256(f'{salt}|{i}'.encode()).hexdigest()[:15], 16) / 16**15 for i in ids]
    return pd.Series((np.array(u) < share).astype(int), index=ids, name='challenger')

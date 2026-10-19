"""Synthetic impairment research: explicit input contracts and cash-flow basis.

This is not an accounting policy or a complete implementation of IFRS 9. Stage
classification is illustrative. Stage 1/2 use annual default buckets and constant
EAD/LGD; credit-impaired funded assets require supplied expected recovery flows.
POCI, modification accounting, cures and accounting entries are outside scope.
"""
from __future__ import annotations

from numbers import Integral
import numpy as np
import pandas as pd


def _count(value, name, maximum=1_000_000):
    if isinstance(value, bool) or not isinstance(value, Integral) or not 1 <= value <= maximum:
        raise ValueError(f"{name}: integer in [1,{maximum}] required")


def _finite(values, name):
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or result.size == 0 or not np.isfinite(result).all():
        raise ValueError(f"{name}: nonempty finite vector required")
    return result


def cartera_sintetica(n: int = 2_000, semilla: int = 91) -> pd.DataFrame:
    """Reproducible synthetic inputs; recovery cash flows are assumed, not fitted."""
    _count(n, "n")
    rng = np.random.default_rng(semilla)
    score = rng.normal(0, 1, n)
    macro = rng.normal(0, 1, n)
    pd_12m = 1 / (1 + np.exp(-(-2.8 - 0.9 * score + 0.35 * macro)))
    out = pd.DataFrame({
        "loan_id": np.arange(1, n + 1), "score": score, "macro": macro,
        "pd_12m": pd_12m.clip(0.001, 0.45),
        "pd_origen": (pd_12m * rng.uniform(.55, .9, n)).clip(.001, .4),
        "dpd": rng.choice([0, 15, 35, 95], n, p=[.78, .12, .07, .03]),
        "ead": rng.lognormal(10.7, .7, n),
        "lgd_base": rng.beta(3, 4, n),
        "ccf": rng.uniform(.2, .85, n), "undrawn": rng.lognormal(9.5, .8, n),
    })
    # Funded gross carrying amount is distinct from a future drawdown exposure.
    out["gross_carrying_amount"] = out.ead
    out["recovery_times"] = [(1., 2., 3.)] * n
    out["recovery_cashflows"] = [tuple(gross * (1-lgd) * np.array([.6, .3, .1]))
                                  for gross, lgd in zip(out.ead, out.lgd_base)]
    return out


def stage(pd_actual: pd.Series, pd_origen: pd.Series, dpd: pd.Series,
          umbral_sicr: float = 2.0) -> pd.Series:
    """Illustrative rule, not a sufficient credit-impairment/SICR definition."""
    if not all(isinstance(x, pd.Series) for x in (pd_actual, pd_origen, dpd)):
        raise ValueError("Stage inputs must be pandas Series with matching index")
    if not pd_actual.index.equals(pd_origen.index) or not pd_actual.index.equals(dpd.index):
        raise ValueError("Stage inputs require identical index and ordering")
    current, origin, arrears = (_finite(x, name) for x, name in
                                [(pd_actual, "pd_actual"), (pd_origen, "pd_origen"), (dpd, "dpd")])
    if ((current < 0).any() or (current > 1).any() or (origin <= 0).any() or (origin > 1).any()
            or (arrears < 0).any() or (arrears != np.floor(arrears)).any()
            or not np.isfinite(umbral_sicr) or umbral_sicr <= 0):
        raise ValueError("Invalid PD, original PD, DPD or SICR threshold")
    ratio = current / origin
    return pd.Series(np.select([arrears >= 90, (arrears >= 30) | (ratio >= umbral_sicr)],
                               [3, 2], default=1), index=pd_actual.index, dtype=int)


def pd_lifetime(pd_12m: pd.Series, horizonte: int = 5,
                crecimiento_hazard: float = .10) -> tuple[np.ndarray, np.ndarray]:
    """Return conditional annual default probabilities and marginal masses.

    The cumulative default mass is sum(marginal), not sum(conditional). Already
    defaulted exposures (PD=1) are outside this future-default hazard conversion.
    """
    probabilities = _finite(pd_12m, "pd_12m")
    _count(horizonte, "horizonte", 120)
    if ((probabilities < 0).any() or (probabilities >= 1).any()
            or not np.isfinite(crecimiento_hazard) or crecimiento_hazard < -1):
        raise ValueError("Require PD in [0,1), finite hazard growth >= -1")
    with np.errstate(over="raise", invalid="raise"):
        hazard0 = -np.log1p(-probabilities)
        hazards = hazard0[:, None] * (1 + crecimiento_hazard) ** np.arange(horizonte)
        conditional = -np.expm1(-hazards)
        survival_start = np.concatenate([np.ones((len(probabilities), 1)),
                                         np.exp(-np.cumsum(hazards[:, :-1], axis=1))], axis=1)
        marginal = survival_start * conditional
    if not np.isfinite(marginal).all():
        raise ArithmeticError("Nonfinite lifetime default curve")
    return conditional, marginal


def credit_impaired_shortfall(gross_carrying_amount: float, recovery_cashflows,
                              recovery_times, effective_interest_rate: float) -> dict[str, float]:
    """Funded, non-POCI illustrative loss from supplied expected net recoveries.

    Times are years from the reporting date; the rate is annual effective. Expected
    net recoveries are nonnegative in this bounded interface. The raw difference
    and any recovery surplus remain visible even when the allowance floor is zero.
    """
    flows = _finite(recovery_cashflows, "recovery_cashflows")
    times = _finite(recovery_times, "recovery_times")
    if (flows.shape != times.shape or (flows < 0).any() or (times < 0).any()
            or (np.diff(times) <= 0).any() or not np.isfinite(gross_carrying_amount)
            or gross_carrying_amount < 0 or not np.isfinite(effective_interest_rate)
            or effective_interest_rate <= -1):
        raise ValueError("Invalid funded carrying amount, recovery cash flows, times or EIR")
    with np.errstate(over="raise", invalid="raise"):
        pv = float(np.sum(flows * np.exp(-np.log1p(effective_interest_rate) * times)))
    if not np.isfinite(pv):
        raise ArithmeticError("Nonfinite recovery present value")
    raw = float(gross_carrying_amount - pv)
    # Within the bounded nonnegative-rate case, avoid cancellation of a tiny
    # delay loss when nominal recoveries equal gross. Preserve the existing
    # surplus/negative-rate route outside that domain.
    nominal = float(np.sum(flows))
    if effective_interest_rate >= 0 and nominal <= gross_carrying_amount:
        delay_loss = -np.expm1(-np.log1p(effective_interest_rate) * times)
        raw = float((gross_carrying_amount - nominal) + np.sum(flows * delay_loss))
    return {"pv_expected_recoveries": pv, "raw_shortfall": raw,
            "ecl": max(raw, 0.), "recovery_surplus": max(-raw, 0.)}


def _validate_portfolio(cartera):
    required = {"loan_id", "pd_12m", "pd_origen", "dpd", "ead", "lgd_base", "ccf", "undrawn"}
    if not isinstance(cartera, pd.DataFrame) or cartera.empty or required - set(cartera):
        raise ValueError("Portfolio is empty or lacks required columns")
    if not cartera.index.is_unique or cartera.loan_id.isna().any() or not cartera.loan_id.is_unique:
        raise ValueError("Unique nonnull loan IDs and unique index required")
    for name in required - {"loan_id"}:
        values = _finite(cartera[name], name)
        if (values < 0).any():
            raise ValueError(f"{name}: negative values")
        if name in {"pd_12m", "pd_origen", "lgd_base", "ccf"} and (values > 1).any():
            raise ValueError(f"{name}: values above one")
    categories = stage(cartera.pd_12m, cartera.pd_origen, cartera.dpd)
    if ((cartera.pd_12m >= 1) & categories.ne(3)).any():
        raise ValueError("PD=1 outside Stage 3 cannot be used in a future-default hazard curve")


def ecl_componentes(cartera: pd.DataFrame, escenario: str = "base", horizonte: int = 5,
                    tasa_descuento: float = .10) -> pd.DataFrame:
    """Stage 1/2 hazard proxy; Stage 3 expected recovery PV with explicit inputs.

    The rate is a supplied illustrative EIR, not inferred from portfolio rates.
    EAD is constant across annual default buckets. This does not implement POCI.
    """
    _validate_portfolio(cartera)
    _count(horizonte, "horizonte", 120)
    if not np.isfinite(tasa_descuento) or tasa_descuento <= -1:
        raise ValueError("Finite effective discount rate > -1 required")
    shocks = {"base": (1., 1.), "adverso": (1.45, 1.18), "severo": (2.10, 1.35)}
    if escenario not in shocks:
        raise ValueError("escenario must be base, adverso or severo")
    pd_mult, lgd_mult = shocks[escenario]
    out = cartera.copy()
    out["stage"] = stage(out.pd_12m, out.pd_origen, out.dpd)
    curve_pd = (out.pd_12m * pd_mult).clip(upper=np.nextafter(1., 0.)).where(out.stage.ne(3), 0.)
    _, marginal = pd_lifetime(curve_pd, horizonte)
    lgd = (out.lgd_base * lgd_mult).clip(upper=1.).to_numpy()
    with np.errstate(over="raise", invalid="raise"):
        ead = (out.ead + out.ccf * out.undrawn).to_numpy()
        discount = np.exp(-np.log1p(tasa_descuento) * np.arange(1, horizonte + 1))
        out["ecl_12m"] = marginal[:, 0] * discount[0] * lgd * ead
        out["ecl_lifetime"] = (marginal * discount).sum(axis=1) * lgd * ead
    out["ecl"] = np.where(out.stage.eq(1), out.ecl_12m, out.ecl_lifetime)
    out["ecl_basis"] = np.where(out.stage.eq(1), "annual_12m_default_proxy", "annual_lifetime_default_proxy")
    out["pv_expected_recoveries"] = np.nan
    out["recovery_surplus"] = 0.
    impaired = out.stage.eq(3)
    if impaired.any():
        required = {"gross_carrying_amount", "recovery_cashflows", "recovery_times"}
        if required - set(out):
            raise ValueError("Stage 3 requires funded gross carrying amount and expected recovery cash flows/times")
        for index in out.index[impaired]:
            row = out.loc[index]
            # Synthetic scenario assumption: scale recoveries, never multiply by
            # a probability of a future default on an already impaired asset.
            base_lgd = float(row.lgd_base)
            stressed_lgd = min(base_lgd * lgd_mult, 1.)
            factor = (1-stressed_lgd)/(1-base_lgd) if base_lgd < 1 else 0.
            result = credit_impaired_shortfall(float(row.gross_carrying_amount),
                np.asarray(row.recovery_cashflows, float) * factor, row.recovery_times, tasa_descuento)
            out.at[index, "ecl"] = result["ecl"]
            out.at[index, "pv_expected_recoveries"] = result["pv_expected_recoveries"]
            out.at[index, "recovery_surplus"] = result["recovery_surplus"]
            out.at[index, "ecl_basis"] = "funded_recovery_cashflows"
    # Future-default bucket diagnostics do not apply to already impaired assets.
    out.loc[impaired, ["ecl_12m", "ecl_lifetime"]] = np.nan
    if (not np.isfinite(out.ecl).all()
            or not np.isfinite(out.loc[~impaired, ["ecl_12m", "ecl_lifetime"]].to_numpy()).all()):
        raise ArithmeticError("Nonfinite ECL result")
    out["escenario"] = escenario
    return out


def ponderar_escenarios(cartera: pd.DataFrame, pesos: dict[str, float]) -> pd.DataFrame:
    if (not isinstance(pesos, dict) or not pesos
            or any(not np.isfinite(peso) or peso < 0 for peso in pesos.values())
            or not np.isclose(sum(pesos.values()), 1., rtol=0, atol=1e-12)):
        raise ValueError("Scenario weights must be finite, nonnegative and sum to one within 1e-12")
    pieces = [ecl_componentes(cartera, name)[["loan_id", "ecl"]].rename(columns={"ecl": name}) for name in pesos]
    result = pieces[0]
    for piece in pieces[1:]:
        result = result.merge(piece, on="loan_id", validate="one_to_one", sort=False)
    with np.errstate(over="raise", invalid="raise"):
        result["ecl_ponderada"] = sum(result[name] * weight for name, weight in pesos.items())
    if not np.isfinite(result.ecl_ponderada).all():
        raise ArithmeticError("Nonfinite weighted ECL")
    return result


def backtest_pd(pd_estimado: pd.Series, default_observado: pd.Series, grupos: int = 10) -> pd.DataFrame:
    """Synthetic/observed calibration input validation; no independent approval."""
    probabilities = _finite(pd_estimado, "pd_estimado")
    observed = _finite(default_observado, "default_observado")
    _count(grupos, "grupos", len(probabilities))
    if (probabilities.shape != observed.shape or (probabilities < 0).any()
            or (probabilities > 1).any() or not np.isin(observed, [0, 1]).all()):
        raise ValueError("Matching probabilities [0,1] and binary default outcomes required")
    if isinstance(pd_estimado, pd.Series) and isinstance(default_observado, pd.Series) and not pd_estimado.index.equals(default_observado.index):
        raise ValueError("Calibration inputs must have identical index")
    frame = pd.DataFrame({"pd": probabilities, "default": observed})
    frame["banda"] = pd.qcut(frame.pd.rank(method="first"), grupos, labels=False)
    summary = frame.groupby("banda", observed=True).agg(cuentas=("default", "size"), pd_media=("pd", "mean"), default_observado=("default", "mean"))
    summary["error_calibracion"] = summary.default_observado - summary.pd_media
    return summary

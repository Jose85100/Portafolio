import hashlib

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.baseline import SOURCE
from src.migration import current, reconciliation


def test_frozen_source_integrity() -> None:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == (
        "c0d747d609e642d3788426d0f20484ad19daa8fccb192238f96b917cf0d643f3"
    )


def test_mixed_portfolio_reconciles_by_identifier() -> None:
    p = current.cartera_sintetica(300, 20261019)
    p["pd_12m"] = 0.05
    p["pd_origen"] = 0.04
    p["lgd_base"] = 0.4
    p["dpd"] = np.tile([0, 35, 95], 100)
    p.index = np.arange(300)[::-1]
    r = reconciliation(p)
    assert r.loan_id.tolist() == p.loan_id.tolist()
    assert r.stage.value_counts().to_dict() == {1: 100, 2: 100, 3: 100}
    assert np.max(np.abs(r.loc[r.stage.ne(3), "relative_difference"])) < 1e-12
    assert r.loc[r.stage.eq(3), "ecl_basis"].eq("funded_recovery_cashflows").all()


@settings(max_examples=100, derandomize=True)
@given(st.floats(min_value=0.001, max_value=0.9, allow_nan=False, allow_infinity=False))
def test_stage3_independent_of_future_pd(pd12: float) -> None:
    p = current.cartera_sintetica(1, 4)
    p["dpd"] = 95
    p["pd_12m"] = pd12
    p["gross_carrying_amount"] = 100.0
    p["recovery_cashflows"] = [(60.0,)]
    p["recovery_times"] = [(2.0,)]
    out = current.ecl_componentes(p)
    assert out.ecl.iloc[0] == pytest.approx(100 - 60 / 1.1**2)
    assert out[["ecl_12m", "ecl_lifetime"]].isna().all().all()


@pytest.mark.parametrize("rate", [0.0, 0.1, -0.1])
def test_zero_rate_negative_rate_and_surplus(rate: float) -> None:
    r = current.credit_impaired_shortfall(100.0, [120.0], [2.0], rate)
    raw = 100 - 120 / (1 + rate) ** 2
    assert r["raw_shortfall"] == pytest.approx(raw)
    assert r["ecl"] == pytest.approx(max(raw, 0))
    assert r["recovery_surplus"] == pytest.approx(max(-raw, 0))


def test_tiny_rate_reaches_current_engine() -> None:
    assert current.credit_impaired_shortfall(100.0, [100.0], [1.0], 1e-18)["raw_shortfall"] > 0


def test_missing_recovery_is_not_silently_zero() -> None:
    p = current.cartera_sintetica(1, 3)
    p["dpd"] = 95
    with pytest.raises(ValueError):
        current.ecl_componentes(p.drop(columns="recovery_cashflows"))


@pytest.mark.parametrize("field,value", [("pd_12m", 0.96), ("lgd_base", 0.96), ("pd_origen", 1e-8)])
def test_unsupported_equivalence_domain_rejected(field: str, value: float) -> None:
    p = current.cartera_sintetica(1, 3)
    p[field] = value
    with pytest.raises(ValueError):
        reconciliation(p)

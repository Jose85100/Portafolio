import json
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.consumer import decide, encode


def test_nonrepresentable_breach_and_transport() -> None:
    r = decide([0.0, 5e-324], "0", 0.5, [3.0, 1.0])
    assert r["es_float"] == 0 and r["breach"] is True and r["output_rounds_to_zero"]
    p = json.loads(encode(r))
    assert Fraction(int(p["es_rational"]["numerator"]), int(p["es_rational"]["denominator"])) > 0


@pytest.mark.parametrize("kwargs", [{"policy": "raise"}, {"max_exact_scenarios": 1}])
def test_refusal_is_not_safe_zero(kwargs: dict) -> None:
    r = decide([1e308, 0], "0", weights=[1e-300, 1e300], **kwargs)
    assert r["status"] == "rejected" and r["breach"] is None
    assert "es_float" not in r
    assert json.loads(encode(r)) == r


@pytest.mark.parametrize("threshold", ["NaN", "inf", "1/0", "", 0.0])
def test_bad_threshold(threshold: str) -> None:
    with pytest.raises(ValueError):
        decide([1.0], threshold)


def test_invalid_data_not_masked() -> None:
    with pytest.raises(ValueError):
        decide([], "0")


def test_json_nonfinite_refused() -> None:
    with pytest.raises(ValueError):
        encode({"es": float("nan")})


@settings(max_examples=100, derandomize=True)
@given(st.integers(-10000, 10000), st.integers(-10000, 10000))
def test_singleton_threshold_property(loss: int, threshold: int) -> None:
    r = decide([float(loss)], str(threshold))
    assert r["breach"] == (loss > threshold)
    assert json.loads(encode(r)) == r


def test_threshold_equality_and_decimal_not_coerced() -> None:
    assert decide([1.0], "1")["breach"] is False
    # float(0.1) is strictly above decimal 1/10; no hidden decimal equivalence.
    assert decide([0.1], "0.1")["breach"] is True


def test_exact_fallback_equality_negative_and_below_boundary() -> None:
    r = decide([0.0, 5e-324], "0", 0.5, [3.0, 1.0])
    pair = r["es_rational"]
    exact = Fraction(int(pair["numerator"]), int(pair["denominator"]))
    assert decide([0.0, 5e-324], str(exact), 0.5, [3.0, 1.0])["breach"] is False
    assert decide([0.0, 5e-324], str(exact / 2), 0.5, [3.0, 1.0])["breach"] is True
    negative = decide([-5e-324, 0.0], "0", 0.5, [3.0, 1.0])
    assert negative["breach"] is False

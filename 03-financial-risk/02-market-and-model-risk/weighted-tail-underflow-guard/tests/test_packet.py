import json
from copy import deepcopy

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.consumer import decide, encode
from src.packet import MAX_BYTES, PacketError, decode


def test_nonrepresentable_and_rejected_roundtrip() -> None:
    for p in [
        decide([0, 5e-324], "0", 0.5, [3, 1]),
        decide([1e308, 0], "0", weights=[1e-300, 1e300], policy="raise"),
    ]:
        assert decode(encode(p).encode()) == p


@settings(max_examples=100, derandomize=True)
@given(st.integers(-10000, 10000), st.integers(-10000, 10000))
def test_singleton_roundtrip(loss: int, threshold: int) -> None:
    p = decide([float(loss)], str(threshold))
    assert decode(encode(p).encode()) == p


@settings(max_examples=100, derandomize=True)
@given(st.integers(-10000, 10000))
def test_flipped_decision_rejected(loss: int) -> None:
    p = decide([float(loss)], "0")
    p["breach"] = not p["breach"]
    with pytest.raises(PacketError):
        decode(encode(p).encode())


@pytest.mark.parametrize(
    "raw",
    [
        b"[]",
        b"null",
        b"{",
        b"\xff",
        b'{"a":0,"a":1}',
        b"[NaN]",
        b"[Infinity]",
        b"[1e999]",
        b"[" * 1500 + b"]" * 1500,
        b" " * (MAX_BYTES + 1),
        b"[1." + b"0" * 130 + b"]",
    ],
)
def test_malformed_or_unbounded(raw: bytes) -> None:
    with pytest.raises(PacketError):
        decode(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", "unknown"),
        ("comparison", ">="),
        ("status", "other"),
        ("breach", 1.0),
        ("output_rounds_to_zero", None),
        ("es_float", True),
        ("es_float", 2.0),
        ("backend", "other"),
        ("fallback_reason", "fake"),
        ("es_rational", {"numerator": "2", "denominator": "2"}),
        ("es_rational", {"numerator": "01", "denominator": "1"}),
        ("es_rational", {"numerator": "1", "denominator": "-1"}),
        ("es_rational", {"numerator": "1", "denominator": "0"}),
        ("es_rational", {"numerator": "1" * 2049, "denominator": "1"}),
        ("es_rational", {"numerator": "1" * 400, "denominator": "1"}),
        ("es_rational", []),
        ("extra", "field"),
    ],
)
def test_schema_and_semantics(field: str, value: object) -> None:
    p = decide([1.0], "0")
    p[field] = value
    with pytest.raises(PacketError):
        decode(json.dumps(p).encode())


def test_duplicate_valid_key_and_reason_and_flag() -> None:
    p = decide([0, 5e-324], "0", 0.5, [3, 1])
    raw = encode(p)
    with pytest.raises(PacketError):
        decode((raw[:-1] + ',"breach":false}').encode())
    for field, value in [("fallback_reason", ""), ("output_rounds_to_zero", False)]:
        bad = deepcopy(p)
        bad[field] = value
        with pytest.raises(PacketError):
            decode(encode(bad).encode())


def test_rejected_not_safe_zero() -> None:
    p = decide([1e308, 0], "0", weights=[1e-300, 1e300], policy="raise")
    for field, value in [("breach", False), ("reason", ""), ("reason", "x" * 1025), ("es_float", 0.0)]:
        bad = deepcopy(p)
        bad[field] = value
        with pytest.raises(PacketError):
            decode(encode(bad).encode())


def test_consistent_forgery_is_not_authentication() -> None:
    # A schema/consistency validator cannot know that the original loss was 1.
    p = decide([1.0], "0")
    p.update(es_float=0.0, es_rational={"numerator": "0", "denominator": "1"}, breach=False)
    assert decode(encode(p).encode())["breach"] is False

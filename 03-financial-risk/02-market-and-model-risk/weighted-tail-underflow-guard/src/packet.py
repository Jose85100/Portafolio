"""Bounded v1 receipt: internal consistency is NOT authenticity or model truth."""

import json
import math
import re
from fractions import Fraction
from typing import Any, NoReturn

MAX_BYTES = 32768
MAX_DIGITS = 2048
BASE = {"schema", "threshold", "comparison", "status", "breach"}
ACCEPTED = BASE | {
    "comparison_basis",
    "es_float",
    "es_rational",
    "output_rounds_to_zero",
    "backend",
    "fallback_reason",
}
INTEGER = re.compile(r"(?:0|-[1-9][0-9]*|[1-9][0-9]*)\Z", re.ASCII)


class PacketError(ValueError):
    """Receipt refused before downstream decision consumption."""


def forbidden_number(token: str) -> NoReturn:
    raise PacketError("nonfinite constant or JSON integer is outside v1")


def finite_float(token: str) -> float:
    if len(token) > 128:
        raise PacketError("numeric token exceeds limit")
    value = float(token)
    if not math.isfinite(value):
        raise PacketError("nonfinite float")
    return value


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PacketError("duplicate object key")
        result[key] = value
    return result


def rational(value: Any) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise PacketError("rational must have exactly numerator/denominator")
    n, d = value["numerator"], value["denominator"]
    for part in [n, d]:
        if not isinstance(part, str) or len(part) > MAX_DIGITS or INTEGER.fullmatch(part) is None:
            raise PacketError("noncanonical or oversized integer string")
    if d == "0" or d.startswith("-"):
        raise PacketError("denominator must be positive")
    fraction = Fraction(int(n), int(d))
    if str(fraction.numerator) != n or str(fraction.denominator) != d:
        raise PacketError("rational must be reduced")
    return fraction


def reason(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 1024 and value.isascii() and value.isprintable()


def decode(payload: bytes) -> dict[str, Any]:
    """Validate bounded UTF-8 JSON and semantics, returning the original fields.

    No ES recomputation, signatures, freshness or issuer authorization. Rejected
    packets remain rejected with breach=None; they never imply financial safety.
    Integer quantities in v1 are canonical strings; native JSON integers refused.
    """
    if not isinstance(payload, bytes) or len(payload) > MAX_BYTES:
        raise PacketError("expected bytes no larger than 32768")
    try:
        packet = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=forbidden_number,
            parse_int=forbidden_number,
            parse_float=finite_float,
        )
    except (UnicodeError, ValueError, RecursionError) as error:
        raise PacketError(f"invalid packet: {error}") from error
    if not isinstance(packet, dict):
        raise PacketError("packet must be an object")
    if packet.get("schema") != "weighted-es-decision/v1" or packet.get("comparison") != ">":
        raise PacketError("unknown schema or comparison")
    limit = rational(packet.get("threshold"))
    if packet.get("status") == "rejected":
        if set(packet) != BASE | {"reason"} or packet["breach"] is not None or not reason(packet["reason"]):
            raise PacketError("invalid rejected packet")
        return packet
    if packet.get("status") != "accepted" or set(packet) != ACCEPTED:
        raise PacketError("unknown status or accepted fields")
    if type(packet["breach"]) is not bool or type(packet["output_rounds_to_zero"]) is not bool:
        raise PacketError("flags must be boolean, not numeric")
    value = rational(packet["es_rational"])
    es = packet["es_float"]
    if type(es) is not float or not math.isfinite(es):
        raise PacketError("es_float must be finite binary64")
    try:
        rounded = float(value)
    except OverflowError as error:
        raise PacketError("rational ES does not fit finite float") from error
    if not math.isfinite(rounded) or es != rounded:
        raise PacketError("float and rational disagree")
    if packet["breach"] != (value > limit):
        raise PacketError("decision disagrees with rational comparison")
    if packet["output_rounds_to_zero"] != (value != 0 and es == 0):
        raise PacketError("representability flag disagrees")
    basis, backend = packet["comparison_basis"], packet["backend"]
    if basis == "binary64-output" and backend == "float64":
        if value != Fraction(es) or packet["fallback_reason"] is not None:
            raise PacketError("invalid binary64 provenance")
    elif basis == "exact-input-rational" and backend == "fraction":
        if not reason(packet["fallback_reason"]):
            raise PacketError("fallback requires reason")
    else:
        raise PacketError("basis and backend disagree")
    return packet

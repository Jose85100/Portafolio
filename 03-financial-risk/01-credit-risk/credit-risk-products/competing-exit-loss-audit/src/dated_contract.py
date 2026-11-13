"""Explicit ACT day-count and availability contract for deterministic scenarios."""
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Literal

from src.term_structure import TermResult, project_term_structure

Basis = Literal['ACT/365F', 'ACT/360']


def denominator(basis: Basis) -> int:
    if basis == 'ACT/365F':
        return 365
    if basis == 'ACT/360':
        return 360
    raise ValueError('only ACT/365F and ACT/360 supported')


@dataclass(frozen=True)
class SourceStamp:
    role: Literal['ead', 'hazards', 'discount']
    identifier: str
    uri: str
    available_at: datetime


@dataclass(frozen=True)
class DatedInterval:
    start: date
    end: date
    default_hazard: float
    prepay_hazard: float
    ead_start: float
    ead_end: float
    discount_force: float


def convert_rate(rate: float, original: Basis, target: Basis) -> float:
    """Preserve integrated force per actual day when changing time unit."""
    if not math.isfinite(rate) or rate < 0:
        raise ValueError('finite nonnegative force required')
    converted = rate * (denominator(target) / denominator(original))
    if not math.isfinite(converted):
        raise ValueError('converted force exceeds finite float range')
    return converted


def project_dated(
    intervals: Sequence[DatedInterval],
    sources: Sequence[SourceStamp],
    valuation_at: datetime,
    basis: Basis,
    lgd: float = .45,
) -> TermResult:
    """Forecast events may be future, but source availability must be <= valuation.

    Rates are annual forces in EXACTLY the supplied day-count unit. Calendar dates
    carry no timezone; valuation/source timestamps must be timezone-aware. This
    guard verifies declared metadata consistency, not truth, licensing or access.
    Intervals start on valuation date and must be contiguous, strictly positive.
    """
    unit = denominator(basis)
    if valuation_at.tzinfo is None or valuation_at.utcoffset() is None:
        raise ValueError('valuation timestamp must be timezone-aware')
    if len(sources) != 3 or {s.role for s in sources} != {'ead','hazards','discount'}:
        raise ValueError('exactly one source stamp for each ead/hazards/discount role')
    for source in sources:
        if not source.identifier.strip() or not source.uri.strip():
            raise ValueError('nonempty source identifier and URI required')
        if source.available_at.tzinfo is None or source.available_at.utcoffset() is None:
            raise ValueError('source timestamp must be timezone-aware')
        if source.available_at.astimezone(UTC) > valuation_at.astimezone(UTC):
            raise ValueError('source not available at valuation timestamp')
    if not 1 <= len(intervals) <= 360:
        raise ValueError('1..360 intervals required')
    if intervals[0].start != valuation_at.date():
        raise ValueError('first event must start on valuation calendar date')
    for index,item in enumerate(intervals):
        if type(item.start) is not date or type(item.end) is not date:
            raise ValueError('event boundaries must be date, not datetime')
        if item.end <= item.start or (index and intervals[index-1].end != item.start):
            raise ValueError('strictly positive contiguous date intervals required')
    durations=[(i.end-i.start).days/unit for i in intervals]
    return project_term_structure(durations,[i.default_hazard for i in intervals],
        [i.prepay_hazard for i in intervals],[i.ead_start for i in intervals],
        [i.ead_end for i in intervals],[i.discount_force for i in intervals],lgd)

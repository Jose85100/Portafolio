"""Provider-neutral contracts. No commercial calls or learned fraud probabilities."""
from dataclasses import dataclass
from math import isfinite
from hashlib import sha256
import numpy as np


@dataclass(frozen=True)
class Decision:
    labels: tuple[str, ...]
    probabilities: tuple[float, ...]
    model_version: str
    schema_version: str = 'decision-v1'

    def __post_init__(self):
        if (not self.labels or len(set(self.labels)) != len(self.labels)
                or len(self.labels) != len(self.probabilities)
                or any(not isinstance(x, str) or not x.strip() for x in self.labels)
                or not self.model_version or self.schema_version != 'decision-v1'):
            raise ValueError('nonempty unique labels and versioned schema required')
        if any(not isfinite(p) or not 0 <= p <= 1 for p in self.probabilities):
            raise ValueError('finite probabilities in [0,1] required')
        if abs(sum(self.probabilities) - 1) > 1e-10:
            raise ValueError('probabilities must sum to one')


def choose_action(p, loss, efficacy, cost, friction):
    """Expected cost per independent case. No estimated causal efficacy."""
    arrays = [np.asarray(x, float) for x in (loss, efficacy, cost, friction)]
    if (not isfinite(p) or not 0 <= p <= 1 or arrays[0].ndim != 1
            or not arrays[0].size or any(x.shape != arrays[0].shape for x in arrays)
            or any(not np.isfinite(x).all() or (x < 0).any() for x in arrays)
            or (arrays[1] > 1).any()):
        raise ValueError('invalid probability or action menu')
    severity, q, c, f = arrays
    expected = p * severity * (1-q) + c + (1-p)*f
    return int(np.argmin(expected)), expected


def select_threshold(confidence, correct, max_error=.1, min_count=30, delta=.05):
    """Finite-grid one-sided Hoeffding union bound on calibration labels.

    Grid is fixed before labels. IID calibration and bounded error required.
    Chooses maximum coverage among certified thresholds; inf means abstain all.
    """
    c, y = np.asarray(confidence, float), np.asarray(correct)
    if (c.ndim != 1 or y.shape != c.shape or not len(c)
            or not np.isfinite(c).all() or ((c<0)|(c>1)).any()
            or not np.isin(y, [0,1]).all() or not 0<max_error<1
            or not 0<delta<1 or not isinstance(min_count, int) or min_count<1):
        raise ValueError('invalid calibration sample or policy')
    grid = np.linspace(.5, .99, 50)
    accepted = []
    for threshold in grid:
        keep = c >= threshold
        n = int(keep.sum())
        if n >= min_count:
            upper = min(1., float((1-y[keep]).mean()) + np.sqrt(np.log(len(grid)/delta)/(2*n)))
            if upper <= max_error:
                accepted.append((n, float(threshold), float(upper)))
    return max(accepted, default=(0, float('inf'), 1.), key=lambda x:x[0])


@dataclass(frozen=True)
class Evidence:
    document_hash: str
    start: int
    end: int
    value: str

    def verify(self, source):
        """Python Unicode code-point offsets on exact immutable source text."""
        return (type(self.start) is int and type(self.end) is int
                and 0 <= self.start < self.end <= len(source)
                and self.document_hash == sha256(source.encode('utf-8')).hexdigest()
                and source[self.start:self.end] == self.value)


def extract_literal(source, literal):
    """Offline deterministic fixture; ambiguous/missing matches abstain.

    This is a test double, not a ScaleDown extractor or OCR implementation.
    """
    if not literal or source.count(literal) != 1:
        return None
    start = source.index(literal)
    return Evidence(sha256(source.encode('utf-8')).hexdigest(), start, start+len(literal), literal)

"""Conservative upper-tail conformal ranks for a frozen anomaly score."""

from bisect import bisect_left
from collections.abc import Sequence
from math import isfinite


class TailCalibrator:
    """Fit on approved inliers only; no model fitting on calibration scores."""

    def __init__(self, scores: Sequence[float]) -> None:
        if len(scores) == 0 or any(not isfinite(x) for x in scores):
            raise ValueError("nonempty finite calibration scores required")
        self.scores = sorted(scores)

    def p_value(self, score: float) -> float:
        if not isfinite(score):
            raise ValueError("finite score required")
        n = len(self.scores)
        return (1 + n - bisect_left(self.scores, score)) / (n + 1)

    def alert(self, score: float, alpha: float) -> bool:
        if not 0 < alpha < 1:
            raise ValueError("alpha must lie strictly between zero and one")
        return self.p_value(score) <= alpha


class ChannelCalibrator:
    """Predefined channels; reject unseen groups instead of silently pooling."""

    def __init__(self, calibration: dict[str, list[float]]) -> None:
        if not calibration:
            raise ValueError("at least one channel required")
        self.channels = {
            key: TailCalibrator(values) for key, values in calibration.items()
        }

    def p_value(self, channel: str, score: float) -> float:
        return self.channels[channel].p_value(score)

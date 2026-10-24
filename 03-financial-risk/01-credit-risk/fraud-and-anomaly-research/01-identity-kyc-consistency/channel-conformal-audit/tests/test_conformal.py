import math
import unittest
from src.conformal import TailCalibrator, ChannelCalibrator


class TestConformal(unittest.TestCase):
    def test_hand_oracle(self):
        c = TailCalibrator([1.0, 2.0, 2.0, 3.0])
        self.assertEqual(c.p_value(2), 4 / 5)
        self.assertEqual(c.p_value(4), 1 / 5)
        self.assertEqual(c.p_value(0), 1)

    def test_exact_leave_one_out_validity_with_ties(self):
        for scores in ([0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 0.0, 1.0, 1.0, 1.0], [1.0] * 5):
            ps = [
                TailCalibrator(scores[:i] + scores[i + 1 :]).p_value(s)
                for i, s in enumerate(scores)
            ]
            for alpha in (0.01, 0.2, 0.4, 0.6, 0.8):
                self.assertLessEqual(
                    sum(p <= alpha for p in ps) / len(ps), alpha + 1e-12
                )

    def test_monotone_permutation(self):
        self.assertEqual(
            TailCalibrator([3.0, 1.0, 2.0]).p_value(2),
            TailCalibrator([1.0, 2.0, 3.0]).p_value(2),
        )
        p = [TailCalibrator([1.0, 2.0, 2.0, 3.0]).p_value(x) for x in range(6)]
        self.assertEqual(p, sorted(p, reverse=True))

    def test_sparse_channel_cannot_alert(self):
        self.assertFalse(TailCalibrator([0.0] * 9).alert(100, 0.05))

    def test_invalid(self):
        for x in ([], [math.nan], [math.inf]):
            with self.assertRaises(ValueError):
                TailCalibrator(x)
        with self.assertRaises(ValueError):
            TailCalibrator([0.0]).p_value(math.nan)
        for a in (0, 1, -0.1):
            with self.assertRaises(ValueError):
                TailCalibrator([0.0]).alert(1, a)
        with self.assertRaises(ValueError):
            ChannelCalibrator({})
        with self.assertRaises(KeyError):
            ChannelCalibrator({"a": [0.0]}).p_value("b", 1)

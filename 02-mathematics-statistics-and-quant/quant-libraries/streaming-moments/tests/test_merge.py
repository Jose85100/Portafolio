"""Rebase+Chan against independent Decimal SD, not self-only equivalence."""

import json
import math
import random
import unittest
from pathlib import Path
from src.dynamic import DynamicMoments
from tests.test_dynamic import oracle


def summarize(values):
    state = DynamicMoments()
    for value in values:
        state = state.push(value)
    return state


class MergeTests(unittest.TestCase):
    def assert_oracle(self, state, xs, ddof=0):
        expected = oracle(xs, ddof)
        actual = state.result(ddof).std
        self.assertIsNotNone(actual)
        self.assertLessEqual(
            abs(actual - expected), max(4 * math.ulp(expected), 1e-12 * abs(expected))
        )

    def test_empty_identity(self):
        state = summarize([1.0, 2.0, 3.0])
        self.assertEqual(state.merge(DynamicMoments()), state)
        self.assertEqual(DynamicMoments().merge(state), state)
        self.assertEqual(DynamicMoments().merge(DynamicMoments()), DynamicMoments())

    def test_zero_chunk_scale(self):
        tiny = math.ulp(0.0)
        for xs in [[tiny, 2 * tiny], [1e-200, 2e-200], [1e200, 2e200]]:
            self.assert_oracle(
                summarize([0.0] * 4).merge(summarize(xs)), [0.0] * 4 + xs
            )
            self.assert_oracle(
                summarize(xs).merge(summarize([0.0] * 4)), xs + [0.0] * 4
            )
        self.assertEqual(
            summarize([0.0] * 3).merge(summarize([0.0] * 4)).result().std, 0.0
        )

    def test_mixed_scale_loss(self):
        a = summarize([1e-300, 2e-300])
        b = summarize([1e300, 2e300])
        state = a.merge(b)
        self.assertGreater(state.rounded_to_zero, 0)
        self.assert_oracle(state, [1e-300, 2e-300, 1e300, 2e300])
        self.assertEqual(state.state.n, 4)
        self.assert_oracle(b.merge(a), [1e-300, 2e-300, 1e300, 2e300], 1)

    def test_partitions_and_reduction(self):
        rng = random.Random(1101)
        for e in [-1070, -700, 0, 700, 1020]:
            xs = [math.ldexp(rng.uniform(-1, 1), e) for _ in range(128)]
            chunks = [summarize(xs[i : i + 8]) for i in range(0, len(xs), 8)]
            for parts in [chunks, chunks[::-1]]:
                result = DynamicMoments()
                for part in parts:
                    result = result.merge(part)
                for ddof in [0, 1]:
                    self.assert_oracle(result, xs, ddof)
                balanced = parts[:]
                while len(balanced) > 1:
                    balanced = [
                        balanced[i].merge(balanced[i + 1])
                        for i in range(0, len(balanced), 2)
                    ]
                self.assert_oracle(balanced[0], xs)

    def test_fixtures(self):
        fixtures = json.loads(Path("fixtures_merge.json").read_text())
        for row in fixtures["cases"]:
            xs = [float.fromhex(x) for x in row["left"] + row["right"]]
            state = summarize([float.fromhex(x) for x in row["left"]]).merge(
                summarize([float.fromhex(x) for x in row["right"]])
            )
            self.assert_oracle(state, xs)

"""Consumer is built by run.sh before discovery; no silent skip."""

import math
import random
import subprocess
import unittest
from src.cpp_bridge import consume
from src.transport import export_state, import_state, MAX_COUNT
from src.dynamic import DynamicMoments
from src.moments import Moments
from tests.test_merge import summarize
from tests.test_dynamic import oracle


class TransportTests(unittest.TestCase):
    def test_roundtrip_exact(self):
        for xs in [
            [],
            [0.0, 0.0],
            [1.0, 2.0, 3.0],
            [1e-300, 2e300],
            [-math.ulp(0.0), math.ulp(0.0)],
        ]:
            state = summarize(xs)
            decoded = import_state(export_state(state))
            self.assertEqual(decoded.state, state.state)
            self.assertEqual(decoded.exponent, state.exponent)
            self.assertEqual(decoded.initialized, state.initialized)
            self.assertEqual(decoded.rounded_to_zero, 0)

    def test_invalid_both_languages(self):
        cases = [
            "MOMENTS_V2 1 0 0x0p+0 0x0p+0 0x0p+0 0",
            "MOMENTS_V1 -1 0 0x0p+0 0x0p+0 0x0p+0 0",
            "MOMENTS_V1 2 0 0x0p+0 0x0p+0 -0x1p+0 1",
            "MOMENTS_V1 1 1025 0x1p-1 0x0p+0 0x0p+0 1",
            "MOMENTS_V1 2 0 nan 0x0p+0 0x0p+0 1",
            "MOMENTS_V1 2 0 0x1p+2 0x0p+0 0x0p+0 1",
            "MOMENTS_V1 0 0 0x0p+0 0x0p+0 0x0p+0 1",
            "MOMENTS_V1 2 0 0x1p-1 0x0p+0 0x0p+0 0",
        ]
        valid = export_state(summarize([1.0, 2.0]))
        for text in cases:
            with self.assertRaises(ValueError):
                import_state(text)
            result = subprocess.run(
                [".build/moments_consumer", "0"],
                input=text + "\n" + valid + "\n",
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
        with self.assertRaises(ValueError):
            export_state(DynamicMoments(Moments(MAX_COUNT + 1)))
        with self.assertRaises(subprocess.CalledProcessError):
            consume(DynamicMoments(Moments(MAX_COUNT)), summarize([0.0]))

    def test_cross_oracle(self):
        rng = random.Random(1102)
        for exponent in [-1070, -700, 0, 700, 1020]:
            for n in [4, 32]:
                xs = [math.ldexp(rng.uniform(-1, 1), exponent) for _ in range(n)]
                a = summarize(xs[: n // 2])
                b = summarize(xs[n // 2 :])
                for ddof in [0, 1]:
                    cpp, answer = consume(a, b, ddof)
                    py = a.merge(b).result(ddof)
                    expected = oracle(xs, ddof)
                    self.assertEqual(cpp.state.n, n)
                    self.assertEqual(answer["status"], py.status)
                    self.assertLessEqual(
                        abs(answer["std"] - expected),
                        max(4 * math.ulp(expected), 1e-12 * abs(expected)),
                    )
                    self.assertLessEqual(
                        abs(answer["std"] - py.std),
                        max(4 * math.ulp(py.std), 1e-12 * abs(py.std)),
                    )

    def test_boundaries_and_ddof(self):
        for xs in [
            [-math.ulp(0.0), math.ulp(0.0)],
            [0.0, math.ulp(0.0)],
            [-1.79e308, 1.79e308],
            [1e-300, 1e300],
            [0.0, 0.0],
        ]:
            for ddof in [0, 1]:
                _, answer = consume(summarize(xs[:1]), summarize(xs[1:]), ddof)
                expected = summarize(xs[:1]).merge(summarize(xs[1:])).result(ddof)
                self.assertEqual(answer["status"], expected.status)
                self.assertEqual(answer["std"], expected.std)
        with self.assertRaises(subprocess.CalledProcessError):
            consume(summarize([1.0]), DynamicMoments(), 1)

"""Automated tests for the independent oracle and CLI rejection contract."""

import math
import subprocess
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from benchmarks.audit import PROJECT, cases, exact_es


class OracleTests(unittest.TestCase):
    def test_boundary(self) -> None:
        alpha = 0.975
        expected = Fraction(100, 100) / (1 - Fraction(alpha))
        self.assertEqual(exact_es([0.0, 100.0], [99.0, 1.0], alpha), expected)

    def test_zero_weights(self) -> None:
        self.assertEqual(
            exact_es([0.0, 100.0, 1e9], [99.0, 1.0, 0.0], 0.975), exact_es([0.0, 100.0], [99.0, 1.0], 0.975)
        )

    def test_constant_negative(self) -> None:
        self.assertEqual(exact_es([-4.0, -4.0], [1.0, 2.0], 0.9), Fraction(-4))

    def test_tiny_probability_remains_representable(self) -> None:
        es = float(exact_es([1e308, 0.0], [1e-300, 1e300], 0.975))
        self.assertGreater(es, 0)
        self.assertAlmostEqual(es / 4e-291, 1)

    def test_invalid_inputs(self) -> None:
        for losses, weights, alpha in [
            ([], [], 0.9),
            ([1.0], [0.0], 0.9),
            ([1.0], [-1.0], 0.9),
            ([math.inf], [1.0], 0.9),
            ([1.0], [1.0], math.nan),
            ([1.0], [1.0], 1.0),
            ([1.0], [1.0, 2.0], 0.9),
        ]:
            with self.subTest(losses=losses, weights=weights, alpha=alpha), self.assertRaises(ValueError):
                exact_es(losses, weights, alpha)

    def test_determinism(self) -> None:
        config = {
            "seed": 17,
            "fixture_trials": 10,
            "fixture_max_n": 32,
            "levels": [0.5, 0.75, 0.875, 0.975, 0.99],
        }
        self.assertEqual(cases(config), cases(config))

    def test_cli_invalid_numbers(self) -> None:
        binary = PROJECT / "build/release/weighted_tail_cli"
        for n in ["0", "-2", "10junk", "1000001"]:
            result = subprocess.run(
                [str(binary), "--bench", "weighted", n, "1", "17", "--csv"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 2)
            self.assertTrue(result.stderr.strip())

    def test_cli_invalid_fixtures(self) -> None:
        binary = PROJECT / "build/release/weighted_tail_cli"
        for text in [
            "0 0.9 1 nan 1",
            "0 0.9 1 1 -1",
            "0 0.9 2 1 1",
            "0 0.9 1 1junk 1",
            "0 0.9 1 1 1 trailing",
        ]:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "fixture.txt"
                path.write_text(text)
                result = subprocess.run(
                    [str(binary), "--fixtures", str(path)], capture_output=True, text=True, timeout=10
                )
                self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()

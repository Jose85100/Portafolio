"""Unit, edge, fault injection, and randomized invariant tests."""
import random
import json
import tempfile
import unittest
from pathlib import Path

from src.engine import InjectedCrash, initialize, inspect, run_job
from src.experiment import faults, trial, run


class RecoveryTests(unittest.TestCase):
    def test_atomic_resume_after_both_crash_points(self):
        for step in (0, 1):
            with self.subTest(step=step), tempfile.TemporaryDirectory() as d:
                p = Path(d) / "db.sqlite"
                initialize(p, "atomic")
                with self.assertRaises(InjectedCrash):
                    run_job(p, "atomic", "w1", step)
                run_job(p, "atomic", "w1")
                run_job(p, "atomic", "w1")  # replay completed job
                self.assertEqual(inspect(p), {"jobs": 1, "completed": 1,
                    "effect_rows": 2, "unique_effects": 2,
                    "duplicate_effects": 0, "bad_payloads": 0})

    def test_naive_and_split_have_duplicates_after_crash(self):
        for mode, step, expected in (("naive", 0, 1), ("naive", 1, 2),
                                     ("split", 0, 1), ("split", 1, 1)):
            with self.subTest(mode=mode, step=step), tempfile.TemporaryDirectory() as d:
                p = Path(d) / "db.sqlite"
                initialize(p, mode)
                with self.assertRaises(InjectedCrash):
                    run_job(p, mode, "w1", step)
                run_job(p, mode, "w1")
                self.assertEqual(inspect(p)["duplicate_effects"], expected)

    def test_randomized_atomic_invariant(self):
        rng = random.Random(20261014)
        for _ in range(30):
            seed = rng.randrange(100000)
            probability = rng.random()
            result = trial("atomic", seed, 8, probability)
            self.assertEqual(result["duplicate_effects"], 0)
            self.assertEqual(result["missing_effects"], 0)
            self.assertEqual(result["completion_rate"], 1.0)

    def test_edge_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "db.sqlite"
            with self.assertRaises(ValueError):
                initialize(p, "invalid")
            initialize(p, "atomic")
            for job in ("", "x" * 129):
                with self.assertRaises(ValueError):
                    run_job(p, "atomic", job)
            with self.assertRaises(ValueError):
                run_job(p, "atomic", "good", 2)
            self.assertEqual(inspect(p)["jobs"], 0)
            self.assertEqual(faults(123, 10, 0), [None] * 10)
            self.assertTrue(all(x in (0, 1) for x in faults(123, 10, 1)))
            with self.assertRaises(ValueError):
                faults(0, 10, -0.01)
            with self.assertRaises(ValueError):
                trial("atomic", 0, 0, 0.5)

    def test_run_writes_real_artifacts_and_config(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            result = run(out, seeds=(3, 5), jobs=6, probability=1.0)
            self.assertEqual(result["config"]["seeds"], [3, 5])
            self.assertEqual(result["config"]["jobs_per_seed"], 6)
            self.assertEqual(result["config"]["fault_probability"], 1.0)
            self.assertEqual(len((out / "raw.csv").read_text().splitlines()), 7)
            self.assertIn("<svg", (out / "duplicates.svg").read_text())
            self.assertEqual(json.loads((out / "summary.json").read_text())["metrics"]["atomic"]["total_duplicates"], 0)

    def test_paired_fault_schedule(self):
        a = trial("naive", 29, 12, 0.75)
        b = trial("atomic", 29, 12, 0.75)
        self.assertEqual(a["injected_crashes"], b["injected_crashes"])
        self.assertGreater(a["duplicate_effects"], 0)
        self.assertEqual(b["duplicate_effects"], 0)


if __name__ == "__main__":
    unittest.main()

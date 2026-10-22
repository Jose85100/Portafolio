import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestEvidence(unittest.TestCase):
    def test_raw_has_exact_experiment_count(self):
        with (ROOT / 'results/raw.csv').open() as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 480)
        self.assertEqual(len(set((r['regime'], r['seed'], r['policy']) for r in rows)), 480)

    def test_summary_has_paired_seed_count(self):
        result = json.loads((ROOT / 'results/summary.json').read_text())
        self.assertEqual(result['config']['calibration_n'], 800)
        self.assertEqual(result['config']['test_n'], 600)
        self.assertTrue(all(v['seeds'] == 40 for v in result['paired_bootstrap'].values()))

    def test_notebook_outputs_are_visible(self):
        nb = json.loads((ROOT / 'notebook.ipynb').read_text())
        code = [c for c in nb['cells'] if c['cell_type'] == 'code']
        self.assertEqual(len(code), 4)
        self.assertTrue(all(c['outputs'] and c['execution_count'] is not None for c in code))

    def test_figure_and_latency_exist(self):
        self.assertIn('<svg', (ROOT / 'results/risk.svg').read_text())
        with (ROOT / 'results/latency.csv').open() as f:
            self.assertEqual(len(list(csv.DictReader(f))), 48)

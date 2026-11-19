"""Semi-synthetic policy evaluation using observed UCI limits, never observed outcomes."""
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'src'))
from experiment import Row, compare_policies, evaluate, known_mean

SOURCE = HERE.parents[2] / '01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci350/data/default-of-credit-card-clients.xls'
SHA256 = '30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933'


def load_x(path=SOURCE):
    import xlrd
    path = Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError('UCI workbook hash mismatch')
    sheet = xlrd.open_workbook(str(path)).sheet_by_index(0)
    if sheet.nrows != 30002 or sheet.cell_value(1, 1) != 'LIMIT_BAL':
        raise ValueError('Unexpected UCI workbook schema')
    limits = [float(sheet.cell_value(i, 1)) for i in range(2, sheet.nrows)]
    if any(not math.isfinite(x) or x <= 0 for x in limits):
        raise ValueError('Limits must be positive and finite')
    return [min(x / 1_000_000.0, 1.0) for x in limits]


def simulate(xs, seed=42):
    """Fixed empirical X; synthetic assignment and potential rewards, known DGP."""
    rng = random.Random(seed)
    rows = []
    for x in xs:
        if not math.isfinite(x) or not 0 <= x <= 1:
            raise ValueError('x must be in [0,1]')
        p = 0.2 + 0.6 * x
        action = int(rng.random() < p)
        reward = action * (0.8*x - 0.1 + rng.gauss(0, 1))
        rows.append(Row(x, action, reward, p))
    return rows


def run(xs, seed=42):
    rows = simulate(xs, seed)
    policies = {'never': lambda x: 0, 'always': lambda x: 1,
                'threshold_0.125': lambda x: int(x >= .125)}
    return {name: {'conditional_truth': sum(known_mean(x, policy(x)) for x in xs)/len(xs),
                   **evaluate(rows, policy, known_mean)}
            for name, policy in policies.items()}


def main():
    xs = load_x()
    threshold = lambda x: int(x >= .125)
    always = lambda x: 1
    comparison = compare_policies(simulate(xs), threshold, always, known_mean)
    comparison['conditional_truth'] = sum(known_mean(x, threshold(x)) - known_mean(x, 1) for x in xs) / len(xs)
    print(json.dumps({'n': len(xs), 'seed': 42, 'source_sha256': SHA256,
                      'limit_ntd_min': min(xs)*1_000_000,
                      'normalized_x_mean': sum(xs)/len(xs),
                      'policies': run(xs),
                      'threshold_vs_always': comparison}, indent=2))


if __name__ == '__main__':
    main()

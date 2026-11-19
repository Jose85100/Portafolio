"""Empirical Markov-state benchmark on SFC IRL stocks; retrospective, not default."""
from collections import Counter
import csv
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'observed-sfc-irl/results/sfc_irl_by_entity_month.csv'
SHA256 = 'd4b1e8eb6bb1606abd9c5f0fed572d00a19d2cd5a4da94d83eb4b5bb1c801929'
LABELS = ('bajo_150', '150_a_250', '250_o_mas')
ALPHA = 0.5


def state(irl):
    if not math.isfinite(irl) or irl < 0:
        raise ValueError('Invalid IRL')
    return 0 if irl < 150 else 1 if irl < 250 else 2


def month(period):
    d = date.fromisoformat(period)
    return d.year * 12 + d.month - 1


def transitions(rows):
    indexed = {}
    for r in rows:
        entity = r['entity_code'].strip()
        period = r['period']
        key = (entity, month(period))
        irl = float(r['irl_pct_reported'])
        rln = float(r['rln_30d_average_thousand_cop'])
        if not entity or not math.isfinite(rln) or rln <= 0 or key in indexed:
            raise ValueError('Invalid or duplicated entity-month, or nonpositive RLN')
        indexed[key] = (period, state(irl))
    result = []
    for (entity, t), (period, target) in sorted(indexed.items()):
        previous = indexed.get((entity, t - 1))
        if previous is not None:
            result.append({'entity': entity, 'period': period, 'from': previous[1], 'to': target})
    return result


def fit(rows, alpha=ALPHA):
    if not rows or not math.isfinite(alpha) or alpha <= 0:
        raise ValueError('Positive smoothing and nonempty training transitions required')
    cells = [[0] * 3 for _ in range(3)]
    for r in rows:
        i, j = r['from'], r['to']
        if i not in range(3) or j not in range(3):
            raise ValueError('Invalid state')
        cells[i][j] += 1
    total = len(rows)
    unconditional = [(sum(row[j] for row in cells) + alpha) / (total + 3 * alpha) for j in range(3)]
    matrix = [[(count + alpha) / (sum(row) + 3 * alpha) for count in row] for row in cells]
    # Estimate pooled switching risk on training; split switches equally across alternatives.
    switch_rate = (sum(cells[i][j] for i in range(3) for j in range(3) if i != j) + alpha) / (total + 2 * alpha)
    persistence = [[1 - switch_rate if i == j else switch_rate / 2 for j in range(3)] for i in range(3)]
    return {'counts': cells, 'transition': matrix, 'unconditional': unconditional,
            'pooled_switch_rate': switch_rate, 'persistence': persistence}


def score(model, row, method):
    probabilities = model['unconditional'] if method == 'unconditional' else model[method][row['from']]
    y = row['to']
    return sum((p - int(j == y)) ** 2 for j, p in enumerate(probabilities)), -math.log(probabilities[y])


def evaluate(model, rows):
    if not rows:
        raise ValueError('Empty evaluation sample')
    output = {}
    for method in ('unconditional', 'transition', 'persistence'):
        values = [score(model, row, method) for row in rows]
        output[method] = {'brier_multiclass': sum(b for b, _ in values) / len(values),
                          'log_loss': sum(l for _, l in values) / len(values)}
    return output


def cluster_interval(model, rows, n=2000, seed=42):
    """Paired resampling by entity, conditional on fixed training estimates."""
    grouped = {}
    for row in rows:
        grouped.setdefault(row['entity'], []).append(row)
    ids = sorted(grouped)
    if len(ids) < 2 or n < 1:
        raise ValueError('At least two clusters and one resample required')
    rng = random.Random(seed)
    differences = []
    for _ in range(n):
        sample = [r for __ in ids for r in grouped[rng.choice(ids)]]
        metric = evaluate(model, sample)
        differences.append(metric['unconditional']['brier_multiclass'] - metric['transition']['brier_multiclass'])
    differences.sort()
    return [differences[int(.025 * (n - 1))], differences[int(.975 * (n - 1))]]


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA256:
        raise ValueError('IRL snapshot hash mismatch')
    with SOURCE.open(encoding='utf-8', newline='') as f:
        pairs = transitions(list(csv.DictReader(f)))
    train = [r for r in pairs if r['period'][:7] <= '2021-12']
    test = [r for r in pairs if '2022-01' <= r['period'][:7] <= '2022-12']
    model = fit(train)
    result = {'source_sha256': SHA256, 'state_labels': LABELS, 'smoothing_alpha': ALPHA,
              'train_target_end': '2021-12', 'test_start': '2022-01', 'test_end': '2022-12',
              'train_transitions': len(train), 'test_transitions': len(test),
              'train_entities': len({r['entity'] for r in train}), 'test_entities': len({r['entity'] for r in test}),
              'training': model, 'test_origin_counts': dict(Counter(LABELS[r['from']] for r in test)),
              'test_destination_counts': dict(Counter(LABELS[r['to']] for r in test)),
              'test': evaluate(model, test),
              'paired_brier_gain_unconditional_minus_transition_cluster_ci95': cluster_interval(model, test)}
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))

if __name__ == '__main__':
    main()

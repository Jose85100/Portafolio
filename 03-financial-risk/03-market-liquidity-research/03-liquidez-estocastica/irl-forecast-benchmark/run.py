"""Retrospective one-step IRL benchmark. No vintage-aware real-time claim."""
import csv
from datetime import date
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'observed-sfc-irl/results/sfc_irl_by_entity_month.csv'
SHA256 = 'd4b1e8eb6bb1606abd9c5f0fed572d00a19d2cd5a4da94d83eb4b5bb1c801929'
START, END = '2022-01', '2022-12'


def index_month(value):
    d = date.fromisoformat(value)
    return d.year * 12 + d.month - 1


def build(rows, start=START, end=END):
    """One row per entity × target month; last and MA3 use previous months only."""
    if start > end:
        raise ValueError('Invalid evaluation range')
    records = {}
    for row in rows:
        entity = row['entity_code'].strip()
        period = row['period']
        month = index_month(period)
        ratio = float(row['irl_pct_reported'])
        rln = float(row['rln_30d_average_thousand_cop'])
        if not entity or not math.isfinite(ratio) or ratio < 0 or not math.isfinite(rln) or rln <= 0:
            raise ValueError('Invalid entity, IRL or RLN')
        key = (entity, month)
        if key in records:
            raise ValueError('Duplicate entity-month')
        records[key] = (period, ratio)
    pairs = []
    eligible_targets = 0
    for (entity, month), (period, actual) in sorted(records.items()):
        if not start <= period[:7] <= end:
            continue
        eligible_targets += 1
        history = [records.get((entity, month - n)) for n in (1, 2, 3)]
        if any(h is None for h in history):
            continue
        carry = history[0][1]
        ma3 = mean(h[1] for h in history)
        pairs.append({'entity_code': entity, 'period': period, 'actual_pct': actual,
                      'carry_pct': carry, 'ma3_pct': ma3,
                      'carry_error_pp': carry - actual, 'ma3_error_pp': ma3 - actual})
    if not pairs:
        raise ValueError('No matched holdout observations')
    return pairs, eligible_targets


def metrics(rows, field):
    err = [r[field] for r in rows]
    return {'n': len(err), 'bias_pp': mean(err), 'mae_pp': mean(map(abs, err)),
            'rmse_pp': math.sqrt(mean(e*e for e in err)), 'median_ae_pp': median(map(abs, err))}


def summarize(rows, eligible):
    groups = sorted({r['period'][:7] for r in rows})
    monthly = []
    for month in groups:
        group = [r for r in rows if r['period'].startswith(month)]
        monthly.append({'month': month, 'carry': metrics(group, 'carry_error_pp'), 'ma3': metrics(group, 'ma3_error_pp')})
    return {'target_start': START, 'target_end': END, 'target_rows': eligible,
            'matched_rows': len(rows), 'excluded_missing_history': eligible-len(rows),
            'entities': len({r['entity_code'] for r in rows}),
            'carry': metrics(rows, 'carry_error_pp'), 'ma3': metrics(rows, 'ma3_error_pp'),
            'monthly': monthly}


def main():
    source_bytes = SOURCE.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != SHA256:
        raise ValueError('IRL source snapshot hash mismatch')
    with SOURCE.open(encoding='utf-8', newline='') as f:
        pairs, eligible = build(csv.DictReader(f))
    summary = summarize(pairs, eligible)
    summary['input_sha256'] = SHA256
    (HERE / 'results.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    with (HERE / 'predictions.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(pairs[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(pairs)
    print(json.dumps({k: v for k, v in summary.items() if k != 'monthly'}, indent=2))

if __name__ == '__main__':
    main()

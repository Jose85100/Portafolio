"""Retrospective baseline on quarterly count-weighted arrears stocks, not PD."""
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'data/processed/delinquency_observed.csv'
SOURCE_HASH = 'c856d4e8ac26b63347d18e722f5467a7f9421dce9b01ab79d3aad4ca5f13ffcf'


def summarize(rows):
    groups = defaultdict(lambda: [0, 0])
    seen = set()
    for r in rows:
        d = date.fromisoformat(r['fecha_corte'])
        phase = r['epoca_cartera']
        key = (d, phase, r['departamento'])
        if key in seen or phase not in ('ESTUDIOS', 'AMORTIZACION') or r['evidencia'] != 'OBSERVADO_AGREGADO':
            raise ValueError('Invalid or duplicated grain/evidence')
        seen.add(key)
        total, late = int(r['creditos_total']), int(r['creditos_mora_mayor_90d'])
        if total <= 0 or not 0 <= late <= total:
            raise ValueError('Invalid counts')
        groups[(d, phase)][0] += total
        groups[(d, phase)][1] += late
    if not groups:
        raise ValueError('No observations')
    return [(d, phase, late / total) for (d, phase), (total, late) in sorted(groups.items())]


def quarter(d):
    if d.month not in (3, 6, 9, 12) or d.day != (30 if d.month in (6, 9) else 31):
        raise ValueError('Expected quarter-end date')
    return d.year * 4 + (d.month // 3)


def evaluate(points, holdout_year=2024, min_history=4):
    by_phase = defaultdict(list)
    for d, phase, value in points:
        if not 0 <= value <= 1:
            raise ValueError('Invalid stock share')
        quarter(d)
        by_phase[phase].append((d, value))
    predictions = []
    for phase, records in sorted(by_phase.items()):
        records.sort()
        if len({d for d, _ in records}) != len(records):
            raise ValueError('Duplicate quarter')
        for i, (d, actual) in enumerate(records):
            history = records[:i]
            if d.year < holdout_year or len(history) < min_history or quarter(d) - quarter(history[-1][0]) != 1:
                continue
            predictions.append({'fecha_corte': d.isoformat(), 'epoca_cartera': phase, 'actual': actual,
                                'previous_quarter': history[-1][1],
                                'expanding_mean': sum(x for _, x in history) / len(history)})
    metrics = {}
    for phase in sorted(by_phase):
        subset = [p for p in predictions if p['epoca_cartera'] == phase]
        if not subset:
            raise ValueError('No comparable holdout observations')
        metrics[phase] = {'n': len(subset), **{f'{model}_mae_pp': 100 * sum(abs(p[model] - p['actual']) for p in subset) / len(subset)
                           for model in ('previous_quarter', 'expanding_mean')}}
    return predictions, metrics


def main():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_HASH:
        raise ValueError('Unexpected source hash')
    with SOURCE.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    points = summarize(rows)
    predictions, metrics = evaluate(points)
    print(json.dumps({'source_sha256': digest, 'source_rows': len(rows), 'dates': len({d for d, _, _ in points}),
                      'first_test_year': 2024, 'metrics': metrics, 'predictions': predictions}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()

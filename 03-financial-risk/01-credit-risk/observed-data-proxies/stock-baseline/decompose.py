"""Exact midpoint decomposition of changes in aggregate arrears stock shares."""
import csv
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from run import SOURCE, SOURCE_HASH, summarize, quarter


def phase_snapshots(rows):
    summarize(rows)  # shared key, evidence and count contract
    grouped = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'late': 0, 'departments': set()}))
    for row in rows:
        d, phase = row['fecha_corte'], row['epoca_cartera']
        g = grouped[d][phase]
        g['total'] += int(row['creditos_total'])
        g['late'] += int(row['creditos_mora_mayor_90d'])
        g['departments'].add(row['departamento'])
    for phases in grouped.values():
        if set(phases) != {'ESTUDIOS', 'AMORTIZACION'}:
            raise ValueError('Both phases are required in each period')
    return grouped


def pair(before, after):
    if set(before) != set(after) or not before:
        raise ValueError('Incompatible phase sets')
    sums = [sum(x[p]['total'] for p in x) for x in (before, after)]
    if any(n <= 0 for n in sums):
        raise ValueError('Nonpositive total')
    contributions = []
    for phase in sorted(before):
        a, b = before[phase], after[phase]
        if any(x['total'] <= 0 or not 0 <= x['late'] <= x['total'] for x in (a, b)):
            raise ValueError('Invalid counts')
        wa, wb = a['total']/sums[0], b['total']/sums[1]
        ra, rb = a['late']/a['total'], b['late']/b['total']
        contributions.append({'phase': phase, 'weight_before': wa, 'weight_after': wb,
                              'arrears_share_before': ra, 'arrears_share_after': rb,
                              'rate_effect_pp': 100*(wa+wb)/2*(rb-ra),
                              'mix_effect_pp': 100*(ra+rb)/2*(wb-wa),
                              'departments_added': sorted(b['departments'] - a['departments']),
                              'departments_removed': sorted(a['departments'] - b['departments'])})
    p0 = sum(g['late'] for g in before.values())/sums[0]
    p1 = sum(g['late'] for g in after.values())/sums[1]
    change = 100*(p1-p0)
    residual = change - sum(x['rate_effect_pp']+x['mix_effect_pp'] for x in contributions)
    if abs(residual) > 1e-9:
        raise ArithmeticError('Decomposition does not reconcile')
    return {'total_share_before': p0, 'total_share_after': p1, 'change_pp': change,
            'rate_effect_pp': sum(x['rate_effect_pp'] for x in contributions),
            'mix_effect_pp': sum(x['mix_effect_pp'] for x in contributions),
            'reconciliation_residual_pp': residual, 'phases': contributions}


def main():
    from datetime import date
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_HASH:
        raise ValueError('Unexpected source hash')
    with SOURCE.open(encoding='utf-8', newline='') as f:
        snapshots = phase_snapshots(list(csv.DictReader(f)))
    dates = sorted(snapshots)
    output = []
    for a, b in zip(dates, dates[1:]):
        if quarter(date.fromisoformat(b))-quarter(date.fromisoformat(a)) != 1:
            continue
        output.append({'start': a, 'end': b, **pair(snapshots[a], snapshots[b])})
    print(json.dumps({'source_sha256': SOURCE_HASH, 'comparisons': output}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()

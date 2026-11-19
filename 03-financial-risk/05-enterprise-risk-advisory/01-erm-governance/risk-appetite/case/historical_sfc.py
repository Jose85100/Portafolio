"""Historical scenario monitoring on fixed SFC snapshots; no real limits implied."""
import calendar
import csv
from datetime import date
import json
from pathlib import Path
import sys

from appetite import evaluate
from observed_sfc import HERE, IRL, ICV, digest

START = (2020, 3)
END = (2022, 12)


def months(start=START, end=END):
    if start > end:
        raise ValueError('start must not exceed end')
    y, m = start
    if not (1 <= m <= 12 and 1 <= end[1] <= 12):
        raise ValueError('invalid month')
    out = []
    while (y, m) <= end:
        out.append(date(y, m, calendar.monthrange(y, m)[1]).isoformat())
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def indexed(rows, filters, periods):
    """Select exact entity and modality; missing observations are never imputed."""
    result = {}
    for row in rows:
        if not all(row.get(k) == v for k, v in filters.items()) or row.get('period') not in periods:
            continue
        period = row['period']
        if period in result:
            raise ValueError(f'duplicate observation in {period}')
        result[period] = row
    return result


def calculate(irl_rows, icv_rows, config, period_list=None):
    periods = months() if period_list is None else list(period_list)
    try:
        parsed = [date.fromisoformat(p) for p in periods]
    except (TypeError, ValueError) as error:
        raise ValueError('periods must be ISO calendar month ends') from error
    if not parsed or periods != months((parsed[0].year, parsed[0].month), (parsed[-1].year, parsed[-1].month)):
        raise ValueError('periods must be contiguous month ends in chronological order')
    irl = indexed(irl_rows, {'entity_code': '1-1'}, set(periods))
    icv = indexed(icv_rows, {'entity_type_code': '1', 'entity_code': '1', 'modality': 'Consumo'}, set(periods))
    # Use the existing metric contracts and thresholds, but evaluate only the base observation.
    base_config = {**config, 'scenarios': ['base']}
    results, consecutive = [], {'mora': 0, 'liquidez': 0}
    for period in periods:
        obs = []
        for data, metric, column in ((icv, 'mora', 'icv_reported_pct'), (irl, 'liquidez', 'irl_pct_reported')):
            if period in data:
                obs.append({'scenario': 'base', 'metric_id': metric, 'value': data[period].get(column), 'unit': '%'})
        classified = {r['metric_id']: r for r in evaluate(base_config, obs)}
        row = {'period': period}
        for metric in ('mora', 'liquidez'):
            item = classified[metric]
            # Only consecutive known breaches count; gaps break the sequence.
            consecutive[metric] = consecutive[metric] + 1 if item['status'] == 'BRECHA' else 0
            row[f'{metric}_value_pct'] = item['value']
            row[f'{metric}_status'] = item['status']
            row[f'{metric}_consecutive_breaches'] = consecutive[metric]
        row['concentracion_status'] = classified['concentracion']['status']
        results.append(row)
    return results


def read_csv(path):
    with Path(path).open(encoding='utf-8', newline='') as source:
        return list(csv.DictReader(source))


def main():
    config = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))
    output = calculate(read_csv(IRL), read_csv(ICV), config)
    print(f'# Fuentes SHA-256 IRL={digest(IRL)} ICV={digest(ICV)}', file=sys.stderr)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(output[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)


if __name__ == '__main__':
    main()

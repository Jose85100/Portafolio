"""Observed ICOCED cost scenarios on a hypothetical cash/debt profile."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
SHARED = HERE.parents[1]
sys.path.insert(0, str(SHARED / 'python/src'))
from risk_models import project_cash_path

SOURCE = LAB / '02-construction-enterprise-risk/06-materials-inflation-and-supply-chain/results/icoced_material_series_bogota.csv'
SHA256 = 'b2e0b7bb52b8b7b588bc7c0bafefc4e54510906694da34a35b3c692de85a4daa'


def scenarios(rows, months=24, cost_share=0.10112):
    if isinstance(months, bool) or not isinstance(months, int) or not math.isfinite(cost_share) or not 0 <= cost_share <= 1:
        raise ValueError('Invalid horizon or cost share')
    selected = [r for r in rows if r['geographic_domain'] == 'Bogotá_Cundinamarca AR'
                and r['cost_group'] == 'Materiales' and r['input'] == 'Concreto común']
    selected.sort(key=lambda r: r['period'])
    if len(selected) != 57 or len({r['period'] for r in selected}) != 57:
        raise ValueError('Unexpected source coverage or duplicate month')
    values = []
    for i, r in enumerate(selected):
        expected = f'{2022 + i // 12:04d}-{1 + i % 12:02d}-01'
        index, weight = float(r['index_dec_2021_100']), float(r['weight_pct_2021_base'])
        if r['period'] != expected or not math.isfinite(index) or index <= 0 or weight != 10.112:
            raise ValueError('Invalid index, weight, or missing period')
        values.append(index)
    if months <= 0 or months > len(values):
        raise ValueError('Invalid horizon')
    output = []
    for i in range(len(values) - months + 1):
        costs = [100 * (1 - cost_share + cost_share * x / values[i]) for x in values[i:i + months]]
        result = project_cash_path([116 - c for c in costs], [15] * months, initial_cash=10)
        output.append({'start': selected[i]['period'], 'end': selected[i + months - 1]['period'],
                       'first_breach_period': result['first_breach_period'],
                       'minimum_funding_cop_millions': result['minimum_funding'],
                       'minimum_dscr': result['minimum_dscr'], 'closing_cash_cop_millions': result['cash_path'][-1]})
    return output


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA256:
        raise ValueError('ICOCED processed source hash mismatch')
    with SOURCE.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    output = scenarios(rows)
    sensitivity = []
    for share in (0.0, 0.10112, 0.2):
        paths = scenarios(rows, cost_share=share)
        sensitivity.append({'assumed_concrete_cost_share': share,
                            'windows_with_shortfall': sum(r['first_breach_period'] is not None for r in paths),
                            'maximum_funding_cop_millions': max(r['minimum_funding_cop_millions'] for r in paths)})
    result = {'source_sha256': SHA256, 'cost_share_sensitivity': sensitivity, 'windows': len(output),
              'windows_with_shortfall': sum(r['first_breach_period'] is not None for r in output),
              'maximum_funding_cop_millions': max(r['minimum_funding_cop_millions'] for r in output),
              'worst_minimum_dscr': min(r['minimum_dscr'] for r in output),
              'windows_detail': output}
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()

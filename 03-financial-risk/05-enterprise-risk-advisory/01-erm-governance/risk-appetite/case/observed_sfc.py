"""Historical SFC indicators with explicitly hypothetical appetite scenarios."""
import copy
import csv
import hashlib
import json
from pathlib import Path

from appetite import evaluate, report

HERE = Path(__file__).resolve().parent
RISK = HERE.parents[3]
IRL = RISK / '03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/results/sfc_irl_by_entity_month.csv'
ICV = RISK / '01-credit-risk/credit-risk-products/observed-sfc-quality-proxy/results/sfc_icv_entity_modality_month.csv'
PERIOD = '2022-12-31'


def select_one(path, conditions):
    with path.open(encoding='utf-8', newline='') as source:
        rows = [row for row in csv.DictReader(source)
                if all(row.get(k) == v for k, v in conditions.items())]
    if len(rows) != 1:
        raise ValueError(f'{path}: expected exactly one matching observation; found {len(rows)}')
    return rows[0]


def build(irl_path=IRL, icv_path=ICV):
    irl = select_one(irl_path, {'period': PERIOD, 'entity_code': '1-1'})
    icv = select_one(icv_path, {'period': PERIOD, 'entity_type_code': '1',
                                'entity_code': '1', 'modality': 'Consumo'})
    liquidity = float(irl['irl_pct_reported'])
    quality = float(icv['icv_reported_pct'])
    config = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))
    config = copy.deepcopy(config)
    for metric in config['metrics']:
        if metric['id'] == 'mora':
            metric['label'] = 'ICV consumo, SFC, entidad 1-1'
        elif metric['id'] == 'liquidez':
            metric['label'] = 'IRL 30 días, SFC, entidad 1-1'
    rows = []
    # Additive percentage-point shocks are scenarios, not observations or forecasts.
    for scenario, quality_shock, irl_shock in [('base', 0, 0), ('adverso', 1.5, -20), ('severo', 3, -50)]:
        rows.extend([{'scenario': scenario, 'metric_id': 'mora', 'value': quality + quality_shock, 'unit': '%'},
                     {'scenario': scenario, 'metric_id': 'liquidez', 'value': liquidity + irl_shock, 'unit': '%'}])
    return evaluate(config, rows)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = build()
    result = report(rows).replace('ejercicio sintético', 'base observada histórica y escenarios hipotéticos')
    result = result.replace('Umbrales, datos y acciones son ilustrativos; no son límites aprobados.',
                            'Base: SFC, entidad 1-1, diciembre de 2022. Choques, umbrales y acciones son ilustrativos; no son límites aprobados ni datos actuales.')
    print(result, end='')
    print(f'Fuentes locales SHA-256: IRL `{digest(IRL)}`; ICV `{digest(ICV)}`.')
    print('Los choques adverso y severo son supuestos en puntos porcentuales. Concentración queda SIN DATO; no inferir exposición individual.\n')


if __name__ == '__main__':
    main()

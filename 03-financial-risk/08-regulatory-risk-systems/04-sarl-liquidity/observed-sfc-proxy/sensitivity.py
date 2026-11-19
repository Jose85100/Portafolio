"""Deterministic sensitivity of the SFC-scaled hypothetical cash ladder."""
from decimal import Decimal
import hashlib
import json

from run import load_snapshot, scenario, verify_snapshot, SOURCE, PDF, SNAPSHOT_DATE, ENTITY_TYPE


FRACTIONS = (Decimal('0.40'), Decimal('0.60'), Decimal('0.80'))
MULTIPLIERS = (Decimal('1.00'), Decimal('1.50'), Decimal('2.00'))


def sensitivity(alm, rln, fractions=FRACTIONS, multipliers=MULTIPLIERS):
    """Evaluate each explicit pair. Funding is upfront, zero-rate and hypothetical."""
    if not fractions or not multipliers:
        raise ValueError('at least one fraction and multiple are required')
    table = []
    for fraction in fractions:
        for multiplier in multipliers:
            ladder = scenario(alm, rln, fraction, multiplier)
            table.append({'usable_alm_fraction': str(fraction),
                          'rln_multiple': str(multiplier),
                          'minimum_initial_funding_cop': ladder['minimum_initial_funding'],
                          'first_shortfall_date': ladder['first_shortfall_date'],
                          'closing_balance_cop': ladder['closing_balance']})
    return table


def main():
    verify_snapshot()
    alm, rln = load_snapshot()
    result = {'source_period': SNAPSHOT_DATE, 'entity_type': ENTITY_TYPE,
              'derived_csv_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'raw_pdf_sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(),
              'units': 'COP', 'scenario_count': len(FRACTIONS) * len(MULTIPLIERS),
              'label': 'Hypothetical deterministic stress; not observed outflows or regulatory liquidity',
              'sensitivity': sensitivity(alm, rln)}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

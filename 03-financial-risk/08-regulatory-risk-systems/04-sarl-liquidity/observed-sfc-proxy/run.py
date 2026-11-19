"""Illustrative cash scenarios scaled to a frozen SFC liquidity snapshot."""
import csv
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FINANCIAL_RISK = HERE.parents[2]
ENGINE = HERE.parents[1] / 'engines'
sys.path.insert(0, str(ENGINE))
from liquidity_ladder import liquidity_ladder, money  # noqa: E402

SOURCE = FINANCIAL_RISK / '03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/results/sfc_irl_bulletin_appendix.csv'
PDF = FINANCIAL_RISK / '03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/data/raw/sfc_resultados_sistema_financiero_2026-08.pdf'
SOURCE_SHA256 = 'eb9282570324306fb3a8509307a95d707df6721d0717439307525473f1615146'
PDF_SHA256 = 'e38b879140f70d523b655af2aa72c12531f802473604d99bddc15fc57f8b985d'
SNAPSHOT_DATE = '2026-08-31'
ENTITY_TYPE = 'Bancos'
AS_OF = date(2026, 11, 1)
SCENARIOS = {'base': (Decimal('0.60'), Decimal('1.00')),
             'adverso': (Decimal('0.60'), Decimal('1.50')),
             'severo': (Decimal('0.60'), Decimal('2.00'))}


def load_snapshot(path=SOURCE):
    with Path(path).open(encoding='utf-8', newline='') as stream:
        rows = [r for r in csv.DictReader(stream) if r.get('period') == SNAPSHOT_DATE and r.get('entity_type') == ENTITY_TYPE]
    if len(rows) != 1:
        raise ValueError('expected exactly one source row for banks and August 2026')
    row = rows[0]
    try:
        alm, rln = (Decimal(row[k]) for k in ('alm_million_cop', 'rln_30d_million_cop'))
    except (KeyError, InvalidOperation) as exc:
        raise ValueError('invalid SFC values') from exc
    if not (alm.is_finite() and rln.is_finite() and alm > 0 and rln > 0):
        raise ValueError('ALM and RLN must be finite and positive')
    return alm, rln


def verify_snapshot(path=SOURCE, pdf=PDF):
    """Require the documented frozen source files, rather than relabeling new data."""
    checks = ((Path(path), SOURCE_SHA256), (Path(pdf), PDF_SHA256))
    for file, expected in checks:
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError(f'source hash mismatch: {file.name}')


def _cents(value):
    return int((value * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def scenario(alm_million, rln_million, asset_fraction, runoff_multiple):
    """Construct fictional 3-bucket obligations; values are COP, rounded to cents."""
    if not all(isinstance(v, Decimal) and v.is_finite() for v in (alm_million, rln_million, asset_fraction, runoff_multiple)):
        raise ValueError('inputs must be finite Decimal values')
    if alm_million <= 0 or rln_million <= 0 or not (0 <= asset_fraction <= 1) or runoff_multiple < 0:
        raise ValueError('invalid assumptions')
    opening = _cents(alm_million * 1_000_000 * asset_fraction)
    total = _cents(rln_million * 1_000_000 * runoff_multiple)
    share, remainder = divmod(total, 3)
    rows = [{'flow_id': f'fictional-outflow-{i}',
             'due_date': (AS_OF + timedelta(days=10*i)).isoformat(), 'currency': 'COP',
             'amount': money(-(share + (1 if i <= remainder else 0)))} for i in range(1, 4)]
    return liquidity_ladder(rows, as_of=AS_OF.isoformat(),
                            through=(AS_OF + timedelta(days=30)).isoformat(),
                            currency='COP', opening=money(opening))


def main():
    verify_snapshot()
    alm, rln = load_snapshot()
    result = {'source': {'period': SNAPSHOT_DATE, 'entity_type': ENTITY_TYPE,
                         'alm_million_cop': str(alm), 'rln_30d_million_cop': str(rln),
                         'ratio_alm_rln_pct': str((100 * alm / rln).quantize(Decimal('.0001'))),
                         'derived_csv_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                         'raw_pdf_sha256': hashlib.sha256(PDF.read_bytes()).hexdigest()},
              'label': 'Hypothetical scenario; snapshot components are not dated cash flows',
              'results': {name: {'assumed_usable_alm_fraction': str(fraction),
                                 'assumed_rln_multiple': str(multiplier),
                                 'ladder': scenario(alm, rln, fraction, multiplier)}
                          for name, (fraction, multiplier) in SCENARIOS.items()}}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

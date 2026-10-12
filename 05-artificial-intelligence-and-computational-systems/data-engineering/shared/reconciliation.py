"""Exact-decimal balance reconciliations with explicit scope."""
from decimal import Decimal

def reconcile(rows, as_of_date, ledger_total, tolerance="0.01"):
    snapshot = [r for r in rows if r["as_of_date"] == as_of_date]
    if len({r["loan_id"] for r in snapshot}) != len(snapshot):
        raise ValueError("duplicate loan in snapshot")
    observed = sum((Decimal(str(r["principal"])) for r in snapshot), Decimal(0))
    expected = Decimal(str(ledger_total))
    diff = observed - expected
    return {"as_of_date": as_of_date, "loans": len(snapshot),
            "observed": str(observed), "ledger": str(expected),
            "difference": str(diff), "passed": abs(diff) <= Decimal(str(tolerance))}

"""Deterministic cash ladder, with synthetic inputs and no regulatory rules."""
import argparse
import csv
from datetime import date
import json
import re

_MONEY = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]{1,2})?\Z")
_CURRENCY = re.compile(r"[A-Z]{3}\Z")


def parse_money(value):
    """Parse signed amounts to integer cents; reject ambiguous precision/formats."""
    if not isinstance(value, str) or not _MONEY.fullmatch(value):
        raise ValueError("amount must be a decimal string with at most two decimals")
    negative = value.startswith("-")
    whole, _, fractional = value.lstrip("-").partition(".")
    cents = int(whole) * 100 + int((fractional + "00")[:2])
    return -cents if negative else cents


def money(cents):
    sign = "-" if cents < 0 else ""
    return f"{sign}{abs(cents) // 100}.{abs(cents) % 100:02d}"


def parse_date(value):
    if not isinstance(value, str):
        raise ValueError("date must be an ISO YYYY-MM-DD string")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("date must be an ISO YYYY-MM-DD string") from exc
    if parsed.isoformat() != value:
        raise ValueError("date must be an ISO YYYY-MM-DD string")
    return parsed


def liquidity_ladder(rows, *, as_of, through, currency, opening):
    """Aggregate signed flows by due date; include opening and horizon balance.

    Inputs are contractual projected flows, not observed cash or regulatory IRL.
    Exactly one currency and one reporting horizon are accepted per calculation.
    """
    start, end = parse_date(as_of), parse_date(through)
    if end < start:
        raise ValueError("through must not precede as_of")
    if not isinstance(currency, str) or not _CURRENCY.fullmatch(currency):
        raise ValueError("currency must be a three-letter uppercase code")
    opening_cents = parse_money(opening)
    if opening_cents < 0:
        raise ValueError("opening balance must be nonnegative")
    totals, seen = {}, set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"flow_id", "due_date", "currency", "amount"}:
            raise ValueError("each flow must contain exactly flow_id, due_date, currency and amount")
        flow_id = row["flow_id"]
        if not isinstance(flow_id, str) or not flow_id.strip() or flow_id != flow_id.strip():
            raise ValueError("flow_id must be nonempty and have no outer whitespace")
        if flow_id in seen:
            raise ValueError(f"duplicate flow_id: {flow_id}")
        seen.add(flow_id)
        due = parse_date(row["due_date"])
        if not start <= due <= end:
            raise ValueError(f"flow {flow_id} lies outside the reporting horizon")
        if row["currency"] != currency:
            raise ValueError(f"flow {flow_id} has incompatible currency")
        amount = parse_money(row["amount"])
        bucket = totals.setdefault(due, {"inflows": 0, "outflows": 0, "flow_ids": []})
        bucket["inflows" if amount >= 0 else "outflows"] += abs(amount)
        bucket["flow_ids"].append(flow_id)

    # Include both boundaries, even if they contain no flows.
    for boundary in (start, end):
        totals.setdefault(boundary, {"inflows": 0, "outflows": 0, "flow_ids": []})
    balance, table, first_shortfall = opening_cents, [], None
    minimum_closing, minimum_date = None, None
    total_inflows = total_outflows = 0
    for due, bucket in sorted(totals.items()):
        inflows, outflows = bucket["inflows"], bucket["outflows"]
        total_inflows += inflows
        total_outflows += outflows
        balance += inflows - outflows
        if minimum_closing is None or balance < minimum_closing:
            minimum_closing, minimum_date = balance, due.isoformat()
        if balance < 0 and first_shortfall is None:
            first_shortfall = due.isoformat()
        table.append({"date": due.isoformat(), "inflows": money(inflows),
                      "outflows": money(outflows), "net_flow": money(inflows - outflows),
                      "closing_balance": money(balance), "flow_ids": sorted(bucket["flow_ids"])})
    return {"as_of": as_of, "through": through, "currency": currency,
            "opening_balance": money(opening_cents), "flow_count": len(seen),
            "total_inflows": money(total_inflows), "total_outflows": money(total_outflows),
            "closing_balance": money(balance), "first_shortfall_date": first_shortfall,
            "minimum_closing_balance": money(minimum_closing),
            "minimum_closing_date": minimum_date,
            "minimum_initial_funding": money(max(0, -minimum_closing)),
            "buckets": table}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", help="UTF-8 CSV with flow_id,due_date,currency,amount")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--through", required=True)
    parser.add_argument("--currency", required=True)
    parser.add_argument("--opening", required=True, help="nonnegative decimal amount")
    args = parser.parse_args()
    try:
        with open(args.csv_file, encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            required = {"flow_id", "due_date", "currency", "amount"}
            if not fields or len(fields) != len(required) or set(fields) != required:
                raise ValueError("CSV header must contain each required field exactly once")
            result = liquidity_ladder(reader, as_of=args.as_of, through=args.through,
                                      currency=args.currency, opening=args.opening)
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""One-command canonical Drive pull and source audit (read-only)."""
import argparse
import json
from pathlib import Path

from drive_readonly import download
from market_sqlite_profile import inspect as inspect_market
from sfc_product_profile import inspect as inspect_credit


def execute(source, stage_dir, results_dir):
    if source not in ("sfc_credit_product", "market_prices"):
        raise ValueError("No validated inspection contract for source")
    manifest = download(source, stage_dir)
    data_file = manifest["local_path"]
    if source == "sfc_credit_product":
        profile = inspect_credit(data_file)
        if profile["rows"] == 0:
            raise ValueError("Empty source")
    else:
        profile = inspect_market(data_file)
        if profile["prices_rows"] == 0:
            raise ValueError("Empty source")
    status = "AUDITED_BLOCKED" if (
        profile.get("duplicate_business_keys", 0) or profile.get("ohlc_inconsistencies", 0)
    ) else "AUDITED_PENDING_BUSINESS_REVIEW"
    result = {"source": source, "download": manifest, "profile": profile,
              "promotion_status": status, "production_approved": False}
    folder = Path(results_dir)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (source + "_audit.json")).write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", choices=("sfc_credit_product", "market_prices"), required=True)
    p.add_argument("--staging", required=True)
    p.add_argument("--results", required=True)
    args = p.parse_args()
    answer = execute(args.source, args.staging, args.results)
    print(json.dumps({"source":answer["source"],"promotion_status":answer["promotion_status"],
                      "output":str(Path(args.results)/(args.source+"_audit.json"))}, indent=2))

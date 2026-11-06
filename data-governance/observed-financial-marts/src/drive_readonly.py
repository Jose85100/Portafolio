"""Read canonical Google Drive files with an existing OAuth access token.
No tokens are stored or logged; download to private staging only.
Google Drive API read-only scope: https://www.googleapis.com/auth/drive.readonly.
"""
import argparse
import hashlib
import json
import os
import pathlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone

APPROVED = {
 "sfc_credit_product": ("11i_8dCzzIq9L6ktpMi0_NkzGKEsNgk8T", "sfc_distribucion_cartera_producto_riesgo_mora.csv"),
 "market_prices": ("1SHpuLhHA9qfIq-q_-I8Lt-ggupnQ6Acs", "market_data.sqlite"),
 "sfc_national": ("1ufW5qhEN2Vvm5oNDYwmvv9L_NzY4YdWR", "sfc_agregado_nacional_mensual_desde_municipios.csv"),
 "banrep_monthly": ("1Hpu_qk99U_-Hf0H3svT2GvVYWtb9EfpE", "banrep_tasas_mensuales.csv"),
}


def download(source_key, output_dir, token=None):
    if source_key not in APPROVED:
        raise ValueError("Unapproved source")
    bearer = token or os.environ.get("DRIVE_ACCESS_TOKEN")
    if not bearer:
        raise RuntimeError("DRIVE_ACCESS_TOKEN required; no anonymous fallback")
    file_id, file_name = APPROVED[source_key]
    directory = pathlib.Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    destination = directory / file_name
    url = "https://www.googleapis.com/drive/v3/files/" + urllib.parse.quote(file_id) + "?alt=media"
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + bearer})
    staging = directory / (file_name + ".partial")
    digest = hashlib.sha256()
    size = 0
    try:
        with urllib.request.urlopen(request, timeout=120) as response, staging.open("wb") as target:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                target.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        if size == 0:
            raise ValueError("Empty download")
        os.chmod(staging, 0o600)
        staging.replace(destination)
    finally:
        if staging.exists():
            staging.unlink()
    return {"source_key": source_key, "drive_file_id": file_id,
            "local_path": str(destination), "bytes": size,
            "sha256": digest.hexdigest(),
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "DOWNLOADED_UNVALIDATED", "raw_owner": "Master_DATOS"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=sorted(APPROVED), required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = download(args.source, args.out)
    print(json.dumps(result, indent=2))

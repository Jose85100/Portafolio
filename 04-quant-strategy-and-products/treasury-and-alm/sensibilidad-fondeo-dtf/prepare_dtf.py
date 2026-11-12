"""Recrear el derivado DTF desde el CSV canónico del Atlas, sin modificarlo."""
import argparse
import csv
import hashlib
from pathlib import Path

EXPECTED = "56e4e436cd7add0aac50dd8e1c29007fa173ed8e07e4b484633d19faa33c79ec"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="CSV banrep_tasas_mensuales.csv descargado del Atlas")
    parser.add_argument("output", type=Path, help="Ruta de salida del derivado")
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        raise ValueError("La salida debe ser distinta del archivo canónico")
    with args.source.open(newline="", encoding="utf-8-sig") as src, args.output.open("w", newline="", encoding="utf-8") as dst:
        reader = csv.DictReader(src)
        fields = ["mes", "dtf_promedio", "observaciones_dtf"]
        if not set(fields).issubset(reader.fieldnames or []):
            raise ValueError("El origen no contiene las columnas esperadas")
        writer = csv.DictWriter(dst, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            writer.writerow({field: row[field] for field in fields})
    actual = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"SHA-256 del derivado: {actual}")
    if actual != EXPECTED:
        raise ValueError("El derivado difiere del snapshot: revisar versión del origen")

if __name__ == "__main__":
    main()

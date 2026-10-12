import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while chunk := f.read(bloque):
            h.update(chunk)
    return h.hexdigest()


def construir(directorio):
    return {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size,
                     "filas": int(sum(1 for _ in open(p)) - 1)}
            for p in sorted(Path(directorio).glob("*.csv"))}


def verificar(directorio, manifiesto):
    actual = construir(directorio)
    hallazgos = []
    for nombre, meta in manifiesto.items():
        if nombre not in actual:
            hallazgos.append(f"FALTA: {nombre}")
        elif actual[nombre]["sha256"] != meta["sha256"]:
            hallazgos.append(f"ALTERADO: {nombre}")
    hallazgos += [f"NO REGISTRADO: {n}" for n in actual if n not in manifiesto]
    return hallazgos


rng = np.random.default_rng(97)
with tempfile.TemporaryDirectory() as tmp:
    for nombre in ("precios", "tasas", "macro"):
        pd.DataFrame(rng.normal(size=(100, 3)), columns=list("abc")).to_csv(Path(tmp) / f"{nombre}.csv", index=False)
    manifiesto = construir(tmp)
    (Path(tmp) / "manifest.json").write_text(json.dumps(manifiesto, indent=2))
    print("Manifiesto construido:")
    for n, m in manifiesto.items():
        print(f"  {n}: {m['sha256'][:16]}... {m['bytes']} bytes, {m['filas']} filas")
    print("Verificacion inicial:", verificar(tmp, manifiesto) or "sin hallazgos")

    with open(Path(tmp) / "tasas.csv", "a") as f:
        f.write("9,9,9\n")                       # alteracion
    (Path(tmp) / "macro.csv").unlink()            # archivo faltante
    pd.DataFrame({"a": [1]}).to_csv(Path(tmp) / "nuevo.csv", index=False)  # no registrado
    print("Verificacion tras cambios:")
    for h in verificar(tmp, manifiesto):
        print("  ", h)

"""Evolucion de contratos: compatibilidad hacia atras y hacia adelante.

Definiciones (lector L, escritor W; "L lee datos de W" si todo registro valido bajo W es valido bajo L):
  BACKWARD(old, new) = el contrato NUEVO (lector) lee datos escritos bajo el VIEJO.
  FORWARD(old, new)  = el contrato VIEJO (lector) lee datos escritos bajo el NUEVO.
  FULL = ambas.
Reglas (tabla) para que L lea datos de W:
  1. Llave primaria: iguales como conjunto.
  2. Campo de L ausente en W: solo si es anulable o tiene valor por defecto.
  3. Campo en ambos: tipo igual, o ampliacion int -> float; si W es anulable L tambien debe serlo (o tener default);
     rango de L debe CONTENER al de W (L.min <= W.min, L.max >= W.max, ausente = infinito);
     `allowed` de L debe ser None o un superconjunto de W.allowed (W.allowed None con L.allowed no None => incompatible);
     patron de L debe ser None o igual al de W.
  4. Campos de W ausentes en L: se ignoran.
La tabla es SUFICIENTE (correcta): si dice compatible, ningun registro valido de W falla en L. No es necesaria a nivel de muestra finita.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd
from .contracts import Contract, Field, validate

_RANGO_INF = float("inf")


@dataclass
class CompatibilityResult:
    backward: bool
    forward: bool
    breaking_changes: list

    @property
    def full(self) -> bool: return self.backward and self.forward


def _lee(writer: Contract, reader: Contract) -> list:
    """Motivos por los que `reader` NO puede leer datos de `writer` (lista vacia = compatible)."""
    motivos = []
    if set(writer.primary_key) != set(reader.primary_key): motivos.append("llave primaria distinta")
    for fr in reader.fields:
        fw = writer.field(fr.name)
        if fw is None:
            if not (fr.nullable or fr.default is not None): motivos.append(f"campo requerido ausente: {fr.name}")
            continue
        if fw.dtype != fr.dtype and not (fw.dtype == "int" and fr.dtype == "float"): motivos.append(f"tipo incompatible en {fr.name}: {fw.dtype} -> {fr.dtype}")
        if fw.nullable and not (fr.nullable or fr.default is not None): motivos.append(f"{fr.name}: el escritor admite nulos y el lector no")
        lo_r, lo_w = (-_RANGO_INF if fr.min is None else fr.min), (-_RANGO_INF if fw.min is None else fw.min)
        hi_r, hi_w = (_RANGO_INF if fr.max is None else fr.max), (_RANGO_INF if fw.max is None else fw.max)
        if lo_r > lo_w: motivos.append(f"{fr.name}: el lector exige min {fr.min} mayor al del escritor")
        if hi_r < hi_w: motivos.append(f"{fr.name}: el lector exige max {fr.max} menor al del escritor")
        if fr.allowed is not None and (fw.allowed is None or not set(fw.allowed) <= set(fr.allowed)): motivos.append(f"{fr.name}: valores permitidos no cubren al escritor")
        if fr.pattern is not None and fr.pattern != fw.pattern: motivos.append(f"{fr.name}: patron distinto")
    return motivos


def compatibility(old: Contract, new: Contract) -> CompatibilityResult:
    back = _lee(old, new); fwd = _lee(new, old)
    return CompatibilityResult(not back, not fwd, [f"[backward] {m}" for m in back] + [f"[forward] {m}" for m in fwd])


_PATRONES = {r"[A-Z]{2}": lambda rg: "".join(rg.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 2)), r"\d{3}": lambda rg: f"{int(rg.integers(0, 1000)):03d}"}


def sample_rows(contract: Contract, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Genera `n` registros que satisfacen el contrato (valores en los bordes con alta probabilidad para tensar las reglas)."""
    cols = {}
    for f in contract.fields:
        if f.allowed is not None: vals = [rng.choice(list(f.allowed)) for _ in range(n)]
        elif f.pattern in _PATRONES: vals = [_PATRONES[f.pattern](rng) for _ in range(n)]
        elif f.dtype in ("int", "float"):
            lo = -50.0 if f.min is None else f.min; hi = 50.0 if f.max is None else f.max
            borde = rng.random(n) < 0.3; u = rng.uniform(lo, hi, n); u = np.where(borde, np.where(rng.random(n) < 0.5, lo, hi), u); vals = list(np.round(u) if f.dtype == "int" else u)
        elif f.dtype == "bool": vals = list(rng.random(n) < 0.5)
        elif f.dtype == "timestamp": vals = list(pd.Timestamp("2024-01-01", tz="UTC") + pd.to_timedelta(rng.integers(0, 10 ** 6, n), unit="s"))
        else: vals = [f"s{int(rng.integers(0, 50))}" for _ in range(n)]
        if f.nullable:
            nul = rng.random(n) < 0.2; vals = [None if m else v for v, m in zip(vals, nul)]
        cols[f.name] = vals
    return pd.DataFrame(cols)


def reference_check(writer: Contract, reader: Contract, n: int = 400, seed: int = 0) -> bool:
    """Verificacion por fuerza bruta: ¿todos los registros generados bajo `writer` son validos bajo `reader`?
    Campos del escritor que el lector no declara se ignoran; los del lector ausentes se rellenan con su default o nulo."""
    rows = sample_rows(writer, n, np.random.default_rng(seed))
    for f in reader.fields:
        if f.name not in rows.columns: rows[f.name] = f.default if f.default is not None else None
    r = validate(rows[[f.name for f in reader.fields]], replace(reader, primary_key=())); return r.quarantine.empty        # la llave se compara por regla, no por muestra

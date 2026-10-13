"""Contratos de datos: definicion declarativa y validacion vectorizada con cuarentena."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

DTYPES = ("int", "float", "str", "bool", "timestamp")


@dataclass(frozen=True)
class Field:
    name: str
    dtype: str
    nullable: bool = False
    min: float | None = None
    max: float | None = None
    allowed: tuple | None = None
    pattern: str | None = None
    default: object = None

    def __post_init__(self):
        if self.dtype not in DTYPES: raise ValueError(f"dtype invalido: {self.dtype}")


@dataclass(frozen=True)
class Contract:
    name: str
    version: int
    fields: tuple
    primary_key: tuple = ()
    freshness_field: str | None = None
    freshness_max_age: pd.Timedelta | None = None

    def field(self, name: str) -> Field | None:
        return next((f for f in self.fields if f.name == name), None)

    @property
    def names(self) -> list[str]: return [f.name for f in self.fields]


@dataclass
class ValidationReport:
    valid_rows: pd.DataFrame
    quarantine: pd.DataFrame
    violations: list = field(default_factory=list)       # [(regla, filas_afectadas)]
    stale: bool = False

    @property
    def ok(self) -> bool: return self.quarantine.empty and not self.stale and not any(r.startswith("missing_column") for r, _ in self.violations)


def _coerce(s: pd.Series, f: Field):
    """Devuelve (serie_convertida, mascara_de_error_de_tipo). Los nulos no son error de tipo."""
    nn = s.notna()
    if f.dtype == "int":
        n = pd.to_numeric(s, errors="coerce"); bad = nn & (n.isna() | (n != np.floor(n.fillna(0)))); return n.where(~bad).astype("Int64"), bad
    if f.dtype == "float":
        n = pd.to_numeric(s, errors="coerce"); bad = nn & n.isna(); return n.astype(float), bad
    if f.dtype == "bool":
        m = {True: True, False: False, 1: True, 0: False, "true": True, "false": False, "True": True, "False": False}
        c = s.map(lambda v: m.get(v, None) if not (isinstance(v, float) and np.isnan(v)) else None); bad = nn & c.isna(); return c.astype("boolean"), bad
    if f.dtype == "timestamp":
        t = pd.to_datetime(s, errors="coerce", utc=True); bad = nn & t.isna(); return t, bad
    return s.where(~nn, s.astype(str)), pd.Series(False, index=s.index)


def validate(df: pd.DataFrame, contract: Contract, now: pd.Timestamp | None = None) -> ValidationReport:
    """Valida `df` contra el contrato sin modificarlo. Cada fila invalida va a cuarentena con `_reason` (primera regla que falla).
    Llave primaria duplicada: se conserva la primera aparicion y las siguientes se envian a cuarentena."""
    viol: list = []; out = df.copy(); n = len(out); reason = pd.Series("", index=out.index, dtype=object)
    faltan = [f.name for f in contract.fields if f.name not in out.columns]
    if faltan:
        for c in faltan: viol.append((f"missing_column:{c}", n))
        q = df.copy(); q["_reason"] = "missing_column:" + ",".join(faltan); return ValidationReport(df.iloc[0:0].copy(), q, viol)
    def marcar(mask, rule):
        mask = mask & (reason == "")
        if mask.any(): reason[mask] = rule
        total = int(mask.sum())
        if total: viol.append((rule, total))
    for f in contract.fields:
        s, bad = _coerce(out[f.name], f); out[f.name] = s; marcar(bad, f"type:{f.name}")
        nulo = out[f.name].isna() & ~bad
        if not f.nullable and f.default is None: marcar(nulo, f"null:{f.name}")
        elif f.default is not None and nulo.any(): out.loc[nulo, f.name] = f.default
        v = out[f.name]
        if f.min is not None: marcar(v.notna() & (pd.to_numeric(v, errors="coerce") < f.min), f"min:{f.name}")
        if f.max is not None: marcar(v.notna() & (pd.to_numeric(v, errors="coerce") > f.max), f"max:{f.name}")
        if f.allowed is not None: marcar(v.notna() & ~v.isin(list(f.allowed)), f"allowed:{f.name}")
        if f.pattern is not None:
            rx = re.compile(f.pattern); marcar(v.notna() & ~v.astype(str).map(lambda x: bool(rx.fullmatch(x))), f"pattern:{f.name}")
    if contract.primary_key:
        pk = list(contract.primary_key); ok_so_far = reason == ""; dup = out[ok_so_far].duplicated(subset=pk, keep="first"); m = pd.Series(False, index=out.index); m[dup[dup].index] = True; marcar(m, "duplicate_pk")
    stale = False
    if contract.freshness_field and contract.freshness_max_age is not None and now is not None:
        ts = pd.to_datetime(out[contract.freshness_field], errors="coerce", utc=True).max()
        ahora = pd.Timestamp(now); ahora = ahora.tz_localize("UTC") if ahora.tzinfo is None else ahora.tz_convert("UTC")
        stale = bool(pd.isna(ts) or ts < ahora - contract.freshness_max_age)
        if stale: viol.append(("freshness", 1))
    bad_rows = reason != ""; valid = out[~bad_rows].copy(); q = df[bad_rows].copy(); q["_reason"] = reason[bad_rows]
    return ValidationReport(valid, q, viol, stale)

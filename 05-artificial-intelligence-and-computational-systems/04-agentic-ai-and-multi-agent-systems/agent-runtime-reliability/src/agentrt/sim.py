"""Simulacion de un servicio dependiente con capacidad finita y de herramientas con efectos laterales."""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from .policies import RetryPolicy, RetryBudget, CircuitBreaker


def simulate_service(arrivals: np.ndarray, capacity, base_fail: float, policy: RetryPolicy, rng: np.random.Generator,
                     budget: RetryBudget | None = None, breaker: CircuitBreaker | None = None, bin_s: float = 1.0, extra_bins: int = 200, collapse: float = 1.0) -> dict:
    """Simulacion por intervalos de 1 s de N solicitudes con reintentos contra un servicio de capacidad finita.

    arrivals[t]: solicitudes nuevas en el intervalo t. capacity: escalar o arreglo por intervalo (peticiones/intervalo que el
    servicio atiende bien; si el arreglo es mas corto que la simulacion se extiende con su ultimo valor). En cada intervalo la carga ofrecida L = nuevas + reintentos programados; cada peticion tiene
    exito con prob. (1-base_fail)*min(1, capacity/L): sobrecarga => mas fallos. `collapse`=alpha: con alpha=1 el servicio satura (atiende `capacity` bien sin importar la carga);
    con alpha>1 hay COLAPSO por congestion (las exitosas = L*(cap/L)^alpha decrecen con L), base de los fallos metaestables.
    Una solicitud falla definitivamente tras max_attempts, o si el presupuesto/cortacircuitos impide reintentar.
    Devuelve series por intervalo y metricas de goodput, amplificacion y latencia.
    """
    T = len(arrivals); H = T + extra_bins; c0 = np.atleast_1d(np.asarray(capacity, float)); cap = np.r_[c0, np.full(max(H - len(c0), 0), c0[-1])][:H] if len(c0) > 1 else np.full(H, c0[0])      # se extiende con el ultimo valor
    pend: list[list[tuple[float, int]]] = [[] for _ in range(H + 400)]          # (t_inicio, numero_de_intento) por intervalo
    offered = np.zeros(H); served_ok = np.zeros(H); rejected_breaker = 0; n_ok = 0; n_fail = 0; lat = []; attempts_total = 0
    for t in range(H):
        new = int(arrivals[t]) if t < T else 0
        if budget is not None:
            for _ in range(new): budget.on_request()
        items = pend[t] + [(float(t), 1)] * new
        ok_calls = []
        # el cortacircuitos decide por intervalo con el estado vigente
        permitidos = []
        for it in items:
            if breaker is not None and not breaker.allow(float(t)): rejected_breaker += 1; n_fail += 1; lat.append(np.nan); continue
            permitidos.append(it)
        L = len(permitidos); offered[t] = L; attempts_total += L
        p_ok = (1 - base_fail) * min(1.0, cap[t] / L) ** collapse if L else 1.0
        res = rng.random(L) < p_ok
        for (t0, k), ok in zip(permitidos, res):
            if ok: n_ok += 1; served_ok[t] += 1; lat.append(t + 1 - t0)
            else:
                if k >= policy.max_attempts or (budget is not None and not budget.try_retry()): n_fail += 1; lat.append(np.nan)
                else:
                    d = policy.delay(k, rng); tt = int(np.ceil(t + 1 + d / bin_s)); pend[min(tt, len(pend) - 1)].append((t0, k + 1))
        if breaker is not None and L:
            for ok in res[: min(len(res), 20)]: breaker.record(bool(ok), float(t))
    total = int(np.sum(arrivals)); lat_ok = np.array([x for x in lat if not np.isnan(x)])
    return {"offered": offered[:H], "ok": served_ok[:H], "goodput": n_ok / max(total, 1), "failed": n_fail, "attempts": attempts_total, "amplification": attempts_total / max(total, 1),
            "latency_p50": float(np.percentile(lat_ok, 50)) if len(lat_ok) else np.nan, "latency_p99": float(np.percentile(lat_ok, 99)) if len(lat_ok) else np.nan,
            "rejected_by_breaker": rejected_breaker, "total": total}


@dataclass
class Ledger:
    """Libro de efectos laterales: cuantas veces se aplico cada operacion (clave de idempotencia o id propio)."""
    applied: dict = field(default_factory=dict)

    def apply(self, key) -> bool:
        first = key not in self.applied; self.applied[key] = self.applied.get(key, 0) + 1; return first

    def duplicates(self) -> int: return sum(v - 1 for v in self.applied.values() if v > 1)
    def total(self) -> int: return sum(self.applied.values())


class SimTool:
    """Herramienta simulada. Cada llamada: (1) con prob. p_fail_before falla SIN efecto; (2) si no, aplica el efecto en el
    libro (con idempotencia opcional por clave); (3) con prob. p_lost la RESPUESTA se pierde (el cliente ve un timeout aunque
    el efecto ya ocurrio). Devuelve ('ok'|'error'|'timeout', latencia)."""
    def __init__(self, ledger: Ledger, p_fail_before: float = 0.0, p_lost: float = 0.0, idempotent: bool = False, lat_mu: float = -3.0, lat_sigma: float = 0.5):
        self.ledger, self.pf, self.pl, self.idem, self.mu, self.sg = ledger, p_fail_before, p_lost, idempotent, lat_mu, lat_sigma
        self.calls = 0; self.seen_keys: set = set()

    def call(self, op_id, key, rng: np.random.Generator):
        self.calls += 1; lat = float(rng.lognormal(self.mu, self.sg))
        if rng.random() < self.pf: return "error", lat
        if self.idem and key in self.seen_keys: pass                      # el servidor reconoce la clave: no repite el efecto
        else:
            self.ledger.apply(op_id)
            if self.idem: self.seen_keys.add(key)
        if rng.random() < self.pl: return "timeout", lat
        return "ok", lat


def call_with_retries(tool: SimTool, op_id, policy: RetryPolicy, rng: np.random.Generator, use_key: bool) -> dict:
    """Cliente: reintenta ante 'error' y 'timeout'. Con use_key=True envia siempre la misma clave de idempotencia."""
    t = 0.0; prev = None; key = ("k", op_id) if use_key else ("k", op_id, 0)
    for k in range(1, policy.max_attempts + 1):
        if not use_key: key = ("k", op_id, k)                              # clave distinta en cada intento: el servidor no puede deduplicar
        res, lat = tool.call(op_id, key, rng); t += lat
        if res == "ok": return {"ok": True, "attempts": k, "time": t}
        if k < policy.max_attempts:
            prev = policy.delay(k, rng, prev); t += prev
    return {"ok": False, "attempts": policy.max_attempts, "time": t}

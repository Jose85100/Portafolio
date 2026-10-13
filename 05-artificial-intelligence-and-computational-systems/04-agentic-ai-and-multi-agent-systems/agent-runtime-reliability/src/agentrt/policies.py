"""Politicas de resiliencia: reintentos, presupuesto de reintentos, cortacircuitos, guardas de presupuesto y bucles."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import numpy as np


@dataclass(frozen=True)
class RetryPolicy:
    """Reintentos con retroceso exponencial. jitter in {'none','full','equal','decorrelated'}.

    Retardo antes del intento k+1 (k=1,2,...): techo = min(cap, base * 2^(k-1)).
      none: techo; full: U(0, techo); equal: techo/2 + U(0, techo/2); decorrelated: min(cap, U(base, 3*previo)).
    """
    max_attempts: int = 3
    base: float = 0.1
    cap: float = 10.0
    jitter: str = "full"

    def delay(self, k: int, rng: np.random.Generator, prev: float | None = None) -> float:
        techo = min(self.cap, self.base * 2 ** (k - 1))
        if self.jitter == "none": return techo
        if self.jitter == "full": return float(rng.uniform(0, techo))
        if self.jitter == "equal": return techo / 2 + float(rng.uniform(0, techo / 2))
        if self.jitter == "decorrelated":
            p = self.base if prev is None else prev
            return float(min(self.cap, rng.uniform(self.base, max(3 * p, self.base))))
        raise ValueError(self.jitter)


class RetryBudget:
    """Presupuesto de reintentos (cubo de fichas): cada llamada original deposita `ratio` fichas (tope `max_tokens`);
    cada reintento consume una. Acota la amplificacion de carga a ~(1+ratio)x en el largo plazo."""
    def __init__(self, ratio: float = 0.1, max_tokens: float = 10.0, initial: float | None = None):
        self.ratio, self.max_tokens = ratio, max_tokens; self.tokens = max_tokens if initial is None else initial

    def on_request(self) -> None: self.tokens = min(self.max_tokens, self.tokens + self.ratio)

    def try_retry(self) -> bool:
        if self.tokens >= 1.0: self.tokens -= 1.0; return True
        return False


class CircuitBreaker:
    """Cortacircuitos cerrado -> abierto -> semiabierto. Reloj inyectado (`now`) para determinismo.

    Cerrado: cuenta fallos en una ventana deslizante de las ultimas `window` llamadas; abre si fallos >= `threshold`
    (con al menos `min_calls`). Abierto: rechaza durante `cooldown`. Semiabierto: deja pasar hasta `probes` llamadas de
    prueba; si todas tienen exito -> cerrado; si alguna falla -> abierto otra vez.
    """
    CLOSED, OPEN, HALF = "closed", "open", "half_open"

    def __init__(self, threshold: float = 0.5, window: int = 20, min_calls: int = 10, cooldown: float = 5.0, probes: int = 3):
        self.threshold, self.window, self.min_calls, self.cooldown, self.probes = threshold, window, min_calls, cooldown, probes
        self.state = self.CLOSED; self.hist: deque[int] = deque(maxlen=window); self.opened_at = -1e18; self._probe_ok = 0; self._probe_sent = 0
        self.transitions: list[tuple[float, str]] = []

    def _to(self, state: str, now: float) -> None:
        if state != self.state: self.state = state; self.transitions.append((now, state))

    def allow(self, now: float) -> bool:
        if self.state == self.OPEN and now - self.opened_at >= self.cooldown:
            self._to(self.HALF, now); self._probe_ok = 0; self._probe_sent = 0
        if self.state == self.OPEN: return False
        if self.state == self.HALF:
            if self._probe_sent >= self.probes: return False
            self._probe_sent += 1
        return True

    def record(self, ok: bool, now: float) -> None:
        if self.state == self.HALF:
            if not ok: self._to(self.OPEN, now); self.opened_at = now; self.hist.clear(); return
            self._probe_ok += 1
            if self._probe_ok >= self.probes: self._to(self.CLOSED, now); self.hist.clear()
            return
        if self.state == self.OPEN: return
        self.hist.append(0 if ok else 1)
        if len(self.hist) >= self.min_calls and sum(self.hist) / len(self.hist) >= self.threshold:
            self._to(self.OPEN, now); self.opened_at = now


class BudgetExceeded(Exception):
    pass


@dataclass
class BudgetGuard:
    """Limites duros para un agente: pasos, costo acumulado y tokens. Lanza BudgetExceeded al cruzar cualquiera."""
    max_steps: int = 50
    max_cost: float = float("inf")
    max_tokens: int = 10 ** 9
    steps: int = 0; cost: float = 0.0; tokens: int = 0

    def charge(self, cost: float = 0.0, tokens: int = 0) -> None:
        self.steps += 1; self.cost += cost; self.tokens += tokens
        if self.steps > self.max_steps: raise BudgetExceeded(f"pasos > {self.max_steps}")
        if self.cost > self.max_cost: raise BudgetExceeded(f"costo > {self.max_cost}")
        if self.tokens > self.max_tokens: raise BudgetExceeded(f"tokens > {self.max_tokens}")


class LoopDetector:
    """Detecta bucles: la misma (herramienta, argumentos) repetida `max_repeats` veces dentro de las ultimas `window` llamadas."""
    def __init__(self, max_repeats: int = 3, window: int = 12):
        self.max_repeats, self.recent = max_repeats, deque(maxlen=window)

    def observe(self, tool: str, args) -> bool:
        key = (tool, repr(args)); self.recent.append(key); return sum(k == key for k in self.recent) >= self.max_repeats

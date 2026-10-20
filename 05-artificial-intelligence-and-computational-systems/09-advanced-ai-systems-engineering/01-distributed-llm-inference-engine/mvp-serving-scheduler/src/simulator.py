"""Discrete-event *surrogate* of single-device LLM serving (no model inference).

The model separates prompt prefill and autoregressive decode. Its latency law is
an explicit assumption, not a measured GPU calibration. All timestamps are in
simulated milliseconds; a request's declared maximum output length is reserved
in the synthetic KV capacity before admission (no clairvoyant actual length).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math
from typing import Literal

Policy = Literal["serial", "prefill_first", "chunked", "tiny_chunks"]

@dataclass(frozen=True)
class Request:
    request_id: int
    arrival_ms: float
    prompt_tokens: int
    output_tokens: int

    def __post_init__(self) -> None:
        if self.request_id < 0 or not math.isfinite(self.arrival_ms) or self.arrival_ms < 0:
            raise ValueError("invalid request id or arrival")
        if not isinstance(self.prompt_tokens, int) or self.prompt_tokens < 1:
            raise ValueError("prompt_tokens must be positive integer")
        if not isinstance(self.output_tokens, int) or self.output_tokens < 1:
            raise ValueError("output_tokens must be positive integer")

@dataclass(frozen=True)
class Config:
    max_batch: int = 12
    kv_capacity_tokens: int = 4096
    token_budget: int = 256
    chunk_tokens: int = 96
    tiny_chunk_tokens: int = 8
    iteration_overhead_ms: float = 0.9
    prefill_ms_per_token: float = 0.012
    decode_ms_per_request: float = 0.12
    interference_ms: float = 0.02
    ttft_slo_ms: float = 60.0
    tpot_slo_ms: float = 6.0

    def __post_init__(self) -> None:
        if any(v < 1 for v in (self.max_batch, self.kv_capacity_tokens, self.token_budget,
                               self.chunk_tokens, self.tiny_chunk_tokens)):
            raise ValueError("batch, capacity and chunk parameters must be positive")
        for v in (self.iteration_overhead_ms, self.prefill_ms_per_token,
                  self.decode_ms_per_request, self.interference_ms):
            if not math.isfinite(v) or v < 0:
                raise ValueError("latency coefficients must be finite and nonnegative")
        if self.iteration_overhead_ms == 0 and self.prefill_ms_per_token == 0 and self.decode_ms_per_request == 0:
            raise ValueError("at least one positive latency coefficient required")
        if (not math.isfinite(self.ttft_slo_ms) or not math.isfinite(self.tpot_slo_ms)
                or self.ttft_slo_ms <= 0 or self.tpot_slo_ms <= 0):
            raise ValueError("SLOs must be positive")

@dataclass
class _State:
    request: Request
    prefill_remaining: int
    token_times: list[float] = field(default_factory=list)

@dataclass(frozen=True)
class Completion:
    request_id: int
    arrival_ms: float
    first_token_ms: float
    finish_ms: float
    token_times: tuple[float, ...]

    @property
    def ttft_ms(self) -> float:
        return self.first_token_ms - self.arrival_ms

    @property
    def tpots_ms(self) -> tuple[float, ...]:
        return tuple(b - a for a, b in zip(self.token_times, self.token_times[1:]))

@dataclass(frozen=True)
class Run:
    policy: str
    completions: tuple[Completion, ...]
    finish_ms: float
    peak_reserved_tokens: int
    iterations: int
    total_prefill_tokens: int
    total_decode_tokens: int

def simulate(requests: list[Request], policy: Policy, cfg: Config = Config()) -> Run:
    if policy not in ("serial", "prefill_first", "chunked", "tiny_chunks"):
        raise ValueError(f"unknown policy: {policy}")
    ids = [r.request_id for r in requests]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate request IDs")
    for r in requests:
        if r.prompt_tokens + r.output_tokens > cfg.kv_capacity_tokens:
            raise ValueError("request cannot fit declared KV capacity")
    pending = sorted(requests, key=lambda r: (r.arrival_ms, r.request_id))
    active: dict[int, _State] = {}
    done: list[Completion] = []
    t = 0.0
    cursor = 0
    reserved = peak = iters = prefill_count = decode_count = 0
    while len(done) < len(pending):
        limit = 1 if policy == "serial" else cfg.max_batch
        while cursor < len(pending) and len(active) < limit:
            r = pending[cursor]
            if r.arrival_ms > t + 1e-10 or reserved + r.prompt_tokens + r.output_tokens > cfg.kv_capacity_tokens:
                break
            active[r.request_id] = _State(r, r.prompt_tokens)
            reserved += r.prompt_tokens + r.output_tokens
            peak = max(peak, reserved)
            cursor += 1
        if not active:
            if cursor >= len(pending):
                raise AssertionError("unfinished request without active or pending")
            t = max(t, pending[cursor].arrival_ms)
            continue
        ordered = sorted(active.values(), key=lambda s: (s.request.arrival_ms, s.request.request_id))
        prefill: tuple[_State, int] | None = None
        decodes: list[_State] = []
        if policy == "serial":
            s = ordered[0]
            if s.prefill_remaining:
                prefill = (s, s.prefill_remaining)
            else:
                decodes = [s]
        elif policy == "prefill_first":
            unfilled = [s for s in ordered if s.prefill_remaining]
            if unfilled:
                s = unfilled[0]
                prefill = (s, s.prefill_remaining)
            else:
                decodes = [s for s in ordered if len(s.token_times) < s.request.output_tokens]
        else:
            decodes = [s for s in ordered if not s.prefill_remaining and len(s.token_times) < s.request.output_tokens]
            if len(decodes) > cfg.token_budget:
                decodes = decodes[:cfg.token_budget]
            unfilled = [s for s in ordered if s.prefill_remaining]
            available = cfg.token_budget - len(decodes)
            if unfilled and available:
                s = unfilled[0]
                chunk = cfg.tiny_chunk_tokens if policy == "tiny_chunks" else cfg.chunk_tokens
                prefill = (s, min(s.prefill_remaining, available, chunk))
        n_prefill = prefill[1] if prefill else 0
        n_decode = len(decodes)
        if n_prefill == 0 and n_decode == 0:
            raise AssertionError("scheduler made no progress")
        dt = (cfg.iteration_overhead_ms + cfg.prefill_ms_per_token * n_prefill
              + cfg.decode_ms_per_request * n_decode
              + cfg.interference_ms * math.sqrt(n_prefill * n_decode))
        if dt <= 0:
            raise AssertionError("nonpositive iteration time")
        t += dt
        iters += 1
        prefill_count += n_prefill
        decode_count += n_decode
        if prefill:
            s, count = prefill
            s.prefill_remaining -= count
            if s.prefill_remaining == 0:
                s.token_times.append(t)
        for s in decodes:
            s.token_times.append(t)
        for s in list(active.values()):
            if len(s.token_times) == s.request.output_tokens:
                done.append(Completion(s.request.request_id, s.request.arrival_ms,
                                       s.token_times[0], t, tuple(s.token_times)))
                reserved -= s.request.prompt_tokens + s.request.output_tokens
                del active[s.request.request_id]
        if reserved < 0 or reserved > cfg.kv_capacity_tokens:
            raise AssertionError("KV accounting invariant violated")
    assert len(done) == len(requests)
    assert prefill_count == sum(r.prompt_tokens for r in requests)
    assert decode_count == sum(r.output_tokens - 1 for r in requests)
    return Run(policy, tuple(sorted(done, key=lambda c: c.request_id)), t, peak,
               iters, prefill_count, decode_count)

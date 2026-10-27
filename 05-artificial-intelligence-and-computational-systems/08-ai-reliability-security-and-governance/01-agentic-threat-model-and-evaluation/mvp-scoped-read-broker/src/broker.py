"""Read-only tool boundary for a synthetic Unix filesystem evaluation.

No LLM is invoked; untrusted tool arguments never grant authority themselves.
A trusted root directory descriptor defines the granted object namespace.
"""

from __future__ import annotations

import os
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Literal, Self

Mode = Literal["prefix", "resolve_then_open", "anchored_fd"]
Hook = Callable[[], None]


class Denied(ValueError):
    """Fail-closed request or filesystem policy rejection."""


def parse_request(payload: object, cap: int = 4096) -> tuple[str, int]:
    if type(payload) is not dict or set(payload) != {"tool", "path", "max_bytes"}:
        raise Denied("schema")
    if payload["tool"] != "read_text" or not isinstance(payload["path"], str):
        raise Denied("tool_or_path_type")
    path = payload["path"]
    limit = payload["max_bytes"]
    if type(limit) is not int or not 1 <= limit <= cap:
        raise Denied("read_budget")
    if not path or len(path) > 256 or "\x00" in path:
        raise Denied("path_length_or_nul")
    return path, limit


def bounded_text(fd: int, limit: int, reject_hardlinks: bool = False) -> str:
    metadata = os.fstat(fd)
    if not stat.S_ISREG(metadata.st_mode):
        raise Denied("regular_files_only")
    if reject_hardlinks and metadata.st_nlink != 1:
        raise Denied("hardlink_policy")
    chunks = []
    remaining = limit + 1
    while remaining:
        data = os.read(fd, min(4096, remaining))
        if not data:
            break
        chunks.append(data)
        remaining -= len(data)
    result = b"".join(chunks)
    if len(result) > limit:
        raise Denied("file_exceeds_read_budget")
    try:
        return result.decode("utf-8")
    except UnicodeError:
        raise Denied("utf8_only") from None


class ReadBroker:
    def __init__(self, root: Path, mode: Mode = "anchored_fd", cap: int = 4096):
        if mode not in ("prefix", "resolve_then_open", "anchored_fd"):
            raise ValueError("unknown mode")
        if type(cap) is not int or not 1 <= cap <= 65536:
            raise ValueError("invalid trusted cap")
        if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
            raise RuntimeError("Unix dir_fd and O_NOFOLLOW required")
        self.root = root.resolve(strict=True)
        self.mode = mode
        self.cap = cap
        self.root_fd = os.open(
            self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        )

    def close(self) -> None:
        if self.root_fd >= 0:
            os.close(self.root_fd)
            self.root_fd = -1

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def read(self, payload: object, *, fault_hook: Hook | None = None) -> str:
        """fault_hook is trusted test instrumentation, never a request field."""
        if self.root_fd < 0:
            raise Denied("broker_closed")
        path, limit = parse_request(payload, self.cap)
        try:
            if self.mode == "anchored_fd":
                return self._anchored(path, limit, fault_hook)
            candidate = self.root / path
            if self.mode == "prefix":
                if not str(candidate).startswith(str(self.root)):
                    raise Denied("prefix")
            else:
                candidate = candidate.resolve(strict=True)
                if not candidate.is_relative_to(self.root):
                    raise Denied("outside_root")
            if fault_hook is not None:
                fault_hook()
            fd = os.open(candidate, os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC)
            try:
                return bounded_text(fd, limit)
            finally:
                os.close(fd)
        except OSError:
            raise Denied("filesystem_rejected") from None

    def _anchored(self, path: str, limit: int, fault_hook: Hook | None) -> str:
        parts = path.split("/")
        if (
            Path(path).is_absolute()
            or len(parts) > 16
            or any(p in ("", ".", "..") or "\\" in p for p in parts)
        ):
            raise Denied("relative_clean_components_only")
        parent = os.dup(self.root_fd)
        try:
            for part in parts[:-1]:
                nxt = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=parent,
                )
                os.close(parent)
                parent = nxt
            if fault_hook is not None:
                fault_hook()
            leaf = os.open(
                parts[-1],
                os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=parent,
            )
            try:
                return bounded_text(leaf, limit, reject_hardlinks=True)
            finally:
                os.close(leaf)
        finally:
            os.close(parent)

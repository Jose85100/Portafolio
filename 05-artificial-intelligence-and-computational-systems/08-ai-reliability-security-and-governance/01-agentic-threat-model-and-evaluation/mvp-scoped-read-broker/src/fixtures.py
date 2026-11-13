"""All fixtures live under a TemporaryDirectory; no real user data."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

CASES = (
    "safe",
    "nested",
    "internal_alias",
    "traversal",
    "prefix_sibling",
    "symlink_file",
    "symlink_dir",
    "race_parent",
    "race_leaf",
    "hardlink",
    "wrong_tool",
    "overbudget",
)
ESCAPE_CASES = {
    "traversal",
    "prefix_sibling",
    "symlink_file",
    "symlink_dir",
    "race_parent",
    "race_leaf",
    "hardlink",
}
BENIGN_CASES = {"safe", "nested", "internal_alias"}


def setup(
    base: Path, case: str, seed: int
) -> tuple[Path, dict[str, object], Callable[[], None] | None, str, str]:
    if case not in CASES:
        raise ValueError("unknown fixture")
    root = base / f"scope-{seed}"
    outside = base / "outside"
    neighbor = Path(str(root) + "-neighbor")
    for folder in (root, outside, neighbor, root / "nested"):
        folder.mkdir(parents=True, exist_ok=True)
    safe = f"PUBLIC_SYNTHETIC_{seed}"
    canary = f"OUTSIDE_SYNTHETIC_CANARY_{seed}"
    for file in (root / "report.txt", root / "nested/report.txt"):
        file.write_text(safe)
    for file in (
        outside / "canary.txt",
        outside / "report.txt",
        neighbor / "canary.txt",
    ):
        file.write_text(canary)
    payload: dict[str, object] = {
        "tool": "read_text",
        "path": "report.txt",
        "max_bytes": 4096,
    }
    hook = None
    if case == "nested":
        payload["path"] = "nested/report.txt"
    elif case == "internal_alias":
        (root / "internal.txt").symlink_to(root / "report.txt")
        payload["path"] = "internal.txt"
    elif case == "traversal":
        payload["path"] = "../outside/canary.txt"
    elif case == "prefix_sibling":
        payload["path"] = str(neighbor / "canary.txt")
    elif case == "symlink_file":
        (root / "link.txt").symlink_to(outside / "canary.txt")
        payload["path"] = "link.txt"
    elif case == "symlink_dir":
        (root / "alias").symlink_to(outside, target_is_directory=True)
        payload["path"] = "alias/canary.txt"
    elif case == "race_parent":
        payload["path"] = "nested/report.txt"

        def swap_parent() -> None:
            (root / "nested").rename(root / "retired")
            (root / "nested").symlink_to(outside, target_is_directory=True)

        hook = swap_parent
    elif case == "race_leaf":

        def swap_leaf() -> None:
            (root / "report.txt").unlink()
            (root / "report.txt").symlink_to(outside / "report.txt")

        hook = swap_leaf
    elif case == "hardlink":
        os.link(outside / "canary.txt", root / "hard.txt")
        payload["path"] = "hard.txt"
    elif case == "wrong_tool":
        payload["tool"] = "delete"
    elif case == "overbudget":
        payload["max_bytes"] = 5000
    return root, payload, hook, safe, canary

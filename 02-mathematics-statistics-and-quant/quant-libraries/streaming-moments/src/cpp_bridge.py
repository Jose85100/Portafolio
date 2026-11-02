"""Subprocess adapter; IPC cost is not kernel compute cost."""

import json
import subprocess
from pathlib import Path
from typing import Any
from src.dynamic import DynamicMoments
from src.transport import export_state, import_state


def consume(
    left: DynamicMoments,
    right: DynamicMoments,
    ddof: int = 0,
    executable: str = ".build/moments_consumer",
) -> tuple[DynamicMoments, dict[str, Any]]:
    command = str(Path(executable).resolve())
    result = subprocess.run(
        [command, str(ddof)],
        input=export_state(left) + "\n" + export_state(right) + "\n",
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    lines = result.stdout.splitlines()
    if len(lines) != 2:
        raise ValueError("consumer response must have state and JSON lines")
    return import_state(lines[0]), json.loads(lines[1])

import json
import resource
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
start = time.perf_counter()
completed = subprocess.run(
    [str(ROOT / "build/sequential_audit")],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
)
elapsed = time.perf_counter() - start
performance = {
    "wall_seconds": elapsed,
    "max_rss_kb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
}
(ROOT / "results/performance.json").write_text(
    json.dumps(performance, indent=2) + "\n"
)
print(completed.stdout, end="")

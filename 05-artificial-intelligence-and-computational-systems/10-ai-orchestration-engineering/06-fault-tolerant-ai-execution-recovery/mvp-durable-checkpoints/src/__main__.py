"""Run the benchmark via python -m src."""
from pathlib import Path
from .experiment import run
import json

if __name__ == "__main__":
    print(json.dumps(run(Path("results"))["metrics"], indent=2))

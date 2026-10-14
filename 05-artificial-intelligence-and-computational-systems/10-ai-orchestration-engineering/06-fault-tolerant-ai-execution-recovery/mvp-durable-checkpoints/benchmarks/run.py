"""CLI entry point for paired benchmark (run from MVP root)."""
from pathlib import Path
from src.experiment import run

if __name__ == "__main__":
    run(Path("results"))
    print("Generated results/raw.csv, results/summary.json, results/duplicates.svg")

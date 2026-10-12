"""Run all independent AI project test suites using stdlib unittest."""
from pathlib import Path
import subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
TESTS=sorted(p for p in ROOT.glob("0*/**/tests") if (p/"test_model.py").exists())
if not TESTS: raise SystemExit("No project tests found")
for folder in TESTS:
    print(f"Testing {folder.relative_to(ROOT)}",flush=True)
    subprocess.run([sys.executable,"-m","unittest","discover","-s",str(folder),"-p","test_model.py","-v"],check=True)
print(f"Validated {len(TESTS)} project suites")

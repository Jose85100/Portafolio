.PHONY: run
export OPENBLAS_NUM_THREADS := 1
export OMP_NUM_THREADS := 1
run:
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements.txt
	.venv/bin/python -m ruff check src tests scripts_execute_notebook.py scripts_write_report.py
	.venv/bin/python -m mypy src
	.venv/bin/python -m pytest --cov=src.transport --cov=src.reference --cov-report=term-missing --cov-report=json:benchmarks/coverage.json tests > benchmarks/tests.txt
	.venv/bin/python -m src.benchmark > benchmarks/run.txt
	.venv/bin/python scripts_execute_notebook.py
	.venv/bin/python scripts_write_report.py

.PHONY: run
run:
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements.txt
	.venv/bin/python -m ruff check src tests
	.venv/bin/python -m mypy src
	.venv/bin/python -m pytest --cov=src.estimators --cov-report=term-missing --cov-report=json:benchmarks/coverage.json tests > benchmarks/tests.txt
	.venv/bin/python -m src.benchmark > benchmarks/run.txt
	.venv/bin/python scripts_execute_notebook.py

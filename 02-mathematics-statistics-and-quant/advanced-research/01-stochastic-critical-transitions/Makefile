PYTHON ?= python3
VENV := .venv
P := $(VENV)/bin/python
export OPENBLAS_NUM_THREADS := 1
export OMP_NUM_THREADS := 1
export MKL_NUM_THREADS := 1
export MPLBACKEND := Agg

.PHONY: run setup verify experiment notebook audit
run: setup
	$(MAKE) verify experiment notebook audit

setup:
	$(PYTHON) -m venv $(VENV)
	$(P) -m pip install --disable-pip-version-check -r requirements.txt

verify:
	mkdir -p benchmarks
	$(P) -m ruff check src tests scripts_notebook.py scripts_report.py scripts_validate.py
	$(P) -m mypy src
	$(P) -m pytest --cov=src.ou --cov=src.reference --cov-report=term-missing --cov-report=json:benchmarks/coverage.json > benchmarks/tests.txt
	$(P) -c 'print(open("benchmarks/tests.txt").read())'
	$(P) -m unittest discover -s ../../numerical-core/tests -v > benchmarks/numerical-core-tests.txt 2>&1

experiment:
	$(P) -m src.benchmark > benchmarks/run.txt
	$(P) scripts_report.py
	$(P) -m pip freeze > benchmarks/environment.txt

notebook:
	$(P) scripts_notebook.py

audit:
	$(P) scripts_validate.py

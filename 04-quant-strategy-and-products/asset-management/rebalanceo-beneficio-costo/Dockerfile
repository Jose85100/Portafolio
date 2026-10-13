FROM python:3.12-slim
WORKDIR /mvp
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["bash", "-c", "python -m ruff check src tests main.py benchmarks && python -m pytest tests -q --cov=src --cov-branch --cov-report=json:results/coverage.json && python main.py && python benchmarks/execute_notebook.py"]

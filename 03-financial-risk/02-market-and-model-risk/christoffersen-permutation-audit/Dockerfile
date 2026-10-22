FROM python:3.12.14-slim
WORKDIR /audit
COPY requirements.lock.txt ./
RUN python -m pip install --no-cache-dir -r requirements.lock.txt
COPY . .
CMD ["bash", "run.sh"]

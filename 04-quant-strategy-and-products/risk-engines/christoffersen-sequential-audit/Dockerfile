FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends cmake g++ python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
CMD ["bash", "run.sh"]

FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends python3.12 python3.12-venv g++ cmake clang-tidy clang-format gcovr && rm -rf /var/lib/apt/lists/*
WORKDIR /audit
COPY . .
CMD ["bash", "run.sh"]

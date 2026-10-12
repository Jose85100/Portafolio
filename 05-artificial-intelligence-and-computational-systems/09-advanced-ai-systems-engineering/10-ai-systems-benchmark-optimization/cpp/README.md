# C++20 latency measurement kernel

Header-only deterministic summary for strictly positive finite latency measurements in milliseconds. Uses linear-interpolation empirical quantiles and throughput estimate **1/mean duration** (sequential tasks, no concurrency); do not interpret this as service throughput under batching/concurrency.

```bash
c++ -std=c++20 -O2 -Wall -Wextra -Werror -I cpp/include cpp/tests/test_latency.cpp -o /tmp/test_latency
/tmp/test_latency
```

These tests verify algebraic values and invalid inputs, not hardware performance. Extend with repeated timed workloads, clock calibration, warm-up, confidence intervals and concurrent throughput benchmarks.

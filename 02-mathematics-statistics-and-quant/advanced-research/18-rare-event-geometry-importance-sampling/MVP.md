# MVP: disconnected Gaussian tail audit

**State: S2, executable prototype, not S3 or production.**

What: ordinary unbiased IS benchmark for P(|X|>a), with exact truth,
closed-form single-tilt second moment and quadrature for mixture second moments.

Run: `make run` in this directory (Python 3.11+, make, pip/network required).
Produces: raw/summary CSV, results JSON, PNG, automated test evidence and coverage,
and an actually executed notebook. The script exits nonzero on the predeclared gate failure.

Does not cover: high-dimensional regions, adaptive cross-entropy, heavy tails,
parameter uncertainty, portfolio calibration, C++ or cross-language EL parity.
The EL=83 contract is unchanged; this is not a quant-libraries contribution.

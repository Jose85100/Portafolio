"""Synthetic off-policy evaluation with known propensities and known outcome means.

Educational experiment only: neither nuisance functions nor causal assumptions
are identified from real applicants in this module.
"""
from dataclasses import dataclass
import math
import random
import statistics


@dataclass(frozen=True)
class Row:
    x: float
    action: int
    reward: float
    propensity: float  # P(A=1 | X)


def generate(n, seed=42):
    """One applicant per row, with observed reward under the assigned action.

    Reject yields zero; approval yields 0.8*x - 0.1 + standard normal noise.
    x is uniform on [0,1], and the logging policy has overlap [0.2,0.8].
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 2:
        raise ValueError("n must be an integer >= 2")
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        x = rng.random()
        p = 0.2 + 0.6 * x
        action = int(rng.random() < p)
        noise = rng.gauss(0, 1)  # drawn for every unit, including rejected cases
        rows.append(Row(x, action, action * (0.8 * x - 0.1 + noise), p))
    return rows


def _contribution(row, policy, outcome_mean):
    if (row.action not in (0, 1) or not math.isfinite(row.x)
            or not math.isfinite(row.reward) or not math.isfinite(row.propensity)
            or not 0 < row.propensity < 1):
        raise ValueError("invalid observation or missing propensity overlap")
    target = policy(row.x)
    if target not in (0, 1):
        raise ValueError("policy must return 0 or 1")
    mu = float(outcome_mean(row.x, target))
    if not math.isfinite(mu):
        raise ValueError("outcome mean must be finite")
    weight = (1.0 / (row.propensity if target == 1 else 1 - row.propensity)
              if row.action == target else 0.0)
    score = mu + weight * (row.reward - mu)
    if not math.isfinite(weight) or not math.isfinite(score):
        raise ValueError("nonfinite policy contribution")
    return mu, weight, score


def evaluate(rows, policy, outcome_mean):
    """Evaluate a fixed binary policy with DM, IPS and augmented IPS (AIPW).

    outcome_mean(x, action) is supplied externally, as is propensity. On real
    data both must be estimated separately, with proper sample splitting.
    Returned standard error assumes independent identically distributed rows.
    """
    direct, ipw, scores, weights = [], [], [], []
    for row in rows:
        mu, weight, score = _contribution(row, policy, outcome_mean)
        direct.append(mu)
        ipw.append(weight * row.reward)
        scores.append(score)
        weights.append(weight)
    if len(scores) < 2:
        raise ValueError("at least two observations are required")
    weight_sum = sum(weights)
    weight_square_sum = sum(w * w for w in weights)
    return {
        "n": len(scores), "direct": statistics.mean(direct),
        "ips": statistics.mean(ipw), "aipw": statistics.mean(scores),
        "aipw_se": statistics.stdev(scores) / math.sqrt(len(scores)),
        "matched": sum(w > 0 for w in weights),
        "effective_sample_size": weight_sum ** 2 / weight_square_sum if weight_square_sum else 0.0,
        "max_weight": max(weights),
    }


def compare_policies(rows, policy, baseline, outcome_mean):
    """Paired AIPW value difference and its IID standard error.

    The policies and nuisance functions must be fixed independently of these
    rows; this SE does not include nuisance fitting or policy selection error.
    """
    differences = []
    for row in rows:
        _, _, target_score = _contribution(row, policy, outcome_mean)
        _, _, baseline_score = _contribution(row, baseline, outcome_mean)
        differences.append(target_score - baseline_score)
    if len(differences) < 2:
        raise ValueError("at least two observations are required")
    estimate = statistics.mean(differences)
    se = statistics.stdev(differences) / math.sqrt(len(differences))
    return {"n": len(differences), "aipw_difference": estimate,
            "aipw_difference_se": se,
            "normal_95_low": estimate - 1.959963984540054 * se,
            "normal_95_high": estimate + 1.959963984540054 * se}


def known_mean(x, action):
    return action * (0.8 * x - 0.1)


def main():
    rows = generate(20000)
    print("Synthetic experiment; known propensity and outcome means (oracle)")
    print("Policy | analytic population value | DM | IPS | AIPW | SE | ESS | max weight")
    for name, policy, truth in (
        ("approve all", lambda x: 1, 0.3),
        ("approve x >= 0.125", lambda x: int(x >= 0.125), 0.30625),
        ("reject all", lambda x: 0, 0.0),
    ):
        result = evaluate(rows, policy, known_mean)
        print(f"{name} | {truth:.5f} | {result['direct']:.5f} | "
              f"{result['ips']:.5f} | {result['aipw']:.5f} | "
              f"{result['aipw_se']:.5f} | {result['effective_sample_size']:.0f} | "
              f"{result['max_weight']:.2f}")


if __name__ == "__main__":
    main()

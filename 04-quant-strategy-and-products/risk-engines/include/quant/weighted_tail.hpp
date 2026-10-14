#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <stdexcept>
#include <vector>

namespace quant {

struct WeightedScenario {
  double loss;
  double weight;
};

struct WeightedTail {
  double mean;
  double var;
  double es;
  double tail_mass;
  std::size_t positive_scenarios;
};

namespace weighted_detail {
// Neumaier summation; extended precision is platform-dependent.
class Sum {
 public:
  void add(long double value) {
    const long double next = total_ + value;
    correction_ += std::abs(total_) >= std::abs(value) ? (total_ - next) + value : (value - next) + total_;
    total_ = next;
  }
  [[nodiscard]] long double value() const { return total_ + correction_; }

 private:
  long double total_ = 0;
  long double correction_ = 0;
};

struct Atom {
  double loss;
  long double probability;
};
}  // namespace weighted_detail

// Loss-positive convention, inverse-CDF VaR and fractional-boundary ES.
// O(n log n) time, O(n) auxiliary memory. Zero weights do not create atoms.
// This is a known finite-distribution ES, not a population estimator guarantee.
inline WeightedTail weighted_tail(const std::vector<WeightedScenario>& scenarios, double alpha = 0.975) {
  if (scenarios.empty() || !std::isfinite(alpha) || alpha <= 0 || alpha >= 1) {
    throw std::invalid_argument("nonempty scenarios and finite 0 < alpha < 1 required");
  }
  double max_weight = 0;
  long double loss_scale = 1;
  for (const auto& scenario : scenarios) {
    if (!std::isfinite(scenario.loss) || !std::isfinite(scenario.weight) || scenario.weight < 0) {
      throw std::invalid_argument("finite losses and finite nonnegative weights required");
    }
    max_weight = std::max(max_weight, scenario.weight);
    if (scenario.weight > 0) {
      loss_scale = std::max(loss_scale, std::abs(static_cast<long double>(scenario.loss)));
    }
  }
  if (max_weight == 0) {
    throw std::invalid_argument("positive total weight required");
  }

  std::vector<weighted_detail::Atom> atoms;
  atoms.reserve(scenarios.size());
  weighted_detail::Sum normalizer;
  for (const auto& scenario : scenarios) {
    if (scenario.weight == 0) {
      continue;
    }
    const long double probability = static_cast<long double>(scenario.weight) / max_weight;
    if (probability == 0) {
      throw std::range_error("weight ratio underflow on this platform");
    }
    atoms.push_back({scenario.loss, probability});
    normalizer.add(probability);
  }
  const long double total = normalizer.value();
  weighted_detail::Sum mean;
  for (auto& atom : atoms) {
    atom.probability /= total;
    mean.add(atom.probability * (static_cast<long double>(atom.loss) / loss_scale));
  }
  std::sort(atoms.begin(), atoms.end(), [](const auto& left, const auto& right) {
    if (left.loss != right.loss) {
      return left.loss < right.loss;
    }
    return left.probability < right.probability;
  });

  const long double confidence = alpha;
  const long double mass = 1.0L - confidence;
  weighted_detail::Sum cdf;
  double var = atoms.back().loss;
  for (const auto& atom : atoms) {
    cdf.add(atom.probability);
    if (cdf.value() >= confidence) {
      var = atom.loss;
      break;
    }
  }
  long double remaining = mass;
  weighted_detail::Sum tail;
  weighted_detail::Sum used_mass;
  for (auto it = atoms.rbegin(); it != atoms.rend() && remaining > 0; ++it) {
    const long double used = std::min(it->probability, remaining);
    tail.add((used / mass) * (static_cast<long double>(it->loss) / loss_scale));
    used_mass.add(used);
    remaining -= used;
  }
  const double es = static_cast<double>(loss_scale * tail.value());
  const double expected_loss = static_cast<double>(loss_scale * mean.value());
  if (!std::isfinite(es) || !std::isfinite(expected_loss)) {
    throw std::range_error("risk metric overflow");
  }
  return {expected_loss, var, es, static_cast<double>(used_mass.value()), atoms.size()};
}
}  // namespace quant

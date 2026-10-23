#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>

namespace quant::sequential_backtest {

enum class Decision { reject, non_reject, undecided };

struct Result {
  Decision decision{Decision::undecided};
  std::uint64_t draws{};
  std::uint64_t extreme{};
  double estimate{};
  double lower{};
  double upper{1.0};
};

inline const char *name(Decision decision) {
  if (decision == Decision::reject)
    return "reject";
  if (decision == Decision::non_reject)
    return "non_reject";
  return "undecided";
}

template <class BernoulliSampler>
Result decide(BernoulliSampler sample, double alpha = 0.05,
              double error_budget = 0.01, std::uint64_t first_look = 256U,
              std::uint64_t max_draws = 65'536U) {
  if (!(alpha > 0.0 && alpha < 1.0) ||
      !(error_budget > 0.0 && error_budget < 1.0) || first_look == 0U ||
      max_draws < first_look)
    throw std::invalid_argument("invalid sequential configuration");
  Result result;
  std::uint64_t target = first_look;
  std::uint64_t look = 0U;
  while (result.draws < max_draws) {
    target = std::min(target, max_draws);
    while (result.draws < target) {
      result.extreme += sample() ? 1U : 0U;
      ++result.draws;
    }
    ++look;
    result.estimate = static_cast<double>(result.extreme) /
                      static_cast<double>(result.draws);
    const double look_delta =
        error_budget / (static_cast<double>(look) * (look + 1.0));
    const double radius = std::sqrt(
        std::log(2.0 / look_delta) / (2.0 * static_cast<double>(result.draws)));
    result.lower = std::max(0.0, result.estimate - radius);
    result.upper = std::min(1.0, result.estimate + radius);
    if (result.upper < alpha) {
      result.decision = Decision::reject;
      return result;
    }
    if (result.lower > alpha) {
      result.decision = Decision::non_reject;
      return result;
    }
    if (target == max_draws)
      return result;
    target = std::min(max_draws, target * 2U);
  }
  return result;
}

} // namespace quant::sequential_backtest

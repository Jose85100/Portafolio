#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <vector>

namespace quant::exact_backtest {

struct PValue {
  double statistic{};
  double conservative{};
  double mid_p{};
  std::uint64_t states{};
};

inline double xlogy(std::uint64_t count, double probability) {
  if (count == 0U)
    return 0.0;
  if (!(probability > 0.0))
    return -std::numeric_limits<double>::infinity();
  return static_cast<double>(count) * std::log(probability);
}

inline double lr_independence(const std::vector<std::uint8_t> &hits) {
  if (hits.size() < 2U)
    throw std::invalid_argument("at least two hits required");
  std::uint64_t n00 = 0U, n01 = 0U, n10 = 0U, n11 = 0U;
  for (std::size_t i = 1U; i < hits.size(); ++i) {
    if (hits[i - 1U] > 1U || hits[i] > 1U)
      throw std::invalid_argument("hits must be binary");
    if (hits[i - 1U] == 0U && hits[i] == 0U)
      ++n00;
    if (hits[i - 1U] == 0U && hits[i] == 1U)
      ++n01;
    if (hits[i - 1U] == 1U && hits[i] == 0U)
      ++n10;
    if (hits[i - 1U] == 1U && hits[i] == 1U)
      ++n11;
  }
  const auto n0 = n00 + n01;
  const auto n1 = n10 + n11;
  const auto total = n0 + n1;
  const double pooled =
      static_cast<double>(n01 + n11) / static_cast<double>(total);
  const double p01 =
      n0 == 0U ? 0.0 : static_cast<double>(n01) / static_cast<double>(n0);
  const double p11 =
      n1 == 0U ? 0.0 : static_cast<double>(n11) / static_cast<double>(n1);
  const double null_ll =
      xlogy(n00 + n10, 1.0 - pooled) + xlogy(n01 + n11, pooled);
  const double markov_ll = xlogy(n00, 1.0 - p01) + xlogy(n01, p01) +
                           xlogy(n10, 1.0 - p11) + xlogy(n11, p11);
  return std::max(0.0, 2.0 * (markov_ll - null_ll));
}

inline std::uint64_t combinations(std::size_t n, std::size_t k) {
  if (k > n)
    return 0U;
  k = std::min(k, n - k);
  std::uint64_t value = 1U;
  for (std::size_t i = 1U; i <= k; ++i) {
    const auto factor = static_cast<std::uint64_t>(n - k + i);
    if (value > std::numeric_limits<std::uint64_t>::max() / factor)
      throw std::overflow_error("combination count overflow");
    value = value * factor / static_cast<std::uint64_t>(i);
  }
  return value;
}

template <class Visitor>
void enumerate_hits(std::size_t n, std::size_t k, Visitor visitor) {
  if (n < 2U || k > n)
    throw std::invalid_argument("invalid n or k");
  std::vector<std::uint8_t> hits(n, 0U);
  std::vector<std::size_t> positions(k);
  std::iota(positions.begin(), positions.end(), 0U);
  if (k == 0U) {
    visitor(hits);
    return;
  }
  while (true) {
    std::fill(hits.begin(), hits.end(), 0U);
    for (const auto position : positions)
      hits[position] = 1U;
    visitor(hits);
    std::size_t i = k;
    while (i > 0U && positions[i - 1U] == n - k + i - 1U)
      --i;
    if (i == 0U)
      break;
    ++positions[i - 1U];
    for (std::size_t j = i; j < k; ++j)
      positions[j] = positions[j - 1U] + 1U;
  }
}

inline PValue exact_p_value(const std::vector<std::uint8_t> &observed,
                            std::uint64_t state_cap = 5'000'000U) {
  const auto k = static_cast<std::size_t>(
      std::count(observed.begin(), observed.end(), 1U));
  const auto states = combinations(observed.size(), k);
  if (states == 0U || states > state_cap)
    throw std::length_error("exact state budget exceeded");
  const double statistic = lr_independence(observed);
  std::uint64_t greater = 0U, equal = 0U;
  constexpr double tolerance = 1e-12;
  enumerate_hits(observed.size(), k, [&](const auto &hits) {
    const double candidate = lr_independence(hits);
    if (candidate > statistic + tolerance)
      ++greater;
    else if (std::abs(candidate - statistic) <= tolerance)
      ++equal;
  });
  return {statistic,
          static_cast<double>(greater + equal) / static_cast<double>(states),
          (static_cast<double>(greater) + 0.5 * static_cast<double>(equal)) /
              static_cast<double>(states),
          states};
}

inline double monte_carlo_p_value(const std::vector<std::uint8_t> &observed,
                                  std::uint64_t replications,
                                  std::uint64_t seed) {
  if (replications == 0U)
    throw std::invalid_argument("replications must be positive");
  const double statistic = lr_independence(observed);
  auto candidate = observed;
  std::mt19937_64 rng(seed);
  std::uint64_t extreme = 0U;
  for (std::uint64_t i = 0U; i < replications; ++i) {
    std::shuffle(candidate.begin(), candidate.end(), rng);
    if (lr_independence(candidate) >= statistic - 1e-12)
      ++extreme;
  }
  return static_cast<double>(extreme + 1U) /
         static_cast<double>(replications + 1U);
}

} // namespace quant::exact_backtest

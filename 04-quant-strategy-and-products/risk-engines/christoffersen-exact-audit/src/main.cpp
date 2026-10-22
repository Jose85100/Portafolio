#include "exact.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <utility>
#include <vector>

int main() {
  using quant::exact_backtest::exact_p_value;
  using quant::exact_backtest::monte_carlo_p_value;
  constexpr std::size_t n = 30U;
  constexpr std::size_t k = 4U;
  std::vector<std::pair<double, std::vector<std::uint8_t>>> candidates;
  candidates.reserve(
      static_cast<std::size_t>(quant::exact_backtest::combinations(n, k)));
  quant::exact_backtest::enumerate_hits(n, k, [&](const auto &hits) {
    candidates.emplace_back(quant::exact_backtest::lr_independence(hits), hits);
  });
  std::sort(candidates.begin(), candidates.end(),
            [](const auto &left, const auto &right) {
              return left.first > right.first;
            });
  std::vector<std::uint8_t> boundary = candidates.front().second;
  double best_distance = std::numeric_limits<double>::infinity();
  std::size_t group_begin = 0U;
  while (group_begin < candidates.size()) {
    std::size_t group_end = group_begin + 1U;
    while (group_end < candidates.size() &&
           std::abs(candidates[group_end].first -
                    candidates[group_begin].first) <= 1e-12)
      ++group_end;
    const double p_value =
        static_cast<double>(group_end) / static_cast<double>(candidates.size());
    const double distance = std::abs(p_value - 0.05);
    if (distance < best_distance) {
      best_distance = distance;
      boundary = candidates[group_begin].second;
    }
    group_begin = group_end;
  }
  const auto start_exact = std::chrono::steady_clock::now();
  const auto exact = exact_p_value(boundary);
  const auto end_exact = std::chrono::steady_clock::now();
  constexpr std::uint64_t repetitions = 999U;
  constexpr std::uint64_t seeds = 200U;
  std::uint64_t disagreements = 0U;
  double max_error = 0.0;
  const auto start_mc = std::chrono::steady_clock::now();
  for (std::uint64_t seed = 1U; seed <= seeds; ++seed) {
    const double estimate = monte_carlo_p_value(boundary, repetitions, seed);
    max_error = std::max(max_error, std::abs(estimate - exact.conservative));
    if ((estimate < 0.05) != (exact.conservative < 0.05))
      ++disagreements;
  }
  const auto end_mc = std::chrono::steady_clock::now();
  const auto exact_us =
      std::chrono::duration<double, std::micro>(end_exact - start_exact)
          .count();
  const auto mc_us =
      std::chrono::duration<double, std::micro>(end_mc - start_mc).count() /
      static_cast<double>(seeds);
  std::cout << std::setprecision(17)
            << "{\n  \"n\": 30,\n  \"exceptions\": 4,\n  \"states\": "
            << exact.states << ",\n  \"statistic\": " << exact.statistic
            << ",\n  \"exact_p\": " << exact.conservative
            << ",\n  \"mid_p\": " << exact.mid_p
            << ",\n  \"mc_replications\": 999,\n  \"mc_seeds\": 200,\n  "
               "\"decision_disagreements\": "
            << disagreements << ",\n  \"max_abs_mc_error\": " << max_error
            << ",\n  \"exact_microseconds\": " << exact_us
            << ",\n  \"mc_microseconds_per_seed\": " << mc_us << "\n}\n";
}

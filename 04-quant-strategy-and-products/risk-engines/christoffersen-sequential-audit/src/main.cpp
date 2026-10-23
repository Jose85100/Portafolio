#include "exact.hpp"
#include "sequential.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <string>
#include <utility>
#include <vector>

namespace {
using Hits = std::vector<std::uint8_t>;
using Candidate = std::pair<double, Hits>;

struct Scenario {
  std::string name;
  Hits hits;
  double exact_p{};
};

std::vector<Scenario> select_scenarios() {
  constexpr std::size_t n = 30U;
  constexpr std::size_t k = 4U;
  std::vector<Candidate> candidates;
  candidates.reserve(static_cast<std::size_t>(
      quant::exact_backtest::combinations(n, k)));
  quant::exact_backtest::enumerate_hits(n, k, [&](const auto &hits) {
    candidates.emplace_back(quant::exact_backtest::lr_independence(hits), hits);
  });
  std::sort(candidates.begin(), candidates.end(),
            [](const auto &a, const auto &b) { return a.first > b.first; });
  std::array<double, 3> targets{0.001, 0.05, 0.50};
  std::array<std::string, 3> names{"clear_reject", "boundary", "clear_non_reject"};
  std::array<double, 3> distances{std::numeric_limits<double>::infinity(),
                                  std::numeric_limits<double>::infinity(),
                                  std::numeric_limits<double>::infinity()};
  std::vector<Scenario> chosen(3);
  std::size_t begin = 0U;
  while (begin < candidates.size()) {
    std::size_t end = begin + 1U;
    while (end < candidates.size() &&
           std::abs(candidates[end].first - candidates[begin].first) <= 1e-12)
      ++end;
    const double p = static_cast<double>(end) / candidates.size();
    for (std::size_t i = 0U; i < targets.size(); ++i) {
      const double distance = std::abs(p - targets[i]);
      if (distance < distances[i]) {
        distances[i] = distance;
        chosen[i] = {names[i], candidates[begin].second, p};
      }
    }
    begin = end;
  }
  return chosen;
}

bool exact_reject(double p) { return p < 0.05; }
} // namespace

int main() {
  constexpr std::uint64_t seeds = 200U;
  constexpr std::uint64_t fixed_draws = 999U;
  constexpr std::uint64_t max_draws = 65'536U;
  std::filesystem::create_directories("results");
  std::ofstream raw("results/trials.csv");
  raw << "scenario,seed,exact_p,exact_decision,fixed_p,fixed_wrong,"
         "sequential_decision,sequential_draws,sequential_estimate,lower,upper,"
         "sequential_wrong\n";
  const auto scenarios = select_scenarios();
  std::cout << std::setprecision(17) << "{\n  \"alpha\": 0.05,\n"
            << "  \"error_budget\": 0.01,\n  \"seeds\": " << seeds
            << ",\n  \"fixed_draws\": " << fixed_draws
            << ",\n  \"max_sequential_draws\": " << max_draws
            << ",\n  \"scenarios\": [\n";
  for (std::size_t index = 0U; index < scenarios.size(); ++index) {
    const auto &scenario = scenarios[index];
    std::uint64_t fixed_wrong = 0U, sequential_wrong = 0U, undecided = 0U;
    std::uint64_t total_draws = 0U;
    for (std::uint64_t seed = 1U; seed <= seeds; ++seed) {
      const double fixed = quant::exact_backtest::monte_carlo_p_value(
          scenario.hits, fixed_draws, seed);
      const bool fixed_error = exact_reject(fixed) != exact_reject(scenario.exact_p);
      fixed_wrong += fixed_error ? 1U : 0U;
      auto candidate = scenario.hits;
      std::mt19937_64 rng(seed);
      const double observed = quant::exact_backtest::lr_independence(scenario.hits);
      const auto result = quant::sequential_backtest::decide([&]() {
        std::shuffle(candidate.begin(), candidate.end(), rng);
        return quant::exact_backtest::lr_independence(candidate) >= observed - 1e-12;
      });
      const bool seq_error =
          (result.decision == quant::sequential_backtest::Decision::reject &&
           !exact_reject(scenario.exact_p)) ||
          (result.decision == quant::sequential_backtest::Decision::non_reject &&
           exact_reject(scenario.exact_p));
      sequential_wrong += seq_error ? 1U : 0U;
      undecided += result.decision == quant::sequential_backtest::Decision::undecided ? 1U : 0U;
      total_draws += result.draws;
      raw << scenario.name << ',' << seed << ',' << scenario.exact_p << ','
          << (exact_reject(scenario.exact_p) ? "reject" : "non_reject") << ','
          << fixed << ',' << fixed_error << ','
          << quant::sequential_backtest::name(result.decision) << ','
          << result.draws << ',' << result.estimate << ',' << result.lower << ','
          << result.upper << ',' << seq_error << '\n';
    }
    std::cout << "    {\"name\": \"" << scenario.name << "\", \"exact_p\": "
              << scenario.exact_p << ", \"fixed_wrong\": " << fixed_wrong
              << ", \"sequential_wrong\": " << sequential_wrong
              << ", \"undecided\": " << undecided
              << ", \"mean_sequential_draws\": "
              << static_cast<double>(total_draws) / seeds << "}"
              << (index + 1U == scenarios.size() ? "\n" : ",\n");
  }
  std::cout << "  ]\n}\n";
}

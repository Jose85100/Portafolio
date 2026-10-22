#include "exact.hpp"

#include <cmath>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace {
void require(bool condition, const char *message) {
  if (!condition)
    throw std::runtime_error(message);
}
} // namespace

int main() {
  using namespace quant::exact_backtest;
  require(combinations(30U, 4U) == 27'405U, "combination count");
  std::uint64_t visited = 0U;
  enumerate_hits(8U, 3U, [&](const auto &hits) {
    require(std::count(hits.begin(), hits.end(), 1U) == 3, "count preserved");
    ++visited;
  });
  require(visited == 56U, "all states visited");
  std::vector<std::uint8_t> spaced(30U, 0U);
  for (const auto position : {3U, 10U, 17U, 24U})
    spaced[position] = 1U;
  std::vector<std::uint8_t> clustered(30U, 0U);
  for (const auto position : {12U, 13U, 14U, 15U})
    clustered[position] = 1U;
  require(lr_independence(clustered) > lr_independence(spaced),
          "cluster statistic");
  const auto exact = exact_p_value(clustered);
  require(exact.states == 27'405U, "exact states");
  require(exact.conservative >= exact.mid_p, "p-value ordering");
  require(exact.conservative > 0.0 && exact.conservative <= 1.0,
          "valid p-value");
  const auto first = monte_carlo_p_value(clustered, 999U, 42U);
  const auto second = monte_carlo_p_value(clustered, 999U, 42U);
  require(first == second, "seed reproducibility");
  require(monte_carlo_p_value(clustered, 999U, 43U) > 0.0,
          "nonzero Monte Carlo p");
  bool invalid = false;
  try {
    (void)lr_independence({1U});
  } catch (const std::invalid_argument &) {
    invalid = true;
  }
  require(invalid, "short input rejected");
  invalid = false;
  try {
    (void)lr_independence({0U, 2U});
  } catch (const std::invalid_argument &) {
    invalid = true;
  }
  require(invalid, "nonbinary input rejected");
  bool capped = false;
  try {
    (void)exact_p_value(std::vector<std::uint8_t>(30U, 0U), 0U);
  } catch (const std::length_error &) {
    capped = true;
  }
  require(capped, "state budget enforced");
  std::cout << "{\"tests\":12,\"status\":\"passed\"}\n";
}

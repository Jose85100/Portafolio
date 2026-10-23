#include "sequential.hpp"

#include <cstdint>
#include <random>
#include <stdexcept>

namespace {
void require(bool condition) {
  if (!condition)
    throw std::runtime_error("test assertion failed");
}
} // namespace

int main() {
  using quant::sequential_backtest::Decision;
  using quant::sequential_backtest::decide;
  auto always_false = [] { return false; };
  const auto reject = decide(always_false, 0.05, 0.01, 256U, 65'536U);
  require(reject.decision == Decision::reject);
  require(reject.draws < 65'536U);
  auto always_true = [] { return true; };
  const auto accept = decide(always_true);
  require(accept.decision == Decision::non_reject);
  require(accept.lower > 0.05);
  std::mt19937_64 rng_a(17U), rng_b(17U);
  std::bernoulli_distribution coin(0.05);
  const auto a = decide([&] { return coin(rng_a); });
  const auto b = decide([&] { return coin(rng_b); });
  require(a.decision == b.decision && a.draws == b.draws &&
          a.extreme == b.extreme);
  require(a.decision == Decision::undecided);
  require(a.draws == 65'536U);
  bool threw = false;
  try {
    static_cast<void>(decide(always_false, 0.0));
  } catch (const std::invalid_argument &) {
    threw = true;
  }
  require(threw);
}

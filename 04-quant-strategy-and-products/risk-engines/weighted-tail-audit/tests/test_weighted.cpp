#include <algorithm>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <random>
#include <string>
#include <utility>
#include <vector>

#include "quant/risk.hpp"
#include "quant/weighted_tail.hpp"

namespace {
std::size_t checks = 0;
void require(bool condition, const std::string& message) {
  ++checks;
  if (!condition) {
    throw std::runtime_error(message);
  }
}
bool near(double left, double right) {
  return std::abs(left - right) <= 1e-10 * std::max({1.0, std::abs(left), std::abs(right)});
}
template <class Function>
void invalid(Function function) {
  bool rejected = false;
  try {
    function();
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  require(rejected, "invalid input accepted");
}
}  // namespace

int main() {
  try {
    using quant::weighted_tail;
    using quant::WeightedScenario;
    const double inf = std::numeric_limits<double>::infinity();
    const double nan = std::numeric_limits<double>::quiet_NaN();
    invalid([] { weighted_tail({}); });
    for (double alpha : {0.0, 1.0, -0.1, inf, nan}) {
      invalid([&] { weighted_tail({{1, 1}}, alpha); });
    }
    for (auto bad : std::vector<WeightedScenario>{{nan, 1}, {inf, 1}, {1, -1}, {1, nan}, {1, inf}}) {
      invalid([&] { weighted_tail({bad}); });
    }
    invalid([] { weighted_tail({{1, 0}, {2, 0}}); });
    const auto discrete = weighted_tail({{0, 99}, {100, 1}, {1e9, 0}});
    require(near(discrete.es, 40) && discrete.var == 0 && near(discrete.mean, 1), "discrete atom");
    require(near(discrete.tail_mass, 0.025) && discrete.positive_scenarios == 2, "tail mass");
    require(weighted_tail({{-5, 4}}).es == -5, "singleton signed");
    const auto large = weighted_tail({{1e308, 1e308}, {1e308, 1e308}}, 0.5);
    require(large.es == 1e308 && large.mean == 1e308, "overflow avoidance");
    const auto cancellation = weighted_tail({{-1e308, 1}, {1e308, 1}}, 0.5);
    require(cancellation.mean == 0 && cancellation.es == 1e308, "signed cancellation");
    require(near(weighted_tail({{1, 1e-300}, {2, 1e300}}).es, 2), "extreme weights");
    const double tiny_es = weighted_tail({{1e308, 1e-300}, {0, 1e300}}).es;
    require(tiny_es > 0 && near(tiny_es / 4e-291, 1), "retain representable ES from tiny probability");
    for (double alpha : {1e-12, 0.5, std::nextafter(1.0, 0.0)}) {
      const auto result = weighted_tail({{1, 1}, {2, 1}, {3, 1}}, alpha);
      require(result.es >= result.var && result.es <= 3 && near(result.tail_mass, 1 - alpha), "edge alpha");
    }
    require(weighted_tail({{0, 1}, {10, 1}}, 0.5).var == 0, "inverse CDF exact boundary");
    require(near(weighted_tail({{5, 2}, {5, 3}, {5, 9}}).es, 5), "ties");

    std::mt19937_64 rng(20261014);
    for (std::size_t trial = 0; trial < 500; ++trial) {
      const auto n = static_cast<std::size_t>(2 + rng() % 30);
      const double alpha = std::vector<double>{0.5, 0.75, 0.875, 0.975, 0.99}[trial % 5];
      std::vector<WeightedScenario> x;
      std::vector<WeightedScenario> y;
      std::vector<WeightedScenario> combined;
      std::vector<WeightedScenario> translated;
      std::vector<WeightedScenario> scaled;
      std::vector<WeightedScenario> monotone;
      std::vector<WeightedScenario> reweighted;
      std::vector<WeightedScenario> uniform;
      std::vector<double> expanded;
      std::vector<double> equal;
      for (std::size_t i = 0; i < n; ++i) {
        const double a = static_cast<double>(static_cast<std::int64_t>(rng() % 2001) - 1000) / 10;
        const double b = static_cast<double>(static_cast<std::int64_t>(rng() % 2001) - 1000) / 10;
        const auto weight = static_cast<std::size_t>(1 + rng() % 8);
        const double w = static_cast<double>(weight);
        x.push_back({a, w});
        y.push_back({b, w});
        combined.push_back({a + b, w});
        translated.push_back({a + 7, w});
        scaled.push_back({3 * a, w});
        monotone.push_back({a + static_cast<double>(i), w});
        reweighted.push_back({a, w * 7});
        uniform.push_back({a, 1});
        expanded.insert(expanded.end(), weight, a);
        equal.push_back(a);
      }
      const auto result = weighted_tail(x, alpha);
      require(near(result.es, quant::tail(expanded, alpha).es), "expanded baseline disagreement");
      require(near(weighted_tail(uniform, alpha).es, quant::tail(equal, alpha).es), "uniform baseline");
      require(near(weighted_tail(translated, alpha).es, result.es + 7), "cash translation");
      require(near(weighted_tail(scaled, alpha).es, result.es * 3), "positive homogeneity");
      require(weighted_tail(monotone, alpha).es >= result.es - 1e-9, "monotonicity");
      require(weighted_tail(combined, alpha).es <= result.es + weighted_tail(y, alpha).es + 1e-9,
              "subadditivity with shared probabilities");
      require(near(weighted_tail(reweighted, alpha).es, result.es), "weight normalization");
      std::shuffle(x.begin(), x.end(), rng);
      require(near(weighted_tail(x, alpha).es, result.es), "permutation invariance");
    }
    std::cout << "{\"checks\":" << checks << ",\"property_trials\":500,\"passed\":true}\n";
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
  return 0;
}

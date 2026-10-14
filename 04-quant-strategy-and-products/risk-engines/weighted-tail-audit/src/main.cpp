#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "quant/risk.hpp"
#include "quant/weighted_tail.hpp"

namespace {
struct BenchmarkConfig {
  std::string mode;
  std::size_t scenarios;
  std::size_t repeats;
  std::uint64_t seed;
};

std::uint64_t unsigned_argument(const std::string& value) {
  std::size_t consumed = 0;
  if (value.empty() || value.front() == '-') {
    throw std::invalid_argument("nonnegative integer required");
  }
  const auto result = std::stoull(value, &consumed);
  if (consumed != value.size()) {
    throw std::invalid_argument("trailing integer data");
  }
  return result;
}

std::size_t self_peak_rss_kib() {
  // Linux VmHWM is measured after exec, unlike fork-inherited wait4 maxima.
  std::ifstream status("/proc/self/status");
  std::string line;
  while (std::getline(status, line)) {
    if (line.rfind("VmHWM:", 0) == 0) {
      std::istringstream record(line);
      std::string label;
      std::string units;
      std::size_t peak = 0;
      if (record >> label >> peak >> units && units == "kB") {
        return peak;
      }
    }
  }
  throw std::runtime_error("Linux /proc/self/status VmHWM unavailable");
}

void fixtures(const std::string& filename) {
  std::ifstream input(filename);
  if (!input) {
    throw std::invalid_argument("cannot open fixtures");
  }
  std::cout << "id,var,es,mean,tail_mass\n" << std::setprecision(17);
  std::string line;
  while (std::getline(input, line)) {
    std::istringstream record(line);
    std::size_t id = 0;
    std::size_t n = 0;
    double alpha = 0;
    if (!(record >> id >> alpha >> n) || n == 0 || n > 1000000) {
      throw std::invalid_argument("invalid fixture dimensions");
    }
    std::vector<quant::WeightedScenario> scenarios(n);
    for (auto& scenario : scenarios) {
      std::string loss;
      std::string weight;
      if (!(record >> loss >> weight)) {
        throw std::invalid_argument("incomplete fixture");
      }
      std::size_t loss_end = 0;
      std::size_t weight_end = 0;
      scenario = {std::stod(loss, &loss_end), std::stod(weight, &weight_end)};
      if (loss_end != loss.size() || weight_end != weight.size()) {
        throw std::invalid_argument("trailing numeric data");
      }
    }
    std::string trailing;
    if (record >> trailing) {
      throw std::invalid_argument("trailing fixture fields");
    }
    const auto result = quant::weighted_tail(scenarios, alpha);
    std::cout << id << ',' << result.var << ',' << result.es << ',' << result.mean << ',' << result.tail_mass
              << '\n';
  }
}

std::vector<quant::WeightedScenario> generate(const BenchmarkConfig& config) {
  std::mt19937_64 rng(config.seed);
  const auto n = config.scenarios;
  std::vector<quant::WeightedScenario> scenarios;
  scenarios.reserve(n);
  for (std::size_t i = 0; i < n; ++i) {
    // Integer operations avoid standard-library-specific distribution algorithms.
    const auto signed_loss = static_cast<std::int64_t>(rng() % 200001) - 100000;
    scenarios.push_back({static_cast<double>(signed_loss) / 100, static_cast<double>(1 + rng() % 8)});
  }
  return scenarios;
}

void benchmark(const BenchmarkConfig& config) {
  const auto& mode = config.mode;
  const auto n = config.scenarios;
  const auto repeats = config.repeats;
  if (n < 2 || n > 1000000 || repeats == 0 || repeats > 1000) {
    throw std::invalid_argument("benchmark dimensions out of range");
  }
  const auto scenarios = generate(config);
  double sink = 0;
  auto evaluate = [&]() {
    if (mode == "weighted") {
      return quant::weighted_tail(scenarios).es;
    }
    if (mode != "expanded" && mode != "uniform_ablation") {
      throw std::invalid_argument("unknown benchmark mode");
    }
    std::vector<double> losses;
    losses.reserve(mode == "expanded" ? 8 * n : n);
    for (const auto& scenario : scenarios) {
      const auto count = mode == "expanded" ? static_cast<std::size_t>(scenario.weight) : 1;
      losses.insert(losses.end(), count, scenario.loss);
    }
    return quant::tail(std::move(losses), 0.975).es;
  };
  sink += evaluate();  // warm-up; excluded from timing, included in process RSS.
  std::cout << "n,mode,repeat,ms,es,self_peak_rss_kib\n" << std::setprecision(17);
  for (std::size_t repeat = 0; repeat < repeats; ++repeat) {
    const auto start = std::chrono::steady_clock::now();
    const double es = evaluate();
    const auto end = std::chrono::steady_clock::now();
    const double ms = std::chrono::duration<double, std::milli>(end - start).count();
    sink += es;
    std::cout << n << ',' << mode << ',' << repeat << ',' << ms << ',' << es << ',' << self_peak_rss_kib()
              << '\n';
  }
  if (!std::isfinite(sink)) {
    throw std::range_error("nonfinite benchmark sink");
  }
}
}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc == 2 && std::string(argv[1]) == "--platform") {
      std::cout << "{\"long_double_digits\":" << std::numeric_limits<long double>::digits
                << ",\"long_double_max_exponent\":" << std::numeric_limits<long double>::max_exponent
                << ",\"scenario_bytes\":" << sizeof(quant::WeightedScenario)
                << ",\"atom_bytes\":" << sizeof(quant::weighted_detail::Atom) << "}\n";
    } else if (argc == 3 && std::string(argv[1]) == "--fixtures") {
      fixtures(argv[2]);
    } else if (argc == 7 && std::string(argv[1]) == "--bench") {
      if (std::string(argv[6]) != "--csv") {
        throw std::invalid_argument("expected --csv");
      }
      benchmark(
          {argv[2], unsigned_argument(argv[3]), unsigned_argument(argv[4]), unsigned_argument(argv[5])});
    } else {
      throw std::invalid_argument("usage: --fixtures FILE | --bench MODE N REPEATS SEED --csv");
    }
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 2;
  }
  return 0;
}

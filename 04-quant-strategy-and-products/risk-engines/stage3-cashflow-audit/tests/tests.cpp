#include "quant/stage3.hpp"
#include <functional>
#include <iostream>
#include <limits>
#include <random>

int main() {
  int checks = 0;
  const auto check = [&](bool valid) {
    ++checks;
    if (!valid) {
      throw std::runtime_error("failed check " + std::to_string(checks));
    }
  };
  const auto rejected = [&](const std::function<void()> &call) {
    try {
      call();
    } catch (const std::invalid_argument &) {
      return true;
    }
    return false;
  };
  const auto loss = quant::stage3_shortfall;
  check(std::abs(loss(100, {50}, {1}, .1) - 54.54545454545455) < 1e-12);
  check(loss(100, {100}, {1}, 1e-18) > 0);
  check(loss(100, {100}, {0}, .1) == 0);
  check(loss(0, {0}, {1}, .1) == 0);
  check(loss(100, {40, 60}, {1, 2}, 0) == 0);
  const double inf = std::numeric_limits<double>::infinity();
  const double nan = std::numeric_limits<double>::quiet_NaN();
  for (double bad : {-1., inf, nan}) {
    check(rejected([&] { loss(bad, {0}, {1}, .1); }));
    check(rejected([&] { loss(100, {bad}, {1}, .1); }));
    check(rejected([&] { loss(100, {0}, {bad}, .1); }));
    check(rejected([&] { loss(100, {0}, {1}, bad); }));
  }
  check(rejected([&] { loss(100, {}, {}, .1); }));
  check(rejected([&] { loss(100, {0}, {}, .1); }));
  check(rejected([&] { loss(100, {101}, {1}, .1); }));
  check(rejected([&] { loss(100, {1e308, 1e308}, {1, 2}, .1); }));
  check(loss(100, {100}, {1e308}, 0) == 0);
  check(loss(100, {100}, {1e308}, 1e308) == 100);
  std::mt19937 rng(20261020);
  for (int i = 0; i < 1000; ++i) {
    const double recovery = static_cast<double>(rng() % 101);
    const double rate = static_cast<double>(rng() % 100) / 100.;
    const double time = static_cast<double>(rng() % 20);
    const double value = loss(100, {recovery}, {time}, rate);
    check(value >= 0 && value <= 100);
    check(loss(100, {recovery}, {time + 1}, rate) >= value);
    check(std::abs(loss(100, {recovery / 2, recovery / 2}, {time, time}, rate) -
                   value) < 1e-12);
  }
  std::cout << "{\"checks\":" << checks << ",\"seed\":20261020}\n";
}

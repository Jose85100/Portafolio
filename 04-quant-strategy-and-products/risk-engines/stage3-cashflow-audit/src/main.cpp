#include "quant/stage3.hpp"
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <string>

// Deliberately subtractive arithmetic ablation, not a valid replacement API.
double subtractive(double gross, const std::vector<double> &cash,
                   const std::vector<double> &years, double rate) {
  double pv = 0;
  for (std::size_t i = 0; i < cash.size(); ++i) {
    pv += cash[i] / std::pow(1 + rate, years[i]);
  }
  return gross - pv;
}

int main(int argc, char **argv) {
  try {
    std::cout << std::setprecision(17);
    if (argc == 3 && std::string(argv[1]) == "--fixtures") {
      std::ifstream input(argv[2]);
      if (!input) {
        throw std::invalid_argument("cannot open fixtures");
      }
      std::size_t id = 0;
      double gross = 0, rate = 0, c1 = 0, c2 = 0, t1 = 0, t2 = 0;
      std::cout << "id,stable,subtractive\n";
      std::size_t count = 0;
      while (input >> id) {
        if (!(input >> gross >> rate >> c1 >> c2 >> t1 >> t2)) {
          throw std::invalid_argument("incomplete fixture");
        }
        const std::vector<double> cash{c1, c2}, years{t1, t2};
        std::cout << id << ','
                  << quant::stage3_shortfall(gross, cash, years, rate) << ','
                  << subtractive(gross, cash, years, rate) << '\n';
        ++count;
      }
      if (!input.eof()) {
        throw std::invalid_argument("malformed fixture");
      }
      if (count == 0) {
        throw std::invalid_argument("empty fixture");
      }
    } else if (argc == 5 && std::string(argv[1]) == "--bench") {
      const std::string mode = argv[2];
      if (mode != "stable" && mode != "subtractive") {
        throw std::invalid_argument("unknown method");
      }
      const auto n = std::stoul(argv[3]);
      if (n == 0 || n > 100000) {
        throw std::invalid_argument("invalid size");
      }
      std::mt19937 rng(static_cast<unsigned int>(std::stoul(argv[4])));
      std::vector<std::vector<double>> cash(n, std::vector<double>(2));
      for (auto &row : cash) {
        row = {static_cast<double>(20 + rng() % 20),
               static_cast<double>(20 + rng() % 20)};
      }
      const std::vector<double> years{1, 2};
      volatile double checksum = 0;
      const auto calculate = [&](const std::vector<double> &row) {
        return mode == "stable" ? quant::stage3_shortfall(100, row, years, .1)
                                : subtractive(100, row, years, .1);
      };
      for (const auto &row : cash) {
        checksum = checksum + calculate(row);
      }
      const auto start = std::chrono::steady_clock::now();
      for (int repeat = 0; repeat < 100; ++repeat) {
        for (const auto &row : cash) {
          checksum = checksum + calculate(row);
        }
      }
      const auto elapsed = std::chrono::duration<double, std::milli>(
                               std::chrono::steady_clock::now() - start)
                               .count() /
                           100;
      // /proc VmHWM belongs to the exec'd CLI. wait4 may retain pre-exec RSS.
      std::ifstream status("/proc/self/status");
      std::string line;
      unsigned long peak_kib = 0;
      while (std::getline(status, line)) {
        if (line.rfind("VmHWM:", 0) == 0) {
          std::istringstream(line.substr(6)) >> peak_kib;
        }
      }
      if (peak_kib == 0) {
        throw std::runtime_error("VmHWM unavailable");
      }
      std::cout << elapsed << ',' << checksum << ',' << peak_kib << '\n';
    } else {
      throw std::invalid_argument(
          "use --fixtures path or --bench method n seed");
    }
    return 0;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 2;
  }
}

#include "risk/portfolio.hpp"
#include <iomanip>
#include <iostream>
int main() {
  std::vector<risk::Exposure> exposures;
  double pd, lgd, ead;
  while (std::cin >> pd >> lgd >> ead) exposures.push_back({pd,lgd,ead});
  if (!std::cin.eof() || exposures.empty()) return 1;
  try { std::cout << std::setprecision(17) << risk::expected_loss(exposures) << ' ' << risk::independent_variance(exposures) << '\n'; }
  catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}

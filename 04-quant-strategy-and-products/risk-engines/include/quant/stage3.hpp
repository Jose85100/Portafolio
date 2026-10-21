#pragma once

#include <cmath>
#include <stdexcept>
#include <vector>

namespace quant {
// Already-impaired, non-POCI, fixed recovery cash flows. No future-default PD.
// Bounded contract: finite nonnegative rate, times, amounts; sum(cash) <=
// gross.
inline double stage3_shortfall(double gross, const std::vector<double> &cash,
                               const std::vector<double> &years, double rate) {
  if (!std::isfinite(gross) || gross < 0 || !std::isfinite(rate) || rate < 0 ||
      cash.empty() || cash.size() != years.size()) {
    throw std::invalid_argument("invalid Stage3 shape, gross or rate");
  }
  double nominal = 0;
  double delay = 0;
  const double log_rate = std::log1p(rate);
  for (std::size_t i = 0; i < cash.size(); ++i) {
    if (!std::isfinite(cash[i]) || cash[i] < 0 || !std::isfinite(years[i]) ||
        years[i] < 0) {
      throw std::invalid_argument("invalid recovery or time");
    }
    nominal += cash[i];
    // Handle zero-rate * huge-time explicitly (both inputs are finite).
    const double exponent = rate == 0 ? 0 : log_rate * years[i];
    delay += cash[i] * (-std::expm1(-exponent));
  }
  if (!std::isfinite(nominal) || nominal > gross) {
    throw std::invalid_argument("nominal recovery exceeds gross");
  }
  const double result = (gross - nominal) + delay;
  if (!std::isfinite(result)) {
    throw std::overflow_error("shortfall not representable");
  }
  return result;
}
} // namespace quant

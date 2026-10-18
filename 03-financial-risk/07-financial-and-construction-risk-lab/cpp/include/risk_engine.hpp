#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace construction_risk {
struct TailRisk { double var; double es; };
inline TailRisk empirical_var_es(std::vector<double> losses, double alpha = 0.95) {
    if (losses.empty() || !(alpha > 0 && alpha < 1)) throw std::invalid_argument("invalid alpha/losses");
    for (double v : losses) if (!std::isfinite(v)) throw std::invalid_argument("nonfinite loss");
    std::sort(losses.begin(), losses.end());
    const auto n = losses.size();
    const auto k = static_cast<std::size_t>(std::ceil(alpha * n)) - 1;
    const long double mass = static_cast<long double>(n) * (1.0 - alpha);
    const auto whole = static_cast<std::size_t>(std::floor(mass));
    const long double fractional = mass - whole;
    long double es = 0.0L;
    for (std::size_t j = n-whole; j < n; ++j)
        es += static_cast<long double>(losses[j]) / mass;
    if (fractional > 0)
        es += static_cast<long double>(losses[n-whole-1]) * (fractional/mass);
    const double result = static_cast<double>(es);
    if (!std::isfinite(result)) throw std::overflow_error("ES is nonfinite");
    return {losses[k], result};
}
inline std::vector<double> cash_path(double opening, const std::vector<double>& collections,
                                     const std::vector<double>& costs, const std::vector<double>& debt) {
    if (collections.size() != costs.size() || costs.size() != debt.size() || collections.empty())
        throw std::invalid_argument("flow lengths mismatch");
    if (!std::isfinite(opening) || opening < 0) throw std::invalid_argument("invalid opening cash");
    std::vector<double> cash;
    cash.reserve(collections.size());
    for (std::size_t t=0; t<collections.size(); ++t) {
        if (!std::isfinite(collections[t]) || !std::isfinite(costs[t]) || !std::isfinite(debt[t]) || collections[t]<0 || costs[t]<0 || debt[t]<0) throw std::invalid_argument("negative flow");
        opening += collections[t]-costs[t]-debt[t];
        if (!std::isfinite(opening)) throw std::overflow_error("cash accumulation overflow");
        cash.push_back(opening);
    }
    return cash;
}
inline double peak_shortfall(const std::vector<double>& cash, double opening, double floor=0.0) {
    if (!std::isfinite(opening) || !std::isfinite(floor)) throw std::invalid_argument("invalid cash/floor");
    double peak = std::max(0.0, floor-opening);
    for (double c : cash) {
        if (!std::isfinite(c)) throw std::invalid_argument("nonfinite cash path");
        peak = std::max(peak, floor-c);
    }
    if (!std::isfinite(peak)) throw std::overflow_error("shortfall overflow");
    return peak;
}
} // namespace construction_risk

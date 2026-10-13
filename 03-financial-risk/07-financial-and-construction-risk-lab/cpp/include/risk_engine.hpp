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
    auto k = static_cast<std::size_t>(std::ceil(alpha * losses.size())) - 1;
    double es = std::accumulate(losses.begin() + k, losses.end(), 0.0) / (losses.size() - k);
    return {losses[k], es};
}
inline std::vector<double> cash_path(double opening, const std::vector<double>& collections,
                                     const std::vector<double>& costs, const std::vector<double>& debt) {
    if (collections.size() != costs.size() || costs.size() != debt.size() || collections.empty())
        throw std::invalid_argument("flow lengths mismatch");
    std::vector<double> cash;
    cash.reserve(collections.size());
    for (std::size_t t=0; t<collections.size(); ++t) {
        if (collections[t]<0 || costs[t]<0 || debt[t]<0) throw std::invalid_argument("negative flow");
        opening += collections[t]-costs[t]-debt[t];
        cash.push_back(opening);
    }
    return cash;
}
inline double peak_shortfall(const std::vector<double>& cash, double opening, double floor=0.0) {
    double peak = std::max(0.0, floor-opening);
    for (double c : cash) peak = std::max(peak, floor-c);
    return peak;
}
} // namespace construction_risk

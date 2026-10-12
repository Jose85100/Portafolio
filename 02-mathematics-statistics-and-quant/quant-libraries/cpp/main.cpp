// C++17: abstracción, polimorfismo y contenedores con gestión RAII.
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

struct Exposure {
    double pd, lgd, ead;
    Exposure(double p, double g, double e) : pd(p), lgd(g), ead(e) {
        if (!std::isfinite(p) || !std::isfinite(g) || !std::isfinite(e) ||
            p < 0 || p > 1 || g < 0 || g > 1 || e < 0)
            throw std::invalid_argument("Parámetros inválidos");
    }
};

class RiskModel {
public:
    virtual ~RiskModel() = default;
    virtual double calculate(const std::vector<Exposure>& xs) const = 0;
};

class DeterministicEL final : public RiskModel {
public:
    double calculate(const std::vector<Exposure>& xs) const override {
        double total = 0.0;
        for (const auto& x : xs) {
            const double term = x.pd * x.lgd * x.ead;
            if (!std::isfinite(term)) throw std::overflow_error("Overflow");
            total += term;
        }
        return total;
    }
};

int main() {
    const std::vector<Exposure> xs = {
        {0.02, 0.4, 1000}, {0.05, 0.6, 2000}, {0.10, 0.3, 500}
    };
    const RiskModel& model = DeterministicEL{};
    const double result = model.calculate(xs);
    if (std::fabs(result - 83.0) > 1e-10) return 1;
    std::cout << std::fixed << std::setprecision(10) << "EL=" << result << "\n";
}

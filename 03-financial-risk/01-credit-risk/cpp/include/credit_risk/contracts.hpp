#pragma once

// Synthetic-only educational domain contract. No I/O, database driver,
// customer identifier, credential, or credit-decision capability is included.

#include <cmath>
#include <cstdint>
#include <optional>
#include <string>

namespace portfolio::credit_risk {

struct RunContext final {
  std::string contract_version{"1.0.0"};
  std::string dataset_version;
  std::string model_version;
  std::string run_id;
  std::int16_t horizon_months{};
  bool synthetic{true};

  [[nodiscard]] bool valid() const noexcept {
    return synthetic && !dataset_version.empty() && !model_version.empty() &&
           !run_id.empty() && horizon_months >= 1 && horizon_months <= 360;
  }
};

struct ExposureSnapshot final {
  std::string exposure_id;  // Synthetic stable ID only.
  std::string as_of_date;   // ISO-8601 calendar date.
  std::string segment_code;
  double ead_cop{};
  std::int32_t days_past_due{};

  [[nodiscard]] bool valid() const noexcept {
    return !exposure_id.empty() && !as_of_date.empty() && !segment_code.empty() &&
           std::isfinite(ead_cop) && ead_cop >= 0.0 && days_past_due >= 0;
  }
};

struct RiskEstimate final {
  double pd_12m{};
  double lgd_downturn{};
  double ead_cop{};
  double expected_loss_cop{};

  [[nodiscard]] bool valid(double tolerance = 0.01) const noexcept {
    const bool domains = std::isfinite(pd_12m) && std::isfinite(lgd_downturn) &&
        std::isfinite(ead_cop) && std::isfinite(expected_loss_cop) &&
        pd_12m >= 0.0 && pd_12m <= 1.0 && lgd_downturn >= 0.0 &&
        lgd_downturn <= 1.0 && ead_cop >= 0.0 && expected_loss_cop >= 0.0;
    return domains && std::abs(expected_loss_cop - pd_12m * lgd_downturn * ead_cop) <= tolerance;
  }
};

class RiskEstimator {
 public:
  virtual ~RiskEstimator() = default;
  [[nodiscard]] virtual std::optional<RiskEstimate> estimate(
      const RunContext& context, const ExposureSnapshot& exposure) const = 0;
};

}  // namespace portfolio::credit_risk

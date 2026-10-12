#pragma once
#include <cmath>
#include <cstddef>
#include <limits>
#include <stdexcept>
#include <vector>
namespace risk {
struct Exposure { double pd, lgd, ead; };
inline void validate(const Exposure& e) {
 if (!std::isfinite(e.pd)||!std::isfinite(e.lgd)||!std::isfinite(e.ead)||e.pd<0||e.pd>1||e.lgd<0||e.lgd>1||e.ead<0) throw std::invalid_argument("invalid exposure");
}
inline double expected_loss(const std::vector<Exposure>& es) {
 long double s=0;
 for(const auto& e:es){validate(e);s+=static_cast<long double>(e.pd)*e.lgd*e.ead;}
 if(s>std::numeric_limits<double>::max()) throw std::overflow_error("expected loss overflow");
 return static_cast<double>(s);
}
inline double independent_variance(const std::vector<Exposure>& es) {
 long double s=0;
 for(const auto& e:es){validate(e);long double a=static_cast<long double>(e.lgd)*e.ead;s+=a*a*e.pd*(1-e.pd);}
 if(s>std::numeric_limits<double>::max()) throw std::overflow_error("variance overflow");
 return static_cast<double>(s);
}
inline double correlated_variance(const std::vector<Exposure>& es,const std::vector<std::vector<double>>& cov) {
 const auto n=es.size();if(cov.size()!=n)throw std::invalid_argument("covariance dimension");
 for(const auto& e:es)validate(e);
 for(const auto& row:cov)if(row.size()!=n)throw std::invalid_argument("covariance dimension");
 long double s=0;
 for(std::size_t i=0;i<n;++i){
  for(std::size_t j=0;j<n;++j){double v=cov[i][j];if(!std::isfinite(v))throw std::invalid_argument("nonfinite covariance");
   if(std::abs(v-cov[j][i])>1e-10)throw std::invalid_argument("asymmetric covariance");
   s+=static_cast<long double>(es[i].lgd)*es[i].ead*es[j].lgd*es[j].ead*v;
  }
 }
 if(s< -1e-8L)throw std::invalid_argument("negative portfolio variance; check PSD");
 if(s>std::numeric_limits<double>::max())throw std::overflow_error("variance overflow");
 return static_cast<double>(s<0?0:s);
}
}

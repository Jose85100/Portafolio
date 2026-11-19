#pragma once
#include <algorithm>
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
// Necessary Bernoulli marginal/pairwise bounds and a semidefinite LDL check.
// Pairwise feasibility and PSD do not establish joint Bernoulli feasibility.
inline void validate_default_covariance(const std::vector<Exposure>& es,
                                        const std::vector<std::vector<double>>& cov) {
 const std::size_t n=es.size();
 constexpr long double tol=1e-10L;
 if(cov.size()!=n) throw std::invalid_argument("covariance dimension");
 for(const auto& e:es) validate(e);
 for(const auto& row:cov) if(row.size()!=n) throw std::invalid_argument("covariance dimension");
 for(std::size_t i=0;i<n;++i){
  for(std::size_t j=0;j<n;++j){
   if(!std::isfinite(cov[i][j]) || std::abs(cov[i][j]-cov[j][i])>tol)
    throw std::invalid_argument("invalid covariance symmetry or value");
   const long double pi=es[i].pd, pj=es[j].pd;
   const long double lower=std::max(0.0L,pi+pj-1)-pi*pj;
   const long double upper=std::min(pi,pj)-pi*pj;
   if(cov[i][j]<lower-tol || cov[i][j]>upper+tol)
    throw std::invalid_argument("covariance violates Bernoulli bounds");
  }
  const long double p=es[i].pd;
  if(std::abs(static_cast<long double>(cov[i][i])-p*(1-p))>tol)
   throw std::invalid_argument("covariance diagonal inconsistent with PD");
 }
 // Unpivoted LDL handles singular PSD matrices: a zero pivot requires a zero residual column.
 std::vector<std::vector<long double>> l(n,std::vector<long double>(n,0));
 std::vector<long double> d(n,0);
 for(std::size_t i=0;i<n;++i){
  long double pivot=cov[i][i];
  for(std::size_t k=0;k<i;++k) pivot-=l[i][k]*l[i][k]*d[k];
  if(pivot < -tol) throw std::invalid_argument("covariance is not PSD");
  d[i]=pivot>tol?pivot:0;
  for(std::size_t j=i+1;j<n;++j){
   long double residual=cov[j][i];
   for(std::size_t k=0;k<i;++k) residual-=l[j][k]*l[i][k]*d[k];
   if(d[i]==0){if(std::abs(residual)>tol) throw std::invalid_argument("covariance is not PSD");}
   else l[j][i]=residual/d[i];
  }
 }
}
inline double correlated_variance(const std::vector<Exposure>& es,const std::vector<std::vector<double>>& cov) {
 validate_default_covariance(es,cov);
 const auto n=es.size();
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

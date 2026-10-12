#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <numeric>
#include <random>
#include <stdexcept>
#include <vector>
namespace quant {
inline void check(bool ok,const char* msg){if(!ok)throw std::invalid_argument(msg);}
struct Tail {double mean,var,es;};
inline Tail tail(std::vector<double> x,double alpha){
 check(x.size()>1&&std::isfinite(alpha)&&alpha>0&&alpha<1,"invalid tail inputs");
 for(double v:x)check(std::isfinite(v),"nonfinite loss");
 double mean=std::accumulate(x.begin(),x.end(),0.0)/x.size();
 std::sort(x.begin(),x.end());
 double pos=(x.size()-1)*alpha;
 std::size_t lo=static_cast<std::size_t>(pos);
 double var=x[lo]+(pos-lo)*(x[std::min(lo+1,x.size()-1)]-x[lo]);
 double mass=(1-alpha)*x.size();
 std::size_t k=static_cast<std::size_t>(mass);
 double sum=0;
 for(std::size_t j=0;j<k;++j)sum+=x[x.size()-1-j];
 if(mass-k>0)sum+=(mass-k)*x[x.size()-1-k];
 return {mean,var,sum/mass};
}
inline double inverse_normal(double p){
 check(std::isfinite(p)&&p>=0&&p<=1,"invalid PD");
 if(p==0)return -INFINITY;
 if(p==1)return INFINITY;
 // Bisection: robust and adequate for portfolio simulation, ~55 iterations.
 double low=-12,high=12;
 for(int j=0;j<60;++j){
  double mid=(low+high)/2;
  if(0.5*std::erfc(-mid/std::sqrt(2.0))<p)low=mid;
  else high=mid;
 }
 return (low+high)/2;
}
struct Loan {
 double pd,lgd,ead,rho;
 Loan(double p,double g,double e,double r):pd(p),lgd(g),ead(e),rho(r){
  check(std::isfinite(p)&&std::isfinite(g)&&std::isfinite(e)&&std::isfinite(r)
   &&p>=0&&p<=1&&g>=0&&g<=1&&e>=0&&r>=0&&r<1,"invalid loan");
 }
};
struct CreditResult {double analytic_el,mc_el,var,es,standard_error;};
class CreditEngine {
 std::vector<Loan> loans;
public:
 explicit CreditEngine(std::vector<Loan> xs):loans(std::move(xs)){check(!loans.empty(),"empty loans");}
 CreditResult run(std::size_t n,std::uint64_t seed,double alpha=0.99)const{
  check(n>1,"need >=2 scenarios");
  std::mt19937_64 gen(seed);std::normal_distribution<double> normal(0,1);
  std::vector<double> cut;for(auto& x:loans)cut.push_back(inverse_normal(x.pd));
  std::vector<double> losses;losses.reserve(n);
  double el=0;for(auto& x:loans)el+=x.pd*x.lgd*x.ead;
  for(std::size_t s=0;s<n;++s){
   double z=normal(gen),l=0;
   for(std::size_t i=0;i<loans.size();++i){
    const auto& x=loans[i];
    double a=std::sqrt(x.rho)*z+std::sqrt(1-x.rho)*normal(gen);
    if(a<cut[i])l+=x.lgd*x.ead;
   }
   losses.push_back(l);
  }
  auto t=tail(losses,alpha);
  double ss=0;for(double x:losses)ss+=(x-t.mean)*(x-t.mean);
  return {el,t.mean,t.var,t.es,std::sqrt(ss/(n*(n-1.0)))};
 }
};
inline double kupiec(std::size_t exceptions,std::size_t n,double alpha){
 check(n>0&&exceptions<=n&&alpha>0&&alpha<1,"invalid kupiec");
 double p=1-alpha,q=static_cast<double>(exceptions)/n;
 auto xlogy=[](double x,double y){return x==0?0.0:x*std::log(y);};
 return std::max(0.0,2*(xlogy(exceptions,q)+xlogy(n-exceptions,1-q)
                         -xlogy(exceptions,p)-xlogy(n-exceptions,1-p)));
}
struct MarketResult {Tail metrics;std::size_t exceptions;double kupiec_lr;};
class MarketEngine {
public:
 MarketResult run(std::size_t n,std::uint64_t seed,double position=1e6,
                  double sigma=0.015,double alpha=0.975)const{
  check(n>1&&position>=0&&sigma>=0&&std::isfinite(position)&&std::isfinite(sigma),"invalid market");
  std::mt19937_64 gen(seed);std::normal_distribution<double> normal(0,1);
  std::vector<double> losses;losses.reserve(n);
  for(std::size_t i=0;i<n;++i)losses.push_back(-position*sigma*normal(gen));
  auto m=tail(losses,alpha);
  std::size_t exceptions=0;for(double x:losses)if(x>m.var)++exceptions;
  // In-sample exception count is descriptive, NOT a valid out-of-sample backtest.
  return {m,exceptions,kupiec(exceptions,n,alpha)};
 }
 MarketResult backtest(const std::vector<double>& losses,
                       const std::vector<double>& forecast,double alpha)const{
  check(losses.size()==forecast.size()&&losses.size()>1,"invalid vectors");
  std::size_t count=0;
  for(std::size_t i=0;i<losses.size();++i){
   check(std::isfinite(losses[i])&&std::isfinite(forecast[i]),"nonfinite");
   if(losses[i]>forecast[i])++count;
  }
  return {tail(losses,alpha),count,kupiec(count,losses.size(),alpha)};
 }
};
struct Flow {
 double inflow,outflow,margin;
 Flow(double a,double b,double c):inflow(a),outflow(b),margin(c){
  check(std::isfinite(a)&&std::isfinite(b)&&std::isfinite(c)
        &&a>=0&&b>=0&&c>=0,"invalid flow");
 }
};
struct Path {std::vector<double> cash;std::size_t first_breach;double max_shortfall;};
inline Path project(double initial,const std::vector<Flow>& flows){
 check(std::isfinite(initial)&&initial>=0&&!flows.empty(),"invalid projection");
 Path p{{},flows.size()+1,0};
 double cash=initial;
 for(std::size_t t=0;t<flows.size();++t){
  cash+=flows[t].inflow-flows[t].outflow-flows[t].margin;
  check(std::isfinite(cash),"cash overflow");
  p.cash.push_back(cash);
  if(cash<0&&p.first_breach==flows.size()+1)p.first_breach=t+1;
  p.max_shortfall=std::max(p.max_shortfall,-cash);
 }
 return p;
}
struct LiquidityResult {double breach_probability,mean_max_shortfall;};
class LiquidityEngine {
public:
 LiquidityResult run(std::size_t n,std::size_t horizon,double initial,std::uint64_t seed)const{
  check(n>1&&horizon>0,"invalid dimensions");
  std::mt19937_64 gen(seed);std::normal_distribution<double> normal(0,1);
  std::size_t breaches=0;double shortfall=0;
  for(std::size_t s=0;s<n;++s){
   std::vector<Flow> flows;flows.reserve(horizon);
   for(std::size_t t=0;t<horizon;++t){
    double z=normal(gen);
    flows.emplace_back(3.5,std::max(0.0,4+1.2*z),std::max(0.0,1.5*z));
   }
   auto path=project(initial,flows);
   breaches+=path.first_breach<=horizon;
   shortfall+=path.max_shortfall;
  }
  return {static_cast<double>(breaches)/n,shortfall/n};
 }
};
}

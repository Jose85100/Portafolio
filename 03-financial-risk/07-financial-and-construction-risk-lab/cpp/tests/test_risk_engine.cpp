#include "risk_engine.hpp"
#include <cassert>
#include <cmath>
#include <stdexcept>
int main() {
  using namespace construction_risk;
  auto path=cash_path(100,{80,80},{60,60},{10,10});
  assert(path.size()==2 && path[0]==110 && path[1]==120);
  assert(peak_shortfall(path,100)==0);
  assert(peak_shortfall(cash_path(0,{0},{100},{0}),0)==100);
  auto r=empirical_var_es({1,2,3,4,5},0.8);
  assert(r.var==4 && std::abs(r.es-4.5)<1e-12);
  bool caught=false;try {cash_path(0,{1},{1,2},{1});}catch(const std::invalid_argument&){caught=true;}
  assert(caught);
}

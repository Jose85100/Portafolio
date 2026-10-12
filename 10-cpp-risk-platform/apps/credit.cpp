#include "quant/risk.hpp"
#include <iostream>
#include <iomanip>
int main(int argc,char** argv){
 try{
  auto n=argc>1?std::stoull(argv[1]):100000ULL;
  quant::CreditEngine model({{0.02,0.4,1000,0.15},{0.05,0.6,2000,0.2},{0.1,0.3,500,0.1}});
  auto r=model.run(n,42);
  std::cout<<std::setprecision(10)<<"analytic_el="<<r.analytic_el<<"\nmc_el="<<r.mc_el
           <<"\nvar99="<<r.var<<"\nes99="<<r.es<<"\nstandard_error="<<r.standard_error<<"\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}

#include "quant/risk.hpp"
#include <iostream>
#include <string>
#include <iomanip>
int main(int argc,char** argv){
 try{
  auto n=argc>1?std::stoull(argv[1]):100000ULL;
  auto r=quant::LiquidityEngine{}.run(n,30,100,42);
  std::cout<<std::setprecision(10)<<"breach_probability="<<r.breach_probability
           <<"\nmean_max_shortfall="<<r.mean_max_shortfall<<"\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}

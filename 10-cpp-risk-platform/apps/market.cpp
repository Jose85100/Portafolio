#include "quant/risk.hpp"
#include <iostream>
#include <string>
#include <iomanip>
int main(int argc,char** argv){
 try{
  auto n=argc>1?std::stoull(argv[1]):100000ULL;
  auto r=quant::MarketEngine{}.run(n,42);
  std::cout<<std::setprecision(10)<<"var975="<<r.metrics.var<<"\nes975="<<r.metrics.es
           <<"\nmean_loss="<<r.metrics.mean<<"\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}

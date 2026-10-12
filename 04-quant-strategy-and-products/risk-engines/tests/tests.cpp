#include "quant/risk.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
int main(){
 using namespace quant;
 auto eq=[](double x,double y){return std::abs(x-y)<1e-8;};
 auto t=tail({0,0,10,20},0.625);
 assert(eq(t.es,25.0/1.5)&&t.es>=t.var);
 assert(std::abs(inverse_normal(0.5))<1e-8);
 assert(std::abs(0.5*std::erfc(-inverse_normal(0.01)/std::sqrt(2.0))-0.01)<1e-8);
 auto cr=CreditEngine({{0,0.5,100,0.1},{1,0.4,200,0.2}}).run(1000,12);
 assert(eq(cr.analytic_el,80)&&eq(cr.mc_el,80)&&eq(cr.es,80));
 auto m=MarketEngine{}.run(1000,42);
 assert(m.metrics.es>=m.metrics.var);
 auto bt=MarketEngine{}.backtest({1,2,3,4},{2,2,2,2},0.75);
 assert(bt.exceptions==2);
 assert(eq(kupiec(0,100,0.99),-200*std::log(0.99)));
 auto p=project(5,{{0,2,0},{0,4,0},{0,1,0}});
 assert(p.first_breach==2&&eq(p.max_shortfall,2));
 auto lr=LiquidityEngine{}.run(100,10,10,42);
 assert(lr.breach_probability>=0&&lr.breach_probability<=1);
 bool invalid=false;try{Loan x(-1,0.5,100,0.1);(void)x;}catch(const std::invalid_argument&){invalid=true;}
 assert(invalid);
 std::cout<<"all tests passed\n";
}

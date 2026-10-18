#include "risk_engine.hpp"
#include <cmath>
#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
void check(bool ok,const std::string& message){if(!ok)throw std::runtime_error(message);}
int main(){
 using namespace construction_risk;
 auto path=cash_path(100,{80,80},{60,60},{10,10});
 check(path.size()==2 && path[0]==110 && path[1]==120,"cash path");
 check(peak_shortfall(path,100)==0,"shortfall");
 check(peak_shortfall(cash_path(0,{0},{100},{0}),0)==100,"cash deficit");
 auto result=empirical_var_es({1,2,3,4,5},.8);
 check(result.var==4 && std::abs(result.es-5)<1e-12,"fractional ES");
 std::ifstream file(TAIL_FIXTURE_PATH);check(file.good(),"fixture missing");
 std::string line;std::getline(file,line);int cases=0;
 while(std::getline(file,line)){
   std::istringstream row(line);std::string a,v,e,losses;
   std::getline(row,a,',');std::getline(row,v,',');std::getline(row,e,',');std::getline(row,losses);
   std::istringstream values(losses);std::string value;std::vector<double>x;
   while(std::getline(values,value,';'))x.push_back(std::stod(value));
   auto r=empirical_var_es(x,std::stod(a));
   check(r.var==std::stod(v),"fixture VaR");check(std::abs(r.es-std::stod(e))<1e-9,"fixture ES");++cases;
 }
 check(cases==100,"fixture count");
 bool caught=false;try{cash_path(0,{std::numeric_limits<double>::quiet_NaN()},{1},{0});}catch(const std::invalid_argument&){caught=true;}
 check(caught,"nonfinite input accepted");
 std::cout<<"100 independent hinge-oracle fixtures and active Release checks passed\n";
}

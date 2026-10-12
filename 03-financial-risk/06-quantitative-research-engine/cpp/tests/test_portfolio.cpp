#include "risk/portfolio.hpp"
#include <cassert>
#include <cmath>
#include <stdexcept>
#include <vector>
int main(){
 using risk::Exposure;
 std::vector<Exposure> e{{0.1,0.5,100.0},{0.2,0.25,200.0}};
 assert(std::abs(risk::expected_loss(e)-15.0)<1e-12);
 assert(std::abs(risk::independent_variance(e)-625.0)<1e-12);
 std::vector<std::vector<double>> cov{{0.09,0.03},{0.03,0.16}};
 assert(std::abs(risk::correlated_variance(e,cov)-775.0)<1e-12);
 bool thrown=false;try{risk::expected_loss({{-0.1,0.5,100}});}catch(const std::invalid_argument&){thrown=true;}assert(thrown);
 thrown=false;try{risk::correlated_variance(e,{{0.09,0.5},{0.5,0.16}});}catch(const std::invalid_argument&){thrown=true;}
 return 0;
}

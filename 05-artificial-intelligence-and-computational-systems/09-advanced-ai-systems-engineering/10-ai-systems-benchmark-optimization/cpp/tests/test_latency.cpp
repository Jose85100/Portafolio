#include "ai_benchmark/latency.hpp"
#include <cassert>
#include <cmath>
#include <stdexcept>
int main(){
 auto s=ai_benchmark::summarize({10.,20.,30.,40.});
 assert(std::abs(s.mean_ms-25.)<1e-12);
 assert(std::abs(s.p50_ms-25.)<1e-12);
 assert(std::abs(s.p99_ms-39.7)<1e-10);
 assert(std::abs(s.throughput_per_sec-40.)<1e-12);
 bool rejected=false;try{ai_benchmark::summarize({0.});}catch(const std::invalid_argument&){rejected=true;}assert(rejected);
}

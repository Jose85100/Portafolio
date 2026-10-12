#pragma once
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <numeric>
#include <stdexcept>
#include <vector>
namespace ai_benchmark {
struct Summary { double mean_ms; double p50_ms; double p99_ms; double throughput_per_sec; };
inline Summary summarize(const std::vector<double>& durations_ms) {
 if(durations_ms.empty()) throw std::invalid_argument("empty measurements");
 auto v=durations_ms;long double total=0;
 for(double x:v){if(!std::isfinite(x)||x<=0)throw std::invalid_argument("duration must be finite and positive");total+=x;}
 std::sort(v.begin(),v.end());
 const auto quantile=[&](double p){double idx=p*static_cast<double>(v.size()-1);auto lo=static_cast<std::size_t>(std::floor(idx));auto hi=static_cast<std::size_t>(std::ceil(idx));return v[lo]+(idx-lo)*(v[hi]-v[lo]);};
 double mean=static_cast<double>(total/v.size());
 return {mean,quantile(.5),quantile(.99),1000.0/mean};
}
}

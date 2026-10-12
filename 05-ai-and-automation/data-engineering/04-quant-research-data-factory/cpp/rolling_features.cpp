// Compile: c++ -std=c++17 -O2 -Wall -Wextra -pedantic rolling_features.cpp -o rolling_features
// Input: asset,YYYY-MM-DD,close (unquoted CSV, sorted internally).
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Observation = std::pair<std::string, double>;
using PriceSeries = std::map<std::string, std::vector<Observation>>;

static PriceSeries read_prices(std::istream& input) {
    PriceSeries prices;
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty()) continue;
        const auto first = line.find(',');
        const auto second = line.find(',', first == std::string::npos ? first : first + 1);
        if (first == std::string::npos || second == std::string::npos ||
            line.find(',', second + 1) != std::string::npos)
            throw std::runtime_error("expected three columns");
        const std::string asset = line.substr(0, first);
        const std::string date = line.substr(first + 1, second - first - 1);
        const std::string value = line.substr(second + 1);
        std::size_t used = 0;
        const double close = std::stod(value, &used);
        if (asset.empty() || date.size() != 10 || used != value.size() ||
            !std::isfinite(close) || close <= 0)
            throw std::runtime_error("invalid price observation");
        prices[asset].emplace_back(date, close);
    }
    for (auto& [asset, rows] : prices) {
        (void)asset;
        std::sort(rows.begin(), rows.end());
        for (std::size_t i = 1; i < rows.size(); ++i)
            if (rows[i - 1].first == rows[i].first)
                throw std::runtime_error("duplicate asset/date");
    }
    return prices;
}

int main(int argc, char** argv) {
    try {
        if (argc != 4) throw std::invalid_argument("usage: rolling_features FILE LOOKBACK HORIZON");
        const auto lookback = std::stoull(argv[2]);
        const auto horizon = std::stoull(argv[3]);
        if (lookback == 0 || horizon == 0) throw std::invalid_argument("positive windows required");
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("cannot open file");
        const auto prices = read_prices(input);
        std::cout << std::setprecision(15)
                  << "asset,feature_date,momentum,target_end,forward_return\n";
        for (const auto& [asset, rows] : prices) {
            if (rows.size() <= horizon || lookback >= rows.size() - horizon) continue;
            for (std::size_t i = lookback; i + horizon < rows.size(); ++i) {
                std::cout << asset << ',' << rows[i].first << ','
                          << rows[i].second / rows[i - lookback].second - 1.0 << ','
                          << rows[i + horizon].first << ','
                          << rows[i + horizon].second / rows[i].second - 1.0 << '\n';
            }
        }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}

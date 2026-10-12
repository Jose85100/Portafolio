// Compile: c++ -std=c++17 -O2 -Wall -Wextra -pedantic loan_snapshot.cpp -o loan_snapshot
// Input: loan_id,YYYY-MM-DD,principal_cents,days_past_due (no quoted CSV fields).
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

struct LoanPosition {
    std::string date;
    std::int64_t cents;
    int days_past_due;
};
using Portfolio = std::map<std::string, LoanPosition>;

static std::vector<std::string> split(const std::string& line) {
    std::istringstream stream(line);
    std::vector<std::string> fields;
    std::string field;
    while (std::getline(stream, field, ',')) fields.push_back(field);
    return fields;
}

static bool valid_date(const std::string& date) {
    if (date.size() != 10 || date[4] != '-' || date[7] != '-') return false;
    for (std::size_t i = 0; i < date.size(); ++i) {
        if (i != 4 && i != 7 && (date[i] < '0' || date[i] > '9')) return false;
    }
    const int month = std::stoi(date.substr(5, 2));
    const int day = std::stoi(date.substr(8, 2));
    return month >= 1 && month <= 12 && day >= 1 && day <= 31;
}

static Portfolio load_snapshot(std::istream& in, const std::string& as_of) {
    if (!valid_date(as_of)) throw std::invalid_argument("invalid cutoff date");
    Portfolio portfolio;
    std::string line;
    std::size_t line_number = 0;
    while (std::getline(in, line)) {
        ++line_number;
        if (line.empty()) continue;
        const auto f = split(line);
        if (f.size() != 4 || f[0].empty() || !valid_date(f[1]))
            throw std::runtime_error("invalid input at line " + std::to_string(line_number));
        std::size_t consumed = 0;
        const auto cents = std::stoll(f[2], &consumed);
        if (consumed != f[2].size() || cents < 0)
            throw std::runtime_error("invalid principal cents");
        consumed = 0;
        const int dpd = std::stoi(f[3], &consumed);
        if (consumed != f[3].size() || dpd < 0)
            throw std::runtime_error("invalid delinquency");
        if (f[1] > as_of) continue;
        const LoanPosition current{f[1], cents, dpd};
        auto it = portfolio.find(f[0]);
        if (it != portfolio.end() && it->second.date == current.date &&
            std::tie(it->second.cents, it->second.days_past_due) !=
                std::tie(current.cents, current.days_past_due))
            throw std::runtime_error("conflicting same-date records: " + f[0]);
        if (it == portfolio.end() || it->second.date < current.date)
            portfolio[f[0]] = current;
    }
    return portfolio;
}

int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::invalid_argument("usage: loan_snapshot FILE YYYY-MM-DD");
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("cannot open input");
        const auto loans = load_snapshot(input, argv[2]);
        std::int64_t total = 0;
        std::cout << "loan_id,as_of_date,principal_cents,days_past_due\n";
        for (const auto& [id, row] : loans) {
            if (row.cents > INT64_MAX - total) throw std::overflow_error("balance overflow");
            total += row.cents;
            std::cout << id << ',' << row.date << ',' << row.cents << ','
                      << row.days_past_due << '\n';
        }
        std::cerr << "loans=" << loans.size() << " principal_cents=" << total << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}

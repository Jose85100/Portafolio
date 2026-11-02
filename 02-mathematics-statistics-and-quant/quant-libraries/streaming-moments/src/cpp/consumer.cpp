#include "moments.hpp"
#include <iostream>
int main(int argc, char** argv) {
    try {
        if(argc!=2 || (std::string(argv[1])!="0" && std::string(argv[1])!="1"))
            throw std::invalid_argument("usage: moments_consumer ddof(0|1)");
        std::string a,b,extra;
        if(!std::getline(std::cin,a) || !std::getline(std::cin,b)) throw std::invalid_argument("two summaries required");
        while(std::getline(std::cin,extra)) if(extra.find_first_not_of(" \t\r")!=std::string::npos)
            throw std::invalid_argument("extra input");
        const auto s=moments::merge(moments::parse(a),moments::parse(b));
        const auto result=moments::result_json(s,std::stoi(argv[1]));
        std::cout<<moments::encode(s)<<'\n'<<result<<'\n';
    } catch(const std::exception& e) { std::cerr<<"error: "<<e.what()<<'\n'; return 2; }
}

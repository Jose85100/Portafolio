#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace moments {
static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits==53, "binary64 required");
constexpr std::uint64_t max_count = (std::uint64_t{1} << 53) - 1;
struct Summary {std::uint64_t n{}; int e{}; double a{}, b{}, q{}; bool initialized{};};
inline void validate(const Summary& s) {
    if (s.n > max_count || s.e < -1073 || s.e > 1024 ||
        !std::isfinite(s.a) || !std::isfinite(s.b) || !std::isfinite(s.q) ||
        std::abs(s.a)>1 || std::abs(s.b)>2 || s.q<0 || s.q>4*static_cast<double>(s.n))
        throw std::invalid_argument("invalid normalized state");
    if ((!s.initialized || s.n==0) && (s.initialized || s.e!=0 || s.a!=0 || s.b!=0 || s.q!=0))
        throw std::invalid_argument("inconsistent zero/empty state");
}
inline double parse_double(const std::string& s) {
    if (s.find("0x")==std::string::npos || s.find('p')==std::string::npos)
        throw std::invalid_argument("hex float required");
    char* end=nullptr;
    const double x=std::strtod(s.c_str(), &end);
    if (end!=s.c_str()+s.size() || !std::isfinite(x)) throw std::invalid_argument("invalid float");
    return x;
}
inline Summary parse(const std::string& line) {
    std::istringstream in(line); std::vector<std::string> fields; std::string token;
    while(in>>token) fields.push_back(token);
    if (fields.size()!=7 || fields[0]!="MOMENTS_V1" || (fields[6]!="0" && fields[6]!="1"))
        throw std::invalid_argument("invalid protocol");
    auto integer=[](const std::string& x) {
        std::size_t used=0; const long long result=std::stoll(x,&used);
        if (used!=x.size()) throw std::invalid_argument("invalid integer");
        return result;
    };
    const auto n=integer(fields[1]); const auto e=integer(fields[2]);
    if(n<0 || n>static_cast<long long>(max_count) || e < -1073 || e >1024)
        throw std::invalid_argument("integer range");
    Summary s{static_cast<std::uint64_t>(n),static_cast<int>(e),parse_double(fields[3]),
              parse_double(fields[4]),parse_double(fields[5]),fields[6]=="1"};
    validate(s); return s;
}
inline std::string encode(const Summary& s) {
    validate(s); std::ostringstream out;
    out<<"MOMENTS_V1 "<<s.n<<' '<<s.e<<' '<<std::hexfloat<<s.a<<' '<<s.b<<' '<<s.q<<' '<<s.initialized;
    return out.str();
}
inline Summary rebase(Summary s, int e) {
    const int shift=s.e-e;
    s.a=std::ldexp(s.a,shift); s.b=std::ldexp(s.b,shift); s.q=std::ldexp(s.q,2*shift); s.e=e;
    return s;
}
inline Summary merge(Summary a, Summary b) {
    validate(a); validate(b);
    if(a.n==0) return b;
    if(b.n==0) return a;
    if(a.n>max_count-b.n) throw std::invalid_argument("merged count exceeds exact integer domain");
    const int e=a.initialized ? (b.initialized ? std::max(a.e,b.e) : a.e) : (b.initialized ? b.e : 0);
    a=rebase(a,e); b=rebase(b,e);
    const double n=static_cast<double>(a.n+b.n), an=static_cast<double>(a.n), bn=static_cast<double>(b.n);
    const double delta=(b.a-a.a)+(b.b-a.b);
    Summary result{a.n+b.n,e,a.a,a.b+delta*(bn/n),a.q+b.q+delta*delta*(an*bn/n),a.initialized||b.initialized};
    validate(result); return result;
}
inline std::string result_json(const Summary& s, int ddof) {
    if((ddof!=0 && ddof!=1) || s.n<=static_cast<std::uint64_t>(ddof))
        throw std::invalid_argument("invalid ddof/count");
    const double v=s.q/static_cast<double>(s.n-static_cast<std::uint64_t>(ddof));
    const double sd=std::ldexp(std::sqrt(v),s.e), variance=std::ldexp(v,2*s.e);
    std::string status="ok";
    if(!std::isfinite(sd)) status="std_overflow";
    else if(sd==0 && v>0) status="std_underflow";
    else if(!std::isfinite(variance)) status="variance_overflow";
    else if(variance==0 && v>0) status="variance_underflow";
    std::ostringstream out; out<<std::setprecision(17)<<"{\"status\":\""<<status<<"\",\"std\":";
    if(status=="std_overflow" || status=="std_underflow") out<<"null"; else out<<sd;
    out<<",\"variance\":";
    if(status=="ok" || status=="variance_underflow") out<<variance; else out<<"null";
    out<<'}'; return out.str();
}
}

#include "moments.hpp"
#include <iostream>
void check(bool condition) {if(!condition) throw std::runtime_error("test failed");}
int main() {
    using namespace moments;
    const auto a=parse("MOMENTS_V1 2 2 0x1p-2 0x1p-3 0x1p-5 1");
    const auto b=parse("MOMENTS_V1 2 3 0x1.8p-2 0x1p-4 0x1p-7 1");
    const auto merged=merge(a,b);
    check(merged.n==4); check(std::abs(merged.q/4*64-1.25)<1e-14);
    check(parse(encode(merged)).q==merged.q);
    check(merge(Summary{},a).n==2);
    check(merge(Summary{3,0,0,0,0,false},Summary{1,-1073,.5,0,0,true}).e==-1073);
    int rejected=0;
    for(const auto& text:{"MOMENTS_V2 1 0 0x0p+0 0x0p+0 0x0p+0 0", "MOMENTS_V1 -1 0 0x0p+0 0x0p+0 0x0p+0 0", "MOMENTS_V1 2 0 0x0p+0 0x0p+0 -0x1p+0 1", "MOMENTS_V1 2 0 nan 0x0p+0 0x0p+0 1"}) {
        try {parse(text);} catch(const std::exception&) {++rejected;}
    }
    check(rejected==4);
    try {merge(Summary{max_count,0,0,0,0,false},Summary{1,0,0,0,0,false}); return 1;} catch(const std::exception&) {}
    std::cout<<"core: counts, roundtrip, zero/subnormal, rejection, overflow passed\n";
}

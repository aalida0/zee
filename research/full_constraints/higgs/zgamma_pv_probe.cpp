// Read-only LoopTools 2.13 probe; outputs PV coefficients, never a decay width.
#include "Herwig/Looptools/clooptools.h"
#include <iostream>
#include <iomanip>
using namespace Herwig::Looptools;
int main() {
  ltini("/tmp/zee-zgamma-looptools.log");
  std::cout << std::setprecision(17);
  double s,t,a,b,uv,mu;
  while (std::cin >> s >> t >> a >> b >> uv >> mu) {
    setdelta(uv); setmudim(mu); clearcache();
    auto db=B0(s,a,b)-B0(t,a,b);
    auto cp=C0(t,0,s,a,a,b), cr=C0(t,0,s,b,a,a);
    auto k=C0i(cc12,t,0,s,a,b,b)+C0i(cc22,t,0,s,a,b,b)+C0i(cc2,t,0,s,a,b,b);
    auto c00=C0i(cc00,t,0,s,a,b,b);
    auto bs=B0(s,a,b);
    std::cout << "PV";
    for (auto z: {db,cp,cr,k,c00,bs}) std::cout << ' ' << z.real() << ' ' << z.imag();
    std::cout << '\n';
  }
  ltexi("/tmp/zee-zgamma-looptools.log");
}

// Restricted R2HDM control on a saved Zee card. Output is NOT a Zee total width.
#include "AnyHdecay.hpp"
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
int main(int argc,char **argv) {
  if(argc!=9) return 2;
  using namespace AnyHdecay;
  SMParameters p;
  p.alphaS=.118; p.mS=.0935; p.mC=1.273; p.mB=4.183; p.mT=172.4;
  p.mTau=1.77686; p.mMu=.1056583755; p.invAlpha=137.035999084;
  p.GF=1/(std::sqrt(2.)*std::pow(246.21965,2));p.mW=80.379;p.mZ=91.1876;
  // remaining W/Z widths and CKM entries are the pinned library defaults.
  Hdecay h(p);
  auto result=h.r2hdm(Yukawa::typeII,TanBeta{std::atof(argv[1])},
    SquaredMassPar{std::atof(argv[2])},AMass{std::atof(argv[3])},HcMass{std::atof(argv[4])},
    HMass{std::atof(argv[5])},HMass{std::atof(argv[6])},MixAngle{std::atof(argv[7])});
  std::cout << std::setprecision(17);
  for(const auto &[key,value]:result) std::cout<<key<<" "<<value<<"\n";
  // SM reference at the same heavy mass checks transferable vector/fermion scaling.
  if(std::atoi(argv[8])) for(const auto &[key,value]:h.sm(HMass{std::atof(argv[5])}))
    std::cout<<"SM_"<<key<<" "<<value<<"\n";
}

// Matched 125 GeV SM reference only. Same inputs as the saved HDECAY receipts.
#include "AnyHdecay.hpp"
#include <cmath>
#include <iomanip>
#include <iostream>
extern "C" double runm_hdec_(double*, int*);
int main() {
  using namespace AnyHdecay;
  SMParameters p;
  p.alphaS=.118; p.mS=.0935; p.mC=1.273; p.mB=4.183; p.mT=172.4;
  p.mTau=1.77686; p.mMu=.1056583755; p.invAlpha=137.035999084;
  p.GF=1/(std::sqrt(2.)*std::pow(246.21965,2)); p.mW=80.379; p.mZ=91.1876;
  Hdecay h(p);
  std::cout << std::setprecision(17);
  for(const auto &[key,value]:h.sm(HMass{125.}))
    std::cout << key << " " << value << "\n";
  double scale=1.273; int flavour=4;
  double at_mc=runm_hdec_(&scale,&flavour);
  double mc3=p.mC*1.273/at_mc;
  std::cout << "diagnostic_mc_at_1p273 " << at_mc << "\n";
  std::cout << "converted_mc3 " << mc3 << "\n";
  p.mC=mc3;
  Hdecay corrected(p);
  for(const auto &[key,value]:corrected.sm(HMass{125.}))
    std::cout << "corrected_" << key << " " << value << "\n";
}

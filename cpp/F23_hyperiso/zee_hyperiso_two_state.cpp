// F23: REAL HyperIso v1.0.3 C++ matching-patch two charged Zee B->Xs gamma.
// One Type-II charged scalar H1 is the native THDM baseline.  For EACH
// perturbative order/operator, add sin^2(gamma)*(C(H2)-C(H1)) to native
// BSM matching. The matching manager then builds TOTAL and evolves
// through the original HyperIso B/BR observable (not BR averaging).
// CP-conserving Type-II quark sector only; NO 2026 NNLO likelihood/CL.
#include <cmath>
#include <complex>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
#include "HyperisoMaster.h"
#include "ObservableInterface.h"
#include "WilsonMatchingPatch.h"
#include "Math.h"
#include "Logger.h"

namespace {
struct Input {
  double light, heavy, tanb, gamma;
};
bool finite(double v) { return std::isfinite(v); }
bool nonzero(WCoef c, QCDOrder o) {
  if(c==WCoef::C7 || c==WCoef::C8) return true;
  if(c==WCoef::C4) return o != QCDOrder::LO;
  return o == QCDOrder::NNLO;
}
double thdm_coeff(WCoef c, QCDOrder order, double mass,
                  double tanb, double running_mt, double muW) {
  if(!(mass>0 && tanb>0 && running_mt>0 && muW>0))
    throw std::invalid_argument("invalid THDM matching scales/mass/tanbeta");
  const double lu=1./tanb, ld=-tanb, y=std::pow(running_mt/mass,2);
  const double L=2.*std::log(muW/mass);
  const double Lt=2.*std::log(muW/running_mt);
  if(c==WCoef::C3 && order==QCDOrder::NNLO)
    return G3H(y,lu)+Delta3H(y,lu)*L;
  if(c==WCoef::C4 && order==QCDOrder::NLO)
    return EH(y,lu);
  if(c==WCoef::C4 && order==QCDOrder::NNLO)
    return G4H(y,lu)+Delta4H(y,lu)*L;
  if(c==WCoef::C5 && order==QCDOrder::NNLO)
    return -(G3H(y,lu)+Delta3H(y,lu)*L)/10. + 2.*EH(y,lu)/15.;
  if(c==WCoef::C6 && order==QCDOrder::NNLO)
    return -3.*(G3H(y,lu)+Delta3H(y,lu)*L)/16. + EH(y,lu)/4.;
  if(c==WCoef::C7) {
    if(order==QCDOrder::LO)
      return lu*lu*F7_1(y)/3. - lu*ld*F7_2(y);
    if(order==QCDOrder::NLO)
      return G7H(y,lu,ld)+Delta7H(y,lu,ld)*L - 4.*EH(y,lu)/9.;
    if(order==QCDOrder::NNLO)
      return C7H2(y,lu,ld,Lt);
  }
  if(c==WCoef::C8) {
    if(order==QCDOrder::LO)
      return lu*lu*F8_1(y)/3. - lu*ld*F8_2(y);
    if(order==QCDOrder::NLO)
      return G8H(y,lu,ld)+Delta8H(y,lu,ld)*L - EH(y,lu)/6.;
    if(order==QCDOrder::NNLO)
      return C8H2(y,lu,ld,Lt);
  }
  return 0.;
}
void validate(Input p) {
  if(!finite(p.light)||!finite(p.heavy)||!finite(p.tanb)||!finite(p.gamma)||
     p.light<180 || p.heavy<180 || p.tanb<=0 ||
     p.gamma<0 || p.gamma>std::acos(-1.)/2)
    throw std::invalid_argument("Invalid physical benchmark for Type-II matching");
}
} // namespace

int main(int argc,char**argv) {
  try {
    if(argc!=6) {
      std::cerr<<"Usage: zee_hyperiso_two_state THDM_SPECTRUM_LHA mH1 mH2 tanbeta gamma_rad\n";
      return 2;
    }
    const std::string input=argv[1];
    const Input p{std::stod(argv[2]),std::stod(argv[3]),
                  std::stod(argv[4]),std::stod(argv[5])};
    validate(p);
    const double heavy_weight=std::pow(std::sin(p.gamma),2);
    Logger::getInstance()->setLevel(Logger::LogLevel::WARN);
    HyperisoConfig config;
    config.model=Model::THDM; // SM-only path discards explicit BSM patches.
    // We intentionally pass a source-pinned 2HDMC THDM spectrum with
    // MASS[37], UCOUPL/DCOUPL and Type-II YU/YD already populated.
    // DO NOT invoke 2HDMC again or silently regenerate another spectrum.
    config.flags[ExternalFlag::IS_LHA_SPECTRUM]=true;
    config.flags[ExternalFlag::HAS_WILSON_INPUT]=false;
    config.flags[ExternalFlag::HAS_TH_OBSERVABLE_INPUT]=false;
    HyperisoMaster core;
    core.init(input,config);
    ObservableInterface observable;
    // Install BSM patches before activating the observable.  The
    // coefficient manager adds the correction to native H1 THDM BSM
    // matching and keeps the usual SM+BSM composition and RG running.
    int installed=0;
    for(auto coeff : {WCoef::C3,WCoef::C4,WCoef::C5,WCoef::C6,
                       WCoef::C7,WCoef::C8}) {
      for(auto order : {QCDOrder::LO,QCDOrder::NLO,QCDOrder::NNLO}) {
        if(!nonzero(coeff,order)) continue;
        WilsonMatchingPatch patch;
        patch.group=GroupMapper::to_id(WGroup::B);
        patch.coefficient=WCoefMapper::to_id(coeff);
        patch.order=order;
        patch.contribution=ContributionType::BSM;
        patch.sources={
          ParamId{ParameterType::WILSON,"WPARAM_MATCH_SM",LhaID(6)},
          ParamId{ParameterType::WILSON,"EW_SCALE",LhaID(1)}
        };
        patch.compute=[=](const ParamSrc& s)->scalar_t {
          const double mt=s.get_val(ParameterType::WILSON,"WPARAM_MATCH_SM",6);
          const double Q=s.get_val(ParameterType::WILSON,"EW_SCALE",1);
          const double c1=thdm_coeff(coeff,order,p.light,p.tanb,mt,Q);
          const double c2=thdm_coeff(coeff,order,p.heavy,p.tanb,mt,Q);
          const double delta=heavy_weight*(c2-c1);
          if(!finite(delta))throw std::runtime_error("F23 nonfinite matching correction");
          return scalar_t(delta);
        };
        patch.label="F23_two_state_TypeII_"+WCoefMapper::str(coeff)+"_"+OrderMapper::str(order);
        patch.marty_only=false;
        observable.add_matching_patch(patch);
        ++installed;
      }
    }
    // C3(1)+C4(2)+C5(1)+C6(1)+C7(3)+C8(3) = 11
    if(installed!=11)throw std::runtime_error("Wrong number of F23 matching patches");

    observable.add_observable(Observables::BR_B_XS_GAMMA,QCDOrder::NNLO);
    auto result=observable.compute_observable(Observables::BR_B_XS_GAMMA);
    if(result.size()!=1)
      throw std::runtime_error("HyperIso returned wrong number of B->Xs gamma results");
    const double br=std::real(result.at(0).value);
    if(!finite(br) || br<0 || br>0.1)
      throw std::runtime_error("HyperIso returned implausible or nonfinite BR");
    std::cout<<std::setprecision(17)
      <<"F23_HYPERISO_V103_TWO_STATE_CONDITIONAL"
      <<" BR_B_XS_GAMMA "<<br
      <<" mH1 "<<p.light<<" mH2 "<<p.heavy
      <<" tanbeta "<<p.tanb<<" gamma "<<p.gamma
      <<" wH1 "<<1.-heavy_weight<<" wH2 "<<heavy_weight
      <<" n_patches "<<installed
      <<" FULL_MODEL_ALLOWED UNKNOWN"
      <<std::endl;
    return 0;
  }catch(const std::exception& exc){
    std::cerr<<"F23_HYPERISO_FAILURE "<<exc.what()<<"\n";
    return 1;
  }
}

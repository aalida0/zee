// Gate B audit client; links the unmodified pinned release, never implements kernels.
#include <iomanip>
#include <iostream>
#include "CliUtils.h"
#include "WilsonInterface.h"
#include "QCDHelper.h"

int main(int argc, char** argv) {
    const auto opts = CliOptions::parse(argc, argv, 1);
    auto hyp = init_hyperiso_from_cli(opts);
    init_all_builtins();
    WilsonInterface w;
    w.build(WilsonBuildConfig({GroupMapper::to_id(WGroup::B)}, 160., 160., QCDOrder::LO));
    std::cout << std::setprecision(17);
    std::cout << "GATE_B mt " << QCDHelper::msbar_mass(6,160.,MassType::MSBAR) << '\n';
    for (const auto name : {"C1","C2","C3","C4","C5","C6","C7","C8"}) {
        auto g=GroupMapper::to_id(WGroup::B);
        auto c=WCoefMapper::id_of(name);
        std::cout << "GATE_B " << name << ' '
                  << w.getFM(g,c,QCDOrder::LO,ContributionType::SM) << ' '
                  << w.getFM(g,c,QCDOrder::LO,ContributionType::BSM) << ' '
                  << w.getFM(g,c,QCDOrder::LO,ContributionType::TOTAL) << '\n';
    }
    if (opts.flag("patch-probe",false)) {
        // Nonphysical API test values, never interpreted as Zee Yukawas or BR.
        auto g=GroupMapper::to_id(WGroup::B);
        auto c=WCoefMapper::id_of("C7");
        const auto before=w.getFM(g,c,QCDOrder::LO,ContributionType::BSM);
        WilsonMatchingPatch patch;
        patch.group=g;patch.coefficient=c;patch.contribution=ContributionType::BSM;
        patch.compute=[](const ParamSrc&) -> scalar_t {
            return complex_t(0.001,0.002)+complex_t(-0.003,0.004);
        };
        patch.label="GateB:nonphysical-complex-API-test";
        w.addMatchingPatch(patch);
        std::cout << "GATE_B PATCH "
                  << w.getFM(g,c,QCDOrder::LO,ContributionType::BSM)-before << '\n';
    }
}

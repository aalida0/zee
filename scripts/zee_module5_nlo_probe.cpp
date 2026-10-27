// Gate C2 external client: unmodified native matching, no patches or decay calls.
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
    w.build(WilsonBuildConfig({GroupMapper::to_id(WGroup::B)},160.,160.,QCDOrder::NLO));
    std::cout << std::setprecision(17);
    std::cout << "C2 mt " << QCDHelper::msbar_mass(6,160.,MassType::MSBAR) << '\n';
    std::cout << "C2 alpha_s " << QCDHelper::alpha_s(160.) << '\n';
    for (const auto name : {"C1","C2","C3","C4","C5","C6","C7","C8"}) {
        const auto g=GroupMapper::to_id(WGroup::B);
        const auto c=WCoefMapper::id_of(name);
        std::cout << "C2 " << name << ' '
                  << w.getM(g,c,QCDOrder::LO,ContributionType::BSM) << ' '
                  << w.getM(g,c,QCDOrder::NLO,ContributionType::BSM) << ' '
                  << w.getFM(g,c,QCDOrder::LO,ContributionType::BSM) << ' '
                  << w.getFM(g,c,QCDOrder::NLO,ContributionType::BSM) << '\n';
    }
}

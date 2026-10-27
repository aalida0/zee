// External v1.0.3 client. No kernels, observable, or upstream modifications.
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include "CliUtils.h"
#include "WilsonInterface.h"
#include "QCDHelper.h"

int main(int argc, char** argv) {
    try {
        const auto o = CliOptions::parse(argc, argv, 1);
        const auto mode = o.get("mode", "patch");
        if (mode != "patch" && mode != "native" && mode != "diagnostic")
            throw std::runtime_error("Unknown mode");
        const bool patch = mode != "native";
        if (o.get("model") != (mode == "patch" ? "SM" : "THDM"))
            throw std::runtime_error("Production requires SM; THDM is diagnostic/native only (double-count risk)");
        if (o.get("contribution") != "BSM" || o.get("order") != "LO" ||
            o.get("top-scheme") != "MSBAR_AT_QMATCH" || o.get_double("qmatch", 0.) != 160.)
            throw std::runtime_error("Require BSM, LO, qmatch=160, MSBAR_AT_QMATCH");
        const double qh = o.get_double("qhad", 0.);
        if (!std::isfinite(qh) || qh <= 0.) throw std::runtime_error("Explicit positive qhad required");
        auto hyp = init_hyperiso_from_cli(o);
        init_all_builtins();
        WilsonInterface w;
        const auto g = GroupMapper::to_id(WGroup::B);
        w.build(WilsonBuildConfig({g}, 160., qh, QCDOrder::LO));
        const double mt = QCDHelper::msbar_mass(6, 160., MassType::MSBAR);
        std::cout << std::setprecision(17) << "C0 MT " << mt << '\n';
        if (patch && (!std::isfinite(o.get_double("mt", 0.)) ||
                      std::abs(o.get_double("mt", 0.) - mt) > 2e-12))
            throw std::runtime_error("Top mass differs from native QCDHelper MSbar(160)");
        auto emit = [&](const char* stage) {
            for (const auto name : {"C1","C2","C3","C4","C5","C6","C7","C8"}) {
                const auto c = WCoefMapper::id_of(name);
                for (const auto cont : {ContributionType::SM,ContributionType::BSM,ContributionType::TOTAL}) {
                    std::cout << "C0 " << stage << ' ' << name << ' ' << static_cast<int>(cont)
                              << ' ' << w.getFM(g,c,QCDOrder::LO,cont)
                              << ' ' << w.getFR(g,c,QCDOrder::LO,cont,WilsonBasis::B_STANDARD) << '\n';
                }
            }
        };
        emit("BEFORE");
        if (!patch) return 0;
        complex_t shifts[2];
        for (int i=0; i<2; ++i) {
            const std::string key = i == 0 ? "c7" : "c8";
            if (!o.has(key) || !o.has(key+"-imag")) throw std::runtime_error("Explicit signed dipoles required");
            const double re=o.get_double(key,0.), im=o.get_double(key+"-imag",0.);
            if (!std::isfinite(re) || !std::isfinite(im)) throw std::runtime_error("Nonfinite dipole");
            if (mode == "patch" && im != 0.) throw std::runtime_error("Physical frozen quark coefficients must be real");
            shifts[i] = complex_t(re,im);
            const bool split=o.flag("split",false);
            if (split && mode != "diagnostic") throw std::runtime_error("Split is diagnostic only");
            for (int j=0; j<(split ? 2 : 1); ++j) {
                WilsonMatchingPatch p;
                p.group=g;p.coefficient=WCoefMapper::id_of(i==0 ? "C7" : "C8");
                p.order=QCDOrder::LO;p.contribution=ContributionType::BSM;
                const auto value=shifts[i]*(split ? (j==0 ? .25 : .75) : 1.);
                p.compute=[value](const ParamSrc&) -> scalar_t { return value; };
                p.label="C0:BSM:LO:"+key;
                w.addMatchingPatch(p);
            }
        }
        emit("AFTER");
        double residual=0.;
        for (int i=0;i<2;++i) {
            const auto c=WCoefMapper::id_of(i==0 ? "C7" : "C8");
            // Production SM has no native BSM. Reject a silently discarded patch.
            residual=std::max(residual,std::abs(complex_t(w.getFM(g,c,QCDOrder::LO,ContributionType::BSM))-shifts[i]));
        }
        if (mode=="patch") {
            std::cerr << "HYPERISO_PATCH_INTEGRATION_BLOCKED_SM_BSM_PATCH_DROPPED residual=" << std::setprecision(17) << residual << '\n';
            return 3;
        }
        std::cout << "C0 " << (mode=="patch" ? "INJECTION_PRESENT" : "DIAGNOSTIC_ONLY_NOT_ZEE_ADAPTER") << '\n';
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "C0 REJECTED " << e.what() << '\n';return 2;
    }
}

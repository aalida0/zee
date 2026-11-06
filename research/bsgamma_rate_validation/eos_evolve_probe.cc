// SPDX-License-Identifier: GPL-2.0-only
// Calls the unmodified EOS library; no anomalous-dimension code copied.
#include <eos/models/wilson-coefficients.hh>
#include <eos/utils/qcd.hh>
#include <array>
#include <complex>

extern "C" void zee_evolve(const double * c0, const double * c1,
                            const double * c2, double as0, double asb,
                            double * output)
{
    std::array<std::complex<double>, 15> a{}, b{}, c{};
    for (unsigned i = 0; i < 15; ++i) { a[i] = c0[i]; b[i] = c1[i]; c[i] = c2[i]; }
    const double nf = 5;
    auto w = eos::evolve(a, b, c, as0, asb, nf, eos::QCD::beta_function_nf_5);
    for (unsigned i = 0; i < 15; ++i) {
        output[i] = w._sm_like_coefficients[i].real();
        output[i + 15] = w._sm_like_coefficients[i].imag();
    }
}

extern "C" double zee_alpha_s(double mu, double as_ref, double mu_ref)
{
    return eos::QCD::alpha_s(mu, as_ref, mu_ref, eos::QCD::beta_function_nf_5);
}

#include <eos/models/model.hh>
#include <eos/rare-b-decays/inclusive-b-to-s-gamma.hh>
#include <eos/utils/diagnostics.hh>
#include <string>

extern "C" int zee_sm(double scale, double * output)
{
    try {
        auto p = eos::Parameters::Defaults();
        auto model = eos::Model::make(eos::qnp::OptionValue("SM"), p, eos::Options{});
        auto w = model->wilson_coefficients_b_to_s(scale, eos::LeptonFlavor::muon);
        std::array<std::complex<double>, 8> c{w.c1(), w.c2(), w.c3(), w.c4(), w.c5(), w.c6(), w.c7(), w.c8()};
        for (unsigned i = 0; i < 8; ++i) { output[i] = c[i].real(); output[i + 8] = c[i].imag(); }
        output[16] = model->alpha_s(scale);
        output[17] = model->m_t_msbar(scale);
        return 0;
    } catch (...) { return 1; }
}

extern "C" int zee_rate_diagnostics(const char ** keys, const double * values,
                                     unsigned n, double * output)
{
    try {
        auto p = eos::Parameters::Defaults();
        for (unsigned i = 0; i < n; ++i) p[std::string(keys[i])] = values[i];
        eos::Options opts{{eos::qnp::OptionKey("model"), eos::qnp::OptionValue("WET")}};
        eos::BToXsGamma<eos::NLO> rate(p, opts);
        unsigned i = 0;
        for (const auto & entry : rate.diagnostics()) {
            if (entry.description.find("R_quark") != std::string::npos) output[i++] = entry.value;
        }
        return i == 2 ? 0 : 2;
    } catch (...) { return 1; }
}

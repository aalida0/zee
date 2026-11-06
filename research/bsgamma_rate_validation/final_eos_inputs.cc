// SPDX-License-Identifier: GPL-2.0-only
// Inspect the unchanged model's derived inputs, without a custom rate kernel.
#include <eos/models/model.hh>
#include <eos/utils/parameters.hh>
#include <cmath>
#include <string>
extern "C" int final_eos_inputs(const char **keys, const double *values,
                                  unsigned n, double scale, double *out) {
    try {
        auto p = eos::Parameters::Defaults();
        for(unsigned i=0;i<n;i++) p[std::string(keys[i])] = values[i];
        auto m = eos::Model::make(eos::qnp::OptionValue("SM"),p,eos::Options{});
        out[0]=m->alpha_s(scale);out[1]=m->m_b_msbar(scale);
        out[2]=m->m_b_pole();out[3]=m->m_b_kin(1.0);out[4]=m->m_c_msbar(scale);
        out[5]=std::norm(m->ckm_tb()*std::conj(m->ckm_ts()));
        return 0;
    } catch (...) {return 1;}
}

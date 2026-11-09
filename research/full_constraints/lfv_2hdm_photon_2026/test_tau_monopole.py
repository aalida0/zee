"""Restricted published neutral-tau photon monopole source controls."""
import copy
import math
import unittest

import numpy as np

from module2.interface import decode
from research.full_constraints.lfv_2hdm_photon_2026.tau_monopole import (
    card_inputs, paper_prefactor, source_tau_monopole, source_y2_independent,
)


def close(a,b,rtol=1e-11):
    if abs(a-b)>rtol*max(abs(a),abs(b),1.e-80):
        raise AssertionError((a,b,abs(a-b)))


class TestPublishedTauPhoton(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards=card_inputs()

    def test_four_cards_independent_yukawa_form(self):
        for w in self.cards:
            x=source_tau_monopole(w)
            y=source_y2_independent(w)
            for k in ("gLV","gRV"):
                close(x[k],y[k])

    def test_chirality_is_not_symmetrized(self):
        w=copy.deepcopy(self.cards[0])
        original=source_tau_monopole(w)
        D=decode(w["yukawas"]["D"])
        Ye2=decode(w["yukawas"]["Ye2"])
        # Change the SOURCE LEPTON tau-row -> mu column, only.
        D[2,1]=0j
        Ye2[2,1]=0j
        w["yukawas"]["D"]={"real":D.real.tolist(),"imag":D.imag.tolist()}
        w["yukawas"]["Ye2"]={"real":Ye2.real.tolist(),"imag":Ye2.imag.tolist()}
        new=source_tau_monopole(w)
        self.assertEqual(new["gLV"],0j)
        close(new["gRV"],original["gRV"])

    def test_pure_2hdm_no_F_or_gamma_dependence(self):
        for w in self.cards:
            x=source_tau_monopole(w)
            a=copy.deepcopy(w)
            a["yukawas"]["F"]={"real":[[0.]*3 for _ in range(3)],
                                "imag":[[0.]*3 for _ in range(3)]}
            a["module2_input"]["scalar"]["record"]["physical"]["gamma"]+=.381
            y=source_tau_monopole(a)
            self.assertEqual(x,y)

    def test_native_lepton_field_rephasing(self):
        for w in self.cards:
            x=source_tau_monopole(w)
            a=copy.deepcopy(w)
            phases=np.exp(1j*np.array([.23,-.57,.31]))
            P=np.diag(phases)
            for matrix in ("D","Ye2"):
                M=decode(a["yukawas"][matrix])
                M=P.conjugate()@M@P
                a["yukawas"][matrix]={"real":M.real.tolist(),"imag":M.imag.tolist()}
            y=source_tau_monopole(a)
            # D_{tau mu} D_{tau e}* -> P_mu P_e*
            relative=phases[1]*phases[0].conjugate()
            close(y["gLV"],relative*x["gLV"])
            close(y["gRV"],relative*x["gRV"])
            yi=source_y2_independent(a)
            close(y["gLV"],yi["gLV"])
            close(y["gRV"],yi["gRV"])

    def test_physical_scalar_mass_suppression(self):
        for w in self.cards:
            a=copy.deepcopy(w)
            p=a["module2_input"]["scalar"]["record"]["physical"]
            x=source_tau_monopole(a)
            p["mh1"]*=2;p["mh2"]*=2;p["ma"]*=2
            y=source_tau_monopole(a)
            self.assertLess(abs(y["gLV"]),abs(x["gLV"]))
            self.assertLess(abs(y["gRV"]),abs(x["gRV"]))

    def test_prefactor_small_mass_ratio_sign(self):
        a=paper_prefactor(1.77686,500.)
        self.assertGreater(a,0)
        # Source Eq(3.25) has a 4+3 log, not the radiative dipole loop.
        close(a,-1/137.035999084/(18*math.pi*500**2)*
              (4+3*math.log((1.77686/500)**2)))

    def test_sum_h_H_A_and_no_common_operator_claim(self):
        for w in self.cards:
            out=source_tau_monopole(w)
            for chirality in ("gLV","gRV"):
                key=chirality+"_GeV_minus2"
                close(out[chirality],sum(complex(*term[key]) for term in out["by_scalar"].values()))
            self.assertNotEqual(out["gLV"],out["gRV"])


if __name__=="__main__":
    unittest.main()

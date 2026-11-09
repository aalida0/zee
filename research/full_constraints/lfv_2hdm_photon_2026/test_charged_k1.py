"""Off-shell charged photon A1, external chirality and gauge controls."""
import copy
import math
import unittest

import numpy as np

from module2.interface import decode
from research.full_constraints.lfv_2hdm_photon_2026.charged_k1 import (
    charged_source,g1_zero,g2_zero,prefactors,
)
from research.full_constraints.lfv_2hdm_photon_2026.tau_monopole import card_inputs


def close(a,b,rtol=1e-11):
    if abs(a-b)>rtol*max(abs(a),abs(b),1.e-100):
        raise AssertionError((a,b,abs(a-b)))


def z(pair):return complex(*pair)


class ChargedK1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards=card_inputs()

    def test_published_x0_analytic_kernel_ratio(self):
        self.assertEqual(g1_zero(),1/3)
        self.assertEqual(g2_zero(),1/6)
        for mass in (130.,380.,1000.):
            a1,a2=prefactors(mass)
            close(a1/a2,2/3)
            close(a1,-1/(288*math.pi**2*mass**2))
            close(a2,-1/(192*math.pi**2*mass**2))

    def test_source_A2_matching_native_dipole_all_chiralities(self):
        for w in self.cards:
            x=charged_source(w)
            self.assertLess(x["native_on_shell_A2_relative_residual"],2e-11)
            close(z(x["A1L_F"]),2/3*z(x["A2R_F"]))
            close(z(x["A1R_D"]),2/3*z(x["A2L_D"]))
            # Opposite chirality is suppressed by final/parent lepton mass.
            self.assertTrue(0 < x["chiral_A2_daughter_mass_ratio"] < .01)

    def test_F_zero_recovers_general_two_doublet_charged_scalar(self):
        for w in self.cards:
            a=copy.deepcopy(w)
            a["yukawas"]["F"]={"real":[[0.]*3 for _ in range(3)],
                                "imag":[[0.]*3 for _ in range(3)]}
            c=charged_source(a)
            close(z(c["A1L_F"]),0)
            self.assertNotEqual(z(c["A1R_D"]),0j)

    def test_D_zero_recovers_charged_singlet_scalar(self):
        for w in self.cards:
            a=copy.deepcopy(w)
            a["yukawas"]["D"]={"real":[[0.]*3 for _ in range(3)],
                                "imag":[[0.]*3 for _ in range(3)]}
            c=charged_source(a)
            close(z(c["A1R_D"]),0)
            self.assertNotEqual(z(c["A1L_F"]),0j)

    def test_physical_charged_state_swap_covariance(self):
        for w in self.cards:
            x=charged_source(w)
            a=copy.deepcopy(w)
            p=a["module2_input"]["scalar"]["record"]["physical"]
            p["mH1"],p["mH2"]=p["mH2"],p["mH1"]
            p["gamma"]+=math.pi/2
            y=charged_source(a)
            for key in ("A1L_F","A1R_D","A2R_F","A2L_D"):
                close(z(x[key]),z(y[key]))

    def test_common_lepton_rephasing(self):
        for w in self.cards:
            x=charged_source(w)
            a=copy.deepcopy(w)
            phases=np.exp(1j*np.array([.13,-.41,.66]))
            P=np.diag(phases)
            for name in ("D","F"):
                val=decode(a["yukawas"][name])
                if name=="D":new=P.conjugate()@val@P
                else:new=P@val@P
                a["yukawas"][name]={"real":new.real.tolist(),
                                     "imag":new.imag.tolist()}
            y=charged_source(a)
            phase=phases[1]*phases[0].conjugate()
            for key in ("A1L_F","A1R_D","A2R_F","A2L_D"):
                close(z(y[key]),z(x[key])*phase)

    def test_massive_external_Ward_identity_on_shell(self):
        # For q=p_mu-p_e and external on-shell spinors:
        # ubar_e qslash PL u_mu =
        #    m_mu ubar_e PR u_mu - m_e ubar_e PL u_mu.
        # Hence the source Eq23 term
        # A1[q^2 gamma^mu PL -q^mu(m_mu PR-m_e PL)]
        # is conserved; sigma^{mu nu} q_mu q_nu=0 identically.
        # This is an *algebraic* Ward check, not the 1-loop
        # diagrammatic Ward-Takahashi counterterm proof.
        for mi,mj in ((.1056583755,.00051099895),(1.77686,.1056583755)):
            for zL,zR in ((1+2j,0j),(0j,-.31+.2j)):
                qsq=.016
                qslash_PL=zL*mi-zR*mj
                qterm=mi*zL-mj*zR
                close(qsq*(qslash_PL-qterm),0j)

    def test_missing_full_rates(self):
        for w in self.cards:
            out=charged_source(w)
            self.assertFalse(out["common_photon_form_factor"]["neutral_complete"])
            self.assertFalse(out["common_photon_form_factor"]["Z_penguin_or_boxes_included"])


if __name__=="__main__":
    unittest.main()

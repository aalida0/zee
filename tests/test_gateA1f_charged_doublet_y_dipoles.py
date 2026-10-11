"""Tests for charged Y-only dipole and coherent one-loop amplitude assembly."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1f_charged_doublet_y_dipoles import (
    charged_doublet_mass_weight,charged_doublet_y_dipole,report
)
from gateA1b_hierarchical_no_seed import M1,M2,GAMMA

class TestChargedDoubletY(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=report()

    def test_mixings_at_zero_and_pi_over_two(self):
        self.assertAlmostEqual(charged_doublet_mass_weight(0,M1,M2),
                               1/M1**2,places=17)
        self.assertAlmostEqual(charged_doublet_mass_weight(np.pi/2,M1,M2),
                               1/M2**2,places=17)

    def test_degenerate_masses_independent_of_mixing(self):
        a=charged_doublet_mass_weight(0.21,400,400)
        b=charged_doublet_mass_weight(1.17,400,400)
        self.assertAlmostEqual(a,b,places=17)
        self.assertAlmostEqual(a,1/400**2,places=17)

    def test_chiral_contraction_and_higher_order_scaling(self):
        Y=np.array([[.001,0,.003j],[.002+.001j,.004,0],
                    [0,0,.005]],complex)
        CL,CR=charged_doublet_y_dipole(Y,parent=1,daughter=0)
        expected=sum(Y[0,k]*np.conj(Y[1,k]) for k in range(3))
        expected*=charged_doublet_mass_weight()/(96*np.pi**2)
        self.assertAlmostEqual(abs(CL-expected),0,places=22)
        self.assertEqual(CR,0j)
        Cscaled,_=charged_doublet_y_dipole(2*Y,parent=1,daughter=0)
        self.assertAlmostEqual(abs(Cscaled/CL),4)
        self.assertEqual(charged_doublet_y_dipole(
            np.zeros((3,3),complex),parent=1,daughter=0),(0j,0j))

    def test_Y_only_candidate_expected_partial_values(self):
        refs={
            "mu_to_e_gamma":2.882989053887049e-32,
            "tau_to_mu_gamma":3.0863641960062116e-29,
            "tau_to_e_gamma":3.917892816629852e-35,
        }
        for key,expected in refs.items():
            got=self.result["channels"][key]["charged_doublet_Y_ONLY_squared_BR"]
            self.assertAlmostEqual(got,expected,delta=abs(expected)*1e-8)

    def test_coherent_one_loop_not_sum_of_branching_ratios(self):
        refs={
            "mu_to_e_gamma":1.5224654915015368e-18,
            "tau_to_mu_gamma":2.5769972610544062e-20,
            "tau_to_e_gamma":3.8337822275312325e-19,
        }
        for key,expected in refs.items():
            row=self.result["channels"][key]
            got=row["coherent_scalar_ONELOOP_ONLY_BR_NOT_FULL_PHYSICAL"]
            self.assertAlmostEqual(got,expected,delta=abs(expected)*1e-8)
            incoherent=sum(row[k] for k in (
                "charged_doublet_Y_ONLY_squared_BR",
                "charged_singlet_f_ONLY_squared_BR",
                "neutral_ONELOOP_ONLY_squared_BR"
            ))
            self.assertGreater(abs(got-incoherent),max(1e-25,.0001*abs(got)))
        self.assertIn("NOT_FULL",self.result["status"])

if __name__=="__main__":
    unittest.main()

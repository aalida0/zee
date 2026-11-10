import math
import unittest
import numpy as np

from module3 import tree
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_exact_dipole_phase_space import (
    SIGMA, METRIC, photon_width, radiative_width_unit, kernel_range,
    phase_independent_tree_dipole_envelope, evaluate,
)

M, E, MU = 1.77686, 0.00051099895, 0.1056583755


class ExactTauDipoleTests(unittest.TestCase):
    def test_ward_antisymmetry(self):
        q=np.array([0.7,0.2,-0.1,0.3])
        q_cov=q*METRIC
        sigma_q=np.einsum("mnab,n->mab",SIGMA,q_cov)
        np.testing.assert_allclose(np.einsum("m,mab->ab",q_cov,sigma_q),
                                   np.zeros((4,4)),atol=2e-15)

    def test_electron_logarithm_and_muon_mass_correction(self):
        re=photon_width(M,E,E,ns=52,nz=20)/radiative_width_unit(M,E)
        rm=photon_width(M,MU,MU,ns=52,nz=20)/radiative_width_unit(M,MU)
        leading_e=1/137.035999084/(3*math.pi)*(math.log(M*M/E**2)-2.75)
        leading_mu=1/137.035999084/(3*math.pi)*(math.log(M*M/MU**2)-2.75)
        self.assertLess(abs(re/leading_e-1), 4e-5)
        self.assertLess(abs(rm/0.00227621-1), 2e-4)
        self.assertGreater(rm, leading_mu*1.015)
        self.assertLess(rm, leading_mu*1.017)

    def test_crossed_symmetrization_massive_muon(self):
        # Explicit both-diagrams integration with moderate z quadrature
        # is independently reproduced by the exchange-symmetry formula.
        from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_exact_dipole_phase_space import (
            photon_tensors, spin_inner
        )
        ps=tree.momenta(M,(MU,MU,MU),s=0.6,z=0.2)
        d,c=photon_tensors(ps,M,1.,0.,identical=True)
        both=tree.spin_sum(d+c,ps,M,(MU,MU,MU))
        pieces=(tree.spin_sum(d,ps,M,(MU,MU,MU)) +
                tree.spin_sum(c,ps,M,(MU,MU,MU)) +
                2*spin_inner(d,c,ps,M,(MU,MU,MU)).real)
        self.assertAlmostEqual(both/pieces,1,places=11)

    def test_kernel_spectrum_covers_all_phases(self):
        for ma,mb in ((E,E),(MU,MU),(E,MU),(MU,E)):
            k=kernel_range(M,ma,mb,ns=40,nz=16)
            lo,hi=k["conversion_eigen_min"],k["conversion_eigen_max"]
            self.assertGreater(lo,0)
            self.assertGreaterEqual(hi,lo)
            for key in ("pure_CL_conversion","pure_CR_conversion",
                        "equal_real_CL_CR_conversion",
                        "relative_imaginary_CL_CR_conversion"):
                self.assertGreaterEqual(k[key],lo-2e-14)
                self.assertLessEqual(k[key],hi+2e-14)

    def test_integrated_cp_rephasing(self):
        a=photon_width(M,MU,MU,1+0.2j,-0.5+0.3j,ns=30,nz=12)
        b=photon_width(M,MU,MU,1-0.2j,-0.5-0.3j,ns=30,nz=12)
        self.assertLess(abs(a-b)/a,2e-12)
        self.assertAlmostEqual(
            photon_width(M,MU,MU,0.7+0.4j,-0.2+0.1j,ns=30,nz=12)/
            photon_width(M,MU,MU,0.7+0.4j,-0.2+0.1j,ns=30,nz=12),
            1.,places=12)

    def test_triangulation_limits_and_validation(self):
        v=phase_independent_tree_dipole_envelope(2e-12,3e-12,1e-14)
        self.assertLess(v["subset_norm_lower"],2e-12)
        self.assertGreater(v["subset_norm_upper"],3e-12)
        self.assertIsNone(v["physical_full_threebody_BR"])
        self.assertIsNone(v["missing_other_amplitudes_norm_bound"])
        w=phase_independent_tree_dipole_envelope(1.,4.,2.25)
        self.assertEqual(w["subset_norm_lower"],0)
        for params in ((-1,2,1),(3,2,1),(1,2,float('nan'))):
            with self.assertRaises(ValueError):phase_independent_tree_dipole_envelope(*params)

    def test_invalid_integrator_inputs(self):
        for kwargs in ({"mass":M,"ma":E,"mb":E,"ns":6},
                       {"mass":M,"ma":E,"mb":E,"nz":1},
                       {"mass":M,"ma":E,"mb":E,"cl":complex(float('nan'))},
                       {"mass":M,"ma":MU,"mb":M},
                       {"mass":-M,"ma":E,"mb":E}):
            with self.assertRaises(ValueError): photon_width(**kwargs)

    def test_four_original_cards_and_unknown_status(self):
        result=evaluate(ns=36,nz=16,tree_order=10)
        self.assertEqual(list(result["cards"]),["D7_NO","D7_IO","F13_NO","F13_IO"])
        self.assertTrue(result["all_other_full_model_amplitudes_unbounded"])
        self.assertEqual(result["physical_lfv"],"UNKNOWN")
        self.assertIsNone(result["global_acceptance"])
        self.assertEqual(len(result["kernel"]),4)
        for card,meta in result["cards"].items():
            self.assertEqual(len(meta["channels"]),4)
            for channel,row in meta["channels"].items():
                a=row["norm_only_conditional_tree_dipole_envelope"]
                self.assertGreater(row["partial_source_radiative_BR"],0.)
                self.assertLessEqual(a["subset_norm_lower"],a["subset_norm_upper"])
                self.assertIsNone(row["physical_total_BR"])
                self.assertIsNone(a["physical_full_threebody_BR"])


if __name__=="__main__":
    unittest.main()

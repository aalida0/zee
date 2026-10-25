"""Gate 6 regression tests: paper mass inversion, theoretical gates and widths."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate6_benchmark import benchmark
from gate6_width_inventory import inventory


class Gate6ScalarTests(unittest.TestCase):
    def test_p2_transcription(self):
        p=benchmark()
        self.assertEqual(p["inputs"]["m12sq"],57700.)
        self.assertEqual(p["inputs"]["k12"],-.001266)
        self.assertAlmostEqual(p["inputs"]["alpha"],1.398)

    def test_beta_equals_alpha_invalid(self):
        p=benchmark(beta=1.398)
        self.assertLess(p["quartics"]["lambda1"],0)
        self.assertFalse(p["sufficient_global_quartic_BFB"])

    def test_beta_shift_scalar_bound_and_unitarity(self):
        p=benchmark(beta=1.394)
        self.assertAlmostEqual(p["quartics"]["lambda1"],2.5323266,places=4)
        self.assertTrue(p["sufficient_global_quartic_BFB"])
        self.assertTrue(p["tree_unitarity_pass"])
        self.assertAlmostEqual(p["max_abs_unitarity_eigenvalue"],18.13677909,places=5)

    def test_h1_h2_mass_reconstruction(self):
        p=benchmark()
        for obs,wanted in zip(p["rebuilt_charged_masses_GeV"],[300,700]):
            self.assertAlmostEqual(obs,wanted,places=6)
        for obs,wanted in zip(p["rebuilt_neutral_masses_GeV"],[125,580.7]):
            self.assertAlmostEqual(obs,wanted,places=6)
        self.assertAlmostEqual(p["reconstructed_pseudoscalar_mass_GeV"],633.7,places=6)

    def test_all_four_unitarity_scattering_matrices(self):
        p=benchmark()
        self.assertEqual({k:len(v) for k,v in p["unitarity_eigenvalues"].items()},
                         {"Q2Y1":6,"Q1Y1":6,"Q1Y0":6,"Q0Y0":13})
        for eigenvalues in p["unitarity_eigenvalues"].values():
            self.assertTrue(all(math.isfinite(v) for v in eigenvalues))

    def test_conditional_widths_reference(self):
        result=inventory()
        h2=result["partial_widths_GeV"]["H2"]
        # Independent 70-digit two-body-current calculation with
        # g12=(MZ/v)*sin(gamma)*cos(gamma); the former reference used
        # a rounded historical G12, shifting this by 6.07e-8 GeV.
        self.assertAlmostEqual(h2["H1_Z"],9.411343258642539,places=9)
        self.assertAlmostEqual(h2["W_hheavy"],1.07103074347,places=7)
        self.assertAlmostEqual(h2["H1_h125"],0.267036408817508,places=7)
        self.assertAlmostEqual(h2["tb"],1.558105504752286,places=7)

    def test_z_width_follows_charged_mixing(self):
        # Cancel MZ^2 analytically between the derivative coupling and
        # longitudinal polarization sum, instead of using vector_width.
        M,m,mz,v=700.,300.,91.1876,246.21965
        discriminant=(M*M-m*m-mz*mz)**2-4*m*m*mz*mz
        for gamma in (.2,.71,1.3):
            expected=math.sin(2*gamma)**2*discriminant**1.5/(64*math.pi*v*v*M**3)
            actual=inventory(gamma=gamma)["partial_widths_GeV"]["H2"]["H1_Z"]
            self.assertAlmostEqual(actual,expected,places=11)

    def test_nominal_fraction_is_not_physical_br(self):
        r=inventory()
        self.assertAlmostEqual(
            r["conditional_fractions_included_channels_only"]["H2"]["H1_Z"],
            .7623963010683606,places=8)
        self.assertIn("NOT_PHYSICAL",r["status"])
        self.assertGreater(len(r["missing"]),0)

    def test_light_charged_tb_width(self):
        r=inventory()
        self.assertAlmostEqual(r["partial_widths_GeV"]["H1"]["tb"],
                               .09094937533835987,places=7)
        self.assertAlmostEqual(
            r["conditional_fractions_included_channels_only"]["H1"]["tb"],
            .9559329373337353,places=7)


if __name__=="__main__":
    unittest.main()

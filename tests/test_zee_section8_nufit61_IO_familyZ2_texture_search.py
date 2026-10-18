"""NuFIT IO family-Z2 profile minimax regression with ONLY synthetic data.

The official NuFIT SHA256 verification is mandatory in real runs;
test mocks explicitly mark the synthetic fixture as untrusted.
"""
from pathlib import Path
from unittest.mock import patch
import lzma
import tempfile
import unittest

from sys import path
path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_nufit61_IO_familyZ2_texture_search import (
    STATUS,ProfileGate,source_shape,independent_dirac_phase,
    optimize_case,parse_positive_floats,parse_seeds
)
from zee_section8_IO_first_octant_witness import WITNESS


class TestFamilyZ2ModernIOProjectionSearch(unittest.TestCase):
    @staticmethod
    def fixture(filename,delta_chi2=4.):
        with lzma.open(filename,"wt",encoding="utf-8") as f:
            for section,xs,ys in (
                 ("T13/T12",[.015,.03],[.25,.38]),
                 ("T23/DCP",[.3,.7],[-180.,0.]),
                 ("DMS/DMA",[-6.,-3.],[-3.5,-1.5])):
                f.write("# "+section+" projection: SYNTHETIC NOT OFFICIAL\n")
                for x in xs:
                    for y in ys:
                        f.write(f"{x} {y} {delta_chi2}\n")

    def test_witness_dirac_phase_and_neutrino_mass_ratio(self):
        w=source_shape(WITNESS["tanbeta"],WITNESS["coordinates"])
        self.assertAlmostEqual(w["deltaCP_degrees_signed"],-142.7938027,places=5)
        self.assertAlmostEqual(w["solar_over_abs_atm_ratio"],.03649996682,places=7)
        self.assertLess(w["charged_mass_closure_GeV"],1e-9)

    def test_synthetic_profile_same_in_approx_and_dense_exact_sampling(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.txt.xz"
            self.fixture(p,delta_chi2=4.)
            with patch("zee_section8_nufit61_IO_familyZ2_texture_search.verify",
                       return_value={"SYNTHETIC_TEST_ONLY":True}):
                gate=ProfileGate(p,"TBoff-IO",r_nodes=121,y_samples=121)
            w=source_shape(WITNESS["tanbeta"],WITNESS["coordinates"])
            a=gate.scores(w,precise=False)
            b=gate.scores(w,precise=True)
            self.assertEqual(set(a),set(b))
            for name in a:
                with self.subTest(name=name):
                    self.assertAlmostEqual(a[name],4.,places=10)
                    self.assertAlmostEqual(b[name],4.,places=10)
            self.assertAlmostEqual(gate.score_one(w),4.)

    def test_out_of_grid_objective_is_smooth_but_strict_score_rejects(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.txt.xz"
            self.fixture(p,delta_chi2=4.)
            with patch("zee_section8_nufit61_IO_familyZ2_texture_search.verify",
                       return_value={"SYNTHETIC_TEST_ONLY":True}):
                gate=ProfileGate(p,"TBoff-IO",r_nodes=121,y_samples=121)
            w=source_shape(WITNESS["tanbeta"],WITNESS["coordinates"])
            outside=dict(w,observables=dict(w["observables"]))
            outside["observables"]["sin2theta13"]=.23
            with self.assertRaisesRegex(ValueError,"Outside official table support"):
                gate.score_one(outside)
            proxy=gate.soft_domain_search_score(outside)
            self.assertTrue(0 < proxy < 1e8)
            self.assertGreater(proxy,gate.score_one(w))
            # Clipped score NEVER returns as an official Delta chi2.
            self.assertAlmostEqual(gate.score_one(w),4.)

    def test_physical_angular_anchors_are_finite_across_tanbeta(self):
        from zee_section8_nufit61_IO_familyZ2_texture_search import (
            START_ANGULAR_SEEDS,
        )
        for tb,coordinates in START_ANGULAR_SEEDS.items():
            with self.subTest(tanbeta=tb):
                w=source_shape(tb,coordinates)
                for obsname in ("sin2theta12","sin2theta13","sin2theta23"):
                    self.assertTrue(0<=w["observables"][obsname]<=1)
                self.assertLess(w["charged_mass_closure_GeV"],1e-9)
                self.assertGreater(w["solar_over_abs_atm_ratio"],0)
                self.assertGreaterEqual(w["deltaCP_degrees_signed"],-180)
                self.assertLessEqual(w["deltaCP_degrees_signed"],180)

    def test_tiny_minimax_not_a_joint_likelihood_or_allowed_claim(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.txt.xz"
            self.fixture(p,delta_chi2=4.)
            with patch("zee_section8_nufit61_IO_familyZ2_texture_search.verify",
                       return_value={"SYNTHETIC_TEST_ONLY":True}):
                gate=ProfileGate(p,"TBoff-IO",r_nodes=121,y_samples=121)
            result=optimize_case(gate,tanbeta=15.,seed=113,
                                 maxiter=1,popsize=3)
            self.assertAlmostEqual(result[
                "worst_2D_profile_delta_chi2_NOT_JOINT"],4.,places=7)
            self.assertTrue(result[
                "all_three_2D_profiles_at_or_below_3sigma"])
            self.assertFalse(result["full_NuFIT6p1_joint_likelihood"])
            self.assertIsNone(result["physical_Zee_allowed"])
            self.assertFalse(result["optimizer_global_optimum_proved"])
            self.assertGreater(result["strictly_in_range_evaluations"],0)
            self.assertTrue(result["domain_continuation_is_search_heuristic_NOT_experimental_Delta_chi2"])
            self.assertIn("NOT_JOINT_FIT_OR_ALLOWED",STATUS)

    def test_rejects_unsupported_or_duplicate_options(self):
        self.assertEqual(parse_positive_floats("10,15"),[10.,15.])
        self.assertEqual(parse_seeds("31,41"),[31,41])
        for x in ("10,10","0,15","nan,10"):
            with self.assertRaises(ValueError):parse_positive_floats(x)
        for x in ("31,31","-1,10"):
            with self.assertRaises(ValueError):parse_seeds(x)

if __name__=="__main__":
    unittest.main()

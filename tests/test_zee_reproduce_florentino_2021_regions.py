"""Literature source input provenance and fail-closed Florentino tests."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_reproduce_florentino_2021_regions import (
    load_regions,build_inputs,evaluate,STATUS,
)

class TestFlorentino2021Table2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=load_regions()

    def test_published_quartics_converted_from_100_times_printed_rows(self):
        p=self.source["benchmarks"]["P2"]
        self.assertAlmostEqual(p["lambda_c"],4.473)
        self.assertAlmostEqual(p["k1"],1.082)
        self.assertAlmostEqual(p["k2"],.00398)
        self.assertAlmostEqual(p["k12"],.01267)
        self.assertEqual(p["m12sq_GeV2"],58000)
        self.assertEqual(p["mH1_interval_GeV"],[250,360])
        self.assertEqual(p["mH2_interval_GeV"],[635,800])

    def test_p2_midpoint_is_explicitly_chosen_not_an_exact_paper_point(self):
        p=build_inputs(self.source["benchmarks"]["P2"])
        self.assertEqual(p["mH1"],305)
        self.assertEqual(p["mH2"],717.5)
        self.assertEqual(p["beta"],1.398)
        self.assertAlmostEqual(p["k12"],.01267)
        self.assertEqual(p["gamma"],1.089)

    def test_p2_mass_reconstruction_and_no_physical_allowed_claim(self):
        x=evaluate(self.source,"P2",mH1=300.,mH2=700.,
                   beta=1.398)
        self.assertEqual(x["status"],STATUS)
        self.assertEqual(x["mass_eigenvalue_closure"],"PASS")
        self.assertIsNone(x["physical_Zee_allowed"])
        self.assertFalse(x["paper_exact_benchmark_reproduced"])
        for k in ("conditional_included_channel_BR_H2_H1Z",
                  "conditional_included_channel_BR_H1_tb"):
            self.assertGreaterEqual(x[k],0)
            self.assertLessEqual(x[k],1)

    def test_p2_beta_equals_alpha_is_necessarily_unbounded(self):
        x=evaluate(self.source,"P2",mH1=300.,mH2=700.,beta=1.398)
        b=x["alternative_analytic_quartic_BFB"]
        self.assertLess(b["lambda1"],0)
        self.assertTrue(b["negative_lambda1_proves_unbounded_quartic"])
        self.assertFalse(b["alternative_global_quartic_BFB_sufficient"])
        self.assertFalse(x["scalar_sufficient_BFB"])

    def test_p2_beta_1394_is_analytically_certified_quartic_bfb(self):
        x=evaluate(self.source,"P2",mH1=300.,mH2=700.,beta=1.394)
        b=x["alternative_analytic_quartic_BFB"]
        self.assertGreater(b["lambda1"],0)
        self.assertTrue(b["neutral_2HDM_BFB"])
        self.assertTrue(b["singlet_cross_PSD_sufficient"])
        self.assertGreater(b["singlet_cross_PSD_determinant"],0)
        self.assertTrue(b["alternative_global_quartic_BFB_sufficient"])
        # Old Gate6 test is more conservative and intentionally unchanged.
        self.assertFalse(x["scalar_sufficient_BFB"])
        self.assertIsNone(x["physical_Zee_allowed"])

    def test_k12_zero_variant_is_explicitly_not_original_P2_and_bfb(self):
        x=evaluate(self.source,"P2",mH1=300.,mH2=700.,
                   beta=1.394,k12=0.)
        self.assertTrue(x["k12_source_overridden_for_softly_broken_Z2"])
        self.assertFalse(x["source_Table2_exact_scalar_parameters_used"])
        self.assertEqual(x["source_k12_value"],.01267)
        self.assertEqual(x["inputs"]["k12"],0.)
        self.assertTrue(x["family_Z2_exact_quartics_operator_audit"])
        self.assertFalse(x["family_Z2_neutrino_LFV_fitted"])
        self.assertTrue(x["scalar_sufficient_BFB"])
        self.assertTrue(x["alternative_analytic_quartic_BFB"][
            "alternative_global_quartic_BFB_sufficient"])
        self.assertTrue(x["scalar_tree_unitarity"])
        self.assertIsNone(x["physical_Zee_allowed"])

    def test_original_k12_not_symmetry_compatible(self):
        x=evaluate(self.source,"P2",mH1=300.,mH2=700.,
                   beta=1.394)
        self.assertFalse(x["k12_source_overridden_for_softly_broken_Z2"])
        self.assertTrue(x["source_Table2_exact_scalar_parameters_used"])
        self.assertFalse(x["family_Z2_exact_quartics_operator_audit"])

    def test_explicitly_rejects_signed_gamma_in_unvalidated_backend(self):
        for key in ("P3","P4"):
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,
                                                    "Signed gamma"):
                build_inputs(self.source["benchmarks"][key])

    def test_region_bounds_are_required(self):
        with self.assertRaisesRegex(ValueError,"outside source"):
            build_inputs(self.source["benchmarks"]["P2"],mH1=200.)

    def test_name_and_table_regions_are_explicit(self):
        self.assertIn("Table 2",self.source["source"]["table"])
        self.assertEqual(set(self.source["benchmarks"]),{
            "P1","P2","P3","P4"})
        self.assertIn("REGION",STATUS)
        self.assertNotIn("EXCLUDED",STATUS)

if __name__=="__main__":
    unittest.main()

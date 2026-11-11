"""Read-only consistency tests for the publication-scoped Zee B physics gate.

No third-party code needed, no rates recalculated in these focused checks.
The underlying 16-source-scalar NNLO matching and stress evidence was
already evaluated against public HEPfit and the pinned SuperIso receipts.
"""
from __future__ import annotations
import json,math,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
NNLO=HERE/"bsgamma_nnlo_hepfit_2026/16_scalar_three_loop_source_matched_evidence.json"
STRESS=HERE/"bsgamma_nnlo_hepfit_2026/16_scalar_adversarial_three_method_B_stress.json"
REFERENCE_2026=(3.54e-4,3.49e-4,0.14e-4,0.19e-4)

class Published2026BPhysicsScopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nnlo=json.loads(NNLO.read_text())
        cls.stress=json.loads(STRESS.read_text())
        cls.pulls={z["id"]:z for z in cls.nnlo["cases"]}
        cls.rows={z["id"]:z for z in cls.stress["entries"]}

    def test_complete_original_source_card_provenance_and_evaluable_screens(self):
        self.assertEqual(len(self.pulls),16)
        self.assertEqual(set(self.pulls),set(self.rows))
        self.assertEqual(self.nnlo["one_sided_95_LO_NP_n"],10)
        self.assertEqual(self.nnlo["two_sided_95_LO_NP_n"],16)
        self.assertEqual(self.nnlo["source_git_blob"],"8029be52c3e2f83490dfe3199f80e5db484dd23b")
        self.assertLess(self.nnlo["match_LO_all_original_2026_pull_residual_max"],1e-12)
        for id,datum in self.pulls.items():
            self.assertEqual(datum["scalar_sha256"],self.rows[id]["original_scalar_sha256"])
            self.assertIsNone(datum["global_acceptance"])
            self.assertEqual(datum["physical_NNLO_B"],"UNKNOWN")
            self.assertLess(abs(sum(datum["squared_doublet_weights"])-1),3e-15)
            br=(REFERENCE_2026[0]
                -8.51e-4*datum["mixed_three_orders_Hepfit"]["0"]["C7"]
                -2.16e-4*datum["mixed_three_orders_Hepfit"]["0"]["C8"])
            self.assertAlmostEqual(br,datum["LO_NP_Misiak2026_rate"],delta=2e-14)

    def test_independent_LO_and_NLO_BMU_source_basis_parity(self):
        checks=self.nnlo["SuperIso_NLO_three_benchmark_BMU_parity_witnesses"]
        self.assertEqual({x["scalar_id"] for x in checks},{15591,15673,2264})
        for x in checks:
            self.assertLess(x["max_absolute_lo_nlo_BMU_parity_residual"],1e-12)

    def test_separate_source_schemes_and_nonprobabilistic_stress_survivors(self):
        s=self.stress
        self.assertEqual(s["one_sided_95_stress_surviving"],3)
        self.assertEqual(s["two_sided_95_stress_surviving"],10)
        self.assertEqual({z["id"] for z in s["entries"] if z["one_sided_stress_survival"]},
                         {11016,14074,15673})
        self.assertTrue(self.rows[15673]["one_sided_stress_survival"])
        self.assertFalse(self.rows[15591]["one_sided_stress_survival"])
        self.assertFalse(self.rows[2264]["one_sided_stress_survival"])
        for id,row in self.rows.items():
            self.assertEqual(row["physical_B"],"UNKNOWN")
            self.assertIsNone(row["global_acceptance"])
            self.assertEqual(self.pulls[id]["global_acceptance"],None)
            self.assertGreaterEqual(row["adversarial_sum_stress_NotTheoryError"],0)

    def test_closure_at_declared_order_is_not_full_2026_nnlo(self):
        self.assertEqual(self.stress["physical_full_model_B"],"UNKNOWN")
        self.assertEqual(self.nnlo["status"],
                         "NNLO_HEPFIT_MATCHING_COEFFICIENTS_NUMERICALLY_VALIDATED__FULL_2026_NNLO_RATE_UNKNOWN")
        self.assertIsNone(self.nnlo["physical_NNLO_model_rate"])
        self.assertIsNone(self.nnlo["model_NP_uncertainty"])
        self.assertIsNone(self.nnlo["global_acceptance"])

if __name__=="__main__":
    unittest.main()

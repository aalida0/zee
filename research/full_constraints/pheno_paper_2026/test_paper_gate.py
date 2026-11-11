"""Fail-closed tests for the manuscript benchmark and approximation gates."""
from __future__ import annotations
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path

from research.full_constraints.pheno_paper_2026 import paper_gate as g


class PaperGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=g.build()
        cls.row={r["scalar_id"]:r for r in cls.report["rows"]}

    def test_original_actual_production_must_cover_13_and_only_three_at_14(self):
        d=self.report
        self.assertEqual(d["n_original_certified_scalar_spectra"],16)
        self.assertEqual(d["n_actual_13TeV_scalar_production_rates"],16)
        self.assertEqual(d["n_actual_14TeV_scalar_production_rates"],3)
        self.assertFalse(d["fresh_64_source_cards_consumed_in_this_replay"])
        self.assertEqual({i for i,r in self.row.items()
                          if r["sigma14_actual_LO_5FS_fb"] is not None},
                         {15591,15673,2264})
        self.assertAlmostEqual(self.row[15673]["sigma14_actual_LO_5FS_fb"],4.2345,places=9)
        self.assertAlmostEqual(self.row[15673]["sigma13_actual_LO_5FS_fb"],2.9876,places=9)
        self.assertAlmostEqual(self.report["Z_to_ee_or_mumu_branching_sum_PDG"],0.067294,places=12)
        raw=self.row[15673]["events14_3000fb_minus1_before_Z_top_decays_and_selection"]
        dilep=self.row[15673]["events14_3000fb_minus1_Z_to_ee_or_mumu_before_top_and_detector"]
        self.assertAlmostEqual(dilep[0],raw[0]*0.067294,places=8)
        self.assertLess(dilep[1],raw[1])
        self.assertIsNone(self.row[14074]["sigma14_actual_LO_5FS_fb"])
        self.assertIsNone(self.row[11016]["sigma14_H2_H1Z_tb_product_range_fb"])

    def test_b_confidence_and_adversarial_stress_separate(self):
        self.assertEqual(self.report["n_B_one_sided_source_LO_NP_screen"],10)
        self.assertEqual(self.report["n_B_two_sided_source_LO_NP_screen"],16)
        self.assertEqual(self.report["n_B_one_sided_adversarial_stress_screen"],3)
        self.assertEqual({r["scalar_id"] for r in self.report["rows"]
                          if r["B_one_sided_nonprobabilistic_stress_survival"]},
                         {11016,14074,15673})
        self.assertTrue(self.row[15673]["B_one_sided_Gaussian_LO_NP_screen"])
        self.assertFalse(self.row[15591]["B_one_sided_Gaussian_LO_NP_screen"])
        self.assertFalse(self.row[2264]["B_one_sided_Gaussian_LO_NP_screen"])

    def test_never_convert_integrated_events_into_detector_CL(self):
        for r in self.report["rows"]:
            self.assertIsNone(r["global_acceptance"])
            self.assertIsNone(r["LHC_95CL_exclusion_or_discovery"])
            self.assertIsNone(r["production_scale_uncertainty"])
            self.assertIsNone(r["production_PDF_uncertainty"])
            self.assertIsNone(r["total_h125_and_H_A_widths_physical"])
            self.assertIsNone(r["full_mu_to_3e_and_conversion_new_family"])
            self.assertTrue(r["B_method_stress_is_not_theory_sigma"])
            if r["sigma14_actual_LO_5FS_fb"] is not None:
                self.assertGreater(
                    r["events14_3000fb_minus1_before_Z_top_decays_and_selection"][0],0)
                self.assertGreater(
                    r["epsilon_for_10_selected_at_14TeV_using_min_rate"],0)
        self.assertIsNone(self.report["model_fully_allowed_count"])

    def test_new_constructed_yukawa_ensemble_is_optional_and_source_checked(self):
        _,points,_,historical,_,_,_,_=g.load_sources()
        families=[]
        for i,orig in sorted(points.items()):
            for ordering in ("NO","IO"):
                for k,seed in enumerate((20261111,20261112)):
                    f=historical[(i,13,ordering,k)]
                    br=f["BR_H2_H1Z"]
                    tb=f["H1_decay_BR_separate"]["t anti-b"]
                    families.append({
                        "id":i,"scalar_sha256":orig["scalar_sha256"],
                        "ordering":ordering,"seed":seed,
                        "perturbativity_status":"NEUTRINO_PERTURBATIVE",
                        "neutrino_closure":1e-15,
                        "physical_LFV":"UNKNOWN","global_acceptance":None,
                        "D4_cascade_product":br*tb,
                        "D4_BR_H2_H1Z":br,
                        "D4_BR_H1_tb":tb,
                        "partial_mu_to_e_gamma_BR":1e-19
                    })
        fake_new={"new_neutrino_family_count":64,
                  "source_16_certified_original_scalar_IDs":list(points),
                  "families":families}
        # This is a *synthetic test fixture*, never a generated physics result.
        reconstructed=g.build(fake_new)
        self.assertTrue(reconstructed["fresh_64_source_cards_consumed_in_this_replay"])
        self.assertEqual(reconstructed["BR_input_family_scope"],"new_64_constructed_neutrino_families")
        self.assertIsNone(reconstructed["model_fully_allowed_count"])
        wrong=copy.deepcopy(fake_new)
        wrong["families"][0]["D4_cascade_product"]+=0.1
        with self.assertRaises(ValueError):
            g.build(wrong)
        wrong=copy.deepcopy(fake_new)
        wrong["families"][0]["scalar_sha256"]="broken"
        with self.assertRaises(ValueError):
            g.build(wrong)
        wrong=copy.deepcopy(fake_new)
        wrong["families"][0]["global_acceptance"]="PASS"
        with self.assertRaises(ValueError):
            g.build(wrong)

    def test_csv_and_report_are_reproducible_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/"paper"
            g.outputs(self.report,directory)
            saved=json.loads((directory/"SOURCE_LOCKED_PAPER_GATE.json").read_text())
            with (directory/"PAPER_BENCHMARK_SUMMARY.csv").open() as handle:
                csv_data=list(csv.DictReader(handle))
            self.assertEqual(len(saved["rows"]),len(csv_data))
            self.assertEqual(len(saved["rows"]),16)
            self.assertEqual(csv_data[0]["global_acceptance"],"")
            review=(directory/"PAPER_SCOPE_AND_REVIEWER_NOTES.md").read_text()
            self.assertIn("not globally allowed",review.lower())
            self.assertIn("4.23450 fb",review)
            with self.assertRaises(FileExistsError):
                g.outputs(self.report,directory)


if __name__=="__main__":
    unittest.main()

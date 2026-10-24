#!/usr/bin/env python3
"""One integrated HyperIso F23 production-source contract regression, no fake physics."""
import importlib.util,io,json,tempfile,gzip,hashlib,math,unittest
from pathlib import Path
FILE=Path(__file__).resolve().parents[1]/"scripts/zee_paper1_F23_hyperiso_one_shot_integrated_157.py"
spec=importlib.util.spec_from_file_location("f23",FILE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class F23BigCampaignContracts(unittest.TestCase):
    def test_correct_original_2HDMC_TypeII_spectrum_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/"thdm_ref.lha"
            original.write_text("""Block MINPAR
  3 10.
  24 4
Block MASS
  37 310.5
  35 300.0
Block UCOUPL
  1 1 .1
  2 2 .1
  3 3 .1
Block DCOUPL
  1 1 -10
  2 2 -10
  3 3 -10
DECAY 37 .1
 1 2 1 2
""")
            txt=m.update_spectrum(original,680.,6.)
            self.assertIn("   37 6.8000000000000000e+02",txt)
            self.assertIn("    3 6.0000000000000000e+00",txt)
            self.assertIn("BLOCK YU",txt)
            self.assertIn("BLOCK YD",txt)
            self.assertIn("BLOCK YE",txt)
            self.assertIn("1.6666666666666666e-01",txt)
            self.assertIn("-6.0000000000000000e+00",txt)
            self.assertIn("  35 300.0",txt)
            original.write_text("Block MASS\\n 37 310.5\\n")
            with self.assertRaisesRegex(ValueError,"no longer has required"):
                m.update_spectrum(original,680.,6.)
    def test_tagged_native_complete_13_matching_patches_required(self):
        payload=("F23_HYPERISO_V103_TWO_STATE_CONDITIONAL "
          "BR_B_XS_GAMMA 0.000351234 mH1 672 mH2 1576 tanbeta 7.95 "
          "gamma 1.19 wH1 0.13 wH2 0.87 n_patches 13 FULL_MODEL_ALLOWED UNKNOWN")
        val,record=m.parse_native("verbosity\n"+payload+"\n")
        self.assertAlmostEqual(val,.000351234,places=14)
        with self.assertRaisesRegex(ValueError,"patch count"):
            m.parse_native(payload.replace("n_patches 13","n_patches 12"))
        with self.assertRaisesRegex(ValueError,"status"):
            m.parse_native(payload.replace("FULL_MODEL_ALLOWED UNKNOWN","FULL_MODEL_ALLOWED True"))
    def test_frozen_source_integrity_for_real_157_and_priority_9(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            cases=[]
            for i in range(157):
                b=700+i
                e={"campaign_key":f"1/F21_s1_{i:07d}",
                   "fully_Zee_allowed_or_excluded":None,
                   "physical_LHC_cross_section_pb_evaluated":False,
                   "full_HiggsTools_applied":False,
                   "F21c_ranked_source_csv":{
                      "mH1_GeV":"350","mH2_GeV":str(b),
                      "tanbeta":"6.5","gamma_rad":"1.02",
                      "analytic_LO_Bsgamma_BR_x1e4_NOT_CL":"3.8",
                      "complex_Yukawa_included_cascade_proxy_NOT_MadWidth":"0.46",
                      "partial_LFV_Wgamma_max_ratio_NOT_CL":"0.0004"}}
                cases.append(e)
            pri={
                "status":"F22_F21C_FULL_COMPLEX_YUKAWA_157_BENCHMARK_FREEZE_NOT_ALLOWED",
                "entries":cases[:9]}
            p=root/"F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json"
            p.write_text(json.dumps(pri))
            a=root/"F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz"
            with gzip.open(a,"wt") as f:
                for row in cases:f.write(json.dumps(row)+"\n")
            man={"status":pri["status"],"model_fully_allowed_or_excluded":None,
                 "preserved_real_complex_neutrino_and_partial_LFV_cases":157,
                 "priority_benchmarks":9,
                 "complete_2026_Bsgamma_or_complete_general_Zee_LFV":False,
                 "output_SHA256":{x.name:m.sha(x) for x in (p,a)}}
            (root/"F22_freeze_SHA256_manifest.json").write_text(json.dumps(man))
            files,met,all157,prior9=m.verify_f22(root)
            self.assertEqual(len(all157),157);self.assertEqual(len(prior9),9)
            p.write_text(p.read_text()+"\n")
            with self.assertRaisesRegex(ValueError,"SHA"):
                m.verify_f22(root)

if __name__=="__main__":unittest.main()

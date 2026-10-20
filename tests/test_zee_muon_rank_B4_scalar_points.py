"""B4 scalar/EWPO prior-screened Zee muon pair ranking regressions."""
from __future__ import annotations
import csv
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_muon_rank_B4_scalar_points import (
    REQUIRED,STATUS,input_candidate,evaluate,mass_diverse,run,
)

def fake_row(id="B4_1"):
    x={
        "id":id,"seed_id":"32",
        "mH1":"250","mH2":"500",
        "mh2":"480","ma":"500",
        "gamma":"0.7853981633974483",
        "alpha":"1.4","beta":"1.395","m12sq":"25000",
        "lc":"4.1","k1":"1.2","k2":".02","k12":"-.001",
        "max_unitarity":"10.0","chi2_Gfitter":"1.2",
        "chi2_PDG":"1.8",
        "BR_H2_H1Z_nonleptonic_included_upper_proxy":".75",
        "BR_H1_tb_nonleptonic_included_upper_proxy":".9",
        "candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"}
    return x

class TestRankScreenedB4(unittest.TestCase):
    def test_not_model_allowed(self):
        x=evaluate(input_candidate(fake_row()),1500,.5)
        self.assertEqual(x["model_allowed"],"unknown")
        self.assertIn("NOT_ALLOWED",x["status"])
        self.assertIn("NOT_ALLOWED",STATUS)

    def test_both_charge_rate_and_two_light_higgs_factors(self):
        r=evaluate(input_candidate(fake_row()),1500,.5)
        self.assertGreater(r["sigma_Z_both_charges_fb"],0)
        expected=r["n_produced_pairs"]*.75*.9*.9
        self.assertAlmostEqual(r["n_tb_tb_Z_included_only_ceiling"],
                               expected,delta=1e-10)
        self.assertAlmostEqual(
            r["n_tb_tb_Z_ee_mumu_included_only_ceiling"]/expected,
            .0673,delta=1e-12)

    def test_wrong_csv_cannot_be_laundered_into_screened(self):
        x=fake_row()
        x["candidate_status"]="PHYSICALLY_ALLOWED"
        with self.assertRaisesRegex(ValueError,"Not a B4"):
            input_candidate(x)
        del x["candidate_status"]
        with self.assertRaisesRegex(ValueError,"Require original"):
            input_candidate(x)

    def test_bad_conditional_branching_ratio(self):
        x=fake_row()
        x["BR_H1_tb_nonleptonic_included_upper_proxy"]="1.2"
        with self.assertRaisesRegex(ValueError,"Unphysical"):
            input_candidate(x)

    def test_diverse_mass_bins(self):
        a=evaluate(input_candidate(fake_row("B4_1")),1500,.5)
        b=evaluate(input_candidate(fake_row("B4_2")),1500,.5)
        c=dict(a,candidate_id="B4_3",mH1_GeV=325.)
        self.assertEqual(len(mass_diverse([a,b,c])),2)

    def test_small_example_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=root/"all_screened.csv"
            with source.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=REQUIRED)
                w.writeheader()
                w.writerow(fake_row("B4_1"))
                w.writerow(fake_row("B4_2"))
            result=run(source,root/"results")
            self.assertEqual(result["n_distinct_B4_spectra"],2)
            self.assertEqual(result["n_energy_spectrum_rows"],6)
            self.assertEqual(
                len(list(csv.DictReader(open(result["output_csv"])))),6)
            self.assertIsNone(result["n_model_allowed_points"])

if __name__=="__main__":
    unittest.main()

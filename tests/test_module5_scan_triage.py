"""Tests of exploratory, NOT physical, 2026 flavor scan sensitivity."""
import copy
import math
import sys
import tempfile
import json
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module5.bsgamma_scan_triage import evaluate,scenario_variance,STATUS

REFERENCE={
    "point_id":"illustrative_550_900_not_accepted",
    "mH1_GeV":550.0,"mH2_GeV":900.0,
    "beta_rad":math.atan(5.3),"gamma_rad":1.09,
    "mt_MSbar_GeV":163.96892236746697,
    "matching_scale_GeV":160.0
}

def example():
    return {
      "schema_version":"1.0.0",
      "points":[copy.deepcopy(REFERENCE)],
      "assumed_uncertainty_scenarios":[
          {"name":"illustrative_zero_NP_sigma_uncorrelated",
           "rho_SM_exp":0.0,"assumed_NP_sigma_in_1e_minus4":0.0},
          {"name":"illustrative_positive_NP_error",
           "rho_SM_exp":0.0,"assumed_NP_sigma_in_1e_minus4":0.2}
      ]
    }

class ScanSensitivityTests(unittest.TestCase):
    def test_source_baseline_and_no_classification(self):
        r=evaluate(example())
        self.assertEqual(r["status"],STATUS)
        self.assertFalse(r["filter_ready"])
        self.assertIsNone(r["physical_exclusions"])
        p=r["points"][0]
        self.assertAlmostEqual(p["delta_C7"],-0.03737804303348145,places=13)
        self.assertAlmostEqual(p["delta_C8"],-0.04231149396472201,places=13)
        self.assertAlmostEqual(p["linearized_value_in_1e_minus4"],3.9494799731787267,places=12)
        self.assertEqual(p["flavor_classification"],"UNCLASSIFIED")
        self.assertIsNone(p["global_zee_acceptance"])
        self.assertIsNone(p["physical_BR"])
        self.assertEqual(p["nonlinear_error"],"UNKNOWN")

    def test_uncertainty_scenario_is_explicit_and_nonphysical(self):
        r=evaluate(example())
        scenarios=r["assumed_scenarios"]
        self.assertAlmostEqual(scenarios[0]["hypothetical_sigma_in_1e_minus4"],
                               math.hypot(0.14,0.19),places=13)
        self.assertGreater(scenarios[1]["hypothetical_sigma_in_1e_minus4"],
                           scenarios[0]["hypothetical_sigma_in_1e_minus4"])
        pulls=r["points"][0]["hypothetical_scenario_comparisons"]
        self.assertGreater(pulls[0]["hypothetical_abs_pull"],pulls[1]["hypothetical_abs_pull"])
        self.assertTrue(all(p["not_an_exclusion"] for p in pulls))

    def test_covariance_sign_and_no_auto_statistics(self):
        self.assertAlmostEqual(scenario_variance(0.0,0.),0.14**2+0.19**2,places=14)
        self.assertLess(scenario_variance(0.9,0.),scenario_variance(0.,0.))
        self.assertGreater(scenario_variance(-0.9,0.),scenario_variance(0.,0.))
        for rho in (-1,0,1):
            self.assertGreater(scenario_variance(rho,0.),0.)

    def test_mass_interchange_and_gamma(self):
        inp=example()
        p=copy.deepcopy(REFERENCE)
        p["point_id"]="relabelled_exchange"
        p["mH1_GeV"],p["mH2_GeV"]=p["mH2_GeV"],p["mH1_GeV"]
        p["gamma_rad"]=math.pi/2-REFERENCE["gamma_rad"]
        inp["points"].append(p)
        r=evaluate(inp)
        self.assertAlmostEqual(r["points"][0]["linearized_value_in_1e_minus4"],
                               r["points"][1]["linearized_value_in_1e_minus4"],places=13)

    def test_fail_closed_invalid_point_and_scenarios(self):
        bads=[
            lambda x: x["points"][0].__setitem__("matching_scale_GeV",81.),
            lambda x: x["points"][0].__setitem__("mt_MSbar_GeV",float("nan")),
            lambda x: x["points"][0].__setitem__("gamma_rad",False),
            lambda x: x["points"].append(copy.deepcopy(x["points"][0])),
            lambda x: x["points"][0].__setitem__("allowed",True),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("rho_SM_exp",1.1),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("assumed_NP_sigma_in_1e_minus4",-0.1),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("assumed_NP_sigma_in_1e_minus4",True),
            lambda x: x["assumed_uncertainty_scenarios"].append(copy.deepcopy(x["assumed_uncertainty_scenarios"][0])),
            lambda x: x.__setitem__("filter_ready",True),
            lambda x: x["points"].clear(),
            lambda x: x["assumed_uncertainty_scenarios"].clear(),
        ]
        for mutate in bads:
            obj=example()
            mutate(obj)
            with self.subTest(mutate=str(mutate)), self.assertRaises((ValueError,TypeError)):
                evaluate(obj)

    def test_cli_reject_duplicate_json_without_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            inp=Path(folder)/"in.json";out=Path(folder)/"out.json"
            inp.write_text(json.dumps(example()))
            args=[sys.executable,"-m","module5.bsgamma_scan_triage",
                  "--input",str(inp),"--output",str(out)]
            good=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr)
            previous=out.read_bytes()
            inp.write_text('{"points":[],"points":[]}')
            wrong=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(wrong.returncode,0)
            self.assertEqual(out.read_bytes(),previous)

if __name__=="__main__":
    unittest.main()

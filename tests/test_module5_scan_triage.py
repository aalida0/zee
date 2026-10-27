"""Tests of exploratory, NOT physical, 2026 flavor scan sensitivity."""
import copy
import hashlib
from decimal import Decimal, localcontext
import math
import sys
import tempfile
import json
import subprocess
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module5.bsgamma_scan_triage import evaluate,scenario_variance,STATUS
from module5.hyperiso_patch_contract import make_contract

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
    def test_independent_decimal_arithmetic_oracle(self):
        inp=json.loads((ROOT/"module5/example_scan_triage.json").read_text())
        # Literal published slopes/errors; no production formula/constants imported.
        inp["assumed_uncertainty_scenarios"]=[
            {"name":str(rho)+"_"+str(sigma),"rho_SM_exp":rho,
             "assumed_NP_sigma_in_1e_minus4":sigma}
            for rho in (-1., -.5, 0., .5, 1.) for sigma in (0., .2)]
        result=evaluate(inp)
        with localcontext() as ctx:
            ctx.prec=60
            D=lambda v:Decimal(str(v))
            for point in result["points"]:
                shift=-D('8.51')*D(point["delta_C7"])-D('2.16')*D(point["delta_C8"])
                central=D('3.54')+shift
                diff=central-D('3.49')
                for key, value in [("np_shift_in_1e_minus4",shift),
                                   ("linearized_value_in_1e_minus4",central),
                                   ("linearized_minus_experiment_in_1e_minus4",diff)]:
                    self.assertAlmostEqual(point[key],float(value),places=13)
                for assumption, reported, comparison in zip(inp["assumed_uncertainty_scenarios"],
                        result["assumed_scenarios"],point["hypothetical_scenario_comparisons"]):
                    variance=D('.14')**2+D('.19')**2-2*D(assumption["rho_SM_exp"])*D('.14')*D('.19')+D(assumption["assumed_NP_sigma_in_1e_minus4"])**2
                    sigma=variance.sqrt()
                    self.assertAlmostEqual(reported["hypothetical_sigma_in_1e_minus4"],float(sigma),places=14)
                    self.assertAlmostEqual(comparison["hypothetical_signed_pull"],float(diff/sigma),places=12)
                    self.assertAlmostEqual(comparison["hypothetical_abs_pull"],float(abs(diff/sigma)),places=12)
                    self.assertTrue(comparison["not_an_exclusion"])

    def test_tampered_contract_rejected_by_unchanged_C1(self):
        for field in ("coefficient", "source_hash", "basis"):
            def tamper(inputs):
                c=make_contract(inputs)
                if field=="coefficient":c["coefficients"]["C7"]["real"] *= -1
                elif field=="source_hash":c["zee_lo_source_sha256"]="0"*64
                else:c["coefficient_basis"]="tampered"
                return c
            with self.subTest(field=field), patch("module5.bsgamma_scan_triage.make_contract",side_effect=tamper):
                with self.assertRaises(ValueError):evaluate(example())

    def test_source_baseline_and_no_classification(self):
        r=evaluate(example())
        self.assertEqual(r["status"],STATUS)
        self.assertFalse(r["filter_ready"])
        self.assertFalse(r["2026_LINEARIZED_FLAVOR_FILTER_READY"])
        self.assertEqual(r["FULL_ZEE_ALLOWED"],"NOT_EVALUATED")
        self.assertEqual(r["C1_status"],"2026_EQ4_LO_LINEARIZED_DIAGNOSTIC_NOT_A_CONSTRAINT")
        self.assertEqual(r["linear_formula_source_url"],"https://arxiv.org/html/2608.29863v1")
        for name, digest in r["implementation_sha256"].items():
            self.assertEqual(digest,hashlib.sha256((ROOT/"module5"/name).read_bytes()).hexdigest())
        self.assertIsNone(r["physical_exclusions"])
        p=r["points"][0]
        self.assertEqual(p["C1_status"],r["C1_status"])
        self.assertEqual(p["external_convention_status"],"EXTERNAL_CONVENTION_PASS")
        self.assertTrue({"allowed","excluded","confidence_level","mass_cut"}.isdisjoint(p))
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
            lambda x: x["points"][0].__setitem__("mH1_GeV",10**1000),
            lambda x: x["points"][0].__setitem__("mH1_GeV",float("inf")),
            lambda x: x["points"][0].pop("mt_MSbar_GeV"),
            lambda x: x["points"].append(copy.deepcopy(x["points"][0])),
            lambda x: x["points"].append(dict(x["points"][0],point_id="duplicate_physics")),
            lambda x: x["points"][0].__setitem__("allowed",True),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("rho_SM_exp",1.1),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("assumed_NP_sigma_in_1e_minus4",-0.1),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("assumed_NP_sigma_in_1e_minus4",True),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("assumed_NP_sigma_in_1e_minus4",1e308),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("rho_SM_exp",float("nan")),
            lambda x: x["assumed_uncertainty_scenarios"][0].__setitem__("physical_covariance",[]),
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
            result=json.loads(previous)
            self.assertEqual(result["source_batch_sha256"],hashlib.sha256(inp.read_bytes()).hexdigest())
            valid=inp.read_text()
            invalid=['{"points":[],"points":[]}',valid.replace('550.0','550.0,"mH1_GeV":600.0'),
                     valid.replace('550.0','NaN'),valid.replace('550.0','Infinity'),valid.replace('550.0','1e999')]
            for raw in invalid:
                with self.subTest(raw=raw[:80]):
                    inp.write_text(raw)
                    wrong=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
                    self.assertNotEqual(wrong.returncode,0)
                    self.assertEqual(out.read_bytes(),previous)

if __name__=="__main__":
    unittest.main()

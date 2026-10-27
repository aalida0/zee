"""Independent algebra and fail-closed tests of the 2026 Eq.(4) diagnostic.

These tests do NOT certify the external LEFT convention or a Zee constraint.
"""
import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module5.hyperiso_patch_contract import make_contract
from module5.bsgamma_2026_linear_diagnostic import (
    eq4_conditional, run_contract, STATUS, SOURCE, MATCHING_GEV,
    COEF_C7, COEF_C8
)

BASE={"mH1_GeV":550.,"mH2_GeV":900.,
      "beta_rad":math.atan(5.3),"gamma_rad":1.09,
      "mt_MSbar_GeV":163.96892236746697,"matching_scale_GeV":160.}

class SourceLockedConditionalTest(unittest.TestCase):
    def test_exact_paper_coefficients_and_zero_np_baseline(self):
        self.assertEqual(SOURCE,"arXiv:2608.29863v1")
        self.assertEqual(MATCHING_GEV,160.)
        self.assertEqual((COEF_C7,COEF_C8),(-8.51,-2.16))
        self.assertEqual(eq4_conditional(0.,0.)["conditional_B_times_1e4"],3.54)

    def test_independent_arithmetic_and_linearity(self):
        for d7,d8 in ((0.001,0.),(0.,-0.002),(-0.01,-0.02),(0.03,0.005)):
            a=eq4_conditional(d7,d8)
            expected=3.54-8.51*d7-2.16*d8
            self.assertAlmostEqual(a["conditional_B_times_1e4"],expected,places=13)
            self.assertAlmostEqual(a["delta_B_times_1e4"],-8.51*d7-2.16*d8,places=13)
        d=eq4_conditional(-0.01,-0.02)
        self.assertGreater(d["conditional_B_times_1e4"],3.54)

    def test_two_charged_states_and_no_exclusion(self):
        result=run_contract(make_contract(BASE))
        self.assertEqual(result["status"],STATUS)
        self.assertEqual(result["shift_input"]["DeltaC7"],make_contract(BASE)["coefficients"]["C7"]["real"])
        self.assertEqual(result["shift_input"]["DeltaC8"],make_contract(BASE)["coefficients"]["C8"]["real"])
        self.assertIsNone(result["zee_exclusion"])
        self.assertIsNone(result["zee_likelihood"])
        self.assertIsNone(result["global_zee_acceptance"])
        self.assertEqual(result["experiment_comparison"],"NOT_EVALUATED")
        self.assertEqual(result["hyperiso_injection"],"NOT_USED_SM_BSM_PATCH_DROPPED")

    def test_state_exchange(self):
        a=run_contract(make_contract(BASE))
        b=run_contract(make_contract({**BASE,"mH1_GeV":900.,"mH2_GeV":550.,
                                           "gamma_rad":math.pi/2-1.09}))
        self.assertAlmostEqual(a["linearized"]["conditional_B_times_1e4"],
                               b["linearized"]["conditional_B_times_1e4"],places=13)

    def test_source_contract_tamper_and_scale_fail(self):
        good=make_contract(BASE)
        mods=(
            lambda x:x["coefficients"]["C7"].__setitem__("real",0.),
            lambda x:x["input"].__setitem__("matching_scale_GeV",81.),
            lambda x:x.__setitem__("matching_scale_GeV",81.),
            lambda x:x["coefficients"]["C8"].__setitem__("imag",.1),
            lambda x:x.__setitem__("status","VALIDATED_ZEE_BR"),
            lambda x:x.__setitem__("extra",123),
        )
        for mutate in mods:
            x=copy.deepcopy(good)
            mutate(x)
            with self.assertRaises((ValueError,KeyError)):run_contract(x)

    def test_nonfinite_values_rejected(self):
        for bad in (float("nan"),float("inf"),float("-inf"),True):
            with self.assertRaises(ValueError):eq4_conditional(bad,0.)
        for bad in (float("nan"),float("inf"),False):
            with self.assertRaises(ValueError):eq4_conditional(0.,bad)

    def test_example_cli_and_duplicate_key_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);inp=root/"contract.json";out=root/"result.json"
            inp.write_text(json.dumps(make_contract(BASE)))
            cmd=[sys.executable,"-m","module5.bsgamma_2026_linear_diagnostic",
                 "--input",str(inp),"--output",str(out)]
            a=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(a.returncode,0,a.stderr)
            obj=json.loads(out.read_text())
            self.assertEqual(obj["status"],STATUS)
            old=out.read_bytes()
            inp.write_text('{"input":{},"input":{}}')
            a=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertNotEqual(a.returncode,0)
            self.assertEqual(out.read_bytes(),old)

if __name__=="__main__":
    unittest.main()

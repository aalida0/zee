"""Pure-contract tests; do not imply a HyperIso run or physical flavor constraint."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module5.hyperiso_patch_contract import make_contract,OUTCOME
from module5.bsgamma_lo import compute

BASE={"mH1_GeV":550.,"mH2_GeV":900.,"beta_rad":math.atan(5.3),
      "gamma_rad":1.09,"mt_MSbar_GeV":163.96892236746697,
      "matching_scale_GeV":160.}

class ContractTests(unittest.TestCase):
    def test_signed_two_state_sum_matches_frozen_lo(self):
        out=make_contract(BASE)
        lo=compute(**BASE)
        self.assertEqual(out["status"],OUTCOME)
        self.assertEqual(out["contribution"],"BSM")
        self.assertEqual(out["order"],"LO_ALPHA_S_0")
        for coeff in ("C7","C8"):
            v=out["coefficients"][coeff]
            self.assertAlmostEqual(v["real"],lo["delta_"+coeff+"_LO_at_matching_scale"],
                                   delta=1e-15)
            self.assertAlmostEqual(sum(v["per_state_real"]),v["real"],delta=1e-15)
            self.assertEqual(v["imag"],0.)
        self.assertIsNone(out["misiak_2026_screen"])
        self.assertIsNone(out["physical_BR"])
        self.assertIsNone(out["global_zee_acceptance"])

    def test_single_doublet_gamma_zero(self):
        out=make_contract({**BASE,"gamma_rad":0.})
        for c in ("C7","C8"):
            self.assertEqual(out["coefficients"][c]["per_state_real"][1],0.)

    def test_spectrum_interchange(self):
        r1=make_contract(BASE)
        r2=make_contract({**BASE,"mH1_GeV":BASE["mH2_GeV"],
                               "mH2_GeV":BASE["mH1_GeV"],
                               "gamma_rad":math.pi/2-BASE["gamma_rad"]})
        for c in ("C7","C8"):
            self.assertAlmostEqual(r1["coefficients"][c]["real"],
                                   r2["coefficients"][c]["real"],delta=1e-14)

    def test_no_implicit_mass_running(self):
        a=make_contract(BASE)
        b=make_contract({**BASE,"matching_scale_GeV":81.})
        self.assertEqual(a["coefficients"],b["coefficients"])
        self.assertNotEqual(a["matching_scale_GeV"],b["matching_scale_GeV"])

    def test_missing_extra_complex_and_nonfinite_inputs_rejected(self):
        for record in (
            {k:v for k,v in BASE.items() if k!="gamma_rad"},
            {**BASE,"extra":1},
            {**BASE,"gamma_rad":complex(1,1)},
            {**BASE,"mH2_GeV":float("nan")},
            {**BASE,"mt_MSbar_GeV":-163.},
            {**BASE,"beta_rad":True}
        ):
            with self.subTest(record=record),self.assertRaises((ValueError,TypeError)):
                make_contract(record)

    def test_no_mutation(self):
        data=copy.deepcopy(BASE)
        make_contract(data)
        self.assertEqual(data,BASE)

    def test_cli_fail_closed_and_hash(self):
        with tempfile.TemporaryDirectory() as dirname:
            inp=Path(dirname)/"in.json";out=Path(dirname)/"out.json"
            inp.write_text(json.dumps(BASE))
            cmd=[sys.executable,"-m","module5.hyperiso_patch_contract",
                 "--input",str(inp),"--output",str(out)]
            ok=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(ok.returncode,0,ok.stderr)
            result=json.loads(out.read_text())
            self.assertEqual(result["status"],OUTCOME)
            old=out.read_bytes()
            inp.write_text('{"x":1,"x":2}')
            bad=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertEqual(old,out.read_bytes())

if __name__=="__main__":
    unittest.main()

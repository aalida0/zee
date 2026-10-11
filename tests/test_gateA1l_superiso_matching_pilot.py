"""Gate A1L: source-order and synthetic matching-closure regression tests.

These do not validate the vendor's physical NLO/NNLO coefficients.
"""
import json
import pathlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1l_superiso_nlo_audit import assess
from gateA1l_check_matching_pilot import parse,check

def source_fixture(*, early_assignment=False, missing_clamp=False):
    parts=["void CW_calculator(void) {",
           "for(ie=1;ie<=10;ie++) C0w[ie]=C1w[ie]=C2w[ie]=0.;"]
    if early_assignment:
        for i in (7,8,9,10):
            parts.append(f"C0w[{i}]=42;")
    if not missing_clamp:
        for i in (7,8,9,10):
            parts.append(f"if(cabs(C{i}H_1)*alphas_mu/4./pi>"
                         f"cabs(C0w[{i}])) C{i}H_1*=cabs(C0w[{i}])/"
                         f"cabs(C{i}H_1)*4.*pi/alphas_mu;")
    if not early_assignment:
        for i in (7,8,9,10):
            parts.append(f"C0w[{i}]= C{i}SM_0 + C{i}H_0;")
    return "\n".join(parts+["}"])

def fake_output(path, *, light_weight, heavy_weight, corrupt=False):
    s=["STATUS MATCHING_WILSON_PILOT_NO_PHYSICAL_BR_VENDOR_NLO_C7_C8_AUDIT_REQUIRED",
       f"INPUT muW=160 w1={light_weight:.17g} w2={heavy_weight:.17g}"]
    for o in range(3):
        for i in range(1,11):
            sm=float(i+o)/100
            light=-0.01*i/(o+1)
            heavy=-0.003*i/(o+1)
            if o==1 and i in (7,8,9,10):
                light=heavy=0.
            zee=sm+light_weight*light+heavy_weight*heavy
            if corrupt and o==0 and i==7:
                zee+=0.01
            s.append(f"COEFF order={o} i={i} sm={sm:.17g} "
                     f"delta1={light:.17g} delta2={heavy:.17g} "
                     f"zee={zee:.17g}")
    Path(path).write_text("\n".join(s)+"\n")

class TestSuperIsoNLOClipping(unittest.TestCase):
    def test_zero_initialized_before_clamp(self):
        r=assess(source_fixture())
        self.assertIn("SOURCE_CONFIRMED",r["status"])
        self.assertTrue(all(x["source_order_forces_zero_before_assignment"]
                            for x in r["rows"]))
        for row in r["rows"]:
            self.assertLess(row["array_init_line"],row["clamp_line"])
            self.assertLess(row["clamp_line"],row["first_C0w_assignment_line"])

    def test_assignment_first_does_not_prove_clipping(self):
        r=assess(source_fixture(early_assignment=True))
        self.assertIn("INCOMPLETE",r["status"])
        self.assertFalse(any(x["source_order_forces_zero_before_assignment"]
                             for x in r["rows"]))

    def test_clamp_absent_not_misidentified(self):
        r=assess(source_fixture(missing_clamp=True))
        self.assertFalse(any(x["clamp_present"] for x in r["rows"]))

    def test_matching_endpoint_and_weighted_closure(self):
        with tempfile.TemporaryDirectory() as d:
            files=[Path(d)/f"{i}.txt" for i in range(3)]
            for path,w in zip(files,(1.,0.,0.21471339018904734)):
                fake_output(path,light_weight=w,heavy_weight=1-w)
            audit=assess(source_fixture())
            r=check(*(parse(x) for x in files),audit)
            self.assertIn("VENDOR_NLO",r["status"])
            self.assertFalse(r["allowed_Zee_benchmark"])
            self.assertAlmostEqual(r["closure"]["maximum_absolute_residual"],0,delta=1e-12)
            self.assertAlmostEqual(
                r["selected_benchmark_Wilson"]["order_1"]["C7"]["DeltaH1"],
                0.,places=12)

    def test_corrupted_matching_result_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            files=[Path(d)/f"{i}.txt" for i in range(3)]
            for path,w in zip(files,(1.,0.,0.21471339018904734)):
                fake_output(path,light_weight=w,heavy_weight=1-w,
                            corrupt=(path==files[2]))
            with self.assertRaises(ValueError):
                check(*(parse(x) for x in files),assess(source_fixture()))

if __name__=="__main__":
    unittest.main()

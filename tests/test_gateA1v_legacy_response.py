"""Gate A1V synthetic regression checks (not a substitute for AF physics)."""
from __future__ import annotations
import csv
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1v_run_legacy_response import (
    parse_output,iter_grid,validate_inputs,EXPECTED_K,STATUS,
)


def fake_output(k_override=None,wrong_input=False):
    b0=0.0003382457724
    lin=0.000050
    quad=0.0000048737683821
    br=lambda k:b0+k*lin+k*k*quad
    lines=[
        f"A1V_K k={k:.17g} BR={br(k):.17g}"
        for k in (k_override or EXPECTED_K)
    ]
    lines.extend([
        "A1V_INPUT mH1=300 mH2=700 gamma="
        +("1.08" if wrong_input else "1.089")
        +" tanbeta=5.597170833164245 muW_factor=1 mub_factor=1 muW=160.7384 mub=2.4",
        f"A1V_DECOMP SM={b0:.17g} LINEAR={lin:.17g} "
        f"QUADRATIC={quad:.17g} FULL={br(1.):.17g} "
        f"RESIDUAL_HALF=0 RESIDUAL_DOUBLE=0 INDEPENDENT_SM={b0:.17g}",
        "STATUS "+STATUS,
    ])
    return "\n".join(lines)+"\n"


class TestGateA1V(unittest.TestCase):
    def test_quadratic_split(self):
        p=parse_output(fake_output(),
           (300.,700.,1.089,5.597170833164245,1.,1.))
        self.assertAlmostEqual(p["full_Zee_BR"],.0003931195407821)
        self.assertAlmostEqual(p["linear_delta_BR"],.000050)
        self.assertAlmostEqual(p["quadratic_delta_BR"],.0000048737683821)
        self.assertFalse("model_allowed" in p)

    def test_wrong_input_rejected(self):
        with self.assertRaisesRegex(ValueError,"input mismatch"):
            parse_output(fake_output(wrong_input=True),
               (300.,700.,1.089,5.597170833164245,1.,1.))

    def test_missing_scale_rejected(self):
        with self.assertRaisesRegex(ValueError,"Missing NP-strength"):
            parse_output(fake_output(k_override=(-1.,0.,0.5,1.)),
               (300.,700.,1.089,5.597170833164245,1.,1.))

    def test_duplicate_completed_status_rejected(self):
        with self.assertRaisesRegex(ValueError,"completion"):
            parse_output(fake_output()+"STATUS "+STATUS+"\n",
               (300.,700.,1.089,5.597170833164245,1.,1.))

    def test_negative_response_residual_rejected(self):
        with self.assertRaisesRegex(ValueError,"closure"):
            parse_output(fake_output().replace(
                "RESIDUAL_HALF=0","RESIDUAL_HALF=1e-5"),
               (300.,700.,1.089,5.597170833164245,1.,1.))

    def test_csv_validation_does_not_claim_exclusion(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"inputs.csv"
            f.write_text("mH1,mH2,gamma,tanbeta\n"
                         "300,700,1.089,5.597170833164245\n"
                         "400,750,0.9,5.0\n")
            points=list(iter_grid(f,100))
            self.assertEqual(len(points),2)
            self.assertEqual(points[0][:2],(300.,700.))
            with self.assertRaisesRegex(ValueError,"exceeds"):
                list(iter_grid(f,1))

    def test_kinematic_domain_guards(self):
        for args in [(750.,700.,1.,5.),(300.,700.,-0.1,5.),
                     (300.,700.,0.3,-5.),(10.,700.,1.,5.)]:
            with self.assertRaisesRegex(ValueError,"Invalid"):
                validate_inputs(*args)

    def test_interposition_source_contract(self):
        base=Path(__file__).resolve().parents[1]/"scripts"
        c=(base/"gateA1v_legacy_response.c").read_text()
        py=(base/"gateA1v_run_legacy_response.py").read_text()
        self.assertIn("gateA1u_legacy_two_state_br.c",c)
        self.assertIn("observable_at_fixed_low(&low,high",c)
        self.assertIn("-Wl,--wrap=CW_calculator",py)
        self.assertNotIn("Zee_model_allowed\":True",py)


if __name__=="__main__":
    unittest.main()

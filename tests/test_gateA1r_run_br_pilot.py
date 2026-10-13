"""A1R pilot regression: no fake full NNLO/experimental exclusion claim."""
from __future__ import annotations
import hashlib
import math
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1r_run_br_pilot import (
    MASSES,MODELS,REFERENCE_SM,make_author_reference_control,
    read_br_output,audit_points,finite,
)

def result_values():
    return {(m,o,i):(
        0.1*(o+1)+.0002*m+.001*i)
        for m in MASSES for o,ops in
        {0:(7,8),1:(7,8),2:(3,4,5,6,7,8),3:(7,8)}.items()
        for i in ops}

def typeii_results():
    x={}
    for key,(mode,m) in MODELS.items():
        br=(3.4e-4 if mode=="S" else
            3.4e-4+1e-5*(700/m)+(1e-7 if mode=="A" else 0))
        x[key]={
            "mode":mode,"mH_GeV":m,"tanbeta":5.597170833164245,
            "muW_GeV":160.7384,"mu_b_GeV":2.4,
            "mt_muW_GeV":163.10709645657508,
            "Egamma_cut_GeV":1.6,"BR_B_to_Xs_gamma":br,
        }
    return x

class TestA1ROBS(unittest.TestCase):
    def test_original_source_input_has_separate_4quark_and_raw_dipole(self):
        inputs={"mt_GeV":163.10709645657508,"mu_GeV":160.7384,
                "tanbeta":5.597170833164245}
        with TemporaryDirectory() as temp:
            out=make_author_reference_control(
                Path(temp),result_values(),inputs)
            self.assertEqual(set(out),set(MASSES))
            example=out[700].read_text().splitlines()
            self.assertEqual(example[0],"A1R_AUTHOR_NNLO 1")
            self.assertEqual(example[2],"MASS 700")
            self.assertEqual(example[3],"MUW 160.7384")
            vals=example[6].split(" ")
            self.assertEqual(vals[0],"C2")
            self.assertEqual(len(vals),7)
            ref=result_values()
            self.assertAlmostEqual(float(vals[1]),ref[700,2,3])
            self.assertAlmostEqual(float(vals[5]),ref[700,3,7])
            self.assertAlmostEqual(float(vals[6]),ref[700,3,8])

    def test_real_tagged_superiso_driver_output(self):
        raw=(
            "STATUS A1R_SUPERISO_V5_BR_PILOT_NOT_FLAVOUR_EXCLUSION\n"
            "INPUT mode=V mass_H=700 tanbeta=5.597170833164245 "
            "muW=160.7384 mu_b=2.4 mt_muW=163.10709645657508 "
            "E0_GeV=1.6\n"
            "BR_B_TO_XS_GAMMA=0.00037\n")
        parsed=read_br_output(raw,"V",700.,5.597170833164245)
        self.assertAlmostEqual(parsed["BR_B_to_Xs_gamma"],3.7e-4)
        with self.assertRaisesRegex(ValueError,"mode/mass"):
            read_br_output(raw,"A",700.,5.597170833164245)

    def test_malformed_or_nonfinite_br_output_blocks(self):
        raw=(
            "STATUS A1R_SUPERISO_V5_BR_PILOT_NOT_FLAVOUR_EXCLUSION\n"
            "INPUT mode=S mass_H=2000 tanbeta=5.597170833164245 "
            "muW=160.7384 mu_b=2.4 mt_muW=163.10709645657508 "
            "E0_GeV=1.6\n"
            "BR_B_TO_XS_GAMMA=nan\n")
        with self.assertRaisesRegex(ValueError,"BR or input"):
            read_br_output(raw,"S",2000,5.597170833164245)
        for n in (float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                finite(n)

    def test_all_controls_do_not_imply_exclusion(self):
        report=audit_points(typeii_results(),{},{"example":True},
                            "example.log")
        self.assertIn("AWAITING_INDEPENDENT_ERROR_BUDGET",report["status"])
        self.assertAlmostEqual(report["SM_model_BR"],3.4e-4)
        self.assertEqual(set(report["source_author_vs_vendor_BR_differences"]),
                         {"300","700","1000","2000"})
        self.assertFalse(report["full_NNLO_B_to_Xs_gamma_precision_validated"])
        self.assertFalse(report["experimental_likelihood_calibrated"])
        self.assertFalse(report["Zee_two_state_BR_calculated"])
        self.assertIsNone(report["Zee_model_allowed_or_excluded"])

    def test_suspicious_sm_normalization_blocks(self):
        data=typeii_results()
        data["SM"]["BR_B_to_Xs_gamma"]=2e-4
        with self.assertRaisesRegex(ValueError,"SM result far"):
            audit_points(data,{},{},"fake.log")

    def test_incomplete_mass_scan_blocks(self):
        data=typeii_results()
        data.pop("Original1000")
        with self.assertRaisesRegex(ValueError,"Missing"):
            audit_points(data,{},{},"fake.log")

    def test_cut_value_is_explicit(self):
        self.assertEqual(REFERENCE_SM["photon_cut_GeV"],1.6)
        self.assertAlmostEqual(REFERENCE_SM["B_SM"],3.4e-4)
        self.assertAlmostEqual(REFERENCE_SM["sigma_theory"],0.17e-4)

if __name__=="__main__":
    unittest.main()

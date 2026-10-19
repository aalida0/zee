"""F4b algebra, order bookkeeping and source/row rejection contracts.

No synthetic fixture here is an EOS inclusive rate or a SuperIso result.
"""
import math
import sys
import tempfile
import json
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import zee_gateF4b_fixed_order_dipole_projector as f

class F4bProjectorContracts(unittest.TestCase):
    def test_exact_polynomial_identity(self):
        for sm0,sm1,np0,np1 in [(-.30, 2., -.02, -1.0),
                                (-.31, .2, 0., 0.),
                                (-.2, -.4, .01, .8)]:
            x = f.projector(sm0, sm1, np0, np1, .225)
            self.assertAlmostEqual(
                x["Q7eff_NP_minus_SM_LO"] +
                x["Q7eff_NP_minus_SM_Oalpha_s"] +
                x["Q7eff_NP_minus_SM_partial_Oalpha_s_squared"],
                x["Q7eff_NP_minus_SM_untruncated_square"], places=12)

    def test_zero_np_has_zero_response(self):
        p=f.projector(-.3, 4., 0., 0., .23)
        for n in ("Q7eff_NP_minus_SM_LO",
                  "Q7eff_NP_minus_SM_Oalpha_s",
                  "Q7eff_NP_minus_SM_partial_Oalpha_s_squared"):
            self.assertEqual(p[n], 0.)

    def test_nlo_multiplication_has_no_quadratic_term(self):
        p=f.projector(-.3, 1.2, -.05, 2., .225)
        a=.225/(4*math.pi)
        self.assertAlmostEqual(
            p["Q7eff_NP_minus_SM_Oalpha_s"],
            2*a*((-.35)*(3.2)-(-.3)*(1.2)))
        self.assertNotEqual(
            p["Q7eff_NP_minus_SM_Oalpha_s"],
            p["Q7eff_NP_minus_SM_Oalpha_s"]+
            p["Q7eff_NP_minus_SM_partial_Oalpha_s_squared"])

    def test_reject_nonfinite_and_bad_alpha(self):
        for inputs in [(-.3,0.,.01,math.nan,.225),
                       (-.3,0.,.01,0.,0.),
                       (-.3,0.,.01,0.,-0.3)]:
            with self.assertRaises(ValueError):
                f.projector(*inputs)

    def test_source_alpha_requires_scale_and_marker(self):
        row=("F4B_SOURCE_INPUT muW=160 mub=4.2 alphas_muW=.108 "
             "alphas_mub=.225 mt_running_muW=163 mtmt=163 "
             "mt_pole=172 mb_pole=4.8")
        val=f.parse_source_alpha(row+"\nF4B_NOT_A_BRANCHING_RATIO_OR_EXCLUSION\n",
                                 160.,4.2)
        self.assertAlmostEqual(val["alphas_mub"],.225)
        with self.assertRaises(ValueError):
            f.parse_source_alpha(row,160.,4.2)
        with self.assertRaises(ValueError):
            f.parse_source_alpha(row+"\nF4B_NOT_A_BRANCHING_RATIO_OR_EXCLUSION\n",
                                 160.,3.)

    def test_f4_prior_source_sha_and_full_cohort(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"f4.json"
            rows=[{"mass_GeV":mass,"tanbeta":t}
                  for t in f.TANBETAS for mass in f.MASSES]
            good={"status":"NOT_YET_VALIDATED","a1m_sha256":"pin",
                  "source_checks":{
                      "six_high_scale_effective_rotations_source_checked":True,
                      "no_explicit_low_dipole_inverse_in_base1":True,
                      "three_order_evolution_uses_effective_dipoles":True},
                  "controls":rows}
            path.write_text(json.dumps(good))
            self.assertEqual(len(f.check_f4_source_summary(path,"pin")),8)
            with self.assertRaises(ValueError):
                f.check_f4_source_summary(path,"wrongsha")
            good["controls"][-1]=good["controls"][0]
            path.write_text(json.dumps(good))
            with self.assertRaises(ValueError):
                f.check_f4_source_summary(path,"pin")
            good["controls"]=rows[:-1]
            path.write_text(json.dumps(good))
            with self.assertRaises(ValueError):
                f.check_f4_source_summary(path,"pin")

if __name__=="__main__":
    unittest.main()

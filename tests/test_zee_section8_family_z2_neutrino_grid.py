"""Multi-seed family-Z2 NO/IO texture pilot regression, not an oscillation likelihood."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_family_z2_neutrino_grid import (
    parse_float_list,parse_seed_list,summarize_run,check_results,STATUS,
)
from zee_section8_family_z2_neutrino_texture_pilot import exploratory_optimize


class TestFamilyZ2NeutrinoGrid(unittest.TestCase):
    def test_parser_dedupes_and_rejects_invalid_inputs(self):
        self.assertEqual(parse_float_list("5.597,10,15"),[5.597,10.,15.])
        self.assertEqual(parse_seed_list("11,12"),[11,12])
        for txt in ("", "5,-1", "10,10","nan,15"):
            with self.subTest(txt=txt),self.assertRaises(ValueError):
                parse_float_list(txt)
        for txt in ("","1,1","-1,10","2.4,3"):
            with self.subTest(txt=txt),self.assertRaises(ValueError):
                parse_seed_list(txt)

    def test_multi_seed_summarizer_no_physical_pass(self):
        r=exploratory_optimize(tanbeta=15,ordering="IO",
            maxiter=1,popsize=3,seed=24)
        p=summarize_run(r,24)
        self.assertEqual(p["ordering"],"IO")
        self.assertEqual(p["tanbeta"],15)
        self.assertFalse(p["full_NuFIT_likelihood"])
        self.assertFalse(p["physical_Zee_allowed"])
        self.assertEqual(p["seed"],24)
        self.assertGreaterEqual(p["proxy_score_NOT_chisquare"],0)
        self.assertLess(p["charged_mass_closure_GeV"],1e-9)
        self.assertTrue(check_results([p],[15.],["IO"],[24]))
        p["full_NuFIT_likelihood"]=True
        with self.assertRaisesRegex(ValueError,"Incorrectly promoted"):
            check_results([p],[15.],["IO"],[24])

    def test_code_marks_tanbeta_continuation_as_lepton_only(self):
        self.assertIn("NOT_NUFIT_OR_ALLOWED",STATUS)

if __name__=="__main__":
    unittest.main()

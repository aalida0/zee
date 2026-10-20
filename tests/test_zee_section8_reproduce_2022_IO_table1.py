"""Reproduction gate checks 2022 Table1 (IO) source numbers/diagnostics."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_reproduce_2022_IO_table1 import (
    STATUS,SOURCE,source_distance,parse_tanbetas,parse_seeds,fit_one,
)

class Test2022IOTable1Source(unittest.TestCase):
    def test_source_io_table1_not_old_A1B_target(self):
        self.assertAlmostEqual(SOURCE["sin2theta12"][0],.304)
        self.assertAlmostEqual(SOURCE["sin2theta23"][0],.575)
        self.assertAlmostEqual(SOURCE["sin2theta13"][0],.02238)
        self.assertAlmostEqual(SOURCE["mass_ratio"][0],.0297)
        self.assertEqual(SOURCE["J_CP"],(-.0327,.0008,.0066))
        self.assertIn("NOT_NUFIT_OR_ALLOWED",STATUS)

    def test_2022_asymmetric_j_errors(self):
        baseline={k:float(v[0]) for k,v in SOURCE.items()}
        zero,r=source_distance(baseline)
        self.assertEqual(zero,0.)
        self.assertTrue(all(abs(z)<1e-12 for z in r.values()))
        positive=dict(baseline,J_CP=-.0327+.0066)
        negative=dict(baseline,J_CP=-.0327-.0008)
        a,ra=source_distance(positive)
        b,rb=source_distance(negative)
        self.assertAlmostEqual(a,1.)
        self.assertAlmostEqual(b,1.)
        self.assertAlmostEqual(ra["J_CP"],1.)
        self.assertAlmostEqual(rb["J_CP"],-1.)

    def test_parsing_rejects_duplicates(self):
        self.assertEqual(parse_tanbetas("5.597,10"),[5.597,10.])
        self.assertEqual(parse_seeds("12,13"),[12,13])
        for x in ("10,10","0,5","nan,10"):
            with self.subTest(x=x),self.assertRaises(ValueError):
                parse_tanbetas(x)
        for x in ("11,11","-1,0"):
            with self.subTest(x=x),self.assertRaises(ValueError):
                parse_seeds(x)

    def test_tiny_pilot_never_promotes_to_physical_point(self):
        row,z=fit_one(tanbeta=15.,seed=12,maxiter=1,popsize=3)
        self.assertEqual(row["tanbeta"],15.)
        self.assertEqual(row["seed"],12)
        self.assertFalse(row["NuFIT_6_1_likelihood"])
        self.assertFalse(row["full_Zee_allowed"])
        self.assertFalse(row["complete_LFV"])
        self.assertLess(row["max_charge_mass_error_GeV"],1e-9)
        self.assertTrue(math.isfinite(row[
            "score_standardized_diag_NOT_chi2"]))
        self.assertTrue(all(math.isfinite(v) for v in z.values()))
        self.assertAlmostEqual(sum(v*v for v in z.values()),
            row["score_standardized_diag_NOT_chi2"],places=8)

if __name__=="__main__":
    unittest.main()

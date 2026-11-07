"""Focused repository test of pre-detector 14 TeV raw yields.

No event generation, fitted background or physical exclusion.
Run:
python3 -m unittest discover -s research/full_constraints/collider -p 'test_*.py' -v
"""
import math
import unittest

from research.full_constraints.collider.raw_decay_budget import (
    B, EXPECTED_IDS, evaluate,
)


class RawDecayBudgetTest(unittest.TestCase):
    def test_exact_source_groups_and_numbers(self):
        r = evaluate()
        self.assertEqual(r["status"], "PRE_DETECTOR_TRUTH_DECAY_BUDGET_ONLY")
        self.assertEqual(r["source_family_rows"], 12)
        self.assertIsNone(r["global_acceptance"])
        self.assertIsNone(r["expected_CLs"])
        self.assertIsNone(r["detector_acceptance_efficiency"])
        cases = {row["id"]: row for row in r["benchmarks"]}
        self.assertEqual(set(cases), EXPECTED_IDS)
        for item in cases.values():
            self.assertEqual(item["family_count"], 4)
            self.assertLess(item["ranges"]["BR_H1_to_tb"]["max"], 1)
            self.assertLessEqual(
                item["ranges"]["Zll_exactly_one_direct_top_e_mu"]["min"],
                item["ranges"]["Zll_exactly_one_direct_top_e_mu"]["max"])
        self.assertTrue(math.isclose(
            cases["15591"]["ranges"]["Zll_exactly_one_direct_top_e_mu"]["min"],
            306.82793451083205, rel_tol=1e-12))
        self.assertTrue(math.isclose(
            cases["2264"]["ranges"]["Zll_exactly_one_direct_top_e_mu"]["min"],
            149.10128382995794, rel_tol=1e-12))
        self.assertTrue(math.isclose(
            cases["15673"]["ranges"]["Zll_exactly_one_direct_top_e_mu"]["min"],
            96.4433999065988, rel_tol=1e-12))

    def test_two_three_four_leptons_have_explicit_factors(self):
        r = evaluate()
        f = r["channel_factors_excluding_H1tb"]
        z = B["Z_to_ee"] + B["Z_to_mumu"]
        w = B["W_to_enu"] + B["W_to_munu"]
        h = B["W_to_hadrons"]
        self.assertAlmostEqual(f["Zll_exactly_one_direct_top_e_mu"], z*2*w*h)
        self.assertAlmostEqual(f["Zll_both_top_hadronic"], z*h*h)
        self.assertAlmostEqual(f["Zll_both_tops_direct_e_mu"], z*w*w)
        self.assertAlmostEqual(f["Zll_exactly_one_direct_top_e_mu"], .01936087948872)

    def test_luminosity_linear_and_invalid_rejected(self):
        a = evaluate()
        b = evaluate(luminosity_fb=1500)
        for x, y in zip(a["benchmarks"], b["benchmarks"]):
            self.assertEqual(x["id"], y["id"])
            xa = x["ranges"]["Zll_exactly_one_direct_top_e_mu"]["min"]
            ya = y["ranges"]["Zll_exactly_one_direct_top_e_mu"]["min"]
            self.assertAlmostEqual(xa / ya, 2.)
        for bad in (-1, 0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                evaluate(luminosity_fb=bad)


if __name__ == "__main__":
    unittest.main()

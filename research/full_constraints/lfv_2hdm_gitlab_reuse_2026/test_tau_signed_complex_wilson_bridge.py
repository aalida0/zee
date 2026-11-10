"""Pinned source gates for tau signed 2HDM neutral BZ -> Zee matching."""
from __future__ import annotations

import os
import unittest
from pathlib import Path

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_signed_complex_wilson_bridge import (
    run, CORRECTED_AUTHOR_SHA256, SOURCE_SHA, EXPECTED_IDS
)


class TauComplexSourceBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("ZEE_2HDM_PINNED_SOURCE")
        if not source:
            raise RuntimeError("Exact corrected upstream GitLab source directory required")
        cls.result = run(Path(source), "b5035cd5")

    def test_source_immutability_and_cards(self):
        r=self.result
        self.assertEqual(r["gitlab_thdm_sha256"],CORRECTED_AUTHOR_SHA256)
        self.assertEqual(r["frozen_card_sha256"],SOURCE_SHA)
        self.assertEqual(tuple(r["cards"]),EXPECTED_IDS)
        self.assertEqual(r["physical_lfv"],"UNKNOWN")
        self.assertIsNone(r["global_acceptance"])
        self.assertIsNone(r["full_Zee_gauge_completed_BZ"])

    def test_original_analytic_one_loop_approximation_is_labeled(self):
        for card in self.result["cards"].values():
            for name,row in card["channels"].items():
                bound=0.0001 if name=="tauegamma" else 0.012
                self.assertLess(abs(row["relative_deviation_one_loop"]),bound)
                self.assertFalse(row["source_exact_complex_native_K2_confirmed"])
                self.assertIsNone(row["full_Zee_two_loop"])

    def test_signed_source_neutral_bz_matching_residual_budget(self):
        for card in self.result["cards"].values():
            for name,row in card["channels"].items():
                # A toleranced comparison of two DIFFERENT one-loop schemes.
                # This is not an exact source-level complex K2 validation.
                allowed=0.018 if name=="tauegamma" else 0.006
                self.assertLess(abs(row["relative_deviation_partial_plus"]),allowed)
                self.assertGreater(abs(row["relative_deviation_partial_minus"]),
                                   abs(row["relative_deviation_partial_plus"]))

    def test_corrected_quark_running_masses_not_pole_or_mbmb(self):
        for card in self.result["cards"].values():
            self.assertEqual(card["quark_source_mass_scheme"],"authors running MSbar at mt")
            masses=card["msbar_quark_masses_mt_GeV"]
            self.assertLess(masses["mt"],172.4)
            self.assertGreater(masses["mt"],150.)
            self.assertLess(masses["mb"],4.183)
            self.assertGreater(masses["mb"],2.)
            self.assertGreater(masses["mc"],0.)
            self.assertGreater(masses["ms"],0.)

    def test_complex_signed_coefficients_have_units_and_source_shape(self):
        for card in self.result["cards"].values():
            for row in card["channels"].values():
                for key in ("module3_independent_one_loop_CL_CR_GeV_minus2",
                            "author_neutral_BZ_in_module3_CL_CR_GeV_minus2",
                            "partial_signed_plus_CL_CR_GeV_minus2"):
                    self.assertEqual(len(row[key]),2)
                    self.assertEqual(len(row[key][0]),2)
                    self.assertEqual(len(row[key][1]),2)
                self.assertGreater(row["original_native_plus_neutral_BZ_partial_BR"],0)


if __name__=="__main__":
    unittest.main()

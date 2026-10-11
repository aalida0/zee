"""Rate-gate math and parser tests."""
import math
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from gate4_rate_summary import calculate, cross_section_from_log


class RateGateTests(unittest.TestCase):
    def test_production_and_three_lepton_yield(self):
        r = calculate(.008737, .00004079, 1.089, 3000, .70, .95)
        self.assertAlmostEqual(r["sin_gamma_squared"], .7852866098109527, places=10)
        self.assertAlmostEqual(r["sigma_zee_proxy_LO_fb"], 6.8610491099183, places=9)
        self.assertAlmostEqual(r["3l_before_detector"], 268.2206036088133, places=7)
        self.assertAlmostEqual(r["Zll_and_both_W_had_before_detector"], 418.4738121118985, places=7)

    def test_selected_yields_are_efficiency_conditional(self):
        r = calculate(.008737, .00004079, 1.089, 3000, .70, .95)
        self.assertAlmostEqual(r["3l_selected_if_efficiency_5pct"],
                               .05 * r["3l_before_detector"])

    def test_invalid_br_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate(.008737, 0, 1.089, 3000, 1.1, .95)

    def test_parser_takes_final_and_not_survey_cross_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "run.log"
            p.write_text(
                "- Current estimate of cross-section: 0.00873653613 +- 4.079e-05\n"
                "Cross-section :   0.008737 +- 4.079e-05 pb\n"
            )
            self.assertEqual(cross_section_from_log(p), (.008737, .00004079))

    def test_rejects_log_without_final_cross_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "run.log"
            p.write_text("Current estimate of cross-section: 0.01 pb")
            with self.assertRaises(ValueError):
                cross_section_from_log(p)


if __name__ == "__main__":
    unittest.main()

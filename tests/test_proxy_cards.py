"""Regression tests: run python3 -m unittest discover -s tests -v"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from set_proxy_cards import update_param_card, update_run_card


class CardFormattingTest(unittest.TestCase):
    def setUp(self):
        self.param = (
            "BLOCK MASS # masses\n"
            "   5 4.700000e+00 # b\n"
            "  25 1.200000e+02 # light CP even\n"
            "  35 1.300000e+02 # heavy CP even\n"
            "  36 1.400000e+02 # CP odd\n"
            "  37 1.500000e+02 # charged\n"
            "BLOCK FRBlock\n"
            "  1 1.53748 # tanbeta\n"
            "  2 0.1 # sinbma\n"
            "DECAY 37 1.000e+00 # width\n"
        )
        self.run = (
            "  6500.0 = ebeam1 ! first beam\n"
            "  6500.0 = ebeam2 ! second beam\n"
            "  10000 = nevents ! count\n"
            "  1 = ickkw ! matching\n"
            "  5 = maxjetflavor ! flavour\n"
            "  nn23lo1 = pdlabel ! PDF\n"
        )

    def test_param_line_endings_and_comments_survive(self):
        text = update_param_card(self.param)
        self.assertEqual(len(text.splitlines()), len(self.param.splitlines()))
        self.assertTrue(text.endswith("\n"))
        self.assertIn("37 7.000000000000e+02 # charged\n", text)
        self.assertIn("2 1.000000000000e+00 # sinbma\n", text)
        self.assertIn("DECAY 37 1.000e+00", text)

    def test_run_line_endings_survive(self):
        text = update_run_card(self.run)
        self.assertEqual(len(text.splitlines()), len(self.run.splitlines()))
        self.assertIn("7000 = ebeam1", text)
        self.assertIn("7000 = ebeam2", text)

    def test_update_idempotent(self):
        text = update_param_card(self.param)
        self.assertEqual(update_param_card(text), text)
        text = update_run_card(self.run)
        self.assertEqual(update_run_card(text), text)

    def test_fails_when_mass_is_missing(self):
        with self.assertRaisesRegex(ValueError, "Missing parameter-card entries"):
            update_param_card(self.param.replace("  37 1.500000e+02 # charged\n", ""))

    def test_fails_if_bottom_mass_zero(self):
        with self.assertRaisesRegex(ValueError, "Expected positive MASS 5"):
            update_param_card(self.param.replace("5 4.700000e+00", "5 0.000000e+00"))

    def test_fails_if_run_card_key_missing(self):
        with self.assertRaisesRegex(ValueError, "Missing run-card entries"):
            update_run_card(self.run.replace("  6500.0 = ebeam2 ! second beam\n", ""))


if __name__ == "__main__":
    unittest.main()

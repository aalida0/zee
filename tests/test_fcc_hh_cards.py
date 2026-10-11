"""Ensure FCC-hh proton beam energy is configured correctly."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from set_proxy_cards import update_run_card

CARD="""  7000 = ebeam1 ! proton1
  7000 = ebeam2 ! proton2
  1200 = nevents ! events
  nn23lo1 = pdlabel ! PDF
  4 = maxjetflavor ! 4fs
"""


class TestFccProxyEnergies(unittest.TestCase):
    def test_80tev(self):
        card=update_run_card(CARD,80)
        self.assertIn("40000 = ebeam1",card)
        self.assertIn("40000 = ebeam2",card)
    def test_100tev(self):
        card=update_run_card(CARD,100)
        self.assertIn("50000 = ebeam1",card)
        self.assertIn("50000 = ebeam2",card)
        self.assertEqual(card.count("\n"),CARD.count("\n"))
    def test_14tev_is_default(self):
        card=update_run_card(CARD)
        self.assertIn("7000 = ebeam1",card)
    def test_bad_energy(self):
        with self.assertRaises(ValueError):
            update_run_card(CARD,float("nan"))


if __name__=="__main__":
    unittest.main()

"""Gate 7D independent MadWidth decay-card parser and analytic closure tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate6_width_inventory import inventory
from gate7_check_madwidth import read_widths,compare


def mock_card(drop_channel=False):
    x=inventory()
    h2=x["partial_widths_GeV"]["H2"]; h1=x["partial_widths_GeV"]["H1"]
    t2=sum(h2.values());t1=sum(h1.values())
    rows={
        (23,228):h2["H1_Z"],
        (6,-5):h2["tb"],
        (24,225):h2["W_hheavy"],
        (25,228):h2["H1_h125"],
        (24,25):h2["W_h125"],
        (-15,16):h2["tau_nu_TypeII"],
    }
    s="BLOCK MASS\n   227 700.0\n   228 300.0\n"
    s+=f"DECAY 227 {t2:.15E} # heavy\n"
    for daughters, partial in rows.items():
        if drop_channel and daughters==(23,228):
            continue
        s+=f"  {partial/t2:.15E}   2  {daughters[0]}  {daughters[1]} # channel\n"
    s+=f"DECAY 228 {t1:.15E} # light\n"
    s+=f"  {h1['tb']/t1:.15E}   2   6   -5 # t b~\n"
    s+=f"  {h1['tau_nu_TypeII']/t1:.15E}  2  -15 16\n"
    s+=f"  {h1['W_h125']/t1:.15E} 2 24 25\n"
    return s


class MadwidthTests(unittest.TestCase):
    def test_parser_returns_width_and_br(self):
        r=read_widths(mock_card())
        self.assertAlmostEqual(r[227]["width_GeV"],12.34442400198564,places=6)
        self.assertIn((23,228),r[227]["channels"])
        self.assertIn((-5,6),r[228]["channels"])
        self.assertNotIn(23,r)

    def test_partial_widths_pass_against_own_baseline(self):
        z=compare(mock_card())
        self.assertTrue(z["all_five_partial_width_screens_pass"])
        self.assertLess(abs(z["comparisons"]["H2_to_H1_Z"]["relative_difference_to_Gate6"]),1e-12)
        self.assertIn("NOT_A_PHYSICAL_ZEE_BR",z["status"])

    def test_missing_channel_causes_hard_failure(self):
        z=compare(mock_card(drop_channel=True))
        self.assertFalse(z["all_five_partial_width_screens_pass"])
        self.assertIsNone(z["comparisons"]["H2_to_H1_Z"]["MadWidth_partial_width_GeV"])

    def test_empty_decay_table_rejected(self):
        with self.assertRaises(ValueError):
            compare("DECAY 227 2.0\nDECAY 228 1.0\n")

    def test_nonphysical_branching_sum_rejected(self):
        with self.assertRaises(ValueError):
            compare("DECAY 227 10\n 0.7 2 23 228\n 0.7 2 6 -5\n"
                    "DECAY 228 1\n 1.0 2 6 -5\n")


if __name__=="__main__":unittest.main()

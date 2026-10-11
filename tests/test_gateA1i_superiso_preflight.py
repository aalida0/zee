"""Gate A1I: source inspection cannot imply valid physical matching."""
import math
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1i_superiso_preflight import report, source_inventory
from gate8a_bsgamma_lo_screen import screen, typeii_charged_lo

class TestSuperIsoPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=report()

    def test_gate8a_matching_agrees(self):
        previous=screen()["combined_LO_charged_scalar"]
        self.assertAlmostEqual(previous["DeltaC7"],
                               self.data["lo_matching"]["DeltaC7"],places=14)
        self.assertAlmostEqual(previous["DeltaC8"],
                               self.data["lo_matching"]["DeltaC8"],places=14)

    def test_single_mass_proxies_differ(self):
        d=self.data["single_mass_mapping_NOT_PHYSICAL"]
        self.assertAlmostEqual(d["m_matching_C7_GeV"],551.3641515,places=4)
        self.assertAlmostEqual(d["m_matching_C8_GeV"],563.2478746,places=4)
        self.assertGreater(d["difference_GeV"],10.)
        self.assertFalse(d["valid_as_full_NNLO_Zee_prediction"])

    def test_pure_doublet_limits(self):
        for gamma,mass in ((0.,300.),(math.pi/2,700.)):
            s=screen(gamma=gamma)["combined_LO_charged_scalar"]
            t=typeii_charged_lo(mass,math.tan(1.394),172.)
            self.assertAlmostEqual(s["DeltaC7"],t["C7"],places=12)
            self.assertAlmostEqual(s["DeltaC8"],t["C8"],places=12)

    def test_directory_fingerprint_not_certification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            (root/"src").mkdir()
            (root/"src"/"scan_coeffs.c").write_text("demo only\n")
            (root/"thdm.x").write_text("not an actual executable\n")
            d=source_inventory(root)
            self.assertTrue(d["scan_coeffs_source_detected"])
            self.assertEqual(len(d["manifest"][0]["sha256"]),64)
            self.assertFalse(d["zee_two_state_matching_certified"])
            self.assertEqual(source_inventory(root/"nonexistent")["status"],
                             "NOT_FOUND")

    def test_no_false_acceptance(self):
        self.assertIn("NOT_A_PHYSICAL_BR",self.data["status"])
        self.assertFalse(self.data["superiso"]["zee_two_state_matching_certified"])

if __name__=="__main__":
    unittest.main()

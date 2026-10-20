"""Static SARAH-source checks; NOT SARAH CheckModel or full physics validation."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / "models" / "SARAH" / "ZeeTypeII"

class TestSarahZeeSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = (BASE / "ZeeTypeII.m").read_text()
        cls.par = (BASE / "parameters.m").read_text()
        cls.part = (BASE / "particles.m").read_text()

    def test_actual_model_files(self):
        self.assertTrue(all((BASE / f).is_file() for f in (
            "ZeeTypeII.m", "parameters.m", "particles.m")))

    def test_charge_assignments(self):
        self.assertRegex(self.model, r"\{Splus,\s*1,\s*Sp,\s*1,\s*1,\s*1\}")
        self.assertIn("Fzee/2 l.l.Splus", self.model)
        self.assertIn("Mu4 conj[Splus].H1.H2", self.model)

    def test_all_gate6_scalar_operators(self):
        for param in ("M112", "M222", "M12Sq", "MCS2", "Mu4",
                      "Lambda1", "Lambda2", "Lambda3", "Lambda4",
                      "Lambda5", "LambdaC", "K1", "K2", "K12"):
            self.assertIn(param, self.model)
            self.assertRegex(self.par, r"\{"+param+r",\{Real\s*->\s*True")
        self.assertIn("Lambda1/2", self.model)
        self.assertIn("Lambda2/2", self.model)
        self.assertIn("Lambda5/2", self.model)
        self.assertIn(" - K12", self.model)

    def test_complex_flavor(self):
        self.assertIn("Ye2 conj[H2].e.l", self.model)
        self.assertIn("Yd conj[H1].d.q", self.model)
        self.assertIn("Yu H2.u.q", self.model)
        self.assertIn("Form -> AntiSymmetric", self.par)
        self.assertRegex(self.par, r"\{Fzee,\{Form -> AntiSymmetric,Real -> False")
        self.assertRegex(self.par, r"\{Ye2,\{Real -> False")

    def test_three_charged_gauge_basis(self):
        self.assertIn("{conj[H1p],conj[H2p],conj[Sp]}", self.model)
        self.assertIn("Goldstone -> Hm[{1}]", self.part)
        self.assertIn("Goldstone -> Ah[{1}]", self.part)

    def test_batch_loader_finds_local_sarah_and_records_failure(self):
        runner = (ROOT / "scripts" / "zee_sarah_check.m").read_text()
        self.assertIn('SARAH-4.15.4", "SARAH.m"', runner)
        self.assertIn("Get[sarahSource]", runner)
        self.assertIn('writeStatus["SOURCE_IMPLEMENTED_NOT_VALIDATED"]', runner)
        self.assertIn('writeStatus["SARAH_SOURCE_NOT_FOUND"]', runner)
        self.assertIn('writeStatus["SARAH_LOAD_FAILED"]', runner)
        self.assertIn("AppendTo[$Messages, messageStream]", runner)
        self.assertIn("writeStatus[zeeState_String]", runner)
        self.assertNotIn("Check[Get[sarahSource], $Failed]", runner)
        self.assertNotIn("writeStatus[s_String]", runner)
        self.assertIn("DownValues[SARAH`Start]", runner)
        self.assertIn('startResult = SARAH`Start["ZeeTypeII"]', runner)

    def test_no_false_validation_claims(self):
        self.assertIn("SOURCE_IMPLEMENTED_NOT_VALIDATED", self.model)
        self.assertNotIn("MakeSPheno[]", self.model)

if __name__ == "__main__":
    unittest.main()

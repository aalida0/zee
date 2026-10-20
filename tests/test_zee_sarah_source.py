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

    def test_gauge_es_spinor_metadata(self):
        for name in ("Fd1", "Fd2", "Fu1", "Fu2", "Fe1", "Fe2", "Fv1"):
            self.assertRegex(self.part, r"\{" + name +
                             r",\{Description\s*->\s*\"Dirac")

    def test_gate6_independent_mass_audit_sources(self):
        fixture = (ROOT / "scripts" / "zee_sarah_gate6_fixture.py").read_text()
        audit = (ROOT / "scripts" / "zee_sarah_gate6_mass_audit.m").read_text()
        self.assertIn("from gate6_benchmark import benchmark", fixture)
        self.assertIn("zeeGate6ExpectedHm", fixture)
        for name in ("hh", "Ah", "Hm"):
            self.assertIn("MassMatrix[" + name + "]", audit)
        self.assertIn("SARAH_GATE6_TREE_MASS_MATRICES_NUMERIC_PASS", audit)
        self.assertIn("mass_matrices_raw.txt", audit)
        self.assertNotIn("actual[[i,j]]", audit)
        self.assertIn("mass_matrices_substituted.txt", audit)

    def test_z_vertex_numeric_audit_is_gated(self):
        src = (ROOT / "scripts" / "zee_sarah_z_vertex_numeric_audit.m").read_text()
        fixture = (ROOT / "scripts" / "zee_sarah_gate6_fixture.py").read_text()
        self.assertIn("zeeGate6Beta", fixture)
        self.assertIn("zeeGate6Gamma", fixture)
        self.assertIn("Z_VERTEX_NUMERIC_NOT_VALIDATED", src)
        self.assertIn("Z_VERTEX_MIXING_MASS_MISMATCH", src)
        self.assertIn("Z_VERTEX_NUMERIC_COEFFICIENT_MISMATCH", src)
        self.assertIn("SARAH_GATE6_CHARGED_GAUGE_VERTEX_NUMERIC_PASS", src)
        self.assertIn("cP23=getCoupling", src)
        self.assertIn("cP22=getCoupling", src)
        self.assertIn("cP33=getCoupling", src)
        self.assertIn("cZ23=getCoupling", src)
        self.assertIn("cZ32=getCoupling", src)
        self.assertIn("diagResid", src)

    def test_z_vertex_probe_is_non_certifying(self):
        probe = (ROOT / "scripts" / "zee_sarah_z_vertex_probe.m").read_text()
        self.assertIn("Z_VERTEX_NOT_VALIDATED", probe)
        self.assertIn("Z_VERTEX_EXTRACTED_NOT_YET_PHYSICS_VALIDATED", probe)
        self.assertIn("Z_2_3", probe)
        self.assertIn("PHOTON_2_3", probe)
        self.assertIn("Vertex[item[[2]]", probe)


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

    def test_lepton_vertex_probe_is_non_certifying(self):
        probe = (ROOT / "scripts" / "zee_sarah_lepton_vertex_probe.m").read_text()
        self.assertIn("LEPTON_VERTICES_NOT_VALIDATED", probe)
        self.assertIn("LEPTON_VERTEX_EXPRESSIONS_EXTRACTED_NOT_VALIDATED", probe)
        self.assertIn("Fzee[1,2]+Fzee[2,1]", probe)
        self.assertIn("SARAH`MassMatrix[Fe]", probe)
        self.assertIn("bar[Fe],Fv,Hm", probe)
        self.assertIn("bar[Fv],Fe,conj[Hm]", probe)
        self.assertIn("lepton_vertices_raw.txt", probe)

    def test_no_false_validation_claims(self):
        self.assertIn("SOURCE_IMPLEMENTED_NOT_VALIDATED", self.model)
        self.assertNotIn("MakeSPheno[]", self.model)

if __name__ == "__main__":
    unittest.main()

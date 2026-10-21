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

    def test_fzee_charge_conjugate_orientation_probe(self):
        probe = (ROOT / "scripts" / "zee_sarah_fzee_orientation_probe.m").read_text()
        for text in (
            'FZEE_ORIENTATION_NOT_VALIDATED',
            'FZEE_NOT_FOUND_IN_PROBED_ORIENTATIONS_NOT_VALIDATED',
            'FZEE_PRESENT_IN_PROBED_VERTICES_NORMALIZATION_NOT_VALIDATED',
            'UseSymmASymm',
            'gauge_LL_splus',
            'barbar_Hm',
            'LL_Hp',
            'HAS_FZEE',
            'fzee_orientation_vertices.txt',
        ):
            self.assertIn(text, probe)
        self.assertNotIn('FZEE_PHYSICS_PASS', probe)
        self.assertIn('SARAH`Start["ZeeTypeII"]', probe)
        self.assertIn("SARAH`ModelLoaded", probe)
        self.assertIn("SARAH`AbortStart", probe)
        self.assertIn("SARAH`Vertex[fields", probe)
        for bad in ("SA`Start[", "SA`ModelLoaded", "SA`AbortStart", "SA`Vertex["):
            self.assertNotIn(bad, probe)

    def test_fzee_complex_numeric_amplitude_gate(self):
        src = (ROOT / "scripts" / "zee_sarah_fzee_numeric_audit.m").read_text()
        for marker in (
            "FZEE_COMPLEX_NUMERIC_NOT_VALIDATED",
            "FZEE_NUMERIC_EVALUATION_FAILED",
            "FZEE_COMPLEX_NUMERIC_MISMATCH",
            "SARAH_ZEE_F_COMPLEX_VERTEX_NORMALIZATION_PASS_E3_UNMATCHED",
            "ZEE_F_COMPLEX_MAX_RESIDUAL",
            "makeF[f12_,f13_,f23_]",
            "makeVe[theta_,phase_]",
            "Conjugate[vm[[1,j]]]",
            "fm+Transpose[fm]",
            "bar[Fe[{1}]],bar[Fv[{2}]],Hm[{2}]",
            "eL[{1}],vL[{2}],Sp",
            "fzee_numeric_results.txt",
        ):
            self.assertIn(marker, src)
        self.assertIn('SARAH`Start["ZeeTypeII"]', src)
        self.assertIn("SARAH`Vertex[", src)
        self.assertNotIn("SA`Start[", src)
        self.assertNotIn("SA`Vertex[", src)
        self.assertNotIn("FZEE_FULL_ZEE_ALLOWED", src)

    def test_consolidated_lepton_gate_is_one_shot_and_fail_closed(self):
        audit = (ROOT / "scripts" / "zee_sarah_integrated_lepton_validation.m").read_text()
        shell = (ROOT / "scripts" / "zee_sarah_one_shot_lepton_validation.sh").read_text()
        fixture = (ROOT / "scripts" / "zee_sarah_gate6_fixture.py").read_text()
        self.assertIn("zeeGate6Alpha", fixture)
        for key in (
            "INTEGRATED_TREE_LEPTON_NOT_VALIDATED",
            "ZEE_INTEGRATED_VERTEX_QUERIES",
            "LEPTON_FLAVOR_INPUT_OR_MASS_CLOSURE_FAILED",
            "INTEGRATED_TREE_LEPTON_COMPLEX_MISMATCH",
            "SARAH_ZEE_INTEGRATED_TREE_LEPTON_COMPLEX_PASS_E3_LOOP_UNMATCHED",
            "independentExpected",
            "Conjugate[vm].computedM.ConjugateTranspose[um]",
            "f_gauge",
            "f_plus",
            "f_hc",
            "Y_hminus",
            "Y_hplus",
            "Y_neutralPL",
            "Y_neutralPR",
            "fzee_numeric_results",
        ):
            if key == "fzee_numeric_results":
                self.assertIn("integrated_lepton_residuals.txt", audit)
            else:
                self.assertIn(key, audit)
        self.assertIn("zeeLeptonGeneration===zeeNeutrinoGeneration", audit)
        self.assertIn("With[{zeeLeptonGeneration=pp[[1]]", audit)
        self.assertIn("With[{zeeChargedState=kk}", audit)
        self.assertIn("With[{zeeNeutralState=nn}", audit)
        self.assertIn("GLOBAL_DUMMY_SYMBOL_CONTAMINATION", audit)
        self.assertIn("FZEE_GAUGE_SENTINEL_FAILED", audit)
        self.assertIn("ZEE_INTEGRATED_FZEE_SENTINEL_PASS", audit)
        for bad in ("a=pp[[1]]", "b=pp[[2]]", "k=kk;", "n=nn;",
                    "beta=zeeGate6Beta;", "gamma=zeeGate6Gamma;",
                    "alpha=zeeGate6Alpha;"):
            self.assertNotIn(bad, audit)
        self.assertIn("math -script scripts/zee_sarah_integrated_lepton_validation.m", shell)
        self.assertIn("set -euo pipefail", shell)
        self.assertIn("python3 scripts/zee_sarah_gate6_fixture.py", shell)
        self.assertNotIn("SA`Start[", audit)
        self.assertNotIn("SA`Vertex[", audit)
        self.assertNotIn("FULL_ZEE_ALLOWED", audit)

    def test_integrated_e3_sarah_convention_and_loop_kernel_gate(self):
        fixture = (ROOT / "scripts" / "zee_sarah_e3_convention_fixture.py").read_text()
        audit = (ROOT / "scripts" / "zee_sarah_e3_integrated_validation.m").read_text()
        one_shot = (ROOT / "scripts" / "zee_sarah_e3_one_shot.sh").read_text()
        for text in (
            "target_neutrino_matrix",
            "antisymmetric_f_with_null_condition",
            "solve_lepton_yukawa",
            "charged_lepton_widths",
            "lepton_log_kernel",
            "finite_mass_relative_correction",
            "zeeE3Cases",
            "zeeE3FixtureStatus",
            "ZEE_E3_REAL_309_SOURCE_INCLUDED False",
            "ZEE_E3_SARAH_SELFENERGY_GENERATED False",
            "fs=2.*f",
            "dCoupling=np.sqrt(2.)*y",
        ):
            self.assertIn(text, fixture)
        for text in (
            "E3_SARAH_CONVENTION_NOT_VALIDATED",
            "E3_QUERY_BOOKKEEPING_FAILED",
            "E3_VERTEX_EXTRACTION_FAILED",
            "E3_VERTEX_SUBSTITUTION_FAILED",
            "E3_SARAH_CONVENTION_OR_KERNEL_MISMATCH",
            "E3_SARAH_TREE_CONVENTION_AND_CHEN_KERNEL_CONSISTENT_SELFENERGY_UNVALIDATED",
            "ZEE_E3_GENERATED_SELFENERGY_CHECKED False",
            "ZEE_E3_REAL_309_ARCHIVE_TESTED False",
            "ZEE_E3_MAX_SCALE_RESIDUAL_EV",
            "ZEE_E3_MAX_MNU_CONVENTION_RESIDUAL_EV",
            "ZEE_E3_MAX_WIDTH_RESIDUAL_GEV",
            "zeeCoefficient",
            "zeeNuFromVertex",
            "zeeSentinel",
        ):
            self.assertIn(text, audit)
        self.assertIn("Length[zeeQueries]!=81", audit)
        self.assertIn("zeeCoeffCount!=162", audit)
        self.assertIn("math -script scripts/zee_sarah_e3_integrated_validation.m", one_shot)
        self.assertIn("python3 scripts/zee_sarah_e3_convention_fixture.py", one_shot)
        self.assertIn("set -euo pipefail", one_shot)
        self.assertNotIn("SA`Start[", audit)
        self.assertNotIn("SA`Vertex[", audit)
        self.assertNotIn("FULL_ZEE_ALLOWED", audit)

    def test_independent_sarah_selfenergy_major_gate_is_non_certifying(self):
        audit = (ROOT / "scripts" / "zee_sarah_e3_independent_selfenergy_audit.m").read_text()
        runner = (ROOT / "scripts" / "zee_sarah_e3_selfenergy_one_shot.sh").read_text()
        for text in (
            "CalcLoopCorrections[EWSB]",
            "SelfEnergy1LoopSum[EWSB]",
            "SelfEnergy1LoopList[EWSB]",
            "ParticlesSelfEnergy1LoopSum[EWSB]",
            "SARAH_SELFENERGY_LABEL_ALIGNMENT_FAILED",
            "SARAH_NEUTRINO_EXTERNAL_SECTOR_NOT_IDENTIFIED",
            "SARAH_NEUTRINO_SECTOR_INVENTORY_INCOMPLETE",
            "SARAH_NEUTRINO_SECTOR_REQUIRED_LOOP_INGREDIENTS_NOT_IDENTIFIED",
            "SARAH_FV_SIGMAS_FE_HM_B0_EXTRACTED_MAJORANA_AMPLITUDE_UNVALIDATED",
            "ZEE_E3_SELFENERGY_N_EXTERNAL_LABELS",
            "ZEE_E3_SELFENERGY_NEUTRINO_EXTERNAL_SUM_ENTRIES",
            "zeeNeutrinoExternalQ",
            "zeeLoopInventoryFile",
            "ZEE_E3_SELFENERGY_MAJORANA_MASS_NUMERICALLY_EXTRACTED False",
            "ZEE_E3_SELFENERGY_E3_MNU_NUMERICALLY_MATCHED False",
            "e3_sarah_selfenergy_neutrino_raw.txt",
            "E3_PREVIOUS_CONVENTION_GATE_NOT_PASSED",
        ):
            self.assertIn(text, audit)
        self.assertIn("bash scripts/zee_sarah_e3_one_shot.sh", runner)
        self.assertIn("math -script scripts/zee_sarah_e3_independent_selfenergy_audit.m", runner)
        self.assertIn("set -euo pipefail", runner)
        for text in (
            "SigmaS",
            "SigmaR",
            "SigmaL",
            "SARAH_FV_SIGMAS_FE_HM_B0_EXTRACTED_MAJORANA_AMPLITUDE_UNVALIDATED",
            "SARAH_NEUTRINO_SIGMAS_LFV_STRUCTURE_UNRESOLVED",
            "e3_sarah_neutrino_sigma_components.txt",
            "zeeScalarHasB0",
            "zeeScalarHasMassFe",
            "zeeScalarHasCpLeft",
            "zeeScalarHasCpRight",
            "zeeMasslessNeutrinoRepresentation",
            "zeeMajoranaClassified",
            "ZEE_E3_SIGMAS_COMPLEX_LNV_AMPLITUDE_VERIFIED False",
        ):
            self.assertIn(text, audit)
        self.assertNotIn("SARAH_ZEE_FULL_NEUTRINO_LOOP_PASS", audit)
        self.assertNotIn("First/@zeeRows", audit)
        self.assertNotIn("Select[zeeRows", audit)
        self.assertNotIn("SARAH_NEUTRINO_LOOP_TOPOLOGIES_EXTRACTED_MAJORANA_MASS_UNVALIDATED", audit)
        self.assertNotIn("SARAH_NEUTRINO_EXTERNAL_SECTOR_FE_HM_B0_CANDIDATE_MAJORANA_UNVALIDATED", audit)

    def test_majorana_spinor_ab_stage_is_isolated_and_fail_closed(self):
        generator = (ROOT / "scripts" / "zee_sarah_majorana_spinor_variant.py").read_text()
        wl = (ROOT / "scripts" / "zee_sarah_e3_majorana_ab_validation.m").read_text()
        sh = (ROOT / "scripts" / "zee_sarah_e3_selfenergy_one_shot.sh").read_text()
        import ast
        ast.parse(generator)
        self.assertIn('BASE_FV = "Fv -> {vL,0}"', generator)
        self.assertIn('ALT_FV = "Fv -> {vL,conj[vL]}"', generator)
        self.assertIn("restored != model", generator)
        self.assertIn("if (DEST / name).read_bytes() != source[name]", generator)
        self.assertIn("production_untouched", generator)
        self.assertIn("no_majorana_mass_added", generator)
        self.assertIn("sarah_model_variants", generator)
        self.assertIn("Fv -> {vL,0}", self.model)
        for marker in (
            "MAJORANA_AB_NOT_VALIDATED",
            "MAJORANA_AB_VARIANT_MODEL_MISSING",
            "MAJORANA_AB_SARAH_START_FAILED",
            "MAJORANA_AB_NEUTRINO_SPINOR_CLASSIFICATION_FAILED",
            "MAJORANA_AB_SIGMAS_REQUIRED_STRUCTURE_NOT_PRESENT",
            "MAJORANA_AB_NUMERIC_SIGMAS_AND_NULLS_PASS_E3_SIGN_UNVALIDATED",
            "e3_majorana_ab_sigma.txt",
            "zeeABClassified=MemberQ[MajoranaPart,Fv]",
            "zeeABSelfConjugate=(AntiField[Fv]===Fv)",
            "ZEE_E3_MAJORANA_AB_COMPLEX_MNU_MATRIX_EXTRACTED False",
            "ZEE_E3_MAJORANA_AB_CHEN_E3_NUMERIC_MATCH False",
            "ZEE_E3_MAJORANA_AB_SIGMAS_TREE_MNU_ZERO_IDENTICALLY_ZERO",
            "SigmaS_tree_mnu_zero",
            "ZEE_E3_MAJORANA_AB_SIGMAS_CP_ATOMS",
            "ZEE_E3_MAJORANA_AB_TREE_F_VERTEX_COUNT",
            "ZEE_E3_MAJORANA_AB_TREE_Y_VERTEX_COUNT",
            "ZEE_E3_MAJORANA_AB_TREE_E3_AMPLITUDE_MATCH_VERIFIED False",
            "ZEE_E3_MAJORANA_AB_CP_EXPANSION_TO_FLAVOR_COUPLINGS_VERIFIED False",
            "MAJORANA_AB_SIGMAS_COUPLING_ATOMS_NOT_IDENTIFIED",
            "e3_majorana_ab_sigma_machine.m",
            "e3_majorana_ab_sigma_couplings.txt",
            "e3_majorana_ab_physical_vertices.txt",
            "MAJORANA_AB_NUMERIC_SIGMAS_NOT_RESOLVED",
            "MAJORANA_AB_NUMERIC_MATRIX_STRUCTURE_OR_NULL_FAILURE",
            "MAJORANA_AB_NUMERIC_SIGMAS_AND_NULLS_PASS_E3_SIGN_UNVALIDATED",
            "MAJORANA_AB_UNEXPECTED_SIGMAS_ZERO_TREE_DIAGRAMS",
            "MAJORANA_AB_E3_NUMERIC_FIXTURE_MISSING",
            "ZEE_E3_MAJORANA_NUMERIC_CASE_BEGIN",
            "ZEE_E3_MAJORANA_NUMERIC_RESIDUALS",
            "ZEE_E3_MAJORANA_NULL_RESULT",
            "ZEE_E3_MAJORANA_NUMERIC_MNU_INDEPENDENTLY_MATCHED False",
            "e3_majorana_ab_numeric_matrix_report.txt",
            "zeeABScalarTerms",
            "zeeABGaugeTerms",
            "zeeABStoredVertex",
            "zeeABEvaluateVertex",
            "zeeABFiniteB0",
            "zeeABEvaluateSigma",
            "zeeABMatrix",
            "zeeABNullCases",
            "charged_masses_degenerate",
            "ZEE_E3_MAJORANA_NUMERIC_SIGNAL_MAX_EV",
            "nonzero_Zee_signal_not_detected_",
            "SARAH`CalcLoopCorrections[EWSB]",
        ):
            self.assertIn(marker, wl)
        self.assertIn("python3 scripts/zee_sarah_majorana_spinor_variant.py", sh)
        self.assertIn("math -script scripts/zee_sarah_e3_majorana_ab_validation.m", sh)
        self.assertIn("MAJORANA_AB_STAGE_NOT_STARTED", sh)
        self.assertNotIn("SA`Start[", wl)
        self.assertNotIn("SA`CalcLoopCorrections[", wl)
        self.assertNotIn("ZEE_E3_MAJORANA_NUMERIC_MNU_INDEPENDENTLY_MATCHED True", wl)
        self.assertNotIn("1.*^-9", wl[wl.index("(* FULL COMPLEX MATRIX DIAGNOSTIC"):])

    def test_no_false_validation_claims(self):
        self.assertIn("SOURCE_IMPLEMENTED_NOT_VALIDATED", self.model)
        self.assertNotIn("MakeSPheno[]", self.model)

if __name__ == "__main__":
    unittest.main()

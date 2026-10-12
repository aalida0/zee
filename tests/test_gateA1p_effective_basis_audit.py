"""A1P source-aligned direct/effective dipole basis audit regressions."""
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1p_audit_effective_operator_basis import (audit,Y,Z,HEPFIT_CODE_Z,
    check_superiso_effective_assignments,check_hepfit_nnlo_c8_basis)

def rows():
    out=[]
    for mass in (300.,700.,1000.,2000.):
        for order,ops in ((0,(7,8)),(1,(4,7,8)),(2,(3,4,5,6,7,8))):
            for op in ops:
                base=.2*op*(300./mass) if order==2 else 0.
                delta=.003*(op-3) if order==2 else 0.
                out.append({
                    "mass_GeV":mass,
                    "order":order,"operator":f"C{op}",
                    "superiso_isolated_delta":base+delta,
                    "independent_HEPfit_delta":base,
                })
    return {"compared_count":44,"compared_coefficients":out}

class TestA1PEffectiveBasis(unittest.TestCase):
    def setUp(self):
        self.effective_rhs_7=(
            "C2w[7]-1./3.*C2w[3]-4./9.*C2w[4]"
            "-20./3.*C2w[5]-80./9.*C2w[6]"
        )
        self.effective_rhs_8=(
            "C2w[8]+C2w[3]-1./6.*C2w[4]"
            "+20.*C2w[5]-10./3.*C2w[6]"
        )

    def test_pinned_hepfit_nnlo_c8_assignment_parses(self):
        # Real source excerpt from HEPfit THDMMatching::setWCbsg,
        # including line breaks and the unconventional -20*C5.
        source="""
            CWbsgArrayNNLO[7] = ( n82ct + cd82ct * lstmu
                + ce82ct * lstmu * lstmu)/tan2 +
                n82fr + cd82fr * lstmu + ce82fr * lstmu * lstmu
                + CWbsgArrayNNLO[2]
                - 1./6.*CWbsgArrayNNLO[3]
                - 20.*CWbsgArrayNNLO[4]
                - 10./3.*CWbsgArrayNNLO[5];
        """
        self.assertTrue(check_hepfit_nnlo_c8_basis(source))

    def test_hepfit_commented_debug_echo_is_not_second_assignment(self):
        # Regression for the actual upstream source: the correct NNLO
        # assignment is followed by a commented-out std::cout that
        # prints the text "CWbsgArrayNNLO[7] = ". It is not an
        # additional executable assignment.
        source="""
        switch (order) {
            case NNLO:
                CWbsgArrayNNLO[7] = (n82ct + cd82ct * lstmu
                    + ce82ct * lstmu * lstmu)/tan2 +
                    n82fr + cd82fr * lstmu + ce82fr * lstmu * lstmu
                    + CWbsgArrayNNLO[2]
                    - 1./6.*CWbsgArrayNNLO[3]
                    - 20.*CWbsgArrayNNLO[4]
                    - 10./3.*CWbsgArrayNNLO[5];
        }
        /*std::cout << "CWbsgArrayNNLO[7] = "
              << CWbsgArrayNNLO[7] << std::endl << std::endl;*/
        """
        self.assertTrue(check_hepfit_nnlo_c8_basis(source))

    def test_hepfit_nonparenthesized_second_active_assignment_rejected(self):
        # Do not overstate the source check as a general C++ parser:
        # our pinned upstream source has a parenthesized primary RHS.
        # A second parenthesized assignment must still be rejected.
        source=(
            "CWbsgArrayNNLO[7] = (n82ct)"
            " + CWbsgArrayNNLO[2] - 1./6.*CWbsgArrayNNLO[3]"
            " - 20.*CWbsgArrayNNLO[4]"
            " - 10./3.*CWbsgArrayNNLO[5];"
        )
        with self.assertRaisesRegex(ValueError,"found 2"):
            check_hepfit_nnlo_c8_basis(source+"\n"+source)

    def test_hepfit_missing_c8_assignment_rejected(self):
        with self.assertRaisesRegex(ValueError,"found 0"):
            check_hepfit_nnlo_c8_basis("CWbsgArrayNNLO[6] = 1;")

    def test_hepfit_wrong_c5_sign_rejected(self):
        source=("CWbsgArrayNNLO[7] = x + CWbsgArrayNNLO[2]"
                " -1./6.*CWbsgArrayNNLO[3]"
                " +20.*CWbsgArrayNNLO[4]"
                " -10./3.*CWbsgArrayNNLO[5];")
        with self.assertRaisesRegex(ValueError,"source terms differ"):
            check_hepfit_nnlo_c8_basis(source)

    def test_hepfit_duplicate_c8_definition_rejected(self):
        source=("CWbsgArrayNNLO[7] = x; "
                "CWbsgArrayNNLO[7] = y;")
        with self.assertRaisesRegex(ValueError,"found 2"):
            check_hepfit_nnlo_c8_basis(source)

    def test_real_and_complex_superiso_source_declarations(self):
        for declaration in ("double", "double complex"):
            src=(f"{declaration} C2w7= {self.effective_rhs_7};\n"
                 f"{declaration} C2w8= {self.effective_rhs_8};\n")
            flags=check_superiso_effective_assignments(src)
            self.assertEqual(flags,{
                "SuperIso_RG_effective_C7":True,
                "SuperIso_RG_effective_C8":True})

    def test_reject_altered_C7_coefficient(self):
        src=("double complex C2w7="+
             self.effective_rhs_7.replace("-4./9.", "+4./9.")+";\n"
             "double complex C2w8="+self.effective_rhs_8+";\n")
        with self.assertRaisesRegex(ValueError,"C2w7.*coefficients/signs"):
            check_superiso_effective_assignments(src)

    def test_reject_altered_C8_sign(self):
        src=("double complex C2w7="+self.effective_rhs_7+";\n"
             "double complex C2w8="+
             self.effective_rhs_8.replace("+20.", "-20.")+";\n")
        with self.assertRaisesRegex(ValueError,"C2w8.*coefficients/signs"):
            check_superiso_effective_assignments(src)

    def test_reject_duplicate_or_missing_source_transform(self):
        s7="double complex C2w7="+self.effective_rhs_7+";\n"
        s8="double complex C2w8="+self.effective_rhs_8+";\n"
        with self.assertRaisesRegex(ValueError,"exactly one.*C2w7"):
            check_superiso_effective_assignments(s7+s7+s8)
        with self.assertRaisesRegex(ValueError,"exactly one.*C2w8"):
            check_superiso_effective_assignments(s7)

    def test_basis_recombination_closure(self):
        source={"status":"fixture"}
        result=audit(rows(),source)
        self.assertEqual(len(result["masses"]),4)
        for entry in result["masses"]:
            for name,coeff in entry["dipole_comparisons"].items():
                self.assertAlmostEqual(
                    coeff["superiso_raw"]+coeff["superiso_standard_fourquark_shift"],
                    coeff["superiso_author_standard_effective"],places=12)
                self.assertAlmostEqual(
                    coeff["HEPfit_actual_returned_code_basis"]-
                    coeff["HEPfit_actual_code_fourquark_shift"],
                    coeff["HEPfit_raw_recovered_from_actual_source"],places=12)
                self.assertAlmostEqual(
                    coeff["HEPfit_raw_recovered_from_actual_source"]+
                    coeff["HEPfit_author_standard_fourquark_shift"],
                    coeff["HEPfit_author_standard_effective_reconstructed"],places=12)
                self.assertAlmostEqual(
                    coeff["difference_between_direct_and_effective_discrepancies"],
                    coeff["fourquark_relative_convention_spread"],places=12)
        self.assertFalse(result["theoretical_NNLO_matching_validated"])
        self.assertIsNone(result["Zee_benchmark_excluded"])

    def test_raw_effective_mixing_detected(self):
        item=audit(rows(),{"status":"fixture"})["masses"][0]["dipole_comparisons"]["C7"]
        self.assertNotAlmostEqual(
            item["previous_A1P_mixed_raw_vs_code"],
            item["matched_direct_SuperIso_minus_HEPfit"],places=6)


    def test_hepfit_c8_wrong_sign_shift_is_40_times_C5(self):
        # The original author standard has +20*C5, but the HEPfit
        # source actually contains -20*C5. It matters at NNLO.
        self.assertEqual(Z[5],20.)
        self.assertEqual(HEPFIT_CODE_Z[5],-20.)
        result=audit(rows(),{"status":"fixture"})
        for mass in result["masses"]:
            c8=mass["dipole_comparisons"]["C8"]
            correction=c8["HEPfit_code_to_author_effective_correction"]
            self.assertAlmostEqual(correction,40*c8["HEPfit_C5_NNLO"],places=12)
            self.assertAlmostEqual(
                c8["previous_A1P_direct_difference_WITH_WRONG_HEPFIT_Z5"]-
                c8["matched_direct_SuperIso_minus_HEPfit"],
                correction,places=12)
            self.assertAlmostEqual(
                c8["previous_A1P_effective_difference_WITH_WRONG_HEPFIT_Z5"]-
                c8["matched_effective_SuperIso_minus_HEPfit"],
                correction,places=12)

    def test_hepfit_c7_unaffected_by_c8_sign_inconsistency(self):
        result=audit(rows(),{"status":"fixture"})
        for mass in result["masses"]:
            c7=mass["dipole_comparisons"]["C7"]
            self.assertEqual(c7["HEPfit_code_to_author_effective_correction"],0)
            self.assertAlmostEqual(
                c7["previous_A1P_direct_difference_WITH_WRONG_HEPFIT_Z5"],
                c7["matched_direct_SuperIso_minus_HEPfit"],places=12)

    def test_missing_independent_row_blocks(self):
        fake=rows()
        fake["compared_coefficients"].pop()
        with self.assertRaisesRegex(ValueError,"44-row"):
            audit(fake,{})

    def test_weight_vectors_align_author_supplement(self):
        self.assertAlmostEqual(Y[3],-1/3)
        self.assertAlmostEqual(Y[4],-4/9)
        self.assertAlmostEqual(Y[5],-20/3)
        self.assertAlmostEqual(Y[6],-80/9)
        self.assertAlmostEqual(Z[3],1.)
        self.assertAlmostEqual(Z[4],-1/6)
        self.assertAlmostEqual(Z[5],20.)
        self.assertAlmostEqual(Z[6],-10/3)

if __name__=="__main__": unittest.main()

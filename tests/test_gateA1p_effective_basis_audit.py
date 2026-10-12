"""A1P source-aligned direct/effective dipole basis audit regressions."""
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1p_audit_effective_operator_basis import (audit,Y,Z,
    check_superiso_effective_assignments)

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
                    coeff["superiso_raw"]+coeff["superiso_fourquark_basis_shift"],
                    coeff["superiso_effective"],places=12)
                self.assertAlmostEqual(
                    coeff["HEPfit_effective"]-coeff["HEPfit_fourquark_basis_shift"],
                    coeff["HEPfit_direct"],places=12)
                self.assertAlmostEqual(
                    coeff["difference_between_direct_and_effective_discrepancies"],
                    coeff["fourquark_relative_convention_spread"],places=12)
        self.assertFalse(result["theoretical_NNLO_matching_validated"])
        self.assertIsNone(result["Zee_benchmark_excluded"])

    def test_raw_effective_mixing_detected(self):
        item=audit(rows(),{"status":"fixture"})["masses"][0]["dipole_comparisons"]["C7"]
        self.assertNotAlmostEqual(
            item["SuperIso_raw_minus_HEPfit_effective_INVALID_MIXED_BASIS"],
            item["matched_direct_SuperIso_minus_HEPfit"],places=6)

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

"""A1P source-aligned direct/effective dipole basis audit regressions."""
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1p_audit_effective_operator_basis import audit,Y,Z

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

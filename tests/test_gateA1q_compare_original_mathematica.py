"""Gate A1Q numerical author evaluation input, parsing and basis tests."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1q_compare_original_mathematica import (
    MASSES,OPS,make_inputs,parse_wolfram_number,
    read_authors_values,compare,
)
from gateA1p_audit_effective_operator_basis import Y,Z,HEPFIT_CODE_Z

def original_rows():
    rows=[]
    for mass in MASSES:
        for order,ops in {0:(7,8),1:(4,7,8),
                          2:(3,4,5,6,7,8)}.items():
            for op in ops:
                rows.append({
                    "mass_GeV":mass,"order":order,"operator":f"C{op}",
                    "superiso_isolated_delta":op*.01+order*.1,
                    "independent_HEPfit_delta":op*.02+order*.2,
                })
    assert len(rows)==44
    return {"compared_count":44,"compared_coefficients":rows,
            "running_mt_muW_GeV":163.10709645657508,
            "muW_GeV":160.7384,"tanbeta":5.597170833164245}
def author_reference():
    return {(m,order,op):1. for m in MASSES
            for order,ops in OPS.items() for op in ops}

class TestA1QNumeric(unittest.TestCase):
    def test_input_decomposes_to_exact_rationals(self):
        c=make_inputs(original_rows())
        self.assertEqual(c["mt_numerator"],"4077677411414377")
        self.assertEqual(c["mt_denominator"],"25000000000000")
        self.assertEqual(c["masses_GeV"],[300,700,1000,2000])
        self.assertEqual(c["Yukawa_convention"]["Ad"],"-tanbeta")

    def test_wolfram_precision_and_exponent_parse(self):
        self.assertAlmostEqual(parse_wolfram_number("3.34"+chr(96)+
                              "19.*^-2"),.0334)
        self.assertAlmostEqual(parse_wolfram_number("-0.50000000"),-.5)
        for value in ("Indeterminate","1+I","Infinity","nan"):
            with self.assertRaises(ValueError):
                parse_wolfram_number(value)

    def test_exact_reference_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"values.txt"
            lines=["STATUS A1Q_ORIGINAL_AUTHOR_NUMERICAL_VALUES_NO_BR"]
            for m in MASSES:
                for order,ops in OPS.items():
                    for op in ops:
                        lines.append(
                            f"AUTHOR mass={m} order={order} op={op} value=1.25")
            f.write_text("\n".join(lines)+"\n")
            parsed=read_authors_values(f)
            self.assertEqual(len(parsed),48)
            self.assertEqual(parsed[300,2,8],1.25)
            f.write_text("\n".join(lines[0:-1])+"\n")
            with self.assertRaisesRegex(ValueError,"coverage differs"):
                read_authors_values(f)

    def test_wrong_a1p_count_blocks(self):
        data=original_rows()
        data["compared_count"]=43
        with self.assertRaisesRegex(ValueError,"44"):
            make_inputs(data)

    def test_nnlo_standard_effective_C8_corrects_HEPfit_minus20(self):
        data=original_rows()
        rows=compare(author_reference(),data,make_inputs(data))["comparison_rows"]
        r=next(item for item in rows if
               item["mass_GeV"]==700 and item["author_order"]==2
               and item["operator"]=="C8")
        coeff={int(z["operator"][1:]):z for z in
               data["compared_coefficients"] if z["mass_GeV"]==700
               and z["order"]==2}
        hf=coeff[8]["independent_HEPfit_delta"]
        c5=coeff[5]["independent_HEPfit_delta"]
        self.assertAlmostEqual(r["HEPfit_in_author_basis"],hf+40*c5)
        expected_si=coeff[8]["superiso_isolated_delta"]+sum(
            weight*coeff[op]["superiso_isolated_delta"]
            for op,weight in Z.items())
        self.assertAlmostEqual(r["SuperIso_in_author_basis"],expected_si)

    def test_nnlo_raw_dipole_undoes_actual_HEPfit_rotation(self):
        data=original_rows()
        rows=compare(author_reference(),data,make_inputs(data))["comparison_rows"]
        raw=next(item for item in rows if
               item["mass_GeV"]==700 and item["author_order"]==3
               and item["operator"]=="C8")
        coeff={int(z["operator"][1:]):z for z in
               data["compared_coefficients"] if z["mass_GeV"]==700
               and z["order"]==2}
        expected=coeff[8]["independent_HEPfit_delta"]-sum(
            w*coeff[i]["independent_HEPfit_delta"]
            for i,w in HEPFIT_CODE_Z.items())
        self.assertAlmostEqual(raw["HEPfit_in_author_basis"],expected)
        self.assertAlmostEqual(raw["SuperIso_in_author_basis"],
                               coeff[8]["superiso_isolated_delta"])

    def test_nlo_effective_uses_only_available_C4_rotation(self):
        data=original_rows()
        rows=compare(author_reference(),data,make_inputs(data))["comparison_rows"]
        c7=next(item for item in rows if
                item["mass_GeV"]==300 and item["author_order"]==1
                and item["operator"]=="C7")
        nlo={int(z["operator"][1:]):z for z in
             data["compared_coefficients"] if z["mass_GeV"]==300
             and z["order"]==1}
        want=nlo[7]["superiso_isolated_delta"] + \
             Y[4]*nlo[4]["superiso_isolated_delta"]
        self.assertAlmostEqual(c7["SuperIso_in_author_basis"],want)

    def test_no_full_NNLO_BR_or_exclusion_asserted(self):
        data=original_rows()
        report=compare(author_reference(),data,make_inputs(data))
        self.assertEqual(report["comparison_rows_count"],48)
        self.assertFalse(report["full_NNLO_matching_validated"])
        self.assertFalse(report["BtoXs_gamma_BR_validated"])
        self.assertIsNone(report["Zee_benchmark_allowed"])
        self.assertIsNone(report["Zee_benchmark_excluded"])

if __name__=="__main__":
    unittest.main()

"""Read-only A1P finite-three-loop probe arithmetic and parser tests."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1p_audit_nnlo_finite_functions import (
    read_finite,decompose,raw_hepfit,MASSES)
from gateA1p_audit_effective_operator_basis import HEPFIT_CODE_Z,Y

def fixture():
    rows=[
        "STATUS GATE_A1P_ACTUAL_SUPERISO_THREE_LOOP_FINITE_HELPERS_NO_BR",
        "INPUT mt_fixed_GeV=163.10709645657508",
    ]
    for m in MASSES:
        for op in (7,8):
            rows.append(f"FINITE mH={m:.17g} op={op} term=ct value={op*.125:.17g}")
            rows.append(f"FINITE mH={m:.17g} op={op} term=fr value={-op*.5:.17g}")
    return rows

class TestA1PFiniteMatching(unittest.TestCase):
    def test_direct_cot2_and_cross_term_decomposition(self):
        cot_part,fr_part=5.72,-1.333
        t1,t2=5.597170833164245,2*5.597170833164245
        d1=cot_part/t1**2+fr_part
        d2=cot_part/t2**2+fr_part
        c,f=decompose(d1,d2,t1,t2)
        self.assertAlmostEqual(c,cot_part,places=12)
        self.assertAlmostEqual(f,fr_part,places=12)

    def test_finite_parser_completeness(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            f.write_text("\n".join(fixture())+"\n")
            data=read_finite(f,163.10709645657508)
            self.assertEqual(len(data),16)
            self.assertAlmostEqual(data[700.,8,"ct"],1.)

    def test_finite_parser_rejects_missing_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            f.write_text("\n".join(fixture()[:-1])+"\n")
            with self.assertRaisesRegex(ValueError,"Missing/unexpected"):
                read_finite(f,163.10709645657508)

    def test_finite_parser_rejects_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            lines=fixture()
            f.write_text("\n".join(lines+[lines[2]])+"\n")
            with self.assertRaisesRegex(ValueError,"Duplicated"):
                read_finite(f,163.10709645657508)

    def test_finite_parser_rejects_wrong_mt(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            f.write_text("\n".join(fixture())+"\n")
            with self.assertRaisesRegex(ValueError,"top mass mismatch"):
                read_finite(f,163.0)

    def test_hepfit_actual_c8_minus20_shift(self):
        vec={(2,i):i*0.043 for i in (3,4,5,6,7,8)}
        code_direct=vec[2,8]-sum(HEPFIT_CODE_Z[i]*vec[2,i]
                                   for i in (3,4,5,6))
        self.assertAlmostEqual(raw_hepfit(vec,8),code_direct)
        standard_wrong=vec[2,8]-sum(
            {3:1,4:-1/6,5:20,6:-10/3}[i]*vec[2,i]
            for i in (3,4,5,6))
        self.assertAlmostEqual(
            raw_hepfit(vec,8)-standard_wrong,40.*vec[2,5])

    def test_hepfit_c7_basis_uses_y_vector(self):
        vec={(2,i):i*.01 for i in (3,4,5,6,7,8)}
        reference=vec[2,7]-sum(Y[i]*vec[2,i] for i in (3,4,5,6))
        self.assertAlmostEqual(raw_hepfit(vec,7),reference)

    def test_degenerate_tanbeta_controls_rejected(self):
        with self.assertRaisesRegex(ValueError,"degenerate"):
            decompose(1.,2.,5.,5.)

if __name__=="__main__":
    unittest.main()

"""F4 deterministic contract tests; NOT EOS/SuperIso physics tests."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from zee_gateF4_typeii_basis_interface_pilot import (
    audit_low_basis_source, raw_for_eos, Y7, Y8,
)

def fixture():
    lines = ["void C_calculator_base1() {"]
    for j in (0, 1, 2):
        lines += [
            f"double complex C{j}w7= C{j}w[7]-1./3.*C{j}w[3]-4./9.*C{j}w[4]-20./3.*C{j}w[5]-80./9.*C{j}w[6];",
            f"double complex C{j}w8= C{j}w[8]+C{j}w[3]-1./6.*C{j}w[4]+20.*C{j}w[5]-10./3.*C{j}w[6];"]
    for op in (7, 8):
        lines.append(f"""if(je=={op}) {{
        C0b[ie]+=U0[ie-1][je-1]*C0w{op};
        C1b[ie]+=eta*(U0[ie-1][je-1]*C1w{op}+U1[ie-1][je-1]*C0w{op});
        C2b[ie]+=eta*eta*(U0[ie-1][je-1]*C2w{op}+U1[ie-1][je-1]*C1w{op});
        }}""")
    return "\n".join(lines + ["}", "void C_calculator_base2() {}"])

class F4BasisContract(unittest.TestCase):
    def test_source_shape(self):
        self.assertTrue(audit_low_basis_source(fixture())[
            "no_explicit_low_dipole_inverse_in_base1"])

    def test_reject_wrong_c8_sign(self):
        bad = fixture().replace("+20.*C1w[5]", "-20.*C1w[5]")
        with self.assertRaises(ValueError):
            audit_low_basis_source(bad)

    def test_reject_unexpected_low_reconversion(self):
        bad = fixture().replace("void C_calculator_base2()",
                                "C0b[7]=C0b[7]+C0b[3];\nvoid C_calculator_base2()")
        with self.assertRaises(ValueError):
            audit_low_basis_source(bad)

    def test_inverse_rotation_closes(self):
        eff = {n:0.013*n for n in range(1,9)}
        eff[7]=-0.04
        eff[8]=0.07
        raw = raw_for_eos(eff)
        for op,weights in ((7,Y7),(8,Y8)):
            self.assertAlmostEqual(raw[op]+sum(w*raw[i] for i,w in weights.items()),eff[op])
        self.assertNotEqual(raw[7],eff[7])
        self.assertNotEqual(raw[8],eff[8])

    def test_missing_or_nonfinite_rejected(self):
        for inp in ({7:0.}, {i:float("nan") for i in range(1,9)}):
            with self.assertRaises(ValueError):
                raw_for_eos(inp)

if __name__ == "__main__":
    unittest.main()

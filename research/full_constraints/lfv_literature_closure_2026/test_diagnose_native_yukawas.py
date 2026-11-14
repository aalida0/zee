"""Synthetic tests for read-only *mismatch* diagnostics, not physical LFV."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
from .diagnose_native_yukawas import _comparison,inspect_case,latest_case

def b(name,m):
    z=["BLOCK "+name]
    for i in range(3):
        for j in range(3):
            z.append(f" {i+1} {j+1} {float(m[i,j].real):.17e}")
    z.append("BLOCK IM"+name)
    for i in range(3):
        for j in range(3):
            z.append(f" {i+1} {j+1} {float(m[i,j].imag):.17e}")
    return "\n".join(z)+"\n"

class MatrixAuditTests(unittest.TestCase):
    def test_complex_scaling_and_direction_diagnosis(self):
        f=np.array([[0,1+2j,-3j],[-1-2j,0,2], [3j,-2,0]],complex)*1e-3
        a=_comparison(f,f*1.02)
        self.assertAlmostEqual(a["max_relative_to_source_max"],.02,places=9)
        self.assertAlmostEqual(a["best_complex_multiplicative_factor"][0],1.02,places=9)
        self.assertLess(a["residual_after_best_complex_scale"],1e-13)
        x=_comparison(f,f.conj())
        self.assertAlmostEqual(x["direction_candidates_normalized_residuals"]["conjugate"],0.)
        self.assertGreater(x["direction_candidates_normalized_residuals"]["direct"],0.1)

    def test_slha_natives_and_original_in_block_independent(self):
        f=np.array([[0,1+2j,0],[-1-2j,0,3j],[0,-3j,0]],complex)*1e-3
        y=np.eye(3,dtype=complex)*1e-3
        with tempfile.TemporaryDirectory() as t:
            work=Path(t)
            case=work/'EDM3ZERO_SOURCE64_00000000'/'native-source-64-results'/'Zee_1234_NO_1'
            case.mkdir(parents=True)
            inp=("BLOCK MINPAR\n 10 2.0\nBLOCK SPHENOINPUT\n 57 1\n"+
                 b('FZEEIN',f)+b('YEE2IN',y))
            out=("BLOCK MINPAR\n 10 2.0\nBLOCK MASS\n 25 125.\n"+
                 b('FZEE',f*1.01)+b('YEE2',y)+b('YE',y))
            (case/'input.in').write_text(inp)
            (case/'output.spc').write_text(out)
            r=inspect_case(case)
            self.assertLess(abs(r['FZEE']['max_relative_to_source_max']-.01),1e-12)
            self.assertEqual(r['YEE2']['max_relative_to_source_max'],0.)
            self.assertEqual(r["input_stems"]["F"],"FZEEIN")
            self.assertEqual(latest_case(work),case)
            self.assertIsNone(r['full_physical_LFV'])
            self.assertIn("native_reconstructed_D",r)

if __name__=='__main__':
    unittest.main()

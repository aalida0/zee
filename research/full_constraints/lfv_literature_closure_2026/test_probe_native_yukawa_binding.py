"""Synthetic validation of native Yukawa input microperturbation only."""
import unittest
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import (
    split_slha,block_values)
from .probe_native_yukawa_binding import scaled_matrix_entries

def matrix(name):
    rows=["BLOCK "+name+"\n"]
    for i in range(1,4):
        for j in range(1,4):
            value=(0 if i==j else float(i-j)*1e-5)
            rows.append(f" {i} {j} {value:.17e}\n")
    rows+=["BLOCK IM"+name+"\n"]
    for i in range(1,4):
        for j in range(1,4):
            value=(0 if i==j else float(i-j)*1e-6)
            rows.append(f" {i} {j} {value:.17e}\n")
    return "".join(rows)

BASE=("BLOCK MINPAR\n 10 3.0\nBLOCK SPHENOINPUT\n 11 0\n 57 1\n"+
      matrix("FZEEIN")+matrix("YEE2IN")+"BLOCK SPHENOINPUT\n 11 1\n")

class InputProbeTest(unittest.TestCase):
    def test_f_antisymmetric_and_unrelated_slha_untouched(self):
        updated=scaled_matrix_entries(BASE,"FZEEIN",2.0,((1,2),(2,1)))
        old=split_slha(BASE,allowed_repeated=("SPHENOINPUT",))
        new=split_slha(updated,allowed_repeated=("SPHENOINPUT",))
        for k in ("MINPAR","SPHENOINPUT","YEE2IN","IMYEE2IN"):
            self.assertEqual(old[k],new[k])
        for k in ("FZEEIN","IMFZEEIN"):
            x,y=block_values(old[k]),block_values(new[k])
            self.assertEqual(y[(1,2)],2*x[(1,2)])
            self.assertEqual(y[(2,1)],2*x[(2,1)])
            self.assertEqual(y[(3,3)],0.)
        self.assertEqual(updated.count("BLOCK SPHENOINPUT"),2)
    def test_yee2_diagonal_and_unrelated_f_fixed(self):
        updated=scaled_matrix_entries(BASE,"YEE2IN",2.0,((3,3),))
        sec=split_slha(updated,allowed_repeated=("SPHENOINPUT",))
        sec0=split_slha(BASE,allowed_repeated=("SPHENOINPUT",))
        self.assertEqual(sec0["FZEEIN"],sec["FZEEIN"])
        self.assertEqual(sec0["IMFZEEIN"],sec["IMFZEEIN"])
        self.assertEqual(len(block_values(sec["YEE2IN"])),9)
    def test_fail_closed_on_block_absence_and_zero_perturbation(self):
        with self.assertRaises(ValueError):
            scaled_matrix_entries(BASE,"WRONGNAME",2.,((1,2),))
        for factor in (0,1,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                scaled_matrix_entries(BASE,"FZEEIN",factor,((1,2),))
if __name__=="__main__":unittest.main()

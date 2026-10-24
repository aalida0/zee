#!/usr/bin/env python3
"""F19b focused test: SLHA complex Yukawa mapping and honest LFV outcomes.
Synthetic matrices only; physical numerical results are run at CERN.
"""
from __future__ import annotations
import math,sys,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_paper1_F19b_exact_F17f_neutrino_partial_LFV as m

def fake_source():
    b=1.1
    f=np.array([[0,1.5e-4+0.2e-4j,-2.0e-4j],
                [-1.5e-4-0.2e-4j,0,4.0e-4],
                [2.0e-4j,-4.0e-4,0]],complex)
    y=np.array([[.0001+.00003j,.001,0j],
                [.002j,.003,0j],[.0002,0j,.004]],complex)
    v=246.21965
    mass=np.array([.00051099895,.1056583755,1.77686],float)
    ye=math.cos(b)*np.diag(np.sqrt(2)*mass/v)-math.sin(b)*np.sqrt(2)*y
    ye2=math.sin(b)*np.diag(np.sqrt(2)*mass/v)+math.cos(b)*np.sqrt(2)*y
    mats={"FSARAH":2*f,"YeSARAH":ye,"Ye2SARAH":ye2,"YChen":y}
    def encode(z):return [[[float(a.real),float(a.imag)] for a in row] for row in z]
    row={"vev_GeV":v,"lepton_masses_GeV":mass.tolist(),
         "matrices_re_im":{k:encode(z) for k,z in mats.items()}}
    lines=[]
    for key,name in (("FSARAH","FZEE"),("YeSARAH","YE"),("Ye2SARAH","YEE2")):
        for block,arr in ((name,mats[key].real),("IM"+name,mats[key].imag)):
            lines.append("BLOCK "+block)
            for i in range(3):
                for j in range(3):
                    lines.append(f" {i+1} {j+1} {arr[i,j]:.17e}")
    return row,("\n".join(lines)+"\n").encode(),b,f,y

class TestF19bExactComplexYukawa(unittest.TestCase):
    def test_original_complex_source_and_slha_match(self):
        row,card,b,f,y=fake_source()
        obsF,obsY,proof=m.lepton_basis_from_two_sources(row,card,{"beta":b})
        self.assertLess(np.max(abs(f-obsF)),1e-12)
        self.assertLess(np.max(abs(y-obsY)),1e-12)
        self.assertTrue(proof["Ye_Ye2_to_YChen_rotation"])
    def test_complex_imaginary_source_tamper_rejected(self):
        row,card,b,_,_=fake_source()
        altered=card.replace(b" 1 2 0.00000000000000000e+00",b" 1 2 9.00000000000000000e-01")
        self.assertNotEqual(card,altered)
        with self.assertRaises(ValueError):
            m.lepton_basis_from_two_sources(row,altered,{"beta":b})
    def test_duplicate_slot_fails_closed(self):
        row,card,b,_,_=fake_source()
        corrupted=card+b"BLOCK FZEE\n 1 1 0.0\n"
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            m.lepton_basis_from_two_sources(row,corrupted,{"beta":b})
    def test_missing_imaginary_matrix_fails_closed(self):
        row,card,b,_,_=fake_source()
        corrupted=card.split(b"BLOCK IMFZEE",1)[0]
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            m.lepton_basis_from_two_sources(row,corrupted,{"beta":b})
    def test_central_neutrino_and_full_lfv_must_remain_unresolved(self):
        self.assertIn("partial",m.STATUS.lower())
        self.assertTrue(any("conversion" in x for x in m.OMITTED))
        self.assertTrue(any("likelihood" in x for x in m.OMITTED))

if __name__=="__main__":unittest.main()

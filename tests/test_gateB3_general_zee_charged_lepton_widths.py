"""Regression tests for B3 general-Zee charged leptonic width replacement."""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate6_width_inventory import tau_width, inventory
from gateA1b_hierarchical_no_seed import (
    MTAU, target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,
)
from gateB3_general_zee_charged_lepton_widths import (
    STATUS,charged_lepton_widths,complex_matrix,
    evaluate,run,
)

class TestGateB3(unittest.TestCase):
    def setUp(self):
        self.row={"id":"0","mH1":300.,"mH2":700.,
                  "mh2":580.7,"ma":633.7,"beta":1.394,
                  "alpha":1.398,"gamma":1.089,"m12sq":57700.,
                  "lc":4.473,"k1":1.082,"k2":.00398,
                  "k12":-.001266}
        self.M,_=target_neutrino_matrix()
        self.f,_=antisymmetric_f_with_null_condition(self.M)
        self.Y,rank,_=solve_lepton_yukawa(self.f,self.M)
        self.assertEqual(rank,5)

    def test_reproduce_typeii_tau_width_when_Y_set_to_typeii(self):
        f=np.zeros((3,3),complex)
        Y=np.zeros((3,3),complex)
        tanb=math.tan(self.row["beta"])
        Y[2,2]=MTAU*tanb/246.21965
        g=self.row["gamma"]
        v=charged_lepton_widths(300.,700.,g,f,Y)
        self.assertAlmostEqual(v["H1"]["tau"],tau_width(
            300.,tanb,math.cos(g)**2),delta=2e-5)
        self.assertAlmostEqual(v["H2"]["tau"],tau_width(
            700.,tanb,math.sin(g)**2),delta=2e-5)
        self.assertEqual(v["H1"]["e"],0.)

    def test_singlet_and_doublet_mixing_weights(self):
        f=np.zeros((3,3),complex);f[0,1]=1.e-3;f[1,0]=-1.e-3
        Y=np.zeros((3,3),complex);Y[2,2]=.001
        g=.61
        v=charged_lepton_widths(300.,700.,g,f,Y)
        x1=v["H1"]["e"]/300./math.sin(g)**2
        x2=v["H2"]["e"]/700./math.cos(g)**2
        self.assertAlmostEqual(x1,x2,places=16)
        y1=v["H1"]["tau"]/300./math.cos(g)**2
        y2=v["H2"]["tau"]/700./math.sin(g)**2
        self.assertAlmostEqual(y1,y2,places=16)

    def test_real_neutrino_seed_and_lepton_replacement(self):
        r=evaluate(self.row,self.f,self.Y,self.M)
        self.assertLess(r["neutrino_matrix_closure_eV"],1e-9)
        self.assertGreater(r["totals_included_GeV"]["H2"],0)
        self.assertIn("tau_nu_generalZee",
                      r["partial_widths_included_GeV"]["H2"])
        self.assertNotIn("tau_nu_TypeII",
                         r["partial_widths_included_GeV"]["H2"])
        self.assertLess(r["BR_H2_H1Z_included_general_Zee"],1.)
        self.assertLessEqual(r["production_weighted_partial_cascade_proxy"],1.)
        self.assertIn("NOT_ALLOWED",r["status"])

    def test_f_must_be_antisymmetric(self):
        f=np.eye(3,dtype=complex)
        with self.assertRaisesRegex(ValueError,"antisymmetric"):
            charged_lepton_widths(300.,700.,1.,f,np.zeros((3,3)))

    def test_saved_complex_arrays_strict(self):
        for invalid in ({"real":[1,2],"imag":[1,2]},
                        {"real":[[0.]*3]*3},
                        {"real":[[float("nan")]*3]*3,
                         "imag":[[0.]*3]*3}):
            with self.assertRaisesRegex(ValueError,"matrix|Nonfinite"):
                complex_matrix(invalid,"f")

    def test_integrated_csv_and_B2_Yukawa_pair(self):
        with tempfile.TemporaryDirectory() as d:
            b1=Path(d)/"b1.csv";b2=Path(d)/"b2.json"
            b1.write_text(",".join(
                ("id","mH1","mH2","mh2","ma","alpha","beta",
                 "gamma","m12sq"))+"\n"+
                "0,300,700,580.7,633.7,1.398,1.394,1.089,57700\n")
            c=lambda z:{"real":z.real.tolist(),"imag":z.imag.tolist()}
            b2.write_text(json.dumps({"0":[{
                "candidate_id":"0","f":c(self.f),"Y":c(self.Y),
                "partial_LFV_score_NOT_EXCLUSION":1e-5,
            }]}))
            rows=run(b1,b2,1)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["candidate_id"],"0")
            self.assertIn("NOT_ALLOWED",STATUS)

if __name__=="__main__":
    unittest.main()

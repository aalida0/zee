"""Gate B2: randomized complex neutrino-kernel regression and safety labels."""
from __future__ import annotations
import csv
import math
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,scalar_kappa,
    reconstruct_neutrino,
)
from gateB2_zee_neutrino_family_scan import (
    STATUS,read_candidates,f_from_null_parameter,
    linear_neutrino_operator,family_yukawa,solve_point,
)

class TestGateB2(unittest.TestCase):
    def setUp(self):
        self.M,_=target_neutrino_matrix()
        self.p={"id":"0","mH1":300.,"mH2":700.,
                "mh2":580.7,"ma":633.7,
                "beta":1.394,"alpha":1.398,"gamma":1.089}
        self.kap=scalar_kappa(300.,700.,1.089)

    def test_default_minimum_norm_seed_still_closes(self):
        f,_=antisymmetric_f_with_null_condition(self.M)
        rng=np.random.default_rng(10)
        Y,err=family_yukawa(f,self.M,self.kap,rng,0.)
        self.assertLess(err,1e-9)
        self.assertLess(float(np.max(abs(reconstruct_neutrino(
            f,Y,kappa=self.kap)-self.M))),1e-9)

    def test_four_complex_yukawa_null_modes(self):
        f,_=antisymmetric_f_with_null_condition(self.M)
        A=linear_neutrino_operator(f,self.kap)
        self.assertEqual(A.shape,(6,9))
        _,ss,vh=np.linalg.svd(A,full_matrices=True)
        self.assertEqual(sum(ss>ss[0]*1e-13),5)
        self.assertEqual(vh[5:,:].shape,(4,9))
        self.assertLess(np.max(abs(A@vh[5:,:].conj().T)),1e-8)

    def test_randomized_f_complex_family_is_exact(self):
        rng=np.random.default_rng(13)
        for i in range(15):
            t=complex(rng.uniform(-1.,1.),rng.uniform(-1.,1.))
            f=f_from_null_parameter(self.M,t,10**rng.uniform(-5.,-2.),
                                    root=i%2)
            self.assertLess(np.max(abs(f+f.T)),1e-13)
            Y,err=family_yukawa(f,self.M,self.kap,rng,strength=2.)
            self.assertLess(err,1e-9)

    def test_single_point_computes_partial_lfv_not_physical_pass(self):
        f,_=antisymmetric_f_with_null_condition(self.M)
        point=solve_point(self.p,self.M,f,np.random.default_rng(2),0.)
        self.assertIsNotNone(point)
        self.assertLess(point["neutrino_matrix_closure_eV"],1e-9)
        self.assertIn("NOT_ALLOWED",point["status"])
        self.assertGreaterEqual(point["partial_LFV_score_NOT_EXCLUSION"],0.)

    def test_csv_requires_exact_scalar_context(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"B1.csv"
            path.write_text("\n".join((
                "id,mH1,mH2,mh2,ma,beta,alpha,gamma",
                "0,300,700,580.7,633.7,1.394,1.398,1.089",
                "32,208.7695,681.8519,597.7198,635.226,1.394,1.398,1.12012",
            ))+"\n")
            rows=read_candidates(path)
            self.assertEqual(len(rows),2)
            self.assertEqual([p["id"] for p in rows],["0","32"])
            with self.assertRaisesRegex(ValueError,"duplicate"):
                path.write_text(path.read_text().replace("32,208","0,208"))
                read_candidates(path)

    def test_no_exclusion_implemented(self):
        self.assertIn("NOT_ALLOWED",STATUS)

if __name__=="__main__":
    unittest.main()

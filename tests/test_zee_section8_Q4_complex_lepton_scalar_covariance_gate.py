"""Q4 full-Zee complex rephasing/FLS lepton gate; synthetic beta regression."""
import math
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_complex_lepton_scalar_covariance_gate import (
    ALL_NAMES, CHARGE, COMPLEX_SCALAR, REAL_SCALAR,
    physical_complex_input, field_rephase, independent_fls_lepton,
    check_covariance, check_conjugation, check_lepton_limits, compare,
)

def mock_module(with_lepton_f=True):
    """Toy beta system covariant under H2 and chi rephasings."""
    namespace={}
    for i,name in enumerate(ALL_NAMES):
        # A real linear beta is automatically covariant under field
        # rephasings and complex conjugation; this is a test fixture only.
        local={}
        exec("def beta_"+name+"(nLoop, "+name+"):\n"
             "    return "+str(.25+.013*i)+" * "+name+"\n",{},local)
        namespace["beta_"+name]=local["beta_"+name]

    def fake_lepton(nLoop,Yu1,Yu2,Yd1,Yd2,Ye1,Ye2,f,gp,g2,which):
        yy={"Yu1":Yu1,"Yu2":Yu2,"Yd1":Yd1,"Yd2":Yd2,
            "Ye1":Ye1,"Ye2":Ye2}
        source=independent_fls_lepton(yy,gp,g2)[which]
        if with_lepton_f:
            # f f† is invariant under chi rephasing, and contracts
            # the external lepton-doublet index of Pi_k.
            fmat=np.asarray(f,complex)
            source=source+3*(fmat@fmat.conj().T)@np.asarray(yy[which],complex)
        return source
    def beta_Ye1(nLoop,Yu1,Yu2,Yd1,Yd2,Ye1,Ye2,f,gp,g2):
        return fake_lepton(nLoop,Yu1,Yu2,Yd1,Yd2,Ye1,Ye2,f,gp,g2,"Ye1")
    def beta_Ye2(nLoop,Yu1,Yu2,Yd1,Yd2,Ye1,Ye2,f,gp,g2):
        return fake_lepton(nLoop,Yu1,Yu2,Yd1,Yd2,Ye1,Ye2,f,gp,g2,"Ye2")
    namespace.update({"beta_Ye1":beta_Ye1,"beta_Ye2":beta_Ye2})
    return SimpleNamespace(**namespace)

class TestQ4ComplexCovariance(unittest.TestCase):
    def setUp(self):
        self.values=physical_complex_input()
    def test_exact_antisymmetric_complex_f_fixture(self):
        f=np.asarray(self.values["f"])
        self.assertEqual(f.shape,(3,3))
        self.assertLess(np.max(np.abs(f+f.T)),1e-14)
        self.assertGreater(np.max(np.abs(f.imag)),1e-3)
    def test_higgs2_and_singlet_phase_weights(self):
        theta,psi=.41,-.6
        out=field_rephase(self.values,theta,psi)
        self.assertTrue(np.allclose(out["Yu2"],np.exp(1j*theta)*self.values["Yu2"]))
        self.assertTrue(np.allclose(out["Yd2"],np.exp(-1j*theta)*self.values["Yd2"]))
        self.assertTrue(np.allclose(out["Ye2"],np.exp(-1j*theta)*self.values["Ye2"]))
        self.assertTrue(np.allclose(out["f"],np.exp(-1j*psi)*self.values["f"]))
        self.assertAlmostEqual(out["l5"],np.exp(-2j*theta)*self.values["l5"])
        self.assertAlmostEqual(out["l10"],np.exp(-1j*theta)*self.values["l10"])
        self.assertAlmostEqual(out["muZee"],
                               np.exp(1j*(-theta+psi))*self.values["muZee"])
        self.assertEqual(out["l1"],self.values["l1"])
        self.assertEqual(set(CHARGE)&REAL_SCALAR,set())
    def test_fls_lepton_diagonal_single_doublet_limit(self):
        y=.023
        zero=np.zeros((3,3),complex)
        yy={k:zero.copy() for k in ("Yu1","Yu2","Yd1","Yd2","Ye1","Ye2")}
        yy["Ye1"]=np.eye(3)*y
        ref=independent_fls_lepton(yy,0.,0.)
        np.testing.assert_allclose(ref["Ye1"],4.5*y**3*np.eye(3),atol=1e-17)
        np.testing.assert_allclose(ref["Ye2"],np.zeros((3,3)),atol=1e-17)
    def test_mock_betas_rephase_covariant_all_26(self):
        module=mock_module()
        for t,p in ((.41,0.),(0.,-.6),(.41,-.6)):
            r=check_covariance(module,self.values,t,p)
            self.assertEqual(len(r),26+len(REAL_SCALAR))
            self.assertTrue(all(z["pass"] for z in r.values()),
                            [(k,z) for k,z in r.items() if not z["pass"]])
    def test_mock_betas_conjugation_covariant_all_26(self):
        r=check_conjugation(mock_module(),self.values)
        self.assertEqual(len(r),26)
        self.assertTrue(all(z["pass"] for z in r.values()),r)
    def test_fls_and_genuine_f_feedback_toy(self):
        r=check_lepton_limits(mock_module(),self.values)
        self.assertTrue(all(z["pass"] for z in r.values()),
                        [(k,z) for k,z in r.items() if not z["pass"]])
        self.assertGreater(r["f_lepton_feedback_nonzero_Ye1"]["max_abs_f2_feedback"],1e-9)
    def test_missing_lepton_f_feedback_rejected(self):
        r=check_lepton_limits(mock_module(with_lepton_f=False),self.values)
        self.assertFalse(r["f_lepton_feedback_nonzero_Ye1"]["pass"])
        self.assertFalse(r["f_lepton_feedback_nonzero_Ye2"]["pass"])
        self.assertTrue(r["FLS_f_zero_Ye1"]["pass"])
        self.assertTrue(r["FLS_f_zero_Ye2"]["pass"])
    def test_wrong_l10_complex_rephase_detected(self):
        module=mock_module()
        module.beta_l10=lambda nLoop,l10: np.conjugate(l10)
        res=check_covariance(module,self.values,.43,-.76)
        self.assertFalse(res["l10"]["pass"])
    def test_complex_beta_for_real_quartic_rejected(self):
        module=mock_module()
        module.beta_l1=lambda nLoop,l1: l1+.11j
        res=check_covariance(module,self.values,.43,-.76)
        self.assertFalse(res["l1_realness"]["pass"])
    def test_quark_direct_f_artifact_detected(self):
        module=mock_module()
        module.beta_Yu1=lambda nLoop,Yu1,f: Yu1+np.asarray(f).conj().T@np.asarray(f)@np.asarray(Yu1)
        res=check_lepton_limits(module,self.values)
        self.assertFalse(res["quark_no_direct_f_Yu1"]["pass"])
    def test_compare_detects_real_difference_and_shape(self):
        self.assertTrue(compare(np.eye(3),np.eye(3))["pass"])
        self.assertFalse(compare(np.eye(3),np.eye(3)*1.01)["pass"])
        self.assertFalse(compare(np.ones((3,3)),np.ones((2,2)))["pass"])

if __name__=="__main__":unittest.main()

"""Native TREE amplitudes and independent local dipole algebra, not UV loops.

Live tests require --prepare, math -script, --check (see matching audit).
No skip or operator identity can certify MATCHING_CONVENTION_PASS.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_module5_native_compare import LOCAL, compare


class NativeTreeAmplitudeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=LOCAL/'native_numerical.json'
        if not path.exists():
            raise unittest.SkipTest('Genuine local SARAH numerical evidence absent')
        cls.actual=json.loads(path.read_text())

    def test_all_native_complex_witnesses(self):
        r=compare(self.actual)
        self.assertEqual(r['witnesses'],8)
        self.assertEqual(r['complex_coefficients'],952)
        self.assertLess(r['max_absolute_residual'],2e-12)
        self.assertGreater(abs(r['ckm_Vts_star_Vtb'][1]),.01)

    def test_native_rule_sign_flip_falsified(self):
        a=copy.deepcopy(self.actual)
        a['cases']['complex_base']['plus_{2, 3, 3}'][0]=[-x for x in a['cases']['complex_base']['plus_{2, 3, 3}'][0]]
        with self.assertRaisesRegex(ValueError,'mismatch'): compare(a)

    def test_chiral_swap_falsified(self):
        a=copy.deepcopy(self.actual)
        a['cases']['complex_base']['plus_{2, 3, 3}'].reverse()
        with self.assertRaisesRegex(ValueError,'mismatch'): compare(a)

    def test_conjugate_ckm_channel_falsified(self):
        a=copy.deepcopy(self.actual)
        # i*g -> i*g* (negate real part, preserve imaginary part).
        for pair in a['cases']['complex_base']['plus_{2, 3, 2}']: pair[0]*=-1
        with self.assertRaisesRegex(ValueError,'mismatch'): compare(a)

    def test_photon_gluon_charge_swap_falsified(self):
        a=copy.deepcopy(self.actual)
        case=a['cases']['complex_base']
        case['photon_top'],case['gluon_top']=case['gluon_top'],case['photon_top']
        with self.assertRaisesRegex(ValueError,'mismatch'): compare(a)

    def test_nonfinite_evidence_falsified(self):
        a=copy.deepcopy(self.actual)
        a['cases']['complex_base']['photon_top'][0][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'Nonfinite'): compare(a)

    def test_stale_evidence_falsified(self):
        a=copy.deepcopy(self.actual);a['driver_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Stale'): compare(a)


class LocalDipoleAmplitudeAlgebraTests(unittest.TestCase):
    """Explicit 4x4 Dirac matrices, independent of all scalar kernels."""
    def setUp(self):
        z=np.zeros((2,2),complex);i=np.eye(2,dtype=complex)
        pauli=[np.array([[0,1],[1,0]]),np.array([[0,-1j],[1j,0]]),np.diag([1,-1])]
        self.g=[np.block([[i,z],[z,-i]])]+[np.block([[z,s],[-s,z]]) for s in pauli]
        self.g5=1j*self.g[0]@self.g[1]@self.g[2]@self.g[3]
        self.pl=(np.eye(4)-self.g5)/2;self.pr=(np.eye(4)+self.g5)/2
        self.sigma=np.array([[.5j*(a@b-b@a) for b in self.g] for a in self.g])
        self.q=np.array([2.5,0,0,-2.5])  # covariant components
        self.eps=np.array([0,-1,0,0])

    def test_clifford_and_sigma_chirality(self):
        metric=[1,-1,-1,-1]
        for m in range(4):
            for n in range(4):
                target=2*metric[m]*np.eye(4) if m==n else np.zeros((4,4))
                np.testing.assert_allclose(self.g[m]@self.g[n]+self.g[n]@self.g[m],target,atol=1e-15)
                np.testing.assert_allclose(self.pr@self.sigma[m,n]@self.pr,self.sigma[m,n]@self.pr,atol=1e-15)
                np.testing.assert_allclose(self.pl@self.sigma[m,n]@self.pr,0,atol=1e-15)

    def contraction(self,q,eps):
        # <gamma(q)|F_mn(x)|0> = +i(q_m eps*_n-q_n eps*_m)e^(+iqx).
        field=1j*(np.outer(q,eps)-np.outer(eps,q))
        return np.einsum('mnab,mn->ab',self.sigma,field)@self.pr

    def test_field_strength_factor_two_and_ward_identity(self):
        full=self.contraction(self.q,self.eps)
        half=1j*np.einsum('mnab,m,n->ab',self.sigma,self.q,self.eps)@self.pr
        np.testing.assert_allclose(full,2*half,atol=1e-15)
        self.assertGreater(np.linalg.norm(full-half),1.)
        np.testing.assert_allclose(self.contraction(self.q,self.q),0,atol=1e-15)

    def test_hermitian_conjugate_operator_flips_chirality(self):
        for m in range(4):
            for n in range(4):
                vertex=self.sigma[m,n]@self.pr
                adjoint=self.g[0]@vertex.conj().T@self.g[0]
                np.testing.assert_allclose(adjoint,self.sigma[m,n]@self.pl,atol=1e-15)

    def test_color_generator_normalization(self):
        # One explicit SU(3) generator: native Lam/2, no extra C_F in open line.
        t=np.array([[0,1,0],[1,0,0],[0,0,0]],complex)/2
        self.assertEqual(np.trace(t@t),.5)
        photon=self.contraction(self.q,self.eps)
        gluon=np.kron(t,photon)
        np.testing.assert_allclose(gluon[:4,4:8],photon/2,atol=1e-15)


if __name__=='__main__': unittest.main()

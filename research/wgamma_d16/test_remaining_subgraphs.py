"""Subgraph identities; no assertion of physical gauge closure."""
import unittest
import numpy as np
from module1.scalar_constraints import reconstruct
from module4.couplings import rotations,trilinears
from .test_zee_mixed_hz import fixture
from .f_current_probe import neutrino_w_subloop
from .f_neutrino_rxi import neutrino_w_rxi,longitudinal_numerator_residual
from .neutral_mixing_support import prove


class RemainingSubgraphs(unittest.TestCase):
    def test_neutrino_longitudinal_open_line_identity(self):
        rng=np.random.default_rng(160729)
        for _ in range(10):
            self.assertLess(longitudinal_numerator_residual(rng.normal(size=4),rng.normal(size=4)),2e-13)

    def test_Rxi_subloop_pole_finite_scale_and_nonlocality(self):
        for xi in (.5,1.,3.,7.):
            out=neutrino_w_rxi(-1.,1.,xi)
            self.assertEqual(out['pole'],-xi)
            shifted=neutrino_w_rxi(-1.,1.,xi,mu2=np.exp(.2))
            self.assertAlmostEqual(shifted['finite']-out['finite'],-.2*xi,places=12)
            self.assertIsNone(out['physical_C_LR'])
            self.assertGreater(abs(neutrino_w_rxi(-2.,1.,xi)['finite']-out['finite']),.01)
        self.assertAlmostEqual(neutrino_w_rxi(-1,1,1)['finite'],neutrino_w_subloop(-1,1)['finite'],places=13)
        self.assertNotEqual(neutrino_w_rxi(-1,1,.5)['finite'],neutrino_w_rxi(-1,1,3)['finite'])

    def test_charged_scalar_support_zero_symbolic_and_actual_potentials(self):
        self.assertTrue(all(x=='0' for x in prove()['residuals'].values()))
        for index in (0,1):
            p,_=fixture(index);lag,_,_=reconstruct(p)
            A=trilinears(p,lag)['A'];_,_,R=rotations(p)
            cb,sb=np.cos(p['beta']),np.sin(p['beta']);mu=lag['Mu4']/np.sqrt(2)
            G0=R@(1j*np.array([[0,0,-mu*sb],[0,0,mu*cb],[mu*sb,-mu*cb,0]]))@R.T
            Z=R@np.diag([.3,.3,-.2])@R.T
            f=np.diag([.7,1.3,.2]);g=np.diag([1.7,.3,2.2])
            self.assertLess(abs(np.trace(A@f@Z@g)),1e-10)
            self.assertLess(abs(np.trace(A@f@G0@g)),1e-9)
            self.assertGreater(np.linalg.norm(A[0,1:]),1.)
            self.assertGreater(np.linalg.norm(G0[1:,1:]),1.)


if __name__=='__main__':
    unittest.main()

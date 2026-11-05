"""Focused independent mixed-HZ tests; no D15 or 39-channel replay."""
import json
from pathlib import Path
import unittest

import numpy as np
from scipy.integrate import quad
from module1.scalar_constraints import reconstruct
from module4.couplings import trilinears
from .external_2hdm import sha, load_reference
from .external_2hdm_hw_override import REFERENCE, ML
from .zee_mixed_hz import (mixed_hz, mixed_hz_kernel, mixed_hz_kernel_bounded,
                           scalar_current_tensor, spectral_sum)
from .zee_singlet_hz import singlet_hz, hz_radial_kernel

HERE = Path(__file__).resolve().parent


def fixture(index=0):
    old = json.loads((HERE/'hw_generic_evidence.json').read_text())['records'][index]
    D = np.asarray(old['D']); D = D[..., 0]+1j*D[..., 1]
    p = dict(old['physical'], gamma=.34 if index == 0 else -.27,
             mH2=540. if index == 0 else 670., k1=.3, k2=.18, k12=-.04)
    return p, D


class MixedHZ(unittest.TestCase):
    def test_native_orientations_goldstone_and_contact(self):
        native = json.loads((HERE/'mixed_hz_sources.json').read_text())
        self.assertEqual(native['status'], 'NATIVE_MIXED_HZ_VERTICES_PASS')
        self.assertEqual(len(native['checks']), 64)
        self.assertLess(native['max_abs_residual'], 1e-9)
        for name, expected in native['sources_sha256'].items():
            self.assertEqual(sha(HERE.parents[1]/name), expected)
        for n in (0, 1):
            p, D = fixture(n)
            result = mixed_hz(D, p, ML, 80.379, 91.1876, 1, 0)
            self.assertGreater(np.linalg.norm(result['commutator_M2_T']), 100.)
            self.assertLess(result['G0_identity_abs_residual'], 1e-9)
            self.assertIsNone(result['full_two_loop_C_LR'])

    def test_unprojected_em_and_nonzero_longitudinal_st_identity(self):
        p = np.array([.2, .1, -.3, .4]); k = np.array([.4, -.5, .7, 1.2])
        a, b = 2., 7.
        r = scalar_current_tensor(p, k, a, b)
        self.assertLess(np.linalg.norm(p@r['tensor']), 2e-13)
        self.assertGreater(np.linalg.norm(r['tensor']@k), 1e-4)
        self.assertLess(np.linalg.norm(r['tensor']@k+(b-a)*r['goldstone_current']), 2e-13)
        np.testing.assert_array_equal(r['uv_pole'], np.zeros((4, 4)))
        wrong = scalar_current_tensor(p, k, a, b, contact=False)
        self.assertGreater(np.linalg.norm(p@wrong['tensor']), .01)
        self.assertGreater(np.linalg.norm(wrong['uv_pole']), 1.)

    def test_soft_master_extracted_from_unprojected_diagrams(self):
        k = np.array([0., 0., 0., 1.3]); a, b = .3, 2.
        expected = 2*quad(lambda x:x*(1-x)/((1-x)*a+x*b+x*(1-x)*(k@k)), 0, 1)[0]
        estimates = []
        for h in (.002, .001):
            p = np.array([h, 0., 0., 0.])
            diff = scalar_current_tensor(p, k, a, b)['tensor']-scalar_current_tensor(-p, k, a, b)['tensor']
            estimates.append(-diff[3, 0]/(2*h*k[3]))
        extrapolated = (4*estimates[1]-estimates[0])/3
        self.assertLess(abs(extrapolated-expected), 1e-11)

    def test_two_distinct_radial_integrations_and_degenerate_limit(self):
        for a, b, y in [(2., 7., .4), (.1, 3., 1.), (.9, .9, .53)]:
            val, err = mixed_hz_kernel(a, b, y)
            bounded = mixed_hz_kernel_bounded(a, b, y, 480)
            self.assertLess(abs(val-bounded), 8e-9)
            self.assertEqual(mixed_hz_kernel(b, a, y), (val, err))
            self.assertLess(val, 0.)
            if a == b:
                self.assertLess(abs(val-hz_radial_kernel(a, y)[0]), 1e-10)

    def test_on_shell_photon_longitudinal_and_goldstone_vanish_independently(self):
        # Complex Euclidean null photon. Do NOT discard p_mu tensors first.
        p = np.array([.2j, 0., 0., .2]); k = np.array([.4, -.5, .7, 1.2])
        eps = np.array([0., 1., 0., 0.])
        J = np.array([.3+.1j, .4-.2j, -.1j, .7+.5j])
        for a, b in [(2., 7.), (.3, 2.)]:
            r = scalar_current_tensor(p, k, a, b)
            self.assertLess(abs(eps@r['goldstone_current']), 2e-13)
            values = []
            for xi in (.5, 1., 3., 7.):
                prop = (np.eye(4)-(1-xi)*np.outer(k, k)/(k@k+xi*.8))/(k@k+.8)
                # Two independent chiral currents, no inferred compensator.
                values.append(np.array([eps@r['tensor']@prop@J,
                                        eps@r['tensor']@prop@J.conjugate()]))
            for val in values:
                np.testing.assert_allclose(val, values[0], rtol=2e-11, atol=2e-14)

    def test_strict_doublet_and_unmixed_portal_limits(self):
        # Only new HZ comparison; do not rerun the full reference program.
        ref = load_reference(REFERENCE)
        p, D = fixture()
        p.update(gamma=0., k1=0., k2=0., k12=0.)
        sw2 = 1-(80.379/91.1876)**2; sw, cw = np.sqrt(sw2), 80.379/91.1876
        alpha = (2*80.379/p['v'])**2*sw2/(4*np.pi)
        from module3.core import vertices
        tri = trilinears(p, reconstruct(p)[0])
        for i, j in ((1, 0), (2, 0), (2, 1)):
            expected = np.zeros(2, complex)
            for name, (C, mass) in vertices(D, p, ML).items():
                expected += (-alpha*(-.5+2*sw2)/(sw*cw)*(cw*cw-sw*sw)/(sw*cw)
                    /(128*np.pi**3*ML[i]*mass**2)*tri[name][1, 1]
                    *np.array([C[j, i], C[i, j].conjugate()])
                    *ref.f10((p['mH1']/mass)**2, (91.1876/mass)**2))
            np.testing.assert_allclose(mixed_hz(D,p,ML,80.379,91.1876,i,j)['C_LR'], expected,
                                       rtol=3e-9, atol=1e-23)
            portals = dict(p, k1=.3, k2=.18, k12=-.04)
            singlet = singlet_hz(D,np.zeros((3,3)),portals,ML,80.379,91.1876,i,j)
            np.testing.assert_allclose(mixed_hz(D,portals,ML,80.379,91.1876,i,j)['C_LR'],
                expected+singlet['class_C_LR_GeV_minus2'], rtol=3e-9, atol=1e-23)

    def test_nonzero_offdiagonal_A_cancellation_and_charged_basis(self):
        p, D = fixture(); r = mixed_hz(D,p,ML,80.379,91.1876,1,0)
        self.assertGreater(abs(r['rows']['h']['terms'][1]['weighted_kernel']), .01)
        # Frozen Mu4*S-*(H1^T epsilon H2): A couples to the VEV charged
        # direction, not HD. Its PHYSICAL off-diagonal block vanishes after
        # rotation, although A-G-H trilinears are nonzero. This is stronger
        # than CP alone; never manufacture a nonzero A row to meet a task.
        self.assertLess(np.linalg.norm(r['rows']['A']['G']), 1e-11)
        fullA=trilinears(p,reconstruct(p)[0])['A']
        self.assertGreater(np.linalg.norm(fullA[0,1:]),1.)
        self.assertLess(max(abs(r['rows']['A']['C_LR'])), 1e-27)
        rng = np.random.default_rng(16062026)
        U, _ = np.linalg.qr(rng.normal(size=(2,2))+1j*rng.normal(size=(2,2)))
        for M in (np.diag([p['mH1']**2,p['mH2']**2]), np.eye(2)*300.**2):
            G, T = r['rows']['h']['G'], r['T']
            value = spectral_sum(M,G,T,p['mh1']**2,91.1876**2)[0]
            for R in (U, np.diag([-1.,1.]), np.diag(np.exp(1j*np.array([.4,-.7])))):
                other = spectral_sum(R@M@R.conj().T,R@G@R.conj().T,R@T@R.conj().T,p['mh1']**2,91.1876**2)[0]
                np.testing.assert_allclose(other,value,rtol=3e-11,atol=2e-12)

    def test_rephase_reverse_gamma_null_and_bounded_coupling_decoupling(self):
        p, D = fixture(); r = mixed_hz(D,p,ML,80.379,91.1876,1,0)['C_LR']
        phase = np.exp(1j*np.array([.37,-.81,.22]))
        transformed = phase.conjugate()[:,None]*D*phase[None,:]
        np.testing.assert_allclose(mixed_hz(transformed,p,ML,80.379,91.1876,1,0)['C_LR'],
                                   r*phase[1]/phase[0],rtol=3e-12,atol=1e-26)
        reverse = mixed_hz(D,p,ML,80.379,91.1876,0,1)['C_LR']
        np.testing.assert_allclose(reverse,r[::-1].conjugate()*ML[1]/ML[0],rtol=3e-12,atol=1e-25)
        np.testing.assert_allclose(mixed_hz(D,dict(p,gamma=-p['gamma']),ML,80.379,91.1876,1,0)['C_LR'],r,rtol=3e-12,atol=1e-25)
        np.testing.assert_array_equal(mixed_hz(np.diag(np.diag(D)),p,ML,80.379,91.1876,1,0)['C_LR'],[0j,0j])
        # Fixed portals and gamma=0: no quartics growing with heavy singlet mass.
        p['gamma']=0.
        base=dict(p,k1=0.,k2=0.,k12=0.)
        values=[]
        for mass in (540.,5400.):
            full=mixed_hz(D,dict(p,mH2=mass),ML,80.379,91.1876,1,0)['C_LR']
            common=mixed_hz(D,dict(base,mH2=mass),ML,80.379,91.1876,1,0)['C_LR']
            values.append(np.linalg.norm(full-common))
        self.assertLess(values[1]/values[0],.05)


if __name__ == '__main__':
    unittest.main()

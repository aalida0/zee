"""Independent component, analytic-kernel and mass-invariant audit checks."""
import itertools
import json
import math
from pathlib import Path
import unittest
import mpmath as mp
import numpy as np
from module2.core import forward, loop_kernel, null_cone, solve_fixed_f, NumericalUnknown
from module2.observables import observables, takagi
from module2.data import compare

ROOT = Path(__file__).resolve().parents[1]
ML = np.array([.00051099895, .1056583755, 1.77686])
EVIDENCE = {}


def independent_weights():
    with mp.workdps(80):
        def integral(m):
            z = mp.mpf(float(m))**2
            return mp.quad(lambda x: mp.log((x*z+(1-x)*270**2)/(x*z+(1-x)*910**2)),
                           [0, .9, .999, .99999999, 1])
        return np.array([float(1e9*mp.sin(-.86)/(32*mp.pi**2)*m*integral(m)) for m in ML])


class IndependentAudit(unittest.TestCase):
    def test_kernel_against_unrounded_high_precision_quadrature(self):
        worst=0.
        with mp.workdps(85):
            for m1,m2 in [(270,910),(300,np.nextafter(300.,math.inf)),(1.77686,2.)]:
                a,b=mp.mpf(float(m1))**2,mp.mpf(float(m2))**2
                for ml in ML:
                    z=mp.mpf(float(ml))**2
                    reference=mp.quad(lambda x:mp.log((x*z+(1-x)*a)/(x*z+(1-x)*b)),[0,.9,.999,.99999999,1])
                    error=float(abs((mp.mpf(loop_kernel(m1,m2,ml))-reference)/reference))
                    self.assertLess(error,2e-15);worst=max(worst,error)
        EVIDENCE['kernel_error_vs_unrounded_85_digit_quadrature']=worst

    def test_sparse_source_fixed_chiral_normalization(self):
        # Module 0 CpL/CpR and its pole-mass constructor fix this result before
        # calling forward. Only ee is nonzero; both charge orientations count.
        f, d, gamma = .002+.001j, 1e-6-3e-6j, -.43
        F = np.zeros((3, 3), complex); F[0, 1] = f; F[1, 0] = -f
        D = np.zeros((3, 3), complex); D[1, 0] = d
        with mp.workdps(80):
            z = mp.mpf(float(ML[1]))**2
            b0 = [mp.quad(lambda x: -mp.log(x*z+(1-x)*mass**2), [0, .9, .999, 1])
                  for mass in (270, 910)]
            sl = 2*math.cos(gamma)*math.sin(gamma)*ML[1]*f.conjugate()*d.conjugate()*float(b0[0]-b0[1])
            expected = -sl.conjugate()*1e9/(16*math.pi**2)
        M = forward(F, D, m1=270, m2=910, gamma=gamma, ml=ML)
        self.assertLess(abs(M[0, 0]/expected-1), 2e-14)
        sparse = M.copy(); sparse[0, 0] = 0
        self.assertEqual(np.max(abs(sparse)), 0)
        for mutant in (-expected, 2*expected, expected/2, expected.conjugate()):
            self.assertGreater(abs(mutant/expected-1), .1)
        EVIDENCE['sparse_chiral_normalization_relative_error'] = float(abs(M[0, 0]/expected-1))

    def test_analytic_homogeneous_space_including_isotropic_null_vector(self):
        # If X=W D, FX must be skew in a homogeneous solution. Its null
        # vector n forces FX=cF, hence X=cI+n r.T: four complex directions.
        w = independent_weights(); worst = 0.
        for n in (np.array([1, 2, 3], complex), np.array([1, 1j, 0]), np.array([1+.2j, -.3j, .8])):
            n = n/np.linalg.norm(n)
            F = .002*np.array([[0,n[2],-n[1]],[-n[2],0,n[0]],[n[1],-n[0],0]])
            solution = solve_fixed_f(F, np.zeros((3,3)), m1=270,m2=910,gamma=-.43,ml=ML)
            analytic = [np.diag(1/w)] + [np.outer(n,e)/w[:,None] for e in np.eye(3)]
            Q, _ = np.linalg.qr(np.array(analytic).reshape(4,9).T)
            H = solution['homogeneous'].reshape(4,9).T
            error = float(np.linalg.norm(Q-H@(H.conj().T@Q)))
            self.assertLess(error, 2e-11); worst = max(worst,error)
            self.assertEqual((solution['rank'],solution['nullity_complex']), (5,4))
        EVIDENCE['analytic_homogeneous_span_residual'] = worst

    def test_inverse_against_five_explicit_components(self):
        a = .002-.003j
        F = np.array([[0,a,0],[-a,0,0],[0,0,0]])
        M = np.array([[.01+.02j,.003-.001j,-.005j],[.003-.001j,.03-.01j,.007],[-.005j,.007,0]])
        sol = solve_fixed_f(F,M,m1=270,m2=910,gamma=-.43,ml=ML)
        D = sol['D0']+np.einsum('k,kij->ij',[.1j,.03,-.02j,.07],sol['homogeneous'])
        w = independent_weights()
        actual = np.array([2*a*w[1]*D[1,0], -2*a*w[0]*D[0,1],
                           a*(w[1]*D[1,1]-w[0]*D[0,0]),a*w[1]*D[1,2],-a*w[0]*D[0,2]])
        expected = M[(0,1,0,0,1),(0,1,1,2,2)]
        self.assertLess(np.max(abs(actual-expected)), 2e-9)

    def test_null_cone_scaling_charts_and_free_coordinate(self):
        M = np.array([[.02+.01j,.005j,.004],[.005j,.03-.01j,.007j],[.004,.007j,.05]])
        for chart, root, factor in itertools.product(itertools.permutations(range(3)),[0,1],[1e-200,1.,1e200]):
            F,n = null_cone(M*factor,.3+.4j,.002,root,chart)
            self.assertLess(abs(n.T@M@n)/np.linalg.norm(M),2e-12)
            self.assertLess(np.linalg.norm(F@n),2e-18)
        F,n = null_cone(np.zeros((3,3)),2+.3j,.002,free_x=3-2j)
        self.assertLess(abs(n[1]/n[0]-(3-2j)),2e-15)
        self.assertLess(abs(n[2]/n[0]-(2+.3j)),2e-15)
        with self.assertRaises(ValueError): null_cone(M,.2,.002,free_x=.3)

    def test_takagi_scale_covariance_and_direct_congruence(self):
        rng = np.random.default_rng(6102025); worst = 0.
        Q,_ = np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
        for spectrum, factor, ordering in itertools.product(([0,.7,1.3],[1,1,1],[.2,.2+1e-12,1]),
                                                           [1e-200,1e-100,1.,1e100,1e200],['NO','IO']):
            base = Q.conj()@np.diag(spectrum)@Q.conj().T
            m,U,diag = takagi(base*factor,ordering)
            error = float(np.linalg.norm(U.T@base@U-np.diag(m/factor)))
            self.assertLess(error,8e-14); worst = max(worst,error)
            self.assertLess(np.max(abs(np.sort(m/factor)-spectrum)),2e-14)
            self.assertTrue(np.isfinite(list(diag.values())).all())
        EVIDENCE['scale_covariant_Takagi_congruence_residual'] = worst
        with self.assertRaises(NumericalUnknown): takagi(np.full((3,3),1.7e308),'NO')
        with self.assertRaises(NumericalUnknown): observables(np.diag([1e200,2e200,3e200]),'NO')
        with self.assertRaises(NumericalUnknown): observables(np.diag([1e-200,2e-200,3e-200]),'NO')

    def test_zero_target_free_chart_through_JSON(self):
        from module2.interface import evaluate, encode
        from test_module2_interface import example
        x=example();x['target_eV']=encode(np.zeros((3,3),complex))
        x['homogeneous_coefficients']={'real':[0]*4,'imag':[0]*4}
        x['null_cone']['free_x']={'real':3,'imag':-2}
        r=evaluate(x)
        self.assertEqual(r['observables']['masses_eV'],[0,0,0])
        self.assertEqual(r['gates']['observables'],'UNKNOWN')
        self.assertIsNone(r['observables']['delta_rad'])

    def test_archived_mass_CP_and_beta_invariants(self):
        refs = json.loads((ROOT/'validation/module0/report/majorana_physical.json').read_text())['results']
        errors=[]
        for ref,ordering in itertools.product(refs,['NO','IO']):
            M = np.array(ref['mass_matrix_real_eV'])+1j*np.array(ref['mass_matrix_imag_eV'])
            o = observables(M,ordering)
            H = M.conj().T@M
            independently_signed_J = np.imag(H[0,1]*H[1,2]*H[2,0])/(o['dm21_eV2']*o['dm31_eV2']*o['dm32_eV2'])
            error = abs(independently_signed_J-o['J_CP']); errors.append(float(error))
            self.assertLess(error,3e-14)
            self.assertAlmostEqual(o['m_beta_eV']**2,H[0,0].real,places=16)
        # Two-family analytic Majorana phase; the Dirac phase is undefined.
        angle,phase = .37,1.2
        R = np.array([[math.cos(angle),math.sin(angle),0],[-math.sin(angle),math.cos(angle),0],[0,0,1]])
        M = R@np.diag([.007,.011*np.exp(-1j*phase),.05j])@R.T
        o = observables(M,'NO')
        self.assertIsNone(o['delta_rad'])
        self.assertLess(abs(np.angle(np.exp(1j*(o['alpha21_rad']-phase)))),2e-13)
        EVIDENCE['independent_mass_CP_invariant_error'] = max(errors)

    def test_Majorana_phases_at_zero_reactor_angle(self):
        a,b=.37,.71
        R12=np.array([[math.cos(a),math.sin(a),0],[-math.sin(a),math.cos(a),0],[0,0,1]])
        R23=np.array([[1,0,0],[0,math.cos(b),math.sin(b)],[0,-math.sin(b),math.cos(b)]])
        R=R23@R12;phases=np.array([0,.7,2.2])
        for masses,ordering in [([.007,.011,.05],'NO'),([0,.011,.05],'NO'),([.049,.05,0],'IO')]:
            M=R@np.diag(np.array(masses)*np.exp(-1j*phases))@R.T
            for P in (np.eye(3),np.diag(np.exp(1j*np.array([.3,-.7,1.2])))):
                o=observables(P@M@P,ordering)
                self.assertIsNone(o['delta_rad'])
                for i,j,label in [(0,1,'21'),(0,2,'31'),(1,2,'32')]:
                    value=o['majorana_pair_phases_rad'][label]
                    if masses[i]==0 or masses[j]==0:
                        self.assertIsNone(value)
                    else:
                        self.assertLess(abs(np.angle(np.exp(1j*(value-(phases[j]-phases[i]))))),2e-12)

    def test_correlated_periodic_Gaussian_and_nonfinite_observables(self):
        d = json.loads((ROOT/'module2/data/nufit60_ic19_no.json').read_text())
        d.update(observables=['sin2_theta12','delta_rad'],units={'sin2_theta12':'1','delta_rad':'rad'},
                 mean=[.3,0],covariance=[[.01,.099],[.099,1]])
        o = {'ordering':'NO','sin2_theta12':.8,'delta_rad':.2}
        precision = np.linalg.inv(d['covariance'])
        expected = min(np.array([.5,.2+2*np.pi*k])@precision@np.array([.5,.2+2*np.pi*k]) for k in range(-4,5))
        self.assertAlmostEqual(compare(o,d)['chi2'],expected,places=10)
        o['delta_rad'] += 8*np.pi
        self.assertAlmostEqual(compare(o,d)['chi2'],expected,places=10)
        o['delta_rad'] = float('nan')
        with self.assertRaises(ValueError): compare(o,d)

    def test_pinned_Gaussian_against_published_NuFIT60_table(self):
        # Official v60.tbl-parameters.pdf, IC19 without SK. These are source
        # table entries, independently recorded rather than inferred from files.
        expected={
            'no':([.307,.02195,.561,7.49e-5,2.534e-3],[.012,.00054,.012,.19e-5,.025e-3],[.011,.00058,.015,.19e-5,.023e-3]),
            'io':([.308,.02224,.562,7.49e-5,-2.510e-3],[.012,.00056,.012,.19e-5,.024e-3],[.011,.00057,.015,.19e-5,.025e-3])}
        for ordering,(mean,up,down) in expected.items():
            d=json.loads((ROOT/f'module2/data/nufit60_ic19_{ordering}.json').read_text())
            np.testing.assert_allclose(d['mean'],mean,rtol=1e-15,atol=0)
            sigma=(np.array(up)+down)/2
            np.testing.assert_allclose(d['covariance'],np.diag(sigma**2),rtol=5e-15,atol=0)
            self.assertEqual(d['source']['version'],'NuFIT 6.0 (2024)')
            self.assertEqual(d['likelihood'],'GAUSSIAN_APPROXIMATION')


if __name__ == '__main__': unittest.main()

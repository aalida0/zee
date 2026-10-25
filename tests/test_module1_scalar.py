"""Independent polynomial, analytic spectrum, orbit and likelihood tests."""
import copy
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import mpmath as mp
import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from module1.scalar_constraints import (reconstruct, unitarity, ewpo, evaluate,
                                       validate_input, strict_loads, provenance)
from module1.potential import (Potential, component_value, contact_tensor,
                                scatter_matrix, charge_basis, legacy_neutral_basis, gauge_audit)
from module1.bfb import check_bfb, certificate, orbit_fields, high_precision_quartic
from module1.vacuum import search_vacuum
from gateA1h_correlated_stu_ewpo import grimus_G, grimus_Ghat, FITS, correlated_fit

METRICS = {}


def example():
    return json.loads((ROOT/'module1/example.json').read_text())


def symmetric(mass=500., singlet=800.):
    d = example(); x = d['physical']
    x.update(mh2=mass, ma=mass, mH1=mass, mH2=singlet, alpha=.7, beta=.7,
             gamma=0., m12sq=mass**2*math.sin(.7)*math.cos(.7), lc=.3, k1=.2, k2=.25, k12=.02)
    return d


def deeper():
    d = symmetric(400., 400.); d['benchmark_id'] = 'physical_deeper_singlet'
    d['physical'].update(mH1=120., gamma=math.pi/2, lc=.1, k1=2., k2=2., k12=0.)
    return d


def points():
    a = example()
    b = symmetric(); b['benchmark_id'] = 'aligned_decoupling_500'
    c = symmetric(1500., 2000.); c['benchmark_id'] = 'aligned_decoupling_1500'
    d = symmetric(500., 500.); d['benchmark_id'] = 'degenerate_signed_mixing'
    d['physical']['gamma'] = -.72
    e = example(); e['benchmark_id'] = 'negative_doublet_bfb'; e['physical']['beta'] = 1.398
    f = example(); f['benchmark_id'] = 'singlet_unitarity_failure'; f['physical']['lc'] = 10.
    return [a, b, c, d, deeper(), e, f]


class IndependentPolynomial:
    """Differentiate the expanded SARAH component polynomial, without A,C,T.

    This oracle never invokes the physical inversion to construct a Hessian.
    Symbolic parameter coefficients let it falsify individual mass/sign errors.
    """
    def __init__(self):
        r = sp.symbols('r:10', real=True)
        names = ['Lambda1', 'Lambda2', 'Lambda3', 'Lambda4', 'Lambda5', 'LambdaC',
                 'K1', 'K2', 'K12', 'M112', 'M222', 'M12Sq', 'MCS2', 'Mu4']
        s = sp.symbols(' '.join(names), real=True); q = dict(zip(names, s))
        z = [(r[i]+sp.I*r[i+1])/sp.sqrt(2) for i in range(0, 10, 2)]
        x, y, w = sum(sp.expand_complex(t*sp.conjugate(t)) for t in z[:2]), sum(sp.expand_complex(t*sp.conjugate(t)) for t in z[2:4]), sp.expand_complex(z[4]*sp.conjugate(z[4]))
        t = sum(sp.conjugate(z[i])*z[i+2] for i in (0, 1))
        cubic = z[4].conjugate()*(z[0]*z[3]-z[1]*z[2])
        v = (q['M112']*x+q['M222']*y-q['M12Sq']*(t+sp.conjugate(t))+q['MCS2']*w
             +q['Mu4']*(cubic+sp.conjugate(cubic))+q['Lambda1']/2*x*x+q['Lambda2']/2*y*y
             +q['Lambda3']*x*y+q['Lambda4']*t*sp.conjugate(t)+q['Lambda5']/2*(t*t+sp.conjugate(t*t))
             +q['LambdaC']*w*w+(q['K1']*x+q['K2']*y-q['K12']*(t+sp.conjugate(t)))*w)
        self.v = sp.Poly(sp.expand(v), r)
        self.r, self.names = r, names
        self.value = sp.lambdify((r, s), self.v.as_expr(), 'numpy', cse=True)
        self.gradient = sp.lambdify((r, s), [sp.diff(self.v.as_expr(), a) for a in r], 'numpy', cse=True)
        self.hessian = sp.lambdify((r, s), sp.hessian(self.v.as_expr(), r), 'numpy', cse=True)
        self.symbols = s

    def parameters(self, p):
        return [p[k] for k in self.names]

    def tensor(self, p):
        result = np.zeros((10,)*4)
        for powers, coefficient in self.v.terms():
            if sum(powers) != 4:
                continue
            indices = tuple(i for i, n in enumerate(powers) for _ in range(n))
            value = float(coefficient.subs(dict(zip(self.symbols, self.parameters(p)))))
            value *= math.prod(math.factorial(n) for n in powers)
            for perm in set(itertools.permutations(indices)):
                result[perm] = value
        return result


class TestReconstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = IndependentPolynomial()

    def test_independent_differentiated_polynomial_multiple_points(self):
        configs = [d['physical'] for d in points()]
        arbitrary = example()['physical']
        arbitrary.update(mh1=118., m12sq=-2000., alpha=-.4, beta=.64, gamma=-.3)
        configs.append(arbitrary)
        for gamma, alpha, beta in ((-.71, -.32, .81), (0., .6, .6), (math.pi/2, -.5, .9), (1e-9, 2.2, .2)):
            x = example()['physical']; x.update(gamma=gamma, alpha=alpha, beta=beta)
            configs.append(x)
        gradmax = hmax = massmax = 0.
        rng = np.random.default_rng(771)
        for x in configs:
            p, _, rec = reconstruct(x); args = self.oracle.parameters(p); v = x['v']
            ew = np.zeros(10); ew[[2, 6]] = v*np.array([math.cos(x['beta']), math.sin(x['beta'])])
            g = np.asarray(self.oracle.gradient(ew, args), float)
            h = np.asarray(self.oracle.hessian(ew, args), float)
            self.assertLess(max(abs(g))/v**3, 2e-12)
            # Compare to the requested eigenvalues, not to the inversion's own matrices.
            target = np.sort([0, 0, 0, x['mh1']**2, x['mh2']**2, x['ma']**2,
                              x['mH1']**2, x['mH1']**2, x['mH2']**2, x['mH2']**2])
            residual = max(abs(np.linalg.eigvalsh(h)-target))/max(target)
            self.assertLess(residual, 2e-12)
            for z, ix in ((rec['mixing_rows']['ZH'], [2, 6]), (rec['mixing_rows']['ZA'], [3, 7]),
                          (rec['mixing_rows']['ZP'], [0, 4, 8]), (rec['mixing_rows']['ZP'], [1, 5, 9])):
                z = np.asarray(z); transformed = z@h[np.ix_(ix, ix)]@z.T
                self.assertLess(np.max(abs(transformed-np.diag(np.diag(transformed))))/max(target), 2e-12)
            r = rng.normal(size=10)*v
            val, gr, he = Potential(p).evaluate(r)
            np.testing.assert_allclose(he, self.oracle.hessian(r, args), rtol=2e-12, atol=2e-7)
            gradmax = max(gradmax, max(abs(g))/v**3)
            hmax = max(hmax, np.max(abs(he-self.oracle.hessian(r, args)))/v**2)
            massmax = max(massmax, residual)
        METRICS.update(independent_polynomial_points=len(configs), tadpole_max_over_v3=gradmax,
                       hessian_max_difference_over_v2=hmax, independent_mass_max_scaled_residual=massmax)

    def test_independent_full_gradient_hessian_finite_differences(self):
        p, _, _ = reconstruct(example()['physical']); pot = Potential(p)
        r = np.random.default_rng(92).normal(size=10)*140.; v = 246.21965
        value, grad, h = pot.evaluate(r); step = .001
        gres = hres = 0.
        for i in range(10):
            a = r.copy(); b = r.copy(); a[i] += step; b[i] -= step
            fd = (component_value(a, p)-component_value(b, p))/(2*step)
            gres = max(gres, abs(fd-grad[i])/v**3)
            fdh = (pot.evaluate(a)[1]-pot.evaluate(b)[1])/(2*step)
            hres = max(hres, max(abs(fdh-h[:, i]))/v**2)
        self.assertLess(gres, 2e-8); self.assertLess(hres, 2e-8)
        METRICS.update(finite_difference_gradient_over_v3=gres, finite_difference_hessian_over_v2=hres)

    def test_sign_mutations_are_detected(self):
        p, _, _ = reconstruct(example()['physical']); r = np.zeros(10); r[[2, 6]] = [43.30431094, 242.38162616]
        correct = np.linalg.eigvalsh(Potential(p).evaluate(r)[2])
        changed = dict(p); changed['K12'] *= -1
        self.assertGreater(max(abs(np.linalg.eigvalsh(Potential(changed).evaluate(r)[2])-correct)), 1.)
        changed = dict(p); changed['Mu4'] *= -1
        # Eigenvalues alone cannot detect this sign: check signed mixing.
        self.assertGreater(abs(Potential(changed).evaluate(r)[2][4, 8]-Potential(p).evaluate(r)[2][4, 8]), 1e4)

    def test_quartic_derivatives_combinatorial_factors(self):
        p, _, _ = reconstruct(example()['physical'])
        residual = float(np.max(abs(contact_tensor(p)-self.oracle.tensor(p))))
        self.assertLess(residual, 2e-13); METRICS['fourth_derivative_max_residual'] = residual


class TestUnitarity(unittest.TestCase):
    def test_analytic_O4_and_O2_spectra(self):
        p, _, _ = reconstruct(example()['physical'])
        zero = {k: 0. for k in p}
        for key, val, expected in (('Lambda1', 2., [2.]*9+[6.]), ('Lambda2', 3., [3.]*9+[9.]),
                                    ('LambdaC', 3., [6., 6., 12.])):
            q = dict(zero); q[key] = val
            eig = np.linalg.eigvalsh(scatter_matrix(q))
            nonzero = eig[abs(eig) > 1e-10]
            np.testing.assert_allclose(nonzero, expected, atol=1e-12)
        self.assertEqual(np.count_nonzero(scatter_matrix(zero)), 0)

    def test_gate6_independent_sector_envelopes(self):
        worst = 0.
        for d in points():
            p, old, _ = reconstruct(d['physical']); u = unitarity(p, old)
            worst = max(worst, u['gate6_max_eigenvalue_residual'])
            self.assertFalse(u['gate6_disagreement'])
            # Legacy App.C5 is all-incoming: signed eigenvalues differ.
            # Preserve the difference and verify it by an explicit basis lift.
            eig = np.array(u['eigenvalues'])
            for name, spectrum in old['unitarity_eigenvalues'].items():
                if name != 'Q0Y0':
                    self.assertLess(max(min(abs(eig-z)) for z in spectrum), 2e-10)
            lift, _ = charge_basis(); b = legacy_neutral_basis(lift)
            m = scatter_matrix(p)
            np.testing.assert_allclose(np.linalg.eigvalsh((b.T@m@b).real), old['unitarity_eigenvalues']['Q0Y0'], atol=2e-10)
            np.testing.assert_allclose(np.sort(abs(np.linalg.eigvalsh(b.conj().T@m@b))),
                                       np.sort(abs(np.asarray(old['unitarity_eigenvalues']['Q0Y0']))), atol=2e-10)
            self.assertLess(u['gate6_neutral_all_incoming_residual'], 2e-10)
        METRICS['gate6_max_eigenvalue_residual'] = worst

    def test_real_basis_invariance_and_charge_multiplicities(self):
        p, _, _ = reconstruct(example()['physical']); tensor = contact_tensor(p)
        o, _ = np.linalg.qr(np.random.default_rng(55).normal(size=(10, 10)))
        transformed = np.einsum('ia,jb,kc,ld,ijkl->abcd', o, o, o, o, tensor, optimize=True)
        residual = max(abs(np.linalg.eigvalsh(scatter_matrix(p, tensor))-np.linalg.eigvalsh(scatter_matrix(p, transformed))))
        self.assertLess(residual, 2e-12)
        lift, sectors = charge_basis()
        np.testing.assert_allclose(lift.conj().T@lift, np.eye(55), atol=2e-15)
        sizes = sorted(map(len, sectors.values()))
        self.assertEqual(sizes, sorted([1]*2+[2]*8+[3]*4+[4]*4+[9]))
        METRICS['unitarity_basis_max_eigenvalue_residual'] = float(residual)

    def test_strict_8pi_fail_fixture(self):
        p, old, _ = reconstruct(points()[-1]['physical']); u = unitarity(p, old)
        self.assertEqual(u['assessment'], 'FAIL'); self.assertGreaterEqual(u['max_abs_eigenvalue'], 40.)


class TestBFB(unittest.TestCase):
    def test_certified_and_random_full_complex_orientations(self):
        rng = np.random.default_rng(41)
        for d in (example(), symmetric()):
            p, _, _ = reconstruct(d['physical']); out = check_bfb(p)
            self.assertEqual(out['assessment'], 'PASS')
            for _ in range(1000):
                r = rng.normal(size=10); r /= np.linalg.norm(r)
                self.assertGreater(component_value(r, p, quartic_only=True), 0)

    def test_singlet_K12_complex_and_charge_negative_fixtures(self):
        p, _, _ = reconstruct(symmetric()['physical'])
        base = {k: 0. for k in p}; base.update(Lambda1=1., Lambda2=1., LambdaC=1.)
        fixtures = [dict(base, Lambda1=-.2), dict(base, LambdaC=-.1),
                    dict(base, K1=-2.), dict(base, LambdaC=.1, K1=1., K2=1., K12=2.),
                    dict(base, Lambda3=-2., Lambda4=3.), dict(base, Lambda5=2.)]
        residual = 0.
        for p in fixtures:
            out = check_bfb(p)
            self.assertEqual(out['status'], 'BFB_NEGATIVE_WITNESS')
            w = out['negative_witness']
            self.assertLess(float(w['V4_60digit']), -1e-8)
            self.assertAlmostEqual(w['V4'], component_value(w['canonical_fields'], p, True), delta=1e-12)
            residual = max(residual, w['alternative_evaluation_residual'])
        METRICS.update(bfb_falsifying_fixtures=len(fixtures), bfb_witness_high_precision_residual=residual)

    def test_marginal_flat_quartic_is_unknown(self):
        p, _, _ = reconstruct(symmetric()['physical'])
        p.update(Lambda1=0., Lambda2=1., Lambda3=0., Lambda4=0., Lambda5=0.,
                 LambdaC=1., K1=0., K2=0., K12=0.)
        self.assertIsNone(certificate(p))
        self.assertEqual(check_bfb(p)['assessment'], 'UNKNOWN')

    def test_sufficient_condition_is_not_silently_necessary(self):
        p, _, _ = reconstruct(symmetric()['physical'])
        p.update(Lambda1=.3, Lambda2=.3, Lambda3=.3, Lambda4=0., Lambda5=0.,
                 LambdaC=.3, K1=0., K2=10., K12=1.)
        # Independent proof for this fixture: doublet V4=.15*(x+y)^2,
        # portal >= smallest_eig([[0,-1],[-1,10]])*(x+y)*s.
        # That lower binary quadratic is strictly positive, but the pipeline's
        # conservative three-norm bound cannot certify it. Require UNKNOWN.
        portal_min = np.linalg.eigvalsh([[0., -1.], [-1., 10.]])[0]
        self.assertGreater(portal_min+2*math.sqrt(.15*.3), 0.)
        self.assertIsNone(certificate(p))
        self.assertEqual(check_bfb(p)['assessment'], 'UNKNOWN')

    def test_orbit_covers_independent_complex_gram_components(self):
        r = orbit_fields([.67, .39, .51, .82]); z = (r[::2]+1j*r[1::2])/math.sqrt(2)
        self.assertAlmostEqual(sum(abs(z)**2), 1.)
        overlap = np.vdot(z[:2], z[2:4])
        self.assertGreater(abs(overlap.imag), .01)
        self.assertGreater(abs(z[2]), .01)  # charged relative doublet orientation


def closed_G(I, J, Q):
    """80-digit independent logarithm/arctan Grimus C2, not quadrature."""
    I, J, Q = map(mp.mpf, (I, J, Q))
    t = I+J-Q; r = Q*Q-2*Q*(I+J)+(I-J)**2
    f = (mp.sqrt(r)*mp.log(abs((t-mp.sqrt(r))/(t+mp.sqrt(r)))) if r > 0
         else 2*mp.sqrt(-r)*mp.atan(mp.sqrt(-r)/t) if r < 0 else mp.mpf(0))
    if I == J:
        return -mp.mpf(16)/3+16*I/Q+r*f/Q**3
    return (-mp.mpf(16)/3+5*(I+J)/Q-2*(I-J)**2/Q**2
            +3/Q*((I*I+J*J)/(I-J)-(I*I-J*J)/Q+(I-J)**3/(3*Q**2))*mp.log(I/J)+r*f/Q**3)


def closed_Ghat(I, Q):
    I, Q = mp.mpf(I), mp.mpf(Q)
    t, r = I, I*I-4*I*Q
    f = (mp.sqrt(r)*mp.log(abs((t-mp.sqrt(r))/(t+mp.sqrt(r)))) if r > 0
         else 2*mp.sqrt(-r)*mp.atan(mp.sqrt(-r)/t) if r < 0 else 0)
    tilde = -2+((I-Q)/Q-(I+Q)/(I-Q))*mp.log(I/Q)+f/Q
    return closed_G(I, Q, Q)+12*tilde


class TestEWPO(unittest.TestCase):
    def test_closed_functions_multiple_splittings_scales(self):
        residual = 0.
        with mp.workdps(80):
            for a, b in ((300., 700.), (500., 500.), (500., 500.0001), (1500., 2000.)):
                for m in (80.379, 91.1876):
                    target = float(closed_G(a*a, b*b, m*m))
                    residual = max(residual, abs(grimus_G(a*a, b*b, m*m)-target))
            for a in (118., 125., 580.7, 2000.):
                target = float(closed_Ghat(a*a, 91.1876**2))
                residual = max(residual, abs(grimus_Ghat(a*a, 91.1876**2, n=320)-target))
        self.assertLess(residual, 3e-10); METRICS['loop_closed_form_max_residual'] = residual

    def test_decoupling_custodial_zero_splitting(self):
        results = []
        for d in (symmetric(), symmetric(1500., 2000.)):
            r = ewpo(d['physical'], d['electroweak'], d['ew_fit']); results.append(r['STU'])
            self.assertAlmostEqual(r['STU']['T'], 0., delta=1e-12)
        self.assertLess(abs(results[1]['S']), abs(results[0]['S'])/5)
        self.assertLess(abs(results[1]['U']), abs(results[0]['U'])/5)
        METRICS['decoupling_STU'] = results

    def test_fixed_SM_reference_for_arbitrary_light_mass(self):
        d = symmetric(); d['physical']['mh1'] = 118.; x = d['physical']
        result = ewpo(x, d['electroweak'], d['ew_fit'])
        # Independently run the same published mixing sums with analytic C2/C5
        # loop functions. Also vary the loop mass wrapper's reference MH_SM:
        # its scale cancels, whereas the final physical SM subtraction is fixed.
        with mp.workdps(80):
            with patch('gateA1h_correlated_stu_ewpo.grimus_G', side_effect=lambda I, J, Q, n=160: float(closed_G(I, J, Q))), patch('gateA1h_correlated_stu_ewpo.grimus_Ghat', side_effect=lambda I, Q, n=160: float(closed_Ghat(I, Q))):
                reference = ewpo(x, d['electroweak'], d['ew_fit'])
        np.testing.assert_allclose(list(result['STU'].values()), list(reference['STU'].values()), atol=2e-10)
        # Independent aligned-limit SM-reference formula, not the wrapper's
        # reference correction. Heavy doublet/singlet still contribute S,U.
        with mp.workdps(80):
            mw, mz, mh, mref = map(mp.mpf, (80.379, 91.1876, 118., 125.))
            sw = 1-(mw/mz)**2
            gs = ((1-2*sw)**2+1)*closed_G(500**2, 500**2, mz*mz)+4*sw**2*closed_G(800**2, 800**2, mz*mz)
            hs = closed_Ghat(mh*mh, mz*mz)-closed_Ghat(mref*mref, mz*mz)
            hu = (closed_Ghat(mh*mh, mw*mw)-closed_Ghat(mh*mh, mz*mz)
                  -closed_Ghat(mref*mref, mw*mw)+closed_Ghat(mref*mref, mz*mz))
            expected_s = float((gs+mp.log(mh*mh/(mref*mref))+hs)/(24*mp.pi))
            expected_u = float((2*closed_G(500**2, 500**2, mw*mw)-gs+hu)/(24*mp.pi))
            self.assertAlmostEqual(result['STU']['S'], expected_s, delta=2e-10)
            self.assertAlmostEqual(result['STU']['U'], expected_u, delta=2e-10)
        self.assertNotAlmostEqual(result['STU']['T'], 0., delta=1e-5)

    def test_charged_pair_minus_two_and_full_T_matrix_sum(self):
        from gateA1g_zee_oblique_T import F, oblique_T
        from gateA1h_correlated_stu_ewpo import florentino_mixing
        x = example()['physical']; u, v = florentino_mixing(x['alpha'], x['beta'], x['gamma'])
        uu, uv, vv = u.conj().T@u, u.conj().T@v, v.conj().T@v
        c, n = [300., 700.], [125., 580.7, 633.7]
        numerator = sum(abs(uv[a+1, b+1])**2*F(c[a], n[b]) for a in range(2) for b in range(3))
        numerator -= sum(vv[b+1, j+1].imag**2*F(n[b], n[j]) for b in range(3) for j in range(b+1, 3))
        numerator -= 2*abs(uu[1, 2])**2*F(*c)
        numerator += 3*sum(vv[0, b+1].imag**2*(F(91.1876, n[b])-F(80.379, n[b])) for b in range(3))
        numerator -= 3*(F(91.1876, 125.)-F(80.379, 125.))
        target = numerator/(16*math.pi*(1-(80.379/91.1876)**2)*80.379**2)
        value, _ = oblique_T(); alt, _ = oblique_T(coefficient=.5)
        self.assertAlmostEqual(value, target, delta=2e-14)
        shift = 1.5*abs(uu[1, 2])**2*F(*c)/(16*math.pi*(1-(80.379/91.1876)**2)*80.379**2)
        self.assertAlmostEqual(alt-value, shift, delta=1e-14)
        METRICS.update(T_matrix_sum_residual=abs(value-target), disputed_T_shift=shift)

    def test_covariance_whitening_and_fit_center(self):
        for name, f in FITS.items():
            self.assertEqual(correlated_fit(*f['central'], name)['chi2_relative_to_fit_minimum'], 0.)
            pred = np.array([.2, -.1, .01]); sd = np.array(f['sigma'])
            cov = np.outer(sd, sd)*f['rho']; white = np.linalg.solve(np.linalg.cholesky(cov), pred-f['central'])
            self.assertAlmostEqual(float(white@white), correlated_fit(*pred, name)['chi2_relative_to_fit_minimum'], delta=2e-12)

    def test_unsupported_threshold_fails_closed(self):
        d = example(); d['physical'].update(mH1=10., mH2=20.)
        with self.assertRaisesRegex(ValueError, 'threshold'):
            ewpo(d['physical'], d['electroweak'], d['ew_fit'])


class TestVacuum(unittest.TestCase):
    def test_physical_deeper_charge_breaking_stationary_witness(self):
        d = deeper(); x = d['physical']; p, _, _ = reconstruct(x)
        out = search_vacuum(p, x, starts=64, seeds=(123, 104852))
        self.assertEqual(out['status'], 'VACUUM_DEEPER_WITNESS')
        w = out['deeper_witness']; self.assertEqual(w['kind'], 'CHARGE_BREAKING')
        self.assertLess(w['gradient_over_v3'], 2e-7)
        # In this fixture the singlet-only stationary point is analytic.
        expected = -p['MCS2']**2/(4*p['LambdaC'])/x['v']**4
        self.assertAlmostEqual(w['value_over_v4'], expected, delta=2e-10)
        self.assertGreater(w['min_full_hessian_over_v2'], -2e-7)
        self.assertGreater(w['min_transverse_hessian_over_v2'], 1e-5)
        self.assertEqual(w['broken_gauge_rank'], 1)
        self.assertTrue(all(any(r['credible_stationary_minima'] for r in out['runs'] if r['seed'] == seed) for seed in (123, 104852)))
        METRICS['deeper_stationary_witness'] = w

    def test_gauge_ranks_neutral_generic_and_origin(self):
        p, _, _ = reconstruct(example()['physical']); pot = Potential(p)
        r = np.zeros(10); r[[2, 6]] = [43.304310942892, 242.381626159831]
        self.assertEqual(gauge_audit(r, pot.evaluate(r)[2])[0], 3)
        r = np.random.default_rng(13).normal(size=10)*100.
        self.assertEqual(gauge_audit(r, pot.evaluate(r)[2])[0], 4)
        r = np.zeros(10)
        self.assertEqual(gauge_audit(r, pot.evaluate(r)[2])[0], 0)

    def test_gauge_invariance_including_cubic_and_soft(self):
        p, _, _ = reconstruct(example()['physical'])
        r = np.random.default_rng(19).normal(size=10)*210.
        z = (r[::2]+1j*r[1::2])/math.sqrt(2)
        # Generic SU2 rotation and independent hypercharge rotation.
        angle, phase = .81, .47
        u = np.array([[math.cos(angle), 1j*math.sin(angle)], [1j*math.sin(angle), math.cos(angle)]])
        changed = np.r_[np.exp(.5j*phase)*(u@z[:2]), np.exp(.5j*phase)*(u@z[2:4]), np.exp(1j*phase)*z[4]]
        rp = np.empty(10); rp[::2] = math.sqrt(2)*changed.real; rp[1::2] = math.sqrt(2)*changed.imag
        value = component_value(r, p); other = component_value(rp, p)
        self.assertAlmostEqual(value/246.21965**4, other/246.21965**4, delta=2e-12)
        no_cubic = dict(p, Mu4=0.); no_soft = dict(p, M12Sq=0.)
        self.assertGreater(abs(value-component_value(r, no_cubic)), 1e5)
        self.assertGreater(abs(value-component_value(r, no_soft)), 1e5)


class TestContract(unittest.TestCase):
    def test_required_fields_nonfinite_and_unsupported_operators(self):
        d = example(); validate_input(d)
        for key in d['physical']:
            a = copy.deepcopy(d); del a['physical'][key]
            with self.assertRaises(ValueError): validate_input(a)
        for value in (math.nan, math.inf, True, '125'):
            a = copy.deepcopy(d); a['physical']['mh1'] = value
            with self.assertRaises(ValueError): validate_input(a)
        a = copy.deepcopy(d); a['physical']['lambda6'] = 1.
        with self.assertRaises(ValueError): validate_input(a)
        with self.assertRaises(ValueError): strict_loads('{"a":1,"a":2}')
        with self.assertRaises(ValueError): strict_loads('{"a":NaN}')

    def test_frozen_hash_mismatch_is_rejected(self):
        provenance()
        with patch('module1.scalar_constraints.digest', return_value='bad'):
            with self.assertRaisesRegex(ValueError, 'foundation hash mismatch'):
                provenance()

    def test_cli_jsonl_line_errors_and_exit_code(self):
        result = subprocess.run([sys.executable, '-m', 'module1.scalar_constraints', '--jsonl'],
                                input='{}\n{"a":NaN}\n', text=True, capture_output=True, cwd=ROOT)
        self.assertEqual(result.returncode, 2)
        rows = [json.loads(s) for s in result.stdout.splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r['global_zee_acceptance'] is None for r in rows))

    def test_unknown_never_becomes_acceptance(self):
        d = example()
        with patch('module1.scalar_constraints.search_vacuum', return_value={'status': 'VACUUM_NO_DEEPER_WITNESS_FOUND', 'assessment': 'UNKNOWN'}):
            out = evaluate(d)
        self.assertEqual(out['status'], 'SCALAR_PIPELINE_UNKNOWN')
        self.assertIsNone(out['global_zee_acceptance'])


if __name__ == '__main__':
    unittest.main()

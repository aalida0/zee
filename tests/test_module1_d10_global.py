"""Nine independent D10 checks: full fields, exact proof, singular falsifiers."""
from fractions import Fraction as Q
import json
import math
from pathlib import Path
import unittest

import numpy as np
import sympy as sp

from module1.d10_certificate import (Interval, attempt_certificate, neutral_enclosure,
                                     positive_ldl, rational_parameters, residual_form, singlet_axis_proof, radial_exclusion)
from module1.d10_polynomial import evaluate, invariants
from module1.d10_search import constrained_search, high_precision_check, orbit_fields, verify
from module1.potential import Potential, component_value
from module1.scalar_constraints import reconstruct

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']


def point(name):
    d = next(r['input'] for r in BENCHMARKS if r['input']['benchmark_id'] == name)
    return reconstruct(d['physical'])[0], d['physical']


def test_independent_complete_complex_polynomial():
    p, x = point('P2_beta_shift'); rng = np.random.default_rng(510)
    # Deliberately large signed K12 and Mu4 expose signs otherwise hidden by small portals.
    p = dict(p, K12=-.71, Mu4=-731.1)
    for _ in range(12):
        r = rng.normal(size=10)*x['v']
        a, b = evaluate(r, p), Potential(p).evaluate(r)
        assert abs(a[0]-component_value(r, p))/x['v']**4 < 2e-12
        for ai, bi, power in zip(a, b, (4, 3, 2)):
            assert np.max(np.abs(ai-bi))/x['v']**power < 3e-12
    r = rng.normal(size=10)*100; step = .001
    for i in range(10):
        d = np.eye(10)[i]*step
        assert abs((evaluate(r+d, p)[0]-evaluate(r-d, p)[0])/(2*step)-evaluate(r, p)[1][i])/x['v']**3 < 1e-8


def test_gauge_invariance_and_goldstone_nulls():
    p, x = point('d7_NO_neutral_near_heavy_07'); v = x['v']
    r = np.random.default_rng(43).normal(size=10)*v
    z = (r[::2]+1j*r[1::2])/np.sqrt(2)
    su = np.array([[np.cos(.81), 1j*np.sin(.81)], [1j*np.sin(.81), np.cos(.81)]])
    zz = np.r_[np.exp(.37j/2)*(su@z[:2]), np.exp(.37j/2)*(su@z[2:4]), np.exp(.37j)*z[4]]
    rr = np.empty(10); rr[::2] = np.sqrt(2)*zz.real; rr[1::2] = np.sqrt(2)*zz.imag
    assert abs(evaluate(r, p)[0]-evaluate(rr, p)[0])/v**4 < 1e-12
    ew = np.zeros(10); ew[[2, 6]] = [v*np.cos(x['beta']), v*np.sin(x['beta'])]
    w = verify(ew, p, x)
    assert w['broken_gauge_rank'] == 3
    assert w['gradient_over_v3'] < 1e-12
    assert w['gauge_ward_residual_over_v2'] < 1e-12
    assert w['min_transverse_hessian_over_v2'] > .2


def test_symbolic_full_cubic_square_completion_identity():
    x, y, u, w, s, a, b, e, mu, t = sp.symbols('x y u w s a b e mu t', nonzero=True)
    l1, l2, l3, l4, l5, lc, k1, k2, k12, soft, ms = sp.symbols('l1 l2 l3 l4 l5 lc k1 k2 k12 soft ms')
    c = sp.Matrix([[l1/2, l3/2, 0, 0, k1/2], [l3/2, l2/2, 0, 0, k2/2],
                   [0, 0, l4+l5, 0, -k12], [0, 0, 0, l4-l5, 0],
                   [k1/2, k2/2, -k12, 0, lc]])
    detform = sp.zeros(5); detform[0, 1] = detform[1, 0] = sp.Rational(1, 2)
    detform[2, 2] = detform[3, 3] = -1
    q, q0 = sp.Matrix([x, y, u, w, s]), sp.Matrix([a*a/2, b*b/2, a*b/2, 0, 0])
    m1 = soft*b/a-(l1*a*a+(l3+l4+l5)*b*b)/2
    m2 = soft*a/b-(l2*b*b+(l3+l4+l5)*a*a)/2
    v = lambda qq: (qq.T*c*qq)[0]+m1*qq[0]+m2*qq[1]-2*soft*qq[2]+ms*qq[4]
    n = a*a+b*b; bnorm = (b*b*x+a*a*y-2*a*b*u)/n
    md = n*(soft/(a*b)-(l4+l5)/2)
    meff = ms+(k1*a*a+k2*b*b-2*k12*a*b)/2
    dq = q-q0
    # e|d+mu S/e|² = eD+2mu Re(S*d)+mu²s/e, with all phases retained.
    rhs = (dq.T*(c-e*detform)*dq)[0]+e*(x*y-u*u-w*w)+2*mu*t+mu*mu*s/e
    rhs += (md-e*n/2)*bnorm+(meff-mu*mu/e)*s
    assert sp.factor(v(q)+2*mu*t-v(q0)-rhs) == 0


def test_exact_rational_certificate_and_root_enclosure():
    for name in ('d7_NO_neutral_near_heavy_07', 'F13_heavy_0001330', 'aligned_decoupling_1500'):
        p, x = point(name); c = attempt_certificate(p, x)
        assert c['certified']
        assert all(Q(s) > 0 for s in c['exact_ldl_pivots'])
        assert all(Q(s[0]) > 0 for s in c['nonnegative_coefficient_intervals_GeV2'])
        assert Q(c['neutral_root']['contraction_upper']) < Q(1, 10**25)
        box, _ = neutral_enclosure(p, x)
        assert all(t.hi-t.lo == Q(2, 10**40) for t in box)
        assert positive_ldl(residual_form(rational_parameters(p), Q(c['epsilon'])))
    for source in BENCHMARKS:
        x = source['input']['physical']; p = reconstruct(x)[0]
        bound = radial_exclusion(p, x)
        assert bound and Q(bound['EW_value_GeV4_interval'][1]) < 0
        assert Q(bound['exact_positive_quadratic_at_bound_GeV2']) > 0


def test_exact_interval_and_ldl_negative_controls():
    a, b = Interval(-2, 3), Interval(-4, -1)
    assert (a*b).serial() == ['-12', '8']
    assert (1/b).serial() == ['-1', '-1/4']
    with unittest.TestCase().assertRaises(ZeroDivisionError):
        _ = 1/a
    assert positive_ldl([[Q(1), Q(2)], [Q(2), Q(1)]]) is None
    p, x = point('P2_beta_shift')
    assert not attempt_certificate(p, x)['certified']
    p, x = point('d7_NO_neutral_near_heavy_07')
    assert not attempt_certificate(dict(p, Mu4=100000), x)['certified']
    assert not attempt_certificate(dict(p, LambdaC=-1), x)['certified']


def test_orbit_phase_minimization_including_singular_strata():
    p, x = point('P2_beta_shift'); v = x['v']; rng = np.random.default_rng(34)
    fields = [rng.normal(size=10)*v for _ in range(8)]
    for indices in (range(4), range(4, 8), range(8, 10)):
        r = fields[0].copy(); r[list(indices)] = 0; fields.append(r)
    fields.append(np.zeros(10))
    for r in fields:
        q, d, ss = invariants(r); xx, yy, u, w, s = q
        rho = np.clip(np.hypot(u, w)/np.sqrt(xx*yy), 0, 1) if xx*yy > 0 else 0
        t = [np.sqrt(xx)/v, np.sqrt(yy)/v, np.sqrt(s)/v, np.arccos(rho), np.arctan2(w, u)]
        rr, _ = orbit_fields(t, v, p['Mu4'])
        minimized = evaluate(rr, p)[0]
        expected = evaluate(r, p)[0]-2*p['Mu4']*(ss.conjugate()*d).real-2*abs(p['Mu4'])*abs(ss)*abs(d)
        assert abs(minimized-expected)/v**4 < 2e-12
        assert minimized <= evaluate(r, p)[0]+1e-11*v**4


def test_analytic_deeper_singlet_and_80digit_validation():
    p, x = point('physical_deeper_singlet'); proof = singlet_axis_proof(p, x)
    assert proof and Q(proof['delta_GeV4_interval'][1]) < -5e9
    r = np.zeros(10); r[8] = np.sqrt(-p['MCS2']/p['LambdaC'])
    w = verify(r, p, x); hp = high_precision_check(r, p, x)
    assert w['credible_stationary_minimum'] and w['broken_gauge_rank'] == 1
    assert float(hp['delta_GeV4']) < -5e9
    assert abs(float(hp['value_GeV4'])-float(Q(proof['value_GeV4']))) < 1e-5


def test_cubic_deformation_is_deeper_with_locally_positive_EW():
    p, x = point('P2_beta_shift'); p = dict(p, Mu4=1.5*p['Mu4'])
    ew = np.zeros(10); ew[[2, 6]] = [x['v']*np.cos(x['beta']), x['v']*np.sin(x['beta'])]
    assert verify(ew, p, x)['min_transverse_hessian_over_v2'] > .2
    result = constrained_search(p, x, starts=12)
    w = result['lowest_credible_minimum']
    assert w['kind'] == 'CHARGE_BREAKING' and w['delta_over_v4'] < -.19
    assert verify(w['fields_GeV'], p, x)['credible_stationary_minimum']


def test_source_bound_results_do_not_promote_numerical_absence():
    data = json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())
    statuses = {r['benchmark_id']: r['status'] for r in data['records']}
    assert statuses['P2_beta_shift'] == 'D10_UNKNOWN'
    assert statuses['F13_heavy_0000981'] == statuses['F13_heavy_0001003'] == 'D10_UNKNOWN'
    assert statuses['d7_NO_neutral_near_heavy_07'] == statuses['F13_heavy_0001330'] == 'D10_GLOBAL_CERTIFIED'
    for r in data['records']:
        assert r['global_zee_acceptance'] is None
        assert not r['module1_vacuum']['global_stability_proven']
        assert r['vacuum_decay_lifetime'] == 'NOT_EVALUATED'
        assert r['scalar_gates']['bfb']['assessment'] == r['scalar_gates']['unitarity']['assessment'] == 'PASS'
        if r['status'] == 'D10_GLOBAL_CERTIFIED':
            assert r['certificate_attempt']['certified']


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in sorted(globals().items())
                              if name.startswith('test_') and callable(value))


if __name__ == '__main__':
    unittest.main()

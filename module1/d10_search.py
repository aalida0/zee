"""Independent constrained Gram-orbit minimization and witness verification."""
import math

import mpmath as mp
import numpy as np
from scipy.optimize import minimize

from .d10_polynomial import NAMES, evaluate, functions, invariants
from .potential import gauge_audit


def orbit_fields(t, v, mu):
    """Norm roots A,B,T, misalignment eta, relative neutral phase theta.

    Singlet phase minimizes the sole phase-dependent singlet term exactly.
    This eliminates a physical phase by minimization, not by a gauge assumption.
    Every invariant boundary x=0,y=0,s=0,D=0 is included.
    """
    a, b, s, eta, theta = t
    sign = 1 if mu >= 0 else -1
    r = np.zeros(10)
    r[[2, 4, 6, 7, 8]] = np.sqrt(2)*v*np.array(
        [a, b*math.sin(eta), b*math.cos(eta)*math.cos(theta),
         b*math.cos(eta)*math.sin(theta), sign*s])
    jac = np.zeros((10, 5))
    jac[2, 0] = 1
    jac[[4, 6, 7], 1] = [math.sin(eta), math.cos(eta)*math.cos(theta), math.cos(eta)*math.sin(theta)]
    jac[8, 2] = sign
    jac[[4, 6, 7], 3] = [b*math.cos(eta), -b*math.sin(eta)*math.cos(theta), -b*math.sin(eta)*math.sin(theta)]
    jac[[6, 7], 4] = [-b*math.cos(eta)*math.sin(theta), b*math.cos(eta)*math.cos(theta)]
    return r, jac*np.sqrt(2)*v


def verify(r, p, x):
    v = x['v']
    val, g, h = evaluate(r, p)
    ew = np.zeros(10); ew[[2, 6]] = [v*math.cos(x['beta']), v*math.sin(x['beta'])]
    ewval = evaluate(ew, p)[0]
    rank, transverse, ward = gauge_audit(np.asarray(r), h)
    full = float(np.linalg.eigvalsh(h).min()/v**2)
    grad = float(max(abs(g))/v**3)
    q, _, _ = invariants(r)
    credible = grad < 2e-7 and full > -2e-7 and transverse/v**2 > 2e-7 and ward/v**2 < 2e-6
    return {'fields_GeV': np.asarray(r).tolist(), 'value_over_v4': val/v**4,
            'delta_over_v4': (val-ewval)/v**4, 'gradient_over_v3': grad,
            'min_full_hessian_over_v2': full, 'broken_gauge_rank': rank,
            'min_transverse_hessian_over_v2': transverse/v**2,
            'gauge_ward_residual_over_v2': ward/v**2,
            'credible_stationary_minimum': bool(credible),
            'kind': 'CHARGE_BREAKING' if q[4]/v**2 > 1e-10 or (q[0]*q[1]-q[2]**2-q[3]**2)/v**4 > 1e-10 else 'NEUTRAL'}


def high_precision_check(r, p, x):
    """80-digit independent expanded polynomial at the pinned binary fields."""
    with mp.workdps(80):
        rr = [mp.mpf(float(a)) for a in r]
        args = [mp.mpf(float(p[k])) for k in NAMES]
        value, gradient, hessian = functions('mpmath')
        ew = [mp.mpf(0)]*10
        ew[2], ew[6] = mp.mpf(x['v']*math.cos(x['beta'])), mp.mpf(x['v']*math.sin(x['beta']))
        v = mp.mpf(x['v'])
        h = hessian(rr, args)
        eig = mp.eigsy(h, eigvals_only=True)
        return {'precision_digits': 80, 'value_GeV4': mp.nstr(value(rr, args), 65),
                'delta_GeV4': mp.nstr(value(rr, args)-value(ew, args), 65),
                'gradient_over_v3': mp.nstr(max(abs(a) for a in gradient(rr, args))/v**3, 45),
                'full_hessian_eigenvalues_GeV2': [mp.nstr(a, 45) for a in eig]}


def polish_high_precision(witness, p, x):
    """80-digit chart stationarity polish, then independent full-space rejection."""
    ix = [2, 4, 6, 7, 8, 9]
    r = witness['fields_GeV']
    with mp.workdps(80):
        args = [mp.mpf(float(p[k])) for k in NAMES]
        _, gradient, hessian = functions('mpmath')

        def embed(t):
            rr = [mp.mpf(0)]*10
            for i, a in zip(ix, t):
                rr[i] = a
            return rr

        def fun(*t):
            g = gradient(embed(t), args)
            return [g[i] for i in ix]

        def jac(*t):
            h = hessian(embed(t), args)
            return mp.matrix([[h[i, j] for j in ix] for i in ix])

        root = mp.findroot(fun, [r[i] for i in ix], J=jac, tol=mp.mpf('1e-65'), maxsteps=40)
        rr = embed(root)
        polished = verify([float(a) for a in rr], p, x)
        if not polished['credible_stationary_minimum'] or polished['delta_over_v4'] >= -1e-6:
            raise ValueError('High-precision stationary polish failed full-space checks')
        polished['stationary_fields_80digit_GeV'] = [mp.nstr(a, 70) for a in rr]
        polished['polished_gradient_over_v3'] = mp.nstr(max(abs(a) for a in gradient(rr, args))/mp.mpf(x['v'])**3, 45)
    polished['independent_80digit'] = high_precision_check(polished['fields_GeV'], p, x)
    return polished


def constrained_search(p, x, seed=20261103, starts=16):
    """Finite SLSQP, independent symbolic derivatives; never a global proof."""
    v = x['v']; rng = np.random.default_rng(seed)
    ew = [math.cos(x['beta'])/np.sqrt(2), math.sin(x['beta'])/np.sqrt(2), 0, 0, 0]
    # Explicit singular strata, CP-violating and charged starts, plus modest multiscale random starts.
    choices = [ew, [0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0, 1, 0, 0, 0],
               [0, 0, 1, 0, 0], [.5, .5, .5, math.pi/2, 0], [.5, .5, 0, 0, math.pi/2]]
    for i in range(starts):
        choices.append([*rng.uniform(.05, (.5, 2, 5)[i % 3], 3), rng.uniform(0, math.pi/2), rng.uniform(-math.pi, math.pi)])

    def fun(t):
        r, jac = orbit_fields(t, v, p['Mu4'])
        value, gradient, _ = evaluate(r, p)
        return value/v**4, jac.T@gradient/v**4

    rows = []; candidates = []
    for t in choices:
        result = minimize(fun, t, jac=True, method='SLSQP',
                          bounds=[(0, 12)]*3+[(0, math.pi/2), (-math.pi, math.pi)],
                          options={'maxiter': 500, 'ftol': 2e-13})
        r, _ = orbit_fields(result.x, v, p['Mu4'])
        w = verify(r, p, x)
        boundary = bool(max(result.x[:3]) > 12-1e-5)
        rows.append({'success': bool(result.success), 'iterations': result.nit,
                     'credible': bool(w['credible_stationary_minimum'] and not boundary),
                     'outer_boundary': boundary, 'delta_over_v4': w['delta_over_v4']})
        if w['credible_stationary_minimum'] and not boundary:
            candidates.append(w)
    best = min(candidates, key=lambda w: w['value_over_v4']) if candidates else None
    return {'method': 'SLSQP_PHASE_MINIMIZED_COMPLETE_GRAM_ORBIT', 'seed': seed,
            'norm_root_bound_over_v': 12, 'runs': rows, 'lowest_credible_minimum': best,
            'global_stability_proven': False}

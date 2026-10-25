"""All-orientation sufficient certificates and independently checked witnesses.

V4 >= a*x²+b*y²+c*s²+d*x*y+e*x*s+f*y*s for nonnegative norms,
d=L3+min(0,L4-|L5|), e=K1-|K12|, f=K2-|K12|.
This follows from |z|²<=xy and 2|z|<=x+y. Strict copositivity of
this 3x3 lower-bound form suffices. It is NOT necessary for Zee BFB.
Alternatively a nonnegative portal and strict doublet positivity suffice.
Flat/marginal quartics are UNKNOWN: dimensionful terms can matter there.
"""
import math
import mpmath as mp
import numpy as np
from scipy.optimize import differential_evolution
from .potential import component_value


def orbit_fields(t):
    u, v, rho, phase = t
    x, y, s = math.cos(u)**2*math.cos(v)**2, math.sin(u)**2*math.cos(v)**2, math.sin(v)**2
    z = rho*math.sqrt(x*y)*complex(math.cos(phase), math.sin(phase))
    r = np.zeros(10)
    r[2] = math.sqrt(2*x)
    if x > 1e-28:
        r[4] = math.sqrt(2*max(0., y-abs(z)**2/x))
        r[6], r[7] = math.sqrt(2)*z.real/math.sqrt(x), math.sqrt(2)*z.imag/math.sqrt(x)
    else:
        r[6] = math.sqrt(2*y)
    r[8] = math.sqrt(2*s)
    return r


def high_precision_quartic(r, p):
    """60-digit complex component substitution, with the actual binary inputs."""
    with mp.workdps(60):
        a = [mp.mpf(float(v)) for v in r]
        z = [mp.mpc(a[i], a[i+1])/mp.sqrt(2) for i in range(0, 10, 2)]
        x, y, s = sum(abs(w)**2 for w in z[:2]), sum(abs(w)**2 for w in z[2:4]), abs(z[4])**2
        t = sum(mp.conj(z[i])*z[i+2] for i in (0, 1))
        q = {k: mp.mpf(float(v)) for k, v in p.items() if k.startswith(('Lambda', 'K'))}
        value = (q['Lambda1']/2*x*x+q['Lambda2']/2*y*y+q['Lambda3']*x*y
                 +q['Lambda4']*abs(t)**2+q['Lambda5']*mp.re(t*t)+q['LambdaC']*s*s
                 +(q['K1']*x+q['K2']*y-2*q['K12']*mp.re(t))*s)
        return mp.nstr(value, 55)


def certificate(p):
    # Compute the sufficient inequalities at high precision. Positive margins
    # exclude ambiguous floating-point equality; they are not interval proofs.
    with mp.workdps(60):
        q = {k: mp.mpf(float(v)) for k, v in p.items() if k.startswith(('Lambda', 'K'))}
        l1, l2, lc = q['Lambda1'], q['Lambda2'], q['LambdaC']
        tol = mp.mpf('1e-12')*max(1, *(abs(v) for v in q.values()))
        if min(l1, l2, lc) <= tol:
            return None
        doublet = min(q['Lambda3']+mp.sqrt(l1*l2),
                      q['Lambda3']+q['Lambda4']-abs(q['Lambda5'])+mp.sqrt(l1*l2))
        if (doublet > tol and min(q['K1'], q['K2']) >= 0
                and q['K1']*q['K2']-q['K12']**2 > tol**2):
            return 'STRICT_DOUBLET_AND_NONNEGATIVE_PORTAL'
        a, b, c = l1/2, l2/2, lc
        d = (q['Lambda3']+min(0, q['Lambda4']-abs(q['Lambda5'])))/2
        e, f = (q['K1']-abs(q['K12']))/2, (q['K2']-abs(q['K12']))/2
        bars = (d+mp.sqrt(a*b), e+mp.sqrt(a*c), f+mp.sqrt(b*c))
        if min(bars) > tol:
            last = (mp.sqrt(a*b*c)+d*mp.sqrt(c)+e*mp.sqrt(b)+f*mp.sqrt(a)
                    +mp.sqrt(2*bars[0]*bars[1]*bars[2]))
            if last > tol**mp.mpf('1.5'):
                return 'STRICT_COPOSITIVE_ALL_ORIENTATION_LOWER_BOUND'
    return None


def check_bfb(p, seeds=(173, 991)):
    proof = certificate(p)
    if proof:
        return {'status': 'BFB_CERTIFIED_SUFFICIENT', 'assessment': 'PASS',
                'certificate': proof, 'necessary_and_sufficient': False,
                'precision_digits': 60, 'negative_witness': None}
    # Compact orbit parameterization covers every complex Gram matrix and
    # singlet norm. Singlet phase cannot affect V4. Includes charged doublets.
    bounds = [(0, math.pi/2), (0, math.pi/2), (0, 1), (-math.pi, math.pi)]
    axes = np.sqrt(2)*np.eye(10)[[2, 6, 8]]
    candidates = list(axes)
    diagnostics = []
    objective = lambda t: component_value(orbit_fields(t), p, quartic_only=True)
    for seed in seeds:
        result = differential_evolution(objective, bounds, seed=seed, popsize=10,
                                        maxiter=160, tol=1e-9, polish=True)
        candidates.append(orbit_fields(result.x))
        diagnostics.append({'seed': seed, 'converged': bool(result.success), 'minimum': float(result.fun)})
    best = min(candidates, key=lambda r: component_value(r, p, quartic_only=True))
    value = component_value(best, p, quartic_only=True)
    hp = high_precision_quartic(best, p)
    scale = max(1., *(abs(p[k]) for k in p if k.startswith(('Lambda', 'K'))))
    witness = value < -1e-10*scale and float(hp) < -1e-10*scale
    return {'status': 'BFB_NEGATIVE_WITNESS' if witness else 'BFB_UNKNOWN',
            'assessment': 'FAIL' if witness else 'UNKNOWN', 'certificate': None,
            'necessary_and_sufficient': False, 'searches': diagnostics,
            'negative_witness': {'canonical_fields': best.tolist(), 'V4': value,
                                 'V4_60digit': hp,
                                 'alternative_evaluation_residual': abs(value-float(hp))} if witness else None,
            'absence_of_witness_proves_bfb': False}

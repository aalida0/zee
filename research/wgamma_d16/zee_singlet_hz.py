"""Isolated, unmixed Zee singlet scalar-Z-photon class, NOT full Zee matching.

Both scalar-current triangles and the AZ seagull are included. No W, F,
charged mixing, or overlap with the frozen scalar-photon coefficients is added.
See ZEE_EXTENSION_INVENTORY.md for the Ward identity and restriction proof.
"""
from functools import lru_cache
import numpy as np
from scipy.integrate import quad


@lru_cache(maxsize=128)
def hz_radial_kernel(x, y):
    """f10=-int_0^1 da u int_0^infty dt t/[(t+x)(t+yu)(t+u)].

    Derived by partial fractions of the massive outer Z and scalar
    propagators from the independently normalized scalar-QED photon graph.
    Direct finite parameters, including y=1; no shared author functions.
    Returns value and a conservative quadrature-error estimate.
    """
    if not np.isfinite([x, y]).all() or min(x, y) <= 0:
        raise ValueError('Positive finite squared-mass ratios required')
    inner_errors = []
    def integrand(a):
        u = a*(1-a)
        value, error = quad(lambda t: t/((t+x)*(t+y*u)*(t+u)),
                            0, np.inf, epsabs=1e-10, epsrel=2e-11, limit=250)
        inner_errors.append(u*error)
        return -u*value
    value, error = quad(integrand, 0, .5, epsabs=2e-11, epsrel=2e-10, limit=150)
    error = 2*(error+max(inner_errors, default=0.))
    if not np.isfinite([value, error]).all() or error > 2e-8*max(1., abs(value)):
        raise ArithmeticError('Uncontrolled scalar-Z radial integral')
    return 2*value, error


def singlet_hz(D, F, p, ml, mw, mz, i, j):
    """Only gamma=0, F=0, H2 a pure hypercharge-one singlet.

    Keeps general real K1,K2,K12 portals and complex D. Coefficients belong to
    this complete Abelian class only and are never inserted into matching.py.
    """
    from module1.scalar_constraints import reconstruct
    from module3.core import vertices
    from module4.couplings import trilinears
    D, F, ml = np.asarray(D, complex), np.asarray(F, complex), np.asarray(ml, float)
    if D.shape != (3, 3) or F.shape != (3, 3) or ml.shape != (3,):
        raise ValueError('3x3 Yukawas and three lepton masses required')
    if not np.isfinite(D).all() or not np.isfinite(F).all() or not np.isfinite(ml).all():
        raise ValueError('Finite Yukawas and lepton masses required')
    if p['gamma'] != 0. or np.any(F != 0.):
        raise ValueError('This complete class is certified only at gamma=0, F=0')
    if (i, j) not in ((1, 0), (2, 0), (2, 1)) or min(ml) <= 0:
        raise ValueError('Supported radiative channel and positive masses required')
    if not np.isfinite([mw, mz]).all() or not 0 < mw < mz:
        raise ValueError('On-shell EW masses 0<MW<MZ required')
    lag, _, closure = reconstruct(p)
    if lag['Mu4'] != 0.:
        raise ValueError('Mu4 must vanish for the unmixed singlet class')
    gs = trilinears(p, lag)
    sw2 = 1-mw**2/mz**2; sw, cw = np.sqrt(sw2), mw/mz
    alpha = (2*mw/p['v'])**2*sw2/(4*np.pi)
    vze = (-.5+2*sw2)/(sw*cw)
    tz = -sw/cw  # positive singlet: (T3-Q sw^2)/(sw cw), Q=1, T3=0
    rows = {}; total = np.zeros(2, complex)
    for name, (C, mass) in vertices(D, p, ml).items():
        g = complex(gs[name][2, 2])
        if abs(g.imag) > 1e-10:
            raise ValueError('Real neutral diagonal trilinear required')
        kernel, error = hz_radial_kernel((p['mH2']/mass)**2, (mz/mass)**2)
        ext = np.array([C[j, i], C[i, j].conjugate()])
        # C_gamma=-alpha G ext f9/(32 pi^3 mi M^2).
        # Outer vector-current ratio is -v_e^Z/2 for Q_lepton=-1.
        # The positive massive radial integral is -f10; the two signs cancel.
        # The inner triangle AND contact current ratio is t_Z/Q, Q=1.
        pref = -alpha*vze*tz*g.real/(64*np.pi**3*ml[i]*mass**2)
        value = pref*ext*kernel
        total += value
        rows[name] = dict(G_GeV=g.real, f10_radial=kernel,
            class_C_LR_GeV_minus2=value, quadrature_abs_error=float(abs(pref)*max(abs(ext))*error))
    return dict(status='VALIDATED_RESTRICTED_UNMIXED_SINGLET_HZ_CLASS',
        scope='gamma=0,F=0; complete scalar-current triangles plus AZ seagull; external-invariant leading expansion; no full Zee W matching',
        class_C_LR_GeV_minus2=total, rows=rows, closure=closure,
        positive_singlet_Z_charge_over_e=tz, alpha=alpha, sw2=sw2,
        coherent_inclusion=False)

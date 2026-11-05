"""Unequal-mass physical-charged-scalar HZ calculation in the D15 convention.

The unprojected scalar-current tensor and its nonzero longitudinal identity
are kept independently of the soft, real-photon dipole. See MIXED_HZ_DERIVATION.
This module supplies one class, never a complete Zee two-loop prediction.
"""
from functools import lru_cache

import numpy as np
from scipy.integrate import quad


@lru_cache(maxsize=32)
def rule(n):
    x, w = np.polynomial.legendre.leggauss(n)
    return (x+1)/2, w/2


def scalar_current_tensor(p, k, ma2, mb2, order=64, contact=True):
    """Euclidean DR finite tensor /(e^2 G_ab T_ba/(16 pi^2)).

    p enters the photon, k enters Z; complex Euclidean null p is supported.
    Includes both photon placements and the AZ contact. Returns independently
    integrated J_mu with k_nu T_mu,nu=-(mb2-ma2) J_mu. Pole residues are
    +1,+1,-2 times delta_mu,nu, including d=4-2eps rational terms.
    No transversality is imposed. All masses and momenta use common units.
    """
    p, k = np.asarray(p, complex), np.asarray(k, complex)
    if p.shape != (4,) or k.shape != (4,) or not np.isfinite([p, k]).all():
        raise ValueError('Finite four-momenta required')
    if min(ma2, mb2) <= 0 or not np.isfinite([ma2, mb2]).all():
        raise ValueError('Positive finite charged squared masses required')
    r = p+k
    x, w = rule(order)
    a, b = np.meshgrid(x, x, indexing='ij')
    b = b*(1-a)
    weight = w[:, None]*w[None, :]*(1-a)
    eye = np.eye(4)
    tensor = np.zeros((4, 4), complex)
    current = np.zeros(4, complex)
    scale = np.sqrt(ma2*mb2)
    for first in (True, False):
        u, v = (p, r) if first else (k, r)
        R = a[..., None]*u+b[..., None]*v
        delta = ((1-a-b)*ma2+a*(ma2 if first else mb2)+b*mb2
                 +a*(u@u)+b*(v@v)-np.einsum('...i,...i->...', R, R))
        A = (p if first else p+2*k)-2*R  # photon numerator
        B = (2*p+k if first else k)-2*R  # Z numerator
        tensor += np.einsum('ab,abij->ij', weight,
            -2*np.log(delta/scale)[..., None, None]*eye
            +A[..., :, None]*B[..., None, :]/delta[..., None, None])
        current += np.einsum('ab,abi->i', weight, A/delta[..., None])
    delta = (1-x)*ma2+x*mb2+x*(1-x)*(r@r)
    if contact:
        tensor += 2*np.sum(w*np.log(delta/scale))*eye
    return dict(tensor=tensor, goldstone_current=current,
                uv_pole=(0. if contact else 2.)*eye)


@lru_cache(maxsize=256)
def mixed_hz_kernel(xa, xb, y):
    """Symmetric unequal-mass f10; direct nested positive radial integral.

    -int da u int dt t/[(t+(1-a)xa+a xb)(t+y u)(t+u)].
    Error is an adaptive quadrature estimate, not a rigorous error bound.
    """
    if not np.isfinite([xa, xb, y]).all() or min(xa, xb, y) <= 0:
        raise ValueError('Positive finite squared-mass ratios required')
    if xb < xa:
        return mixed_hz_kernel(xb, xa, y)
    errors = []
    def angular(a):
        u = a*(1-a)
        mass = (1-a)*xa+a*xb
        val, err = quad(lambda t: t/((t+mass)*(t+y*u)*(t+u)),
                        0, np.inf, epsabs=2e-10, epsrel=3e-10, limit=250)
        errors.append(u*err)
        return -u*val
    val, err = quad(angular, 0, 1, epsabs=2e-10, epsrel=3e-10, limit=200)
    err += max(errors, default=0.)
    if not np.isfinite([val, err]).all() or err > 2e-7*max(1., abs(val)):
        raise ArithmeticError('Uncontrolled mixed HZ quadrature')
    return float(val), float(err)


def mixed_hz_kernel_bounded(xa, xb, y, order=256):
    """Independent bounded two-parameter rule, t=u*w/(1-w)."""
    if not np.isfinite([xa, xb, y]).all() or min(xa, xb, y) <= 0:
        raise ValueError('Positive finite squared-mass ratios required')
    a, wa = rule(order)
    z, wz = rule(order)
    u = a[:, None]*(1-a[:, None])
    mass = (1-a[:, None])*xa+a[:, None]*xb
    return float(-np.sum(wa[:, None]*wz[None, :]*u*z[None, :]
        /((y+(1-y)*z[None, :])*(mass*(1-z[None, :])+u*z[None, :]))))


def charges(p, mw, mz):
    from module4.couplings import rotations
    if not np.isfinite([mw, mz]).all() or not 0 < mw < mz:
        raise ValueError('Require on-shell 0<MW<MZ')
    sw, cw = np.sqrt(1-(mw/mz)**2), mw/mz
    e = 2*mw/p['v']*sw
    _, _, zp = rotations(p)
    generator = zp@np.diag([.5-sw*sw, .5-sw*sw, -sw*sw])@zp.T/(sw*cw)
    return generator[1:, 1:], e, sw, cw


def goldstone_trilinear(p, lag):
    """Independent potential derivative, NOT a fitted commutator identity."""
    from module4.couplings import rotations
    _, _, zp = rotations(p)
    cb, sb = np.cos(p['beta']), np.sin(p['beta'])
    mu = lag['Mu4']/np.sqrt(2)
    native = 1j*np.array([[0., 0., -mu*sb], [0., 0., mu*cb],
                         [mu*sb, -mu*cb, 0.]])
    return (zp@native@zp.T)[1:, 1:]


def spectral_sum(mass2, G, T, neutral_mass2, mz2):
    """Basis-covariant spectral contraction, usable in a dense charged basis."""
    mass2, G, T = (np.asarray(z, complex) for z in (mass2, G, T))
    if any(z.shape != (2, 2) or not np.isfinite(z).all() for z in (mass2, G, T)):
        raise ValueError('Finite two-state matrices required')
    if any(not np.allclose(z, z.conj().T, rtol=0, atol=1e-9) for z in (mass2, G, T)):
        raise ValueError('Hermitian matrices required')
    ev, U = np.linalg.eigh(mass2)
    g, t = U.conj().T@G@U, U.conj().T@T@U
    total, error, rows = 0j, 0., []
    for a in range(2):
        for b in range(2):
            f, err = mixed_hz_kernel(float(ev[a]/neutral_mass2),
                                    float(ev[b]/neutral_mass2), float(mz2/neutral_mass2))
            weight = g[a, b]*t[b, a]
            total += weight*f
            error += abs(weight)*err
            rows.append(dict(a=a, b=b, G=g[a, b], T=t[b, a], kernel=f,
                             kernel_error=err, weighted_kernel=weight*f))
    return total, error, rows


def mixed_hz(D, p, ml, mw, mz, i, j):
    """Physical charged scalar-current class only, with complex L/R Wilsons.

    F does not enter these neutral external Yukawas or bosonic loop vertices.
    No statement about F-dependent charged-current amplitudes is made here.
    Both ordered channels are allowed for HC tests with their own parent mass.
    """
    from module1.scalar_constraints import reconstruct
    from module3.core import vertices
    from module4.couplings import trilinears
    D, ml = np.asarray(D, complex), np.asarray(ml, float)
    if (D.shape != (3, 3) or ml.shape != (3,) or not np.isfinite(D).all()
            or not np.isfinite(ml).all() or min(ml) <= 0 or i == j
            or i not in range(3) or j not in range(3)):
        raise ValueError('Finite 3x3 D, positive lepton masses and distinct indices required')
    lag, _, closure = reconstruct(p)
    tri = trilinears(p, lag)
    T, e, sw, cw = charges(p, mw, mz)
    M = np.diag(np.array([p['mH1'], p['mH2']])**2)
    g0 = goldstone_trilinear(p, lag)
    st_residual = np.max(abs(g0-1j*e/mz*(M@T-T@M)))
    if st_residual > 2e-8:
        raise ValueError('Native neutral-Goldstone mass-difference identity failed')
    alpha = e*e/(4*np.pi)
    vz = (-.5+2*sw*sw)/(sw*cw)
    total, error, rows = np.zeros(2, complex), np.zeros(2), {}
    for name, (C, mass) in vertices(D, p, ml).items():
        scalar_sum, err, terms = spectral_sum(M, tri[name][1:, 1:], T, mass**2, mz**2)
        external = np.array([C[j, i], C[i, j].conjugate()])
        prefactor = -alpha*vz/(64*np.pi**3*ml[i]*mass**2)
        val = prefactor*external*scalar_sum
        uncertainty = abs(prefactor*external)*err
        total += val
        error += uncertainty
        rows[name] = dict(C_LR=val, error=uncertainty, terms=terms,
                         G=tri[name][1:, 1:], external_LR=external)
    return dict(status='CALCULATED_MIXED_HZ_CLASS_ONLY', C_LR=total,
                quadrature_error=error, rows=rows, T=T, G0=g0,
                G0_identity_abs_residual=st_residual,
                commutator_M2_T=M@T-T@M, closure=closure,
                coherent_inclusion=False, full_two_loop_C_LR=None)

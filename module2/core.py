"""Finite one-loop mass and complete linear inverse in the frozen SARAH basis."""
import math
import mpmath as mp
import numpy as np


class NumericalUnknown(ValueError):
    """Input is algebraically singular or numerically unresolved; never a pass."""


def real_number(x, name='number'):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, (int, float, np.number)) or not np.isreal(x) or not np.isfinite(x):
        raise ValueError(name+' must be finite real')
    return float(np.real(x))


def matrix(x, kind=None):
    a = np.asarray(x, complex)
    if a.shape != (3, 3) or not np.isfinite(a).all():
        raise ValueError('Require finite complex 3x3 matrix')
    scale = max(float(np.max(abs(a))), np.finfo(float).tiny)
    if kind and np.max(abs(a - a.T if kind == 'symmetric' else a + a.T)) > 2e-13*scale:
        raise ValueError('Matrix must be '+kind)
    return a


def lepton_masses(ml):
    a = np.asarray(ml)
    if a.shape != (3,):
        raise ValueError('Require three charged-lepton masses in GeV')
    a = np.array([real_number(x, 'lepton mass') for x in a])
    if np.any(a <= 0) or np.any(np.diff(a) <= 0):
        raise ValueError('Require 0 < m_e < m_mu < m_tau')
    return a


def loop_kernel(m1, m2, ml):
    """Integral log[(x ml²+(1-x)m1²)/(x ml²+(1-x)m2²)].

    Analytic primitive at 60 digits avoids subtraction loss for adjacent binary64
    scalar masses and removable t=ml² singularities. No massless approximation.
    """
    m1, m2, ml = [real_number(x) for x in (m1, m2, ml)]
    if min(m1, m2) <= 0 or ml < 0:
        raise ValueError('Invalid loop masses')
    if m1 == m2:
        return 0.
    with mp.workdps(60):
        a, b, z = [mp.mpf(x)**2 for x in (m1, m2, ml)]
        if not z:
            return float(mp.log(a/b))
        def primitive(t):
            if t == z:
                return mp.log(z)
            return mp.log(z)-1+t*mp.log(t/z)/(t-z)
        return float(primitive(a)-primitive(b))


def weights(m1, m2, gamma, ml):
    ml = lepton_masses(ml)
    gamma = real_number(gamma, 'gamma')
    if abs(gamma) > math.pi/2:
        raise ValueError('gamma outside frozen mixing chart')
    kernels = np.array([loop_kernel(m1, m2, x) for x in ml])
    sine = 0. if abs(gamma) in (0., math.pi/2) else math.sin(2*gamma)
    return 1e9*sine/(32*math.pi**2)*ml*kernels  # eV, D and F dimensionless


def forward(F, D, *, m1, m2, gamma, ml):
    F, D = matrix(F, 'antisymmetric'), matrix(D)
    a = (F*weights(m1, m2, gamma, ml)) @ D
    result = a+a.T
    if not np.isfinite(result).all():
        raise NumericalUnknown('Nonfinite forward mass')
    return result


def yukawa_rotation(D, beta, v, ml):
    """Return unrestricted Ye,Ye2; c_beta Ye+s_beta Ye2=sqrt(2) Ml/v."""
    D = matrix(D)
    beta, v = real_number(beta), real_number(v)
    if not 0 < beta < math.pi/2 or v <= 0:
        raise ValueError('Invalid beta or v')
    S = np.diag(np.sqrt(2)*lepton_masses(ml)/v)
    c, s = math.cos(beta), math.sin(beta)
    return c*S-s*D, s*S+c*D


def null_cone(M, t, scale, root=0, chart=(0, 1, 2), free_x=None):
    """n[chart]=(1,x,t). Solve a*x²+b*x+c=0 over C; F n=0.

    All nonzero projective n are covered by permutations and the t parameter,
    with free_x supplying the extra coordinate for an identically zero
    polynomial (including M=0). Otherwise free_x must be omitted.
    Linear, identically-zero and empty chart polynomials are handled explicitly.
    scale is the positive maximum modulus of F; its global phase is free via t,
    orientations, or multiplication of returned F by a unit complex number.
    """
    M = matrix(M, 'symmetric')
    t = complex(t)
    if (not np.isfinite(t) or real_number(scale) <= 0 or type(root) is not int or root not in (0, 1)
            or len(chart) != 3 or any(isinstance(i, (bool, np.bool_)) or not isinstance(i, (int, np.integer)) for i in chart)
            or sorted(chart) != [0, 1, 2] or (free_x is not None and not np.isfinite(complex(free_x)))):
        raise ValueError('Invalid null-cone parameters')
    magnitude = float(np.max(abs(M)))
    if not np.isfinite(magnitude):
        raise NumericalUnknown('Null-cone matrix scale exceeds finite numerical range')
    normalized = M/magnitude if magnitude else M
    p = normalized[np.ix_(chart, chart)]
    a, b, c = p[1, 1], 2*(p[0, 1]+t*p[1, 2]), p[0, 0]+2*t*p[0, 2]+t*t*p[2, 2]
    if free_x is not None and (a != 0 or b != 0 or c != 0):
        raise ValueError('free_x applies only to an identically zero null-cone polynomial')
    # Do not discard small nonzero coefficients: they can select a large root.
    if a != 0:
        roots = np.roots([a, b, c])
        roots = sorted(roots, key=lambda z: (abs(z), z.real, z.imag))
        x = roots[root]
    elif b != 0:
        if root:
            raise NumericalUnknown('Only one finite root in this chart')
        x = -c/b
    elif c == 0:
        x = complex(root) if free_x is None else complex(free_x)
    else:
        raise NumericalUnknown('Empty null-cone chart; select another chart or t')
    n = np.empty(3, complex)
    n[list(chart)] = [1, x, t]
    n /= np.max(abs(n))
    n /= np.linalg.norm(n)
    F = np.array([[0, n[2], -n[1]], [-n[2], 0, n[0]], [n[1], -n[0], 0]])
    F *= scale/np.max(abs(F))
    residual = abs(n.T@normalized@n)/max(np.linalg.norm(normalized), np.finfo(float).tiny)
    if not np.isfinite(F).all() or residual > 2e-11:
        raise NumericalUnknown('Unresolved bilinear null cone')
    return F, n


def solve_fixed_f(F, M, *, m1, m2, gamma, ml):
    """D=D0+sum(z_k H_k), k=0..3, arbitrary complex z; no alignment."""
    F, M = matrix(F, 'antisymmetric'), matrix(M, 'symmetric')
    w = weights(m1, m2, gamma, ml)
    if np.max(abs(F)) == 0 or np.min(abs(w)) == 0:
        raise NumericalUnknown('Zero F or vanishing loop weights: inverse undefined')
    upper = np.triu_indices(3)
    cols = []
    for E in np.eye(9).reshape(9, 3, 3):
        a = (F*w)@E
        cols.append((a+a.T)[upper])
    A = np.array(cols).T
    u, s, vh = np.linalg.svd(A, full_matrices=True)
    rank = int(np.count_nonzero(s > s[0]*1e-12))
    if rank != 5 or s[0]/s[4] > 1e10:
        raise NumericalUnknown('Ill-conditioned inverse or unresolved rank (expected five)')
    D0 = vh[:5].conj().T@((u[:, :5].conj().T@M[upper])/s[:5])
    H = vh[5:].conj().reshape(4, 3, 3)
    residual = float(np.linalg.norm(A@D0-M[upper])/max(np.linalg.norm(M[upper]), np.finfo(float).tiny))
    if residual > 2e-10:
        raise ValueError('Target inconsistent with fixed F: n.T M n must vanish')
    nullres = float(np.linalg.norm(A@H.reshape(4, 9).T)/np.linalg.norm(A))
    if nullres > 1e-12:
        raise NumericalUnknown('Homogeneous basis failed')
    return {'D0': D0.reshape(3, 3), 'homogeneous': H, 'rank': rank,
            'nullity_complex': 4, 'singular_values': s, 'condition': float(s[0]/s[4]),
            'relative_residual': residual, 'homogeneous_relative_residual': nullres}

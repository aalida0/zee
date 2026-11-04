"""Independent Dirac/Ward reductions. No published W kernel is used here."""
import math

import numpy as np
from scipy.integrate import quad

ETA = np.array([1., -1., -1., -1.])
METRIC = np.diag(ETA)
ID = np.eye(4, dtype=complex)
_I = np.eye(2, dtype=complex)
_Z = np.zeros((2, 2), dtype=complex)
PAULI = [np.array([[0, 1], [1, 0]], complex),
         np.array([[0, -1j], [1j, 0]], complex), np.diag([1., -1.])]
# Weyl basis, independently of the D15 Dirac-basis spinor implementation.
GAMMA = [np.block([[_Z, _I], [_I, _Z]])] + [
    np.block([[_Z, s], [-s, _Z]]) for s in PAULI]
G5 = 1j*GAMMA[0]@GAMMA[1]@GAMMA[2]@GAMMA[3]
PL, PR = (ID-G5)/2, (ID+G5)/2


def dot(p, k):
    return np.asarray(p) @ (ETA*np.asarray(k))


def slash(p):
    return sum(x*g for x, g in zip(ETA*np.asarray(p), GAMMA))


def spinor(p, mass, spin):
    chi = np.eye(2)[:, spin]
    upper = math.sqrt(p[0]+mass)*chi
    lower = sum(p[a+1]*PAULI[a] for a in range(3))@chi/math.sqrt(p[0]+mass)
    return np.r_[upper-lower, upper+lower]/math.sqrt(2)


def bar(u):
    return u.conjugate()@GAMMA[0]


def propagator_numerator(p, mass):
    """The i is common to both outer attachments and stripped here."""
    den = dot(p, p)-mass*mass
    if abs(den) < 1e-12*max(1., abs(dot(p, p)), mass*mass):
        raise ValueError('Choose a virtual momentum away from the fermion pole')
    return (slash(p)+mass*ID)/den


def outer_current(pi, pj, k, mi, mj, left, right, si=0, sj=0,
                  attachment='both'):
    """k flows OUT of inner loop, INTO the lepton line; scalar momentum q+k.

    gamma^nu S_j(p_j-k) X + X S_i(p_i+k) gamma^nu.
    Contracting k gives -X + X between the on-shell spinors, exactly.
    """
    if attachment not in ('both', 'daughter', 'parent'):
        raise ValueError('Unknown photon attachment')
    X = left*PL+right*PR
    ui, uj = spinor(pi, mi, si), spinor(pj, mj, sj)
    sjprop = propagator_numerator(pj-k, mj)
    siprop = propagator_numerator(pi+k, mi)
    return np.array([bar(uj)@(
        (g@sjprop@X if attachment != 'parent' else np.zeros((4, 4))) +
        (X@siprop@g if attachment != 'daughter' else np.zeros((4, 4))))@ui
        for g in GAMMA])


def decay_momenta(mi=3., mj=.7):
    if not 0 < mj < mi:
        raise ValueError('Require a physical unequal-mass radiative decay')
    direction = np.array([1., 2., 3.])/math.sqrt(14)
    energy = (mi*mi-mj*mj)/(2*mi)
    pi = np.array([mi, 0., 0., 0.])
    q = np.r_[energy, energy*direction]
    return pi, pi-q, q


def source_tensors(q, k, scalar_mass, mw=80.379, order=48):
    """Abe v3 3.8--3.14, G=photon, xi=1 ONLY, with common prefactor stripped.

    This is a transcription of SOURCE tensors, not an independent W-loop
    diagram calculation. p1=q, p2=k are outgoing from the inner loop.
    All A/P/B/C tensors are returned before any contraction or reduction.
    """
    q, k = np.asarray(q), np.asarray(k)
    if abs(dot(q, q)) > 1e-10:
        raise ValueError('This source representation requires one real photon')
    x, w = np.polynomial.legendre.leggauss(order)
    x, w = (x+1)/2, w/2
    xx, t = x[:, None], x[None, :]
    yy = (1-xx)*t
    weight = w[:, None]*w[None, :]*(1-xx)
    k2, s = dot(k, k), dot(q+k, q+k)
    den = 1-k2/mw**2*xx*(1-xx)-(s-k2)/mw**2*xx*yy
    if np.min(den) <= 0:
        raise ValueError('Real quadrature supports the below-threshold domain only')
    j1, j2 = np.sum(weight/den), np.sum(weight*xx*yy/den)
    a = 4*(-4*j1+6*j2+scalar_mass**2/mw**2*j2)
    p, b, c = 3*j1, -3*j1, -j1
    return dict(A=a*(-dot(q, k)*METRIC+np.outer(k, q)),
                P=p*k2*METRIC, B=b*np.outer(k, k),
                C=c*(s-scalar_mass**2)*METRIC,
                pinch=-p*k2*METRIC,
                form_factors=dict(A=float(a), P=float(p), B=float(b), C=float(c)),
                J1=float(j1), J2=float(j2), scalar_virtuality=float(s))


def projected_source_check(delta=.73, left=.037+.019j, right=-.021+.043j,
                           masses=(125., 437.), mi=3., mj=.7, order=48):
    """Check both photon Ward contractions and B/C removal on source tensors.

    Nondegenerate neutral masses are explicit. left/right here denote the
    independent off-diagonal D_ji/sqrt(2), D_ij*/sqrt(2), NOT Wilsons.
    """
    pi, pj, q = decay_momenta(mi, mj)
    k = np.array([.7, 1.9, -.6, 2.3])*(1+mi)
    kappas = (math.cos(delta), math.sin(delta))
    yukawas = (-math.sin(delta), math.cos(delta))
    maxima = dict(B=0., C_sum=0., P_plus_pinch=0., full_minus_A=0.,
                  real_photon_Ward=0., virtual_photon_Ward=0.,
                  source_A_inner_Ward=0., single_attachment_Ward=0.,
                  omitted_H_C_remainder=0., bare_real_photon_Ward=0.)
    for si in range(2):
        for sj in range(2):
            sums = {key: np.zeros(4, complex) for key in ('A', 'P', 'B', 'C', 'pinch')}
            bare = np.zeros(4, complex)
            for index, (ms, kap, y) in enumerate(zip(masses, kappas, yukawas)):
                current = outer_current(pi, pj, k, mi, mj, y*left, y*right, si, sj)
                only_one = outer_current(pi, pj, k, mi, mj, y*left, y*right,
                                         si, sj, 'daughter')
                t = source_tensors(q, k, ms, order=order)
                den = t['scalar_virtuality']-ms*ms
                for name in sums:
                    contribution = kap*t[name]@(ETA*current)/den
                    sums[name] += contribution
                    if name == 'B':
                        maxima['B'] = max(maxima['B'], float(np.max(abs(contribution))))
                    if name == 'C' and index == 0:
                        maxima['omitted_H_C_remainder'] = max(
                            maxima['omitted_H_C_remainder'], float(np.max(abs(contribution))))
                bare += kap*sum(t[name] for name in ('A', 'P', 'B', 'C'))@(ETA*current)/den
                maxima['virtual_photon_Ward'] = max(maxima['virtual_photon_Ward'],
                                                     float(abs(dot(k, current))))
                maxima['single_attachment_Ward'] = max(maxima['single_attachment_Ward'],
                                                        float(abs(dot(k, only_one))))
                maxima['source_A_inner_Ward'] = max(maxima['source_A_inner_Ward'],
                    float(np.max(abs((ETA*q)@t['A']))), float(np.max(abs(t['A']@(ETA*k)))))
            full = sum(sums.values())
            for name, value in [('C_sum', sums['C']), ('P_plus_pinch', sums['P']+sums['pinch']),
                                ('full_minus_A', full-sums['A'])]:
                maxima[name] = max(maxima[name], float(np.max(abs(value))))
            maxima['real_photon_Ward'] = max(maxima['real_photon_Ward'], float(abs(dot(q, full))))
            maxima['bare_real_photon_Ward'] = max(maxima['bare_real_photon_Ward'], float(abs(dot(q, bare))))
    return maxima


def _log_ratio(z, u):
    d = (z-u)/u
    if abs(d) < 1e-5:
        return (1-d/2+d*d/3-d**3/4+d**4/5)/u
    return math.log(z/u)/(z-u)


def reference_kernels(z):
    """Conditional reference comparison, never a selection of a physical kernel."""
    if not math.isfinite(z) or z <= 0:
        raise ValueError('Positive finite mass ratio required')
    def integral(weight):
        return quad(lambda x: weight(x*(1-x))*_log_ratio(z, x*(1-x)),
                    0, 1, epsabs=2e-11, epsrel=2e-11)[0]
    f = z/2*integral(lambda u: 1-2*u)
    g = z/2*integral(lambda u: 1.)
    def dh(x):
        u = x*(1-x)
        d = (z-u)/u
        deriv = ((-.5+2*d/3-3*d*d/4+4*d**3/5)/u**2 if abs(d) < 1e-4
                 else (d/(1+d)-math.log1p(d))/(u*u*d*d))
        return z*z/2*deriv
    h = quad(dh, 0, 1, epsabs=2e-11, epsrel=2e-11)[0]
    goldstone = (f-g)/(2*z)
    return dict(f=f, g=g, h=h, CHK=3*f+23*g/4+3*h/4+goldstone,
                Ilisie=7.5*f+2*g+goldstone, Abe_A=3*f+5*g+goldstone,
                CHK_minus_Abe=.75*(g+h), Ilisie_minus_Abe=1.5*(3*f-2*g),
                CHK_minus_Ilisie=.75*(h+5*g-6*f))


def abe_A_double_integral(z):
    """Independent outer radial/Feynman integral of SOURCE GammaA, no f/g call.

    t/Ms^2=y/(1-y); common signed Wilson prefactor is factored out.
    This closes only the radial reduction of the source transverse tensor.
    """
    if not math.isfinite(z) or z <= 0:
        raise ValueError('Positive finite mass ratio required')
    def inner(x):
        u = x*(1-x)
        return quad(lambda y: (4*z-3*z*u-u/2)/(z*(1-y)+u*y),
                    0, 1, epsabs=2e-10, epsrel=2e-10)[0]
    return quad(inner, 0, 1, epsabs=2e-10, epsrel=2e-10)[0]


def goldstone_F2(z):
    if not math.isfinite(z) or z <= 0:
        raise ValueError('Positive finite mass ratio required')
    return -.5*quad(lambda x: x*(1-x)*_log_ratio(z, x*(1-x)),
                    0, 1, epsabs=2e-11, epsrel=2e-11)[0]


def corrected_abe_B8_photon(z):
    """2016 erratum B.8: return I_W^gamma/e, using direct I1,I2 integrals.

    I1(mW,0)=I2(mW,0)=0 are their continuous limits. No EDM-to-LFV
    extrapolation is made; this checks only the corrected radial source.
    """
    if not math.isfinite(z) or z <= 0:
        raise ValueError('Positive finite mass ratio required')
    i1 = quad(lambda x: -(1-2*x*(1-x))*_log_ratio(z, x*(1-x)),
              0, 1, epsabs=2e-11, epsrel=2e-11)[0]
    i2 = quad(lambda x: -_log_ratio(z, x*(1-x)),
              0, 1, epsabs=2e-11, epsrel=2e-11)[0]
    b = (6+1/z)/4
    return 2*z*(-b*i1+(-4+b)*i2)


def angular_projection(left=.037+.019j, right=-.021+.043j):
    """Independent Weyl-matrix check of the frozen signed outer numerator."""
    X = left*PL+right*PR
    q = np.array([1., .2, -.3, math.sqrt(.87)])
    error = 0.
    for mu in range(4):
        actual = np.zeros((4, 4), complex)
        for k in np.diag([1j, 1., 1., 1.]):
            for nu in range(4):
                gamma_lower = ETA[nu]*GAMMA[nu]
                current = X@slash(k)@gamma_lower-gamma_lower@slash(k)@X
                t = -METRIC[mu, nu]*dot(k, q)+k[mu]*q[nu]
                actual += current*t/4
        expected = 1j*sum(.5j*(GAMMA[mu]@GAMMA[a]-GAMMA[a]@GAMMA[mu])*
                         ETA[a]*q[a] for a in range(4))@X
        error = max(error, float(np.max(abs(actual-expected))))
    return error


def w_propagator(k, mw, xi):
    if xi <= 0:
        raise ValueError('Use separated positive xi values')
    k2 = dot(k, k)
    return -1j/(k2-mw*mw)*(METRIC-(1-xi)*np.outer(k, k)/(k2-xi*mw*mw))

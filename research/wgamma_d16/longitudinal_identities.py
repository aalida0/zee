"""Native contracted vertices and the inverse-propagator/ghost remainder ledger.

These are components needed by a BRST/ST construction, not a declaration
that the full on-shell two-loop Slavnov--Taylor identity is closed.
"""
import numpy as np
import sympy as s
from .algebra import ETA, METRIC, dot


def photon_ww(p, a, b):
    """Native photonWW/(ie); indices mu (photon), alpha(W-), beta(W+)."""
    return np.einsum('mb,a->mab', METRIC, p-b)+np.einsum('ab,m->mab', METRIC, b-a)+\
        np.einsum('ma,b->mab', METRIC, a-p)


def transverse_inverse(p):
    return dot(p, p)*METRIC-np.outer(p, p)


def w_inverse(p, mw2, xi):
    return (dot(p, p)-mw2)*METRIC-(1-1/xi)*np.outer(p, p)


def contracted_triple(p, a, mw2, xi):
    """a.Gamma - m.Gamma_gammaGW = K_W(b)-T_gamma(p)-b b/xi.

    The last term belongs to the gauge-fixing/ghost kernel and must NOT be
    discarded as if a transverse Ward identity completed the ST identity.
    The native photonWG/(ie)=m*g has the same sign for both charge rules.
    """
    b = -np.asarray(p)-np.asarray(a)
    lhs = np.einsum('a,mab->mb', ETA*a, photon_ww(p, a, b))-mw2*METRIC
    inverse_parent = w_inverse(b, mw2, xi)
    photon_parent = -transverse_inverse(p)
    gauge_fixing = -np.outer(b, b)/xi
    return dict(residual=float(np.max(abs(lhs-inverse_parent-photon_parent-gauge_fixing))),
                lhs=lhs, internal_W_parent=inverse_parent,
                external_photon_parent=photon_parent, ghost_kernel_remainder=gauge_fixing)


def scalar_contraction():
    """Exact native sWG contraction, showing BOTH inverse scalar propagators.

    Vertex pW.V_sG-W+ + m.V_sGG - m.V_sghost is an algebraic combination,
    not the full ghost insertion functional of a multi-leg ST identity.
    """
    r2, g2, ms2, mw, xi, vev, kap = s.symbols('r2 pG2 Ms2 mW xi v kappa')
    contracted = s.I*mw*kap/vev*(r2-g2)
    goldstone = -s.I*mw*kap/vev*ms2
    ghost = -s.I*xi*mw**3*kap/vev
    target = s.I*mw*kap/vev*((r2-ms2)-(g2-xi*mw**2))
    return dict(residual=s.expand(contracted+goldstone-ghost-target),
                contracted=contracted, inverse_scalar= s.I*mw*kap/vev*(r2-ms2),
                inverse_goldstone=-s.I*mw*kap/vev*(g2-xi*mw**2),
                ghost_mass_source=ghost)


PARENT_TERMS = {
    'sWG_scalar_inverse': 'r^2-Ms^2 cancels neutral scalar propagator only on this term',
    'sWG_goldstone_inverse': 'pG^2-xi*mW^2 cancels the charged Goldstone propagator',
    'sWG_ghost_mass': 'native sGhost=-i*xi*mW^2*kappa/v; retain BRST insertion kernels',
    'WWgamma_internal_inverse': 'K_W(b) pinches the adjacent W propagator',
    'WWgamma_photon_inverse': 'T_gamma(p) vanishes for on-shell transverse photon only',
    'WWgamma_gauge_fixing': '-b_mu*b_beta/xi; ghost/antighost kernel still required',
    'WWW_neutrino_pinch': 'N=2*n^2*gamma_mu PL+N_rem; box reduces to massive triangle',
    'external_lepton_inverse': 'S_j^-1(p-r) before the scalar vertex must be retained until LSZ sum',
    'charged_H_parents': 'sWH derivative overlaps nonzero; weighted charged masses preclude unweighted closure',
}

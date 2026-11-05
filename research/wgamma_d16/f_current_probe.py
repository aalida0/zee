"""F-dependent selection rule and a surviving regulated two-loop subgraph.

NOT a renormalized two-loop dipole. The nonzero W-neutrino wavefunction
subloop is a counterexample to discarding all F^dagger F terms at m_nu=0.
It retains its UV pole; no missing finite amplitude is filled with zero.
"""
import numpy as np
from scipy.integrate import quad


def neutrino_w_subloop(p2, mw2, mu2=None):
    """Massless internal charged lepton, xi=1, native W numerator.

    Strips common g2²/(32pi²) and the action/self-energy i convention.
    gamma^mu /l gamma_mu PL=(2-d)/l PL. With x the W parameter,
    Delta=x*MW²-x(1-x)*p²; /l -> x /p. The eps*UV term is retained.
    This subloop dresses the existing charged-scalar/neutrino F² parent.
    Its value alone is scheme dependent and is NOT a Wilson coefficient.
    """
    mu2=mw2 if mu2 is None else mu2
    if not np.isfinite([p2,mw2,mu2]).all() or min(mw2,mu2)<=0 or p2>=0:
        raise ValueError('Spacelike p² and positive MW², mu² required')
    finite,err=quad(lambda x:2*x*np.log((x*mw2-x*(1-x)*p2)/mu2),0,1,
                    epsabs=2e-12,epsrel=2e-12)
    return dict(pole=-1.,finite=1+finite,quadrature_error=err,
                rational_epsilon_times_UV=1.,physical_C_LR=None,
                scope='regulated neutrino W self-energy subloop; xi=1; m_internal_lepton=0')


def probe(F):
    from module3.tree import G, PL, PR
    F=np.asarray(F,complex)
    if F.shape!=(3,3) or not np.isfinite(F).all() or not np.allclose(F,-F.T,atol=1e-14):
        raise ValueError('Antisymmetric finite F required')
    p=np.array([.7,.2,-.3,.4]);slash=p[0]*G[0]-sum(p[a]*G[a] for a in (1,2,3))
    return dict(quadratic_FD='VANISHES_BY_FERMION_LEPTON_NUMBER_AT_mnu_0',
        selection_rule='One F or F* changes fermion lepton number by two; D and all bosonic/gauge vertices do not. No L-conserving dipole with exactly one F at quadratic Yukawa order.',
        F_dagger_F=F.conj().T@F,
        same_projector_massless_chain_norm=float(np.linalg.norm(PL@slash@PL)),
        opposite_projector_massless_chain_norm=float(np.linalg.norm(PL@slash@PR)),
        subloop=neutrino_w_subloop(-80.379**2,80.379**2),
        surviving_FF_status='REQUIRES_COMPLETE_GAUGE_AND_COUNTERTERM_SUM',
        full_F_dependent_C_LR=None)

"""Complete W/Goldstone neutrino two-point subgraph at mnu=ml=0, arbitrary xi.

This is an independently regulated SUBGRAPH, never an F†F dipole coefficient.
Ghosts have no direct neutrino vertex; Goldstone couplings vanish at these
internal fermion masses. Photon-emission, scalar, counterterm and LSZ graphs
of the two-loop F†F amplitude remain required.
"""
import numpy as np
from scipy.integrate import quad
from .f_current_probe import neutrino_w_subloop


def neutrino_w_rxi(p2,mw2,xi,mu2=None):
    mu2=mw2 if mu2 is None else mu2
    if not np.isfinite([p2,mw2,xi,mu2]).all() or p2>=0 or min(mw2,mu2,xi)<=0:
        raise ValueError('Spacelike p², positive MW², mu² and xi required')
    transverse=neutrino_w_subloop(p2,mw2,mu2)
    ratio,error=quad(lambda x:x*np.log((mw2-(1-x)*p2)/
                                     (xi*mw2-(1-x)*p2)),0,1,
                     epsabs=2e-12,epsrel=2e-12)
    tadpole_difference=(1-np.log(mw2/mu2))-xi*(1-np.log(xi*mw2/mu2))
    longitudinal=p2/mw2*ratio+tadpole_difference
    return dict(pole=-float(xi),finite=transverse['finite']+longitudinal,
        longitudinal_finite=longitudinal,
        quadrature_error=transverse['quadrature_error']+abs(p2/mw2)*error,
        rational_epsilon_times_UV=1.,
        renormalization='MSbar pole subtraction of this two-point function only; not a full F or EW scheme',
        physical_C_LR=None,scope='NEUTRINO_TWO_POINT_SUBGRAPH_ONLY; mnu=ml_internal=0')


def longitudinal_numerator_residual(p,l):
    """Independent 4D matrix falsifier of the d-dimensional open-line identity."""
    from .algebra import slash,dot
    k=p-l
    actual=slash(k)@slash(l)@slash(k)
    expected=slash(p)@slash(l)@slash(p)-2*dot(l,l)*slash(p)+dot(l,l)*slash(l)
    return float(np.max(abs(actual-expected)))

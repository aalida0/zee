"""Independent Dirac projection, Euclidean parameters and source comparisons.

The matching derivation is in MATCHING_AUDIT.md. This module never supplies a
W amplitude to the coherent ledger. Gauge identities here have narrower scope
than a complete R_xi two-loop calculation.
"""
import itertools
import math
import mpmath as mp
import numpy as np
from scipy.integrate import quad
from module3.tree import G, PL, PR
from .kernels import kernels, w_kernel


METRIC=np.diag([1.,-1.,-1.,-1.])


def epsilon(indices):
    if len(set(indices))!=4:return 0
    return (-1)**sum(indices[i]>indices[j] for i in range(4) for j in range(i+1,4))


def sigma(mu,nu):
    return .5j*(G[mu]@G[nu]-G[nu]@G[mu])


def slash(k):
    return sum(G[a]*(METRIC@k)[a] for a in range(4))


def outer_projection(q=(1.,0.,0.,1.),left=.03+.02j,right=-.01+.04j):
    """Explicit Wick angular average of both lepton-line attachment orders.

    Real photon is outgoing q; the effective vertex uses incoming -q and
    virtual outgoing k. <k_mu k_nu>=-g_mu_nu/4 at K^2=1. No fitted sign.
    The antisymmetric inner tensor reduces to -i gamma5 times the scalar
    projection, fixing (+i Im C_ff, -i Im C_ff) for (CL,CR).
    """
    q=np.asarray(q);qc=METRIC@q;g5=PR-PL;X=left*PL+right*PR
    scalar_error=pseudo_error=0.
    for mu in range(4):
        ns=np.zeros((4,4),complex);npseudo=ns.copy()
        for k in np.diag([1j,1.,1.,1.]):
            kc=METRIC@k;ks=slash(k)
            for nu in range(4):
                gamma=METRIC[nu,nu]*G[nu]
                # X /k gamma_nu + gamma_nu (-/k) X: both outer orders.
                attachment=X@ks@gamma-gamma@ks@X
                tensor=-METRIC[mu,nu]*(k@METRIC@q)+k[mu]*q[nu]
                dual=sum(epsilon((mu,nu,a,b))*kc[a]*(-qc[b])
                         for a in range(4) for b in range(4))
                ns+=attachment*tensor/4
                npseudo+=attachment*dual/4
        target=1j*sum(sigma(mu,a)*qc[a] for a in range(4))@X
        scalar_error=max(scalar_error,float(np.max(abs(ns-target))))
        pseudo_error=max(pseudo_error,float(np.max(abs(npseudo-target@(-1j*g5)))))
    return scalar_error,pseudo_error


def euclidean_parameters(z):
    """Two independent positive Feynman parameters, no logarithmic kernel.

    t=K^2/M^2 = y/(1-y) gives d t/[(1+t)(z+u t)]
    =d y/[z(1-y)+u y]. The outer integral sign is fixed before Wick rotation.
    """
    if not math.isfinite(z) or z<=0:raise ValueError('Positive z required')
    result=[]
    for scalar in (True,False):
        def outer(x):
            u=x*(1-x)
            val=quad(lambda y:1/(z*(1-y)+u*y),0,1,epsabs=2e-10,epsrel=2e-11,limit=300)[0]
            return z*(1-2*u if scalar else 1)*val
        result.append(quad(outer,0,.5,epsabs=1e-11,epsrel=2e-10,limit=300)[0])
    return tuple(result)


def gm2calc_photon_functions(z):
    """EPJC82(2022)229 Eqs.53,54,63-65, photon only, no SM subtraction.

    Evaluate the independent Phi dilogarithm with mS^2=1, mf^2=z,
    using its permutation symmetry Phi(1,z,z)=Phi(z,z,1).
    Returns z*F_even and z*F_odd, which should be (-f,+g).
    """
    with mp.workdps(65):
        z=mp.mpf(str(z))
        if z<=0:raise ValueError('Positive z required')
        if z==mp.mpf('.25'):
            # Analytic removable limit of Phi/(1-4z).
            odd=4*mp.log(2)
        else:
            lam=mp.sqrt(1-4*z);a=(1-lam)/2
            phi=lam/2*(2*mp.log(a)**2-mp.log(z)**2-4*mp.polylog(2,a)+mp.pi**2/3)
            odd=mp.re(phi/(1-4*z))
        even=-2+mp.log(1/z)-(1-2*z)*odd
        return float(z*even),float(z*odd)


def ilisie_fermion_functions(z):
    """Direct Ilisie Eqs.25,26, independently integrated."""
    def integrand(x,odd):
        u=x*(1-x)
        d=(z-u)/u
        ratio=math.log1p(d)/(z-u) if abs(d)>1e-6 else (1-d/2+d*d/3-d**3/4)/u
        return z/2*ratio*(1 if odd else 2*u-1)
    return tuple(quad(integrand,0,1,args=(odd,),epsabs=2e-12,epsrel=2e-12,limit=400)[0]
                 for odd in (False,True))


def chang2001_pseudoscalar(z):
    """PRD63(2001)091301 Eq.10: z*F(z)/2 = g(z)."""
    def integrand(x):
        u=x*(1-x)
        d=(z-u)/u
        return (math.log1p(d)/(z-u) if abs(d)>1e-6 else (1-d/2+d*d/3-d**3/4)/u)
    return z/2*quad(integrand,0,1,epsabs=2e-11,epsrel=2e-12,limit=400)[0]


def w_source_decomposition(z):
    """Exact algebra of three distinct off-shell W constructions.

    CHK14+18; Ilisie21,28; Abe1311.4704v3 Eq3.9 (G=gamma).
    This compares kernels, not complete gauge-independent LFV observables.
    """
    f,g,h=kernels(z)[0]
    goldstone=(f-g)/(2*z)
    abe=3*f+5*g+goldstone
    ilisie=7.5*f+2*g+goldstone
    chk=w_kernel(z)[0]
    return {'z':z,'CHK':chk,'Ilisie':ilisie,'Abe_transverse':abe,
            'common_goldstone':goldstone,
            'CHK_minus_Abe':.75*(g+h),
            'Ilisie_minus_Abe':1.5*(3*f-2*g),
            'CHK_minus_Ilisie':.75*(h+5*g-6*f),
            'old_signed_ratio':-chk/ilisie,
            'normalization_problem':False,
            'complete_W_LFV_matching':'NOT_VALIDATED'}


def ilisie_w_integral(z):
    """Ilisie Eq.28 before reflection symmetry / conversion to f,g."""
    def fun(x):
        u=x*(1-x);d=(z-u)/u
        ratio=math.log1p(d)/(z-u) if abs(d)>1e-6 else (1-d/2+d*d/3-d**3/4)/u
        return .5*(x*(3*x*(4*x-1)+10)*z-u)*ratio
    return quad(fun,0,1,epsabs=2e-11,epsrel=2e-12,limit=400)[0]


def pinch_ward_check(p1=(1.,0.,0.,1.),p2=(2.,.4,-.3,.8),mw=80.,mh=400.):
    """Numerical off-shell source Ward check, not an R_xi diagram calculation.

    Abe Eq3.8 P term is cancelled by Eq3.16 pinch term. B and C terms
    are kept separate: B requires external-line projection, C the scalar
    mixing sum rule. Only the pinch-completed transverse-plus-P tensor is
    tested here; this cannot certify a complete Zee W amplitude.
    """
    p1=np.array(p1);p2=np.array(p2);p1c=METRIC@p1;p2c=METRIC@p2
    k2=p2@p2c;s=(p1+p2)@METRIC@(p1+p2)
    def j(power):
        return quad(lambda x:quad(lambda y:(x*y if power else 1)/(1-k2/mw**2*x*(1-x)-(s-k2)/mw**2*x*y),
                    0,1-x,epsabs=1e-12,epsrel=1e-12)[0],0,1,epsabs=1e-12,epsrel=1e-12)[0]
    j1,j2=j(0),j(1)
    a=4*(-4*j1+6*j2+(mh/mw)**2*j2)
    transverse=a*(-(p1@p2c)*METRIC+np.outer(p2,p1))
    gauge_piece=3*j1*k2*METRIC
    pinch=-3*j1*k2*METRIC
    before=float(np.max(abs(p1c@(transverse+gauge_piece))))
    after=max(float(np.max(abs(p1c@(transverse+gauge_piece+pinch)))),
              float(np.max(abs((transverse+gauge_piece+pinch)@p2c))))
    return {'J1':j1,'J2':j2,'Ward_before_pinch':before,'Ward_after_pinch':after,
            'scope':'Abe transverse and P tensors only; B,C external projections and R_xi LFV matching still required'}

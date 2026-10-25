"""Physical charged-scalar/photon subset; see CHARGED_SCALAR_AUDIT.md.

Only H1,H2 physical charged particles enter. Goldstone and W matching are
separate and remain blocked. Photon charge is the identity in this sector.
"""
from functools import lru_cache
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from module1.scalar_constraints import reconstruct
from module3.core import vertices
from .couplings import trilinears
from .kernels import _ratio


@lru_cache(maxsize=512)
def scalar_loop_kernel(z):
    """F2=-1/2 integral u log(z/u)/(z-u), direct stable quadrature.

    Equals (f-g)/(2z), but subtracting two large functions is unnecessary.
    The error is numerical only, not an external-invariant truncation error.
    """
    z=float(z)
    if not math.isfinite(z) or not 1e-24<=z<=1e10:
        raise ValueError('Require finite 1e-24 <= z <= 1e10')
    value,error=quad(lambda x:-x*(1-x)*_ratio(x*(1-x),z)/(2*z),0,.5,
                     epsabs=min(1e-12,1e-11/z),epsrel=2e-12,limit=500)
    value,error=2*value,2*error
    if not math.isfinite(value) or value>=0 or error>max(1e-12,abs(value)*2e-9):
        raise ArithmeticError('Uncontrolled charged-scalar kernel')
    return value,error


def component(external,g,mass,neutral_mass,mi,alpha,charge=1.):
    """CL,CR in frozen GeV^-2 normalization; L_int=-g s H- H+.

    C_X=alpha Q^2 g/(16 pi^3 mi M_s^2) C_s^X F2(mass^2/M_s^2).
    The signed coefficient follows the triangle+seagull vertex and the
    already-derived emitted-operator matching, not an absolute rate.
    """
    if not all(math.isfinite(x) and x>0 for x in (mass,neutral_mass,mi,alpha)):
        raise ValueError('Positive finite masses and alpha required')
    c=np.asarray(external,dtype=complex)
    if c.shape!=(2,) or not np.isfinite(c).all() or not np.isfinite(complex(g)) or not math.isfinite(charge):
        raise ValueError('Finite external chiral pair, trilinear and charge required')
    if abs(complex(g).imag)>1e-12*max(1.,abs(g)):
        raise ValueError('A real-neutral diagonal Hermitian trilinear must be real')
    g=float(complex(g).real)
    kernel,error=scalar_loop_kernel((mass/neutral_mass)**2)
    pref=alpha*charge*charge*g/(16*math.pi**3*mi*neutral_mass**2)
    return pref*kernel*c,float(abs(pref)*max(abs(c))*error)


def ledger(D,p,ml,alpha,i,j):
    """All h/H/A × H1/H2 diagonal rows, including proven zero A rows.

    With Q=identity, a single off-diagonal G cannot close either triangle or
    seagull loop. Mixing is retained by rotating the full G matrices first.
    """
    from .amplitudes import row,CHANNELS
    if (i,j) not in CHANNELS.values():raise ValueError('Unsupported external channel')
    D=np.asarray(D,dtype=complex)
    if D.shape!=(3,3) or not np.isfinite(D).all():raise ValueError('Finite complex 3x3 D required')
    lag,_,_=reconstruct(p)
    matrices=trilinears(p,lag)
    result={}
    for scalar,(C,M) in vertices(D,p,ml).items():
        matrix=matrices[scalar][1:,1:]
        if not np.allclose(matrix,matrix.conj().T,rtol=2e-13,atol=2e-12):
            raise ValueError('Non-Hermitian native scalar trilinear matrix')
        for index,(species,mass) in enumerate((('H1',p['mH1']),('H2',p['mH2']))):
            g=matrix[index,index]
            value,error=component((C[j,i],C[i,j].conjugate()),g,mass,M,ml[i],alpha)
            entry=row(value,scalar,species+'charged_scalar',
                'Module4:CHARGED_SCALAR_AUDIT;nativeSARAH;Ilisie1502.04199:Eqs13,20,27;Arhrib0104225:Eqs3-6',
                'physical_charged_scalar_photon;two_triangles_plus_seagull;not_full_EW',error,validated=True)
            entry.update(trilinear_G_GeV=float(complex(g).real),charged_mass_GeV=mass,
                neutral_mass_GeV=M,electric_charge_squared=1.,
                offdiagonal_status='ZERO_FOR_IDENTITY_PHOTON_CHARGE',
                uncertainty='Signed physical charged-scalar/photon matching validated; quadrature error only; tree-level native scalar parameters; external-invariant expansion')
            if scalar=='A':
                entry['zero_reason']='CP-conserving potential: G_A diagonal zero; off-diagonal A cannot close photon loop'
            result[scalar+'_'+species+'_scalar_gamma']=entry
    return result


def scalar_qed_tensor(p,q,mass=1.,order=32):
    """Independent DR-finite Euclidean two-triangle plus seagull tensor.

    Strip (e Q)^2 g/(16 pi^2). Both photons may be off shell here. The
    arbitrary common I2 constant cancels: triangle UV coefficients +1,+1,
    seagull -2. The surviving logs are referenced to mass^2. No transverse
    projector is applied; Ward identities must emerge from the diagrams.
    """
    if not math.isfinite(mass) or mass<=0:raise ValueError('Positive finite mass required')
    p,q=np.asarray(p,dtype=float)/mass,np.asarray(q,dtype=float)/mass
    if p.shape!=(4,) or q.shape!=(4,) or not np.isfinite(p).all() or not np.isfinite(q).all():
        raise ValueError('Finite Euclidean four-momenta and positive mass required')
    if type(order) is not int or order<8:raise ValueError('Quadrature order >=8 required')
    x,w=leggauss(order);x,w=(x+1)/2,w/2
    eye=np.eye(4);r=p+q;triangle=np.zeros((4,4))
    for a,wa in zip(x,w):
        for b0,wb in zip(x,w):
            b=(1-a)*b0;weight=wa*wb*(1-a)
            R=a*p+b*r;delta=1+a*(p@p)+b*(r@r)-R@R
            R2=a*q+b*r;delta2=1+a*(q@q)+b*(r@r)-R2@R2
            A,B=p-2*R,2*p+q-2*R
            A2,B2=2*q+p-2*R2,q-2*R2
            triangle+=weight*(-2*eye*math.log(delta)+np.outer(A,B)/delta
                -2*eye*math.log(delta2)+np.outer(A2,B2)/delta2)
    seagull=2*eye*sum(wx*math.log(1+t*(1-t)*(r@r)) for t,wx in zip(x,w))
    return triangle,seagull


def euclidean_scalar_kernel(z):
    """Independent two-loop Euclidean radial parameters, no log or f/g.

    Returns F2=-1/2 integral dx dy u/[z(1-y)+u y].
    """
    if not math.isfinite(z) or z<=0:raise ValueError('Positive z required')
    def outer(x):
        u=x*(1-x)
        inner=quad(lambda y:u/(z*(1-y)+u*y),0,1,epsabs=1e-11,epsrel=2e-11,limit=300)[0]
        return -inner
    return quad(outer,0,.5,epsabs=1e-11,epsrel=2e-10,limit=300)[0]


def mass_basis_trace(mass_squared,G,neutral_mass):
    """Basis-invariant scalar sum Tr[G F2(M_ch^2/M_s^2)] for Q=I.

    Useful also when complex unitary basis changes make both matrices dense.
    Off-diagonal entries are never discarded before the spectral projection.
    """
    m=np.asarray(mass_squared,dtype=complex);g=np.asarray(G,dtype=complex)
    if m.shape!=g.shape or m.ndim!=2 or m.shape[0]!=m.shape[1] or not np.allclose(m,m.conj().T) or not np.allclose(g,g.conj().T):
        raise ValueError('Matching Hermitian mass and trilinear matrices required')
    eigen,vectors=np.linalg.eigh(m)
    if min(eigen)<=0 or neutral_mass<=0:raise ValueError('Positive masses required')
    f=(vectors*np.array([scalar_loop_kernel(float(v)/neutral_mass**2)[0] for v in eigen]))@vectors.conj().T
    return np.trace(g@f)

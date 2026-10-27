"""D4 strictly kinematic/spin-summed tree-level two-body width kernels.

These generic, convention-independent numerical kernels require validated
*physical* complex mass-eigenstate couplings from native SARAH or an
independently proven analytic Lagrangian. They DO NOT derive such couplings.

Gamma[S(M)->s(m)+V(mV)] = |c|^2 * lambda^(3/2)/(16*pi*M^3*mV^2),
for amplitude c*(P+k).epsilon*.
Gamma[S(M)->s1+s2] = |t|^2*sqrt(lambda)/(16*pi*M^3).
Gamma[S(M)->f_i+anti-f_j] = Nc*sqrt(lambda)/(16*pi*M^3)
 *[(|a|^2+|b|^2)(M^2-mi^2-mj^2)-4*Re(a*b*)*mi*mj],
for L_int=S*bar(f_i)*(a*PL+b*PR)*f_j + h.c.

Not a Zee charged-Higgs BR or total-width implementation.
"""
import math

STATUS="GENERIC_TREE_PARTIAL_WIDTH_KERNEL_ONLY"


def real(value,name,allow_zero=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite real")
    v=float(value)
    if v<0 or (v==0 and not allow_zero):
        raise ValueError(f"{name} must be {'nonnegative' if allow_zero else 'positive'}")
    return v


def complex_coupling(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float,complex)):
        raise ValueError(f"{name} must be real or complex")
    z=complex(value)
    if not math.isfinite(z.real) or not math.isfinite(z.imag):
        raise ValueError(f"{name} must be finite")
    return z


def phase_space(M,m1,m2):
    """Return sqrt(lambda(M²,m1²,m2²)) [GeV²]; 0 below threshold."""
    M=real(M,"parent_mass")
    m1=real(m1,"daughter1_mass",allow_zero=True)
    m2=real(m2,"daughter2_mass",allow_zero=True)
    if M <= m1+m2:
        return 0.0
    factors=(M-m1-m2,M+m1+m2,M-m1+m2,M+m1-m2)
    if any(f<=0 or not math.isfinite(f) for f in factors):
        raise ValueError("Invalid Kallen factors")
    lam=math.prod(factors)
    if not math.isfinite(lam):
        raise ValueError("Kallen overflow")
    return math.sqrt(lam)


def scalar_vector(M,ms,mv,c):
    """Amplitude c*(P+k)^mu epsilon_mu; c dimensionless."""
    a=phase_space(M,ms,mv)
    mv=real(mv,"vector_mass")
    c=complex_coupling(c,"scalar_vector_vertex")
    if not a: return 0.0
    result=abs(c)**2*a**3/(16*math.pi*float(M)**3*mv**2)
    if not math.isfinite(result):raise ValueError("Nonfinite scalar-vector width")
    return result


def scalar_scalar(M,m1,m2,t):
    """Nonidentical distinguishable final scalars, vertex t [GeV].

    Caller must separately handle Bose symmetry factors when necessary.
    """
    a=phase_space(M,m1,m2)
    t=complex_coupling(t,"trilinear_GeV")
    if not a:return 0.0
    result=abs(t)**2*a/(16*math.pi*float(M)**3)
    if not math.isfinite(result):raise ValueError("Nonfinite scalar-scalar width")
    return result


def scalar_fermions(M,mi,mj,a,b,ncolor):
    """Couplings a*PL+b*PR, scalar charge/conjugation specified by caller."""
    a=complex_coupling(a,"coupling_PL")
    b=complex_coupling(b,"coupling_PR")
    if type(ncolor) is not int or ncolor not in (1,3):
        raise ValueError("Explicit Ncolor=1 or 3 required")
    lam=phase_space(M,mi,mj)
    mi=real(mi,"fermion_mass",allow_zero=True)
    mj=real(mj,"antifermion_mass",allow_zero=True)
    if not lam:return 0.0
    M=float(M)
    bracket=math.fsum((
      (abs(a)**2+abs(b)**2)*(M*M-mi*mi-mj*mj),
      -4*(a*b.conjugate()).real*mi*mj,
    ))
    if not math.isfinite(bracket) or bracket < 0:
        raise ValueError("Nonphysical spin-summed matrix element")
    width=ncolor*lam*bracket/(16*math.pi*M**3)
    if not math.isfinite(width):raise ValueError("Nonfinite scalar-fermion width")
    return width

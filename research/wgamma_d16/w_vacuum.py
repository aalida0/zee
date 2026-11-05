"""DR WWW parent: open-line Pauli projection, TARCER and independent masters.

TOPOLOGY_ONLY at xiW=1, leading external degree, mnu=0. Not a gauge-complete
Wilson. No function here contributes to zee_two_loop's coherent ledger.
"""
from collections import Counter
from functools import lru_cache
from itertools import permutations
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
import sympy as s
from sympy.parsing.mathematica import parse_mathematica
from sympy.printing.mathematica import mathematica_code

X,Y,Z,W,H,D,V=s.symbols('x y z w h D v')
ZETA2=np.pi**2/6


def dipole_numerator():
    """FeynCalc-derived coefficient of i sigma(mu,nu) q_nu PR, before D0."""
    x,y,z,w,d=X,Y,Z,W,D
    return -2*(2*w*x*y-d*w*x*y-2*x*x*y+d*x*x*y-4*w*y*z+
        6*d*w*y*z-2*d*d*w*y*z+2*x*y*z-4*d*x*y*z+2*d*d*x*y*z-
        2*d*w*z*z+d*d*w*z*z+2*d*x*z*z-d*d*x*z*z)/((d-1)*d*(w-x)*y)


def ibp_input(path,numerator=None):
    """Only partial fractions; all IBP recurrence solving is done by TARCER."""
    den=X*Y*(X-W)**2*(Y-H)*(V-W)
    numerator=dipole_numerator() if numerator is None else numerator
    original=s.cancel(numerator.subs(Z,(X+Y-V)/2)/den)
    terms=[original]
    for var in (V,X,Y):
        terms=[u for t in terms for u in s.Add.make_args(s.apart(t,var))]
    # With no connecting propagator, v=l²+r²-2l.r. The odd independent
    # l.r tadpole tensor vanishes by DR covariance, not a master assumption.
    terms=[u for t in terms for u in s.Add.make_args(
        s.expand(t.subs(V,X+Y)) if not s.denom(t).has(V) and t.has(V) else t)]
    for var in (X,Y):
        terms=[s.factor(u) for t in terms for u in s.Add.make_args(s.apart(t,var))]
    rows=[]
    for term in terms:
        powers=term.as_powers_dict();indices=[];remainder=term
        for var,mass in ((X,W),(Y,H),(V,W)):
            n0=-powers.get(var,0);nm=-powers.get(var-mass,0)
            if nm==0 and powers.get(mass-var,0):
                nm=-powers[mass-var]
                remainder*=(-1)**nm*(mass-var)**nm/(var-mass)**nm
            if n0>0 and nm>0:
                raise ArithmeticError('Partial fractions incomplete')
            n=n0 if n0>0 else nm if nm>0 else -powers.get(var,0)
            if n<0:
                raise ArithmeticError('Unreduced numerator')
            indices.append((int(n),0 if n0>0 else mass if nm>0 else 0))
            if n0>0 or nm>0:
                remainder=s.cancel(remainder*var**n0*(var-mass)**nm)
        if remainder.has(X,Y,V):
            raise ArithmeticError('Unmapped scalar product')
        if indices[2][0]==0 and (indices[0][0]==0 or indices[1][0]==0):
            continue  # Independent scaleless tadpole, zero in DR.
        args=','.join('{%d,%s}'%(n,'0' if m==0 else 'Sqrt[%s]'%m) for n,m in indices)
        rows.append('('+mathematica_code(s.factor(remainder))+') TJI[D,0,{'+args+'}]')
    Path(path).write_text(' +\n'.join(rows)+'\n')
    return len(rows)


def _quad2(fn,tol):
    """Nested adaptive integration with integrated inner error estimates."""
    @lru_cache(None)
    def inner(v):
        return quad(lambda t:fn(t,v),0,1,epsabs=tol,epsrel=tol,limit=200)
    value,error=quad(lambda v:inner(v)[0],0,1,epsabs=tol,epsrel=tol,limit=200)
    propagated,prop_error=quad(lambda v:inner(v)[1],0,1,epsabs=tol,epsrel=tol,limit=200)
    return value,error+propagated+prop_error


@lru_cache(None)
def sunset(masses,tol=2e-9):
    """Euclidean MSbar sunset (-2,-1,0) Laurent coefficients, mu²=1.

    Six primary/Hepp sectors; analytic endpoint subtraction BEFORE eps
    expansion, including the overall Gamma(-1+2eps) and subdivergences.
    Zero masses supported. Errors are quadrature estimates, not bounds.
    """
    if len(masses)!=3 or min(masses)<0 or not np.isfinite(masses).all() or not any(masses):
        raise ValueError('Three nonnegative mass squares, at least one positive')
    i0=i1=err0=err1=0.
    for (a,b,c),multiplicity in Counter(permutations(masses)).items():
        def endpoint(v):
            f=a/(1+v)**2;L=np.log(1+v)-2*np.log(a) if a else 0.
            return f,f*L,f*L*L/2
        def kernel(t,v,order):
            B=1+v+t*v;M=a+t*(b+v*c);f=M/B**2
            L=np.log(B)-2*np.log(M) if M else 0.
            f0,f1,_=endpoint(v)
            return (f-f0)/t if order==0 else (f*L-f1+(f-f0)*np.log(t))/t
        a0,e0=quad(lambda v:endpoint(v)[1],0,1,epsabs=tol,epsrel=tol)
        a1,e1=quad(lambda v:endpoint(v)[2],0,1,epsabs=tol,epsrel=tol)
        b0,f0=_quad2(lambda t,v:kernel(t,v,0),tol)
        b1,f1=_quad2(lambda t,v:kernel(t,v,1),tol)
        i0+=multiplicity*(a0+b0);i1+=multiplicity*(a1+b1)
        err0+=multiplicity*(e0+f0);err1+=multiplicity*(e1+f1)
    A=sum(masses)
    values=np.array([-A/2,-i0/2-A,-i1/2-i0-(2+ZETA2)*A])
    errors=np.array([0.,err0/2,err1/2+err0])
    return values,errors


def tadpole(m2):
    """PV tadpole (pole,finite,eps): eps terms enter two-loop finite parts."""
    L=np.log(m2)
    return m2*np.array([1.,1-L,1-L+L*L/2+ZETA2/2])


def master_combination(h,coefficient_file,tol=2e-9):
    if not np.isfinite(h) or h<=0 or abs(h-4)<1e-7:
        raise ValueError('Nonexceptional positive h required for this IBP chart')
    coeff=[parse_mathematica(c) for c in json.loads(Path(coefficient_file).read_text())['coefficients']]
    a,b=tadpole(h),tadpole(1.)
    product=lambda u,v:np.convolve(u,v)[:3]
    entries=([(product(a,b),np.zeros(3)),(product(b,b),np.zeros(3))]+
        [sunset(m,tol) for m in ((1.,0.,0.),(1.,h,0.),(1.,1.,h))])
    total=np.zeros(3);error=np.zeros(3);masters=[]
    for c,(value,err) in zip(coeff,entries):
        cc=np.array([float(s.diff(c,D,k).subs({D:4,H:h,W:1}))*(-2)**k/float(s.factorial(k)) for k in range(3)])
        total+=np.convolve(cc,value)[:3]
        error+=np.convolve(abs(cc),err)[:3]
        masters.append(dict(laurent=value,error=err,coefficient_epsilon_series=cc))
    return dict(laurent=total,error=error,masters=masters)


def pole_identity(coefficient_file):
    """Exact d-dependent IBP pole cancellation, with independent log masses."""
    coeff=[parse_mathematica(c).subs(W,1) for c in json.loads(Path(coefficient_file).read_text())['coefficients']]
    L=s.log(H)
    poles=[(H,H*(2-L)),(1,2),(-s.Rational(1,2),-s.Rational(3,2)),
        (-(1+H)/2,H*L-s.Rational(3,2)*(1+H)),
        (-(2+H)/2,H*L-s.Rational(3,2)*(2+H))]
    p2=sum(c.subs(D,4)*a for c,(a,b) in zip(coeff,poles))
    p1=sum(c.subs(D,4)*b-2*s.diff(c,D).subs(D,4)*a for c,(a,b) in zip(coeff,poles))
    return tuple(s.factor(p) for p in (p2,p1))


def direct(h,tol=2e-10):
    """Independent finite radial/angular integral, no sunset or IBP calls."""
    if not np.isfinite(h) or h<=0:
        raise ValueError('Positive finite mass ratio required')
    def fn(u,v):
        x=u/(1-u);y=v/(1-v)
        A=x+y+1;T=A+np.sqrt((x-y)**2+2*(x+y)+1)
        return (2*x*y/T**2*(4*x/(3*T)-3+1/(x+1)) /
                ((x+1)**2*(y+h)*(1-u)**2*(1-v)**2))
    return _quad2(fn,tol)


def topology_pair(mw,ms,v,kappa,mi,left,right):
    """Signed Pauli coefficients of native WWW and reversed scalar placement.

    C=+g²*kappa*MW²/(v*mi*(16pi²)²) * I_W * (Y_L,Y_R).
    I_W=direct(Ms²/MW²)/MW². The covariant Pauli projection removes vector
    form factors; this gauge-dependent pair is NOT an observable or full C.
    """
    if not np.isfinite([mw,ms,v,mi,kappa,left,right]).all() or min(mw,ms,v,mi)<=0:
        raise ValueError('Finite couplings and positive scales required')
    value,error=direct((ms/mw)**2)
    factor=(2*mw/v)**2*kappa/(v*mi*(16*np.pi**2)**2)
    return dict(scope='TOPOLOGY_ONLY; xiW=1; WWW, both scalar placements; leading external degree',
        topology_C_LR=factor*value*np.array([left,right]),
        quadrature_error=abs(factor)*error*abs(np.array([left,right])),
        normalized_vacuum_integral=value/mw**2,
        physical_C_LR=None,coherent_inclusion=False,
        gauge_completion='W/G, physical charged, pinch, BRST/ghost, counterterm and LSZ partners missing')


def gww_numerator():
    return 2*X*(Y+Z)/(D*(W-X))


def gww_mass_difference(h,reference=2.,tol=2e-10):
    """Finite mass difference of UV-divergent GWW parents, xi=1.

    Its mass-independent 1/(4 eps) subdivergence cancels in the difference.
    This is a mathematical check, not a Zee-minus-2HDM class subtraction.
    """
    if not np.isfinite([h,reference]).all() or min(h,reference)<=0:
        raise ValueError('Positive mass ratios required')
    def fn(u,v):
        x=u/(1-u);y=v/(1-v)
        T=x+y+1+np.sqrt((x-y)**2+2*(x+y)+1)
        return (x*y*(T+x)*(reference-h)/
                (T*T*(x+1)**3*(y+h)*(y+reference)*(1-u)**2*(1-v)**2))
    return _quad2(fn,tol)

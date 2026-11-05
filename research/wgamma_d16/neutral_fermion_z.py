"""Common neutral-fermion Z-photon class, matched without photon overlap.

The vector-current replacement applies to both orientations and outer orders.
Axial inner current vanishes by charge conjugation; axial outer current by
the transverse-tensor Dirac anticommutator. See ZEE_TWO_LOOP_DERIVATION.md.
"""
from functools import lru_cache
import numpy as np
from scipy.integrate import quad
from module3.core import vertices
from module4.couplings import quarks
from module4.amplitudes import QUARK_QUANTUM


@lru_cache(maxsize=512)
def z_kernels_log_radial(z, r):
    """Return published (f4,f3) with r=MZ²/Ms², directly integrated.

    f3=-int da int dt t/[(t+z)(t+u)(t+r*u)], f4 inserts (1-2u).
    Positive radial master is integrated in log(t), avoiding tiny-mass poles
    and the removable MZ=Ms divided difference. No author functions are used.
    """
    if not np.isfinite([z, r]).all() or min(z, r) <= 0:
        raise ValueError('Positive finite ratios required')
    errors=[]
    def angular(a, even):
        u=a*(1-a)
        low, high=np.log(min(z,u,r*u))-32, np.log(max(z,u,r*u))+32
        def radial(s):
            t=np.exp(s)
            return t*t/((t+z)*(t+u)*(t+r*u))
        val, err=quad(radial,low,high,epsabs=1e-10,epsrel=2e-11,limit=250)
        err += np.exp(2*low)/(2*z*u*r*u)+np.exp(-high)
        # All integrands are positive. Bound the integrated inner error by
        # its worst RELATIVE error times the positive integral. Absolute
        # errors at x->0 grow pointwise and are not an integrated bound.
        errors.append(err/val)
        return -(1-2*u if even else 1)*val
    result=[]
    for even in (True,False):
        errors.clear()
        val,err=quad(lambda a:angular(a,even),0,.5,epsabs=2e-10,epsrel=2e-10,limit=200)
        result.append((2*val,2*err+2*abs(val)*max(errors,default=0.)))
    if not np.isfinite(result).all() or any(e>2e-6*max(1.,abs(v)) for v,e in result):
        raise ArithmeticError('Uncontrolled Z-photon master')
    return tuple(result)


@lru_cache(maxsize=512)
def z_kernels(z,r):
    """Same positive master after analytic radial integration; fast 1D path.

    J(a)=log(z/a)/(z-a); R=[J(u)-r*J(r*u)]/(1-r).
    Independent log-radial quadrature above is retained as a falsifier.
    """
    import mpmath as mp
    if not np.isfinite([z,r]).all() or min(z,r)<=0:
        raise ValueError('Positive finite ratios required')
    def J(a):
        t=(z-a)/a
        if abs(t)<1e-5:
            return (1-t/2+t*t/3-t**3/4)/a
        return np.log(z/a)/(z-a)
    def radial(u):
        if r == 1.:
            t=(z-u)/u
            if abs(t)<1e-4:
                return (.5-t/6+t*t/12-t**3/20)/u
            return (z*np.log(z/u)-(z-u))/(z-u)**2
        if abs(r-1)<1e-4:
            with mp.workdps(40):
                a,b,c=map(mp.mpf,(z,u,r))
                def jm(v):
                    return mp.log(a/v)/(a-v) if a!=v else 1/a
                return float((jm(b)-c*jm(c*b))/(1-c))
        return (J(u)-r*J(r*u))/(1-r)
    result=[]
    for even in (True,False):
        value,error=quad(lambda a:-(1-2*a*(1-a) if even else 1)*radial(a*(1-a)),
                         0,.5,epsabs=2e-10,epsrel=2e-10,limit=300)
        result.append((2*value,2*error))
    if not np.isfinite(result).all() or any(e>2e-7*max(1.,abs(v)) for v,e in result):
        raise ArithmeticError('Uncontrolled Z-photon radial reduction')
    return tuple(result)


def ledger(D,p,ml,mw,mz,fermion_masses,i,j):
    if not np.isfinite([mw,mz]).all() or not 0<mw<mz or (i,j) not in ((1,0),(2,0),(2,1)):
        raise ValueError('On-shell EW masses and physical decay channel required')
    if (np.asarray(D).shape!=(3,3) or np.asarray(ml).shape!=(3,)
            or not np.isfinite(D).all() or not np.isfinite(ml).all() or min(ml)<=0):
        raise ValueError('Finite Yukawas and positive lepton masses required')
    expected=set(QUARK_QUANTUM)|{'electron','muon','tau'}
    if set(fermion_masses) != expected:
        raise ValueError('All nine fermion masses must be explicit')
    if not np.isfinite(list(fermion_masses.values())).all() or min(fermion_masses.values())<=0:
        raise ValueError('Positive finite fermion masses required')
    sw2=1-(mw/mz)**2;sw,cw=np.sqrt(sw2),mw/mz
    alpha=(2*mw/p['v'])**2*sw2/(4*np.pi)
    vze=(-.5+2*sw2)/(sw*cw)
    rows={}
    for name,(C,mass) in vertices(D,p,ml).items():
        external=np.array([C[j,i],C[i,j].conjugate()])
        for species,mf in fermion_masses.items():
            if species in QUARK_QUANTUM:
                nc,Q=QUARK_QUANTUM[species]
                t3=.5 if Q>0 else -.5
                inner=quarks(mf,species,p)[name]
            else:
                index={'electron':0,'muon':1,'tau':2}[species]
                if mf != ml[index]:
                    raise ValueError('Mismatched charged-lepton input scheme')
                nc,Q,t3,inner=1,-1,-.5,C[index,index]
            vzf=(t3-2*Q*sw2)/(sw*cw)
            (f4,ef4),(f3,ef3)=z_kernels((mf/mass)**2,(mz/mass)**2)
            pref=-nc*alpha*Q*vzf*vze*mf/(64*np.pi**3*ml[i]*mass**2)
            effective=inner.real*f4+1j*inner.imag*f3
            val=pref*external*np.array([effective,effective.conjugate()])
            err=abs(pref*external)*(abs(inner.real)*ef4+abs(inner.imag)*ef3)
            rows[name+'_'+species+'_Z_gamma']=dict(C_LR=val,quadrature_error=err,
                f4=f4,f3=f3,vector_Z_charge=vzf,status='COMMON_NEUTRAL_FERMION_Z_CLASS',
                overlap_with_frozen_photon=False)
    return rows

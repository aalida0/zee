"""h125 -> Z gamma at leading one loop, in the frozen tree input scheme.

Tensor convention: Fontes/Romao/Silva 1408.2534 C.1--C.4, D.5.
c=alpha X/(2 pi v), d=alpha Y/(2 pi v). Scalar routing is the independently
validated photon-adjacent routing (Hue18 Eq16), NOT literal Flo21 D.20.
Only h125, real subthreshold charged scalars/W; light fermions retain cuts.
No total width, experimental likelihood, or higher-order error is supplied.
"""
import math

import mpmath as mp
import numpy as np

from module1.scalar_constraints import reconstruct
from module2.interface import decode
from module3.core import vertices
from module4.couplings import rotations, trilinears
from module7.d4_inputs import SM
from research.full_constraints.higgs.diphoton import MASSES, ALPHA0
from research.full_constraints.higgs.sushi_bridge import benchmark as card
from research.full_constraints.higgs.zgamma_source_audit import parameters


def integrals(mh, mz, mass):
    """Fontes E.2--E.4, physical -i0 continuation; high precision for light f.

    This implementation uses acosh rather than subtracting nearly equal
    numbers inside a log. 60 digits also protect the heavy equal-mass limit.
    """
    if not all(math.isfinite(x) and x > 0 for x in (mh,mz,mass)) or mh <= mz:
        raise ValueError('Positive masses and mh>mz required')
    with mp.workdps(60):
        a=4*mp.mpf(mass)**2/mp.mpf(mh)**2
        b=4*mp.mpf(mass)**2/mp.mpf(mz)**2
        def fg(x):
            if x >= 1:
                q=mp.asin(1/mp.sqrt(x))
                return q*q,mp.sqrt(x-1)*q
            q=2*mp.acosh(1/mp.sqrt(x))-1j*mp.pi
            return -q*q/4,mp.sqrt(1-x)*q/2
        fa,ga=fg(a);fb,gb=fg(b)
        i1=a*b/(2*(a-b))+a*a*b*b/(2*(a-b)**2)*(fa-fb)+a*a*b/(a-b)**2*(ga-gb)
        i2=-a*b/(2*(a-b))*(fa-fb)
        return complex(i1),complex(i2)


def quantum_numbers(f):
    if f in ('u','c','t'):return 2/3, .5, 3
    if f in ('d','s','b'):return -1/3, -.5, 3
    if f in ('e','mu','tau'):return -1., -.5, 1
    raise ValueError('Unknown charged fermion')


def scalar_terms(mh,mz,v,e,masses,G,Z,n=80):
    """Ordered species sum, both orientations, triangle + AZ seagull current.

    Xij=-2v/e Gij Zji [K(mi²,mj²)+K(mj²,mi²)]. For equal masses,
    Xii=-v Gii Zii/e I1/mi². Potential V contains +h H- G H+.
    The scalar tensor/current/Ward derivation is retained in the source audit.
    """
    G=np.asarray(G,dtype=complex);Z=np.asarray(Z,dtype=complex)
    size=len(masses)
    if not all(math.isfinite(x) and x>0 for x in (mh,mz,*masses)) or mh<=mz:
        raise ValueError('Positive masses and mh>mz required')
    if G.shape != (size,size) or Z.shape != G.shape or not np.all(np.isfinite(G)) or not np.all(np.isfinite(Z)):
        raise ValueError('Finite square currents required')
    if not np.allclose(G,G.conj().T,rtol=0,atol=1e-11) or not np.allclose(Z,Z.conj().T,rtol=0,atol=1e-13):
        raise ValueError('Hermitian currents required')
    if not all(math.isfinite(x) and x>0 for x in (v,e)):
        raise ValueError('Positive v,e required')
    k=np.array([[parameters(mh*mh,mz*mz,a*a,b*b,n)['k'] for b in masses] for a in masses])
    return {f'H{i+1}H{j+1}':-2*v/e*G[i,j]*Z[j,i]*(k[i,j]+k[j,i])
            for i in range(size) for j in range(size)}


def amplitude(mh,kv,kappas,charged=(),G=None,Z=None,v=SM['EW']['v'],
              mw=SM['EW']['mW'],mz=SM['EW']['mZ'],masses=None,n=80):
    if not all(math.isfinite(x) and x>0 for x in (mh,v,mw,mz)) or not mz<mh<2*mw or not mw<mz:
        raise ValueError('Only h125 below W threshold, on-shell Z, and MW<MZ supported')
    if not math.isfinite(kv):raise ValueError('Finite kV required')
    masses=MASSES if masses is None else masses
    if set(kappas)!=set(MASSES)-{'W'}:raise ValueError('All nine charged fermions required')
    cw=mw/mz;sw=math.sqrt(1-cw*cw);tw2=sw*sw/(cw*cw)
    e=2*mw/v*sw;alpha=e*e/(4*math.pi)
    a,b=integrals(mh,mz,mw);tau=4*mw*mw/(mh*mh)
    even={'W':kv*cw/sw*(4*(3-tw2)*b+((1+2/tau)*tw2-(5+2/tau))*a)}
    odd={};chiral={}
    for f,k in kappas.items():
        k=complex(k)
        if not math.isfinite(k.real) or not math.isfinite(k.imag):raise ValueError('Finite Yukawa required')
        q,t3,nc=quantum_numbers(f);a,b=integrals(mh,mz,masses[f])
        # Zff=i gamma_mu (gL PL+gR PR), gL=e/(sw cw)(T3-Qsw²),
        # gR=-e Q sw/cw. Only their vector sum survives orientation sum.
        l=(t3-q*sw*sw)/(sw*cw);r=-q*sw/cw
        weight=2*nc*q*(l+r)
        even[f]=weight*k.real*(a-b)
        # Native C has right-Weyl row: C PL+C* PR = Re C-i Im C gamma5.
        # Fontes b=-Im(k), Y=-weight*b*I2 = +weight*Im(k)*I2.
        odd[f]=weight*k.imag*b
        chiral[f]=dict(Q=q,T3=t3,Nc=nc,gL_over_e=l,gR_over_e=r)
    scalar=scalar_terms(mh,mz,v,e,charged,G,Z,n) if len(charged) else {}
    even.update(scalar);x=sum(even.values());y=sum(odd.values())
    norm=abs(x)**2+abs(y)**2
    prefactor=alpha**2*mh**3/(128*math.pi**3*v*v)*(1-mz*mz/(mh*mh))**3
    return dict(even=x,odd=y,even_terms=even,odd_terms=odd,scalar_terms=scalar,
                chiral_currents=chiral,norm=norm,width_GeV=prefactor*norm,
                prefactor_GeV=prefactor,alpha_em=alpha,e=e,
                alpha0_scheme_width_GeV=prefactor*norm*(ALPHA0/alpha)**2)


def benchmark(name,n=80):
    r,w=card(name);p=r['input']['physical'];ml=np.asarray(SM['lepton_masses'])
    c=vertices(decode(w['yukawas']['D']),p,ml)['h'][0]
    ku=math.sin(p['alpha'])/math.sin(p['beta']);kd=math.cos(p['alpha'])/math.cos(p['beta'])
    k={f:complex(ku if f in ('u','c','t') else kd) for f in ('u','c','t','d','s','b')}
    k.update(zip(('e','mu','tau'),np.diag(c)*p['v']/ml))
    g=trilinears(p,reconstruct(p)[0])['h'][1:,1:]
    zp=rotations(p)[2][1:];cw=SM['EW']['mW']/SM['EW']['mZ'];sw=math.sqrt(1-cw*cw)
    e=2*SM['EW']['mW']/p['v']*sw
    z=e/(sw*cw)*(.5*zp[:,:2]@zp[:,:2].T-sw*sw*np.eye(2))
    charged=[p['mH1'],p['mH2']];kv=math.cos(p['alpha']-p['beta'])
    full=amplitude(p['mh1'],kv,k,charged,g,z,p['v'],n=n)
    sm=amplitude(p['mh1'],1,{f:1 for f in k},v=p['v'])
    return dict(name=name,scalar_sha256=r['input_sha256'],yukawa_sha256=w['yukawa_sha256'],
                mh_GeV=p['mh1'],v_GeV=p['v'],charged_masses_GeV=charged,G_GeV=g,Z_current=z,
                kV=kv,kappas=k,full=full,SM=sm,ratio_to_SM=full['norm']/sm['norm'],
                W_threshold_gap_GeV=2*SM['EW']['mW']-p['mh1'],
                scalar_threshold_gaps_GeV=[2*m-p['mh1'] for m in charged],
                status='H125_ZGAMMA_LEADING_ONE_LOOP',physical_higgs='UNKNOWN',
                theory_sigma=None,global_acceptance=None)

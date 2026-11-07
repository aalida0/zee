"""Finite leading one-loop h->gamma gamma in the frozen physical tree scheme.

L_int=-h g_ij H_i^- H_j^+; g=d^3V, in GeV. No SPheno pole inputs.
0902.0851 Eqs.24-28, with C_HH+H-=-g; 1408.6133 Eqs.2-4.
The two CP tensors do not interfere in the unpolarized width.
"""
import cmath
import math
import numpy as np
from module1.scalar_constraints import reconstruct
from module2.interface import decode
from module3.core import vertices
from module4.couplings import trilinears, rotations
from module7.d4_inputs import SM

ALPHA0 = 1 / 137.035999084
# One common *tree* input scheme, including the photon vertices:
# g2=2 MW/v, cw=MW/MZ, e=g2 sqrt(1-cw^2). alpha(0) is a separately
# named convention control, never silently mixed with the tree gauge input.
ALPHA_TREE = (2*SM['EW']['mW']/SM['EW']['v'])**2*(1-(SM['EW']['mW']/SM['EW']['mZ'])**2)/(4*math.pi)
MASSES = dict(zip(('u','c','t','d','s','b'), SM['kinematic_masses']))
MASSES.update(zip(('e','mu','tau'), SM['lepton_masses']))
MASSES['W'] = SM['EW']['mW']
# Pinned HiggsTools Basics.hpp values, used ONLY for an independent code control.
HT_MASSES = dict(u=.00216,c=1.51,t=172.5,d=.00467,s=.093,b=4.92,
                 e=.000510998928,mu=.1056583715,tau=1.77682,W=80.385)


def positive(x):
    x=float(x)
    if not math.isfinite(x) or x<=0:
        raise ValueError('Positive finite input required')
    return x


def loops(tau):
    """A0, A1/2, A1, A1/2(odd); tau=m_h^2/(4m^2)."""
    t=positive(tau)
    if t < 1e-4:
        # Analytic expansions prevent cancellation in the heavy-mass limit.
        a0=1/3+8*t/45+4*t*t/35+128*t**3/1575
        af=4/3+14*t/45+8*t*t/63+104*t**3/1575
        aw=-7-22*t/15-76*t*t/105-232*t**3/525
        ap=2+2*t/3+16*t*t/45+8*t**3/35
        return tuple(complex(x) for x in (a0,af,aw,ap))
    if t<=1:
        f=math.asin(math.sqrt(t))**2
    else:
        # acosh(sqrt(t)) avoids loss of significance for light fermions.
        f=-.25*(2*math.acosh(math.sqrt(t))-1j*math.pi)**2
    return ((f-t)/t**2,2*(t+(t-1)*f)/t**2,
            -(2*t*t+3*t+3*(2*t-1)*f)/t**2,2*f/t)


def amplitude(mh, kv, kappas, charged=(), v=SM['EW']['v'], masses=None, alpha=ALPHA_TREE):
    """Complete one-loop rate; charged=(mass_GeV,g_GeV,Q), coherent sum."""
    mh,v,alpha=map(positive,(mh,v,alpha));masses=MASSES if masses is None else masses
    if not math.isfinite(kv):raise ValueError('Finite vector coupling required')
    if set(kappas)!=set(MASSES)-{'W'}:raise ValueError('All nine fermions required')
    even={'W':kv*loops((mh/(2*positive(masses['W'])))**2)[2]};odd={}
    for f,k in kappas.items():
        k=complex(k)
        if not (math.isfinite(k.real) and math.isfinite(k.imag)):raise ValueError('Finite Yukawa required')
        _,af,_,ap=loops((mh/(2*positive(masses[f])))**2)
        weight=4/3 if f in ('u','c','t') else 1/3 if f in ('d','s','b') else 1
        even[f]=weight*k.real*af;odd[f]=weight*k.imag*ap
    for i,(mass,g,q) in enumerate(charged,1):
        mass=positive(mass);g=complex(g)
        if not (math.isfinite(g.real) and math.isfinite(g.imag) and math.isfinite(q)) or abs(g.imag)>1e-12:
            raise ValueError('Hermitian diagonal real trilinear and finite charge required')
        even[f'H{i}']=q*q*g.real*v/(2*mass*mass)*loops((mh/(2*mass))**2)[0]
    s=sum(even.values());p=sum(odd.values())
    norm=abs(s)**2+abs(p)**2
    return dict(even=s,odd=p,even_terms=even,odd_terms=odd,
                norm=norm,width_GeV=alpha**2*mh**3/(256*math.pi**3*v*v)*norm)


def benchmark(physical, witness):
    p=physical;ml=np.asarray(SM['lepton_masses'])
    c=vertices(decode(witness['yukawas']['D']),p,ml)['h'][0]
    ku=math.sin(p['alpha'])/math.sin(p['beta']);kd=math.cos(p['alpha'])/math.cos(p['beta'])
    k={f:complex(ku if f in ('u','c','t') else kd) for f in ('u','c','t','d','s','b')}
    k.update(zip(('e','mu','tau'),np.diag(c)*p['v']/ml))
    lag,_,_=reconstruct(p);g=trilinears(p,lag)['h'][1:,1:]
    charged=[(p[f'mH{i+1}'],g[i,i],1) for i in range(2)]
    kv=math.cos(p['alpha']-p['beta'])
    alpha_tree=(2*SM['EW']['mW']/p['v'])**2*(1-(SM['EW']['mW']/SM['EW']['mZ'])**2)/(4*math.pi)
    full=amplitude(p['mh1'],kv,k,charged,p['v'],alpha=alpha_tree)
    base=amplitude(p['mh1'],kv,k,(),p['v'],alpha=alpha_tree)
    sm=amplitude(p['mh1'],1,{f:1 for f in k},(),p['v'],alpha=alpha_tree)
    # Z generator on physical H+ states; Q=identity. Sign tied to native momentum rule.
    zp=rotations(p)[2][1:];cw=SM['EW']['mW']/SM['EW']['mZ'];sw2=1-cw*cw
    z=2*SM['EW']['mW']/p['v']/cw*(.5*(zp[:,:2]@zp[:,:2].T)-sw2*np.eye(2))
    return dict(full=full,without_charged=base,SM=sm,kappas=k,kV=kv,
                g_h_charged_GeV=g,charged=charged,Z_current=z,
                photon_current=np.eye(2)*math.sqrt(4*math.pi*alpha_tree),
                gamma_Z_seagull_current=2*math.sqrt(4*math.pi*alpha_tree)*z,
                offdiagonal_h_Z_products_GeV=[g[0,1]*z[1,0],g[1,0]*z[0,1]],
                ratio_to_SM=full['norm']/sm['norm'],
                ratio_without_charged_to_SM=base['norm']/sm['norm'],
                common_tree_alpha_em=alpha_tree,
                alpha0_convention_width_GeV=full['width_GeV']*(ALPHA0/alpha_tree)**2,
                input_scheme='v,MW,MZ tree inputs; g2=2MW/v, cw=MW/MZ, e=g2*sw; common fermion propagator/Yukawa masses; all scalar masses/trilinears from physical tree card',
                hZgamma='UNKNOWN',theory_sigma=None,
                status='HIGGS_SCOPED_CHANNEL_VALIDATED',exclusion=None,global_acceptance=None)

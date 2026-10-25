"""Photon-mediated subsets only; explicit complex chirality and source ledger."""
import math
import numpy as np
from module3.core import BASIS, OPERATOR, vertices
from .couplings import quarks
from .kernels import kernels, w_kernel

CHANNELS = {'mu_to_e_gamma':(1,0),'tau_to_mu_gamma':(2,1),'tau_to_e_gamma':(2,0)}
QUARK_QUANTUM = {s:(3,q) for s,q in [('up',2/3),('charm',2/3),('top',2/3),
                  ('down',-1/3),('strange',-1/3),('bottom',-1/3)]}
MISSING = {
    'W_gamma':'UNKNOWN: CHK/Ilisie/Abe off-shell W form factors differ; complete LFV pinch/R_xi matching unresolved; excluded from coherent rate',
    'charged_scalar_gamma':'UNKNOWN_NOT_IMPLEMENTED: native trilinears extracted; independent complete amplitude/normalization and Ward check pending',
    'fermion_Z_gamma':'NOT_EVALUATED: CHK Eq.12 identified; weak-current matching and numerical validation pending',
    'W_Z_gamma':'NOT_EVALUATED: CHK Eqs.17,19 identified; complete Zee matching pending',
    'charged_current_WZ':'NOT_EVALUATED: charged-current and charged-scalar mixed electroweak matching pending',
    'additional_bosonic_two_loop':'NOT_EVALUATED: CHK set C / kite topologies not matched',
    'QED_running_and_radiation':'NOT_EVALUATED',
    'finite_external_invariants_and_neutrino_masses':'NOT_EVALUATED beyond frozen one-loop approximation',
}


def row(c, scalar, species, source, subset, error, validated=False):
    return dict(status='PARTIAL' if validated else 'UNKNOWN',
                validation_status='VALIDATION_PASS' if validated else 'GAUGE_MATCHING_UNRESOLVED',
                C_L=complex(c[0]),C_R=complex(c[1]),scalar=scalar,loop_species=species,
                loop_order=2,source=source,gauge_subset=subset,operator_convention=OPERATOR,
                basis=BASIS,numerical_error=float(error),
                coherent_inclusion=validated,
                uncertainty=('Signed photon-fermion matching validated; ' if validated else 'Complete off-shell W/pinch LFV matching UNRESOLVED; ')+
                    'quadrature error only; nominal unmatched mass/Yukawa scheme; external-invariant expansion')


def fermion_component(C, internal, mass, scalar_mass, mi, alpha, nc, charge):
    """Physical fermion-photon subset from the native vertices and outer matching.

    C = (C_ji, C_ij*). internal is the left-chiral diagonal scalar coupling.
    Direct Wick/Dirac matching, Ilisie19, GM2Calc51-54, Chang2001:9.
    Literal Davidson16+21 has the opposite two-loop sign; retained in the
    source audit, not used as the matching prescription. See MATCHING_AUDIT.
    """
    if not all(math.isfinite(x) and x>0 for x in (mass,scalar_mass,mi,alpha,nc)):
        raise ValueError('Positive finite masses/constants required')
    if not math.isfinite(charge):
        raise ValueError('Finite charge required')
    if np.asarray(C).shape!=(2,) or not np.isfinite(np.asarray(C,dtype=complex)).all() or not np.isfinite(complex(internal)):
        raise ValueError('Two finite complex external chiral couplings and one internal coupling required')
    (f,g,_),(ef,eg,_) = kernels((mass/scalar_mass)**2)
    effective = internal.real*f+1j*internal.imag*g
    pref = -alpha*nc*charge**2/(8*math.pi**3*mi*mass)
    out=pref*np.array([C[0]*effective,C[1]*effective.conjugate()])
    error=abs(pref)*max(abs(C[0]),abs(C[1]))*(abs(internal.real)*ef+abs(internal.imag)*eg)
    return out,float(error)


def ledger(D,p,ml,alpha,fermion_masses,mw,i,j):
    D=np.asarray(D,dtype=complex)
    if D.shape!=(3,3) or not np.isfinite(D).all() or not math.isfinite(mw) or mw<=0:
        raise ValueError('Finite 3x3 D and positive W mass required')
    if (i,j) not in CHANNELS.values():
        raise ValueError('Unsupported external channel')
    expected=set(QUARK_QUANTUM)|{'electron','muon','tau'}
    if set(fermion_masses)!=expected:
        raise ValueError('All nine charged fermion masses must be explicit')
    scalars=vertices(D,p,ml)
    out={}
    for scalar,(C,mphi) in scalars.items():
        external=(C[j,i],C[i,j].conjugate())
        for species,mass in fermion_masses.items():
            if species in QUARK_QUANTUM:
                nc,q=QUARK_QUANTUM[species]
                coupling=quarks(mass,species,p)[scalar]
            else:
                k={'electron':0,'muon':1,'tau':2}[species]
                if mass != ml[k]:
                    raise ValueError('Charged-lepton loop masses differ from external mass convention')
                nc,q,coupling=1,-1,C[k,k]
            value,error=fermion_component(external,coupling,mass,mphi,ml[i],alpha,nc,q)
            out[scalar+'_'+species+'_gamma']=row(value,scalar,species,
                'Module4:MATCHING_AUDIT;Ilisie1502.04199:Eqs9,11,12,19;GM2Calc2110.13238:Eqs51-54;Chang0009292:Eqs6-10',
                'fermion_photon_transverse_subset',error,validated=True)
        if scalar!='A':
            gww=math.cos(p['beta']-p['alpha']) if scalar=='h' else math.sin(p['beta']-p['alpha'])
            kernel,error=w_kernel((mw/mphi)**2)
            pref=-alpha*gww/(16*math.pi**3*ml[i]*p['v'])
            out[scalar+'_W_gamma']=row(pref*kernel*np.array(external),scalar,'W+Goldstone+ghost',
                'Davidson1601.01949:Eq24;CHK9302267:Eqs13,14,18;Haber2024:Eqs39,42',
                'CHK_BI_plus_G_photon_subset;not_full_EW_two_loop',
                abs(pref)*max(map(abs,external))*error)
    return out


def combine(rows):
    if not rows:
        raise ValueError('Empty coherent ledger')
    for r in rows.values():
        if (r.get('operator_convention')!=OPERATOR or r.get('basis')!=BASIS or
            r.get('validation_status')!='VALIDATION_PASS' or r.get('loop_order') not in (1,2)):
            raise ValueError('Incompatible/unvalidated coherent amplitude')
        for key in ('C_L','C_R'):
            if not np.isfinite(complex(r[key])):
                raise ValueError('Nonfinite dipole')
    return np.array([sum(complex(r[k]) for r in rows.values()) for k in ('C_L','C_R')])

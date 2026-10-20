#!/usr/bin/env python3
"""Q4v12 independent general-complex Zee lepton/f one-loop Yukawa beta gate.

Independent Weyl-tensor one-loop RGE from Schienbein et al NPB939 (2019)
Eq.(5.11), κ=1/2 for two-component Weyl fermions. Ten real scalars and
nine left-Weyl leptons (nu_L,e_L,e_R^c). No PyR@TE RGE algebra reused.

Y_a = dM_Weyl/d r_a symmetric 9x9; a=0..9 real field directions.
F=sum_b Y_b† Y_b, S_ab=Re Tr[Y_a† Y_b].
(16π²) beta(Y_a)|Yuk = 1/2 (F.T Y_a + Y_a F)
   + 2 sum_b Y_b Y_a† Y_b + sum_b S_ab Y_b.
Gauge terms for extracted couplings: f*(-3/2 gp²-9/2 g2²);
Ye_k*(-15/4 gp²-9/4 g2²). This uses fermion Casimirs.

Map beta(Y_a) back to complex f, Ye1, Ye2 through *multiple*
independent scalar components; check exact antisymmetry, SU2/complex
scalar consistency, and historical Kanemura/FLS limits.

Directly compare to PyR@TE's saved generated RGEs.py:
(1) beta_f and beta_Ye1, beta_Ye2 with no quark Yukawas;
(2) beta_f and f-induced DELTAS to beta_Ye1, beta_Ye2 with generic
    complex quark Yukawas, subtracting f=0 at the same quark point.
This stage still does NOT validate the other 23 complete equations,
mixed gauge-Yukawa two-loop RGEs, threshold effects, or allowed points.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import traceback
from pathlib import Path
import numpy as np

from zee_section8_Q4_independent_f_quartic_gate import (
    lepton_weyl_mass, synthetic_f, validate_f,
)
from zee_section8_Q4_independent_yukawa_quartic_gate import (
    YUKAWAS,synthetic_yukawas,validate_yukawas,
)
from zee_section8_Q4_generated_source_limit_probe import (
    arg_map,evaluate,find_rges,load_generated,
)

STATUS='Q4_INDEPENDENT_COMPLEX_WEYL_YUKAWA_BETAS_NOT_FULL_ZEE_OR_ALLOWED'
LEPTON_COUPLINGS=('f','Ye1','Ye2')
SQRT2=np.sqrt(2.)

def zeros():
    return {k:np.zeros((3,3),complex) for k in YUKAWAS}

def independent_weyl_tensors(ye1,ye2,f):
    yy=zeros()
    yy['Ye1']=np.asarray(ye1,complex)
    yy['Ye2']=np.asarray(ye2,complex)
    validate_yukawas(yy)
    f=validate_f(f)
    eye=np.eye(10)
    tensors=np.stack([lepton_weyl_mass(eye[a],yy,f)
                      for a in range(10)],axis=0)
    if tensors.shape!=(10,9,9) or np.max(abs(tensors-tensors.transpose(0,2,1)))>1e-12:
        raise AssertionError('Weyl Yukawa mass tensors are not symmetric')
    return tensors

def universal_weyl_beta(Y):
    """Schienbein 2019 one-loop generic real-scalar Weyl Yukawa tensor."""
    Y=np.asarray(Y,complex)
    if Y.ndim!=3 or Y.shape[1]!=Y.shape[2]:
        raise ValueError('Require N real-scalar symmetric square Yukawa tensors')
    if not np.isfinite(Y).all() or np.max(abs(Y-Y.transpose(0,2,1)))>1e-12:
        raise ValueError('Weyl Yukawas must be finite symmetric tensors')
    F=np.einsum('aji,ajk->ik',np.conjugate(Y),Y)
    # S_ab is symmetric real scalar anomalous-dimension trace.
    S=np.einsum('aij,bij->ab',np.conjugate(Y),Y).real
    out=np.empty_like(Y)
    for a,Ya in enumerate(Y):
        wave=(F.T@Ya+Ya@F)/2
        vertex=sum(2*Yb@Ya.conj().T@Yb for Yb in Y)
        scalar_wave=np.einsum('b,bij->ij',S[a],Y)
        out[a]=wave+vertex+scalar_wave
    if not np.isfinite(out).all():
        raise ValueError('Nonfinite generic Weyl beta')
    return out

def extracted_lepton_betas(tensor_betas,atol=5e-11):
    B=np.asarray(tensor_betas,complex)
    if B.shape!=(10,9,9):
        raise ValueError(f'Unexpected beta tensor shape {B.shape}')
    # chi components: 2 f chi -> sqrt(2) f (r8+i r9).
    f8=B[8,:3,3:6]/SQRT2
    f9=B[9,:3,3:6]/(1j*SQRT2)
    # Phi_k components: M_{L,eR^c} = conjugate[Ye_k Phi_k].
    # r_real -> Ye_k* /sqrt(2); r_imag -> -i Ye_k*/sqrt(2).
    ye1=[np.conjugate(SQRT2*B[a,lower:lower+3,6:9])
         for a,lower in ((0,0),(2,3))]
    ye1+= [np.conjugate(1j*SQRT2*B[a,lower:lower+3,6:9])
           for a,lower in ((1,0),(3,3))]
    ye2=[np.conjugate(SQRT2*B[a,lower:lower+3,6:9])
         for a,lower in ((4,0),(6,3))]
    ye2+= [np.conjugate(1j*SQRT2*B[a,lower:lower+3,6:9])
           for a,lower in ((5,0),(7,3))]
    residuals={
        'chi_real_imag':float(np.max(abs(f8-f9))),
        'f_antisymmetry':float(np.max(abs(f8+f8.T))),
        'Ye1_components':max(float(np.max(abs(z-ye1[0]))) for z in ye1),
        'Ye2_components':max(float(np.max(abs(z-ye2[0]))) for z in ye2),
    }
    if max(residuals.values())>atol:
        raise ValueError(f'Weyl coupling projection inconsistent: {residuals}')
    return {'f':f8,'Ye1':ye1[0],'Ye2':ye2[0]},residuals

def independent_betas(yy,f,*,gp=.36,g2=.65):
    yy=validate_yukawas(yy);f=validate_f(f)
    if not np.isfinite((gp,g2)).all() or min(gp,g2)<0:
        raise ValueError('Invalid electroweak gauge inputs')
    Y=independent_weyl_tensors(yy['Ye1'],yy['Ye2'],f)
    B=universal_weyl_beta(Y)
    values,checks=extracted_lepton_betas(B)
    values['f']=values['f']-(1.5*gp**2+4.5*g2**2)*f
    for k in ('Ye1','Ye2'):
        values[k]=values[k]-(15*gp**2/4+9*g2**2/4)*yy[k]
    return values,checks

def generator_lepton_betas(mod,yy,f,*,gp=.36,g2=.65):
    kw=arg_map(gp=gp,g2=g2,g3=1.18,yy=yy,f=np.matrix(f))
    return {k:evaluate(mod,k,kw) for k in LEPTON_COUPLINGS}

def deviation(got,ref):
    got=np.asarray(got,complex);ref=np.asarray(ref,complex)
    if got.shape!=(3,3) or ref.shape!=(3,3):
        return {'pass':False,'shape_mismatch':[list(got.shape),list(ref.shape)]}
    delta=float(np.max(abs(got-ref)))
    scale=max(1.,float(np.max(abs(got))),float(np.max(abs(ref))))
    return {'pass':bool(delta<=2e-9*scale),
            'max_abs':delta,'normalized_difference':delta/scale}

def numeric_case(mod,yy,f,*,gp=.36,g2=.65):
    yy=validate_yukawas(yy);f=validate_f(f)
    independently,projections=independent_betas(yy,f,gp=gp,g2=g2)
    generated=generator_lepton_betas(mod,yy,f,gp=gp,g2=g2)
    direct={key:deviation(generated[key],independently[key])
            for key in LEPTON_COUPLINGS}
    # At generic nonzero quark Yukawas, the Yukawa trace contribution to
    # beta_Pi already exists at f=0. Subtract f=0 at the same quark point.
    yf=zeros()
    yf.update(yy)
    f0=np.zeros((3,3),complex)
    direct_ref0,_=independent_betas(yf,f0,gp=gp,g2=g2)
    generated_ref0=generator_lepton_betas(mod,yf,f0,gp=gp,g2=g2)
    extra={
        'f_increment_Ye1':deviation(generated['Ye1']-generated_ref0['Ye1'],
                                    independently['Ye1']-direct_ref0['Ye1']),
        'f_increment_Ye2':deviation(generated['Ye2']-generated_ref0['Ye2'],
                                    independently['Ye2']-direct_ref0['Ye2']),
    }
    return {'direct':direct,'f_increments':extra,'projections':projections}

def mixed_quark_case(mod,yy,f,*,gp=.36,g2=.65):
    yy=validate_yukawas(yy);f=validate_f(f)
    ref,_=independent_betas(yy,f,gp=gp,g2=g2)
    base,_=independent_betas(yy,np.zeros((3,3),complex),gp=gp,g2=g2)
    generated=generator_lepton_betas(mod,yy,f,gp=gp,g2=g2)
    generated0=generator_lepton_betas(mod,yy,np.zeros((3,3),complex),gp=gp,g2=g2)
    return {
       'full_f_beta_no_quark_direct_term':deviation(generated['f'],ref['f']),
       'f_delta_Ye1':deviation(
           generated['Ye1']-generated0['Ye1'],ref['Ye1']-base['Ye1']),
       'f_delta_Ye2':deviation(
           generated['Ye2']-generated0['Ye2'],ref['Ye2']-base['Ye2']),
    }

def run(mod):
    f_real=np.zeros((3,3),float)
    f_real[0,1]=.12;f_real[0,2]=-.08;f_real[1,2]=.055
    f_real=f_real-f_real.T
    z=zeros()
    cases={
       'f_real_only_g0':(z,f_real,0.,0.),
       'f_real_only_gauge':(z,f_real,.36,.65),
       'f_complex_only_gauge':(z,synthetic_f(20261019),.36,.65),
       'lepton_complex_fzero':(
           {**z,**{k:v for k,v in synthetic_yukawas(20261019).items()
                   if k in ('Ye1','Ye2')}},np.zeros((3,3)),.36,.65),
       'lepton_complex_f_seed0':(
           {**z,**{k:v for k,v in synthetic_yukawas(20261019).items()
                   if k in ('Ye1','Ye2')}},synthetic_f(20261019),.36,.65),
       'lepton_complex_f_seed1':(
           {**z,**{k:v for k,v in synthetic_yukawas(20261020).items()
                   if k in ('Ye1','Ye2')}},synthetic_f(20261020),.36,.65),
       'lepton_complex_f_seed2':(
           {**z,**{k:v for k,v in synthetic_yukawas(20261021).items()
                   if k in ('Ye1','Ye2')}},synthetic_f(20261021),.36,.65),
    }
    results={}
    for name,(yy,f,gp,g2) in cases.items():
        row=numeric_case(mod,yy,f,gp=gp,g2=g2)
        results[name]=row
        fail=[k for group,entry in row.items() if isinstance(entry,dict)
              and group in ('direct','f_increments') for k,v in entry.items()
              if not v['pass']]
        print('Q4_WEYL_LEPTON',name,'PASS' if not fail else 'MISMATCH',
              f'{5-len(fail)}/5','failed',fail,flush=True)
    for seed in (20261019,20261020,20261021):
        yy=synthetic_yukawas(seed)
        f=synthetic_f(seed)
        row=mixed_quark_case(mod,yy,f)
        results[f'quark_mixed_seed_{seed}']={'mixed':row}
        fail=[k for k,v in row.items() if not v['pass']]
        print('Q4_WEYL_LEPTON',f'quark_mixed_seed_{seed}',
              'PASS' if not fail else 'MISMATCH',
              f'{3-len(fail)}/3','failed',fail,flush=True)
    return results

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generator-output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    if a.report.exists():p.error('Refusing to overwrite previous report')
    result={'status':STATUS,
            'independent_complex_lepton_f_sector_checked':False,
            'full_Zee_RGEs_independently_validated':False,
            'allowed_Zee_point':None}
    try:
        src=find_rges(a.generator_output)
        result['RGEs_SHA256']=hashlib.sha256(src.read_bytes()).hexdigest()
        cases=run(load_generated(src))
        checks=[(case,group,key,val) for case,info in cases.items()
                for group,entries in info.items() if group in ('direct','f_increments','mixed')
                for key,val in entries.items()]
        failed=[f'{case}/{group}/{key}' for case,group,key,val in checks
                if not val.get('pass')]
        result.update({'cases':cases,'comparisons_total':len(checks),
                       'comparisons_passed':len(checks)-len(failed),
                       'failed_checks':failed,
                       'independent_complex_lepton_f_sector_checked':not failed})
        print('Q4_INDEPENDENT_COMPLEX_F_PI',len(checks)-len(failed),'/',len(checks))
        print('Q4_COMPLETE_ZEE_RGE_VALIDATED False')
        return 0 if not failed else 2
    except Exception as exc:
        result['error']=repr(exc)
        result['traceback']=traceback.format_exc()
        print('Q4_COMPLEX_WEYL_FAIL_CLOSED',repr(exc),file=sys.stderr)
        return 1
    finally:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('Q4_COMPLEX_WEYL_REPORT',a.report)

if __name__=='__main__':
    raise SystemExit(main())

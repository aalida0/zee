#!/usr/bin/env python3
"""Partial LFV adapter. Missing matching is represented by None, never zero."""
import csv, json, math, hashlib, subprocess, tempfile
from pathlib import Path
import numpy as np
from module2.interface import decode
from research.full_constraints.lfv.source_to_code import box_kernel, generated_box_driver

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def pair(z): return [float(complex(z).real),float(complex(z).imag)]
def al_kernel(DL,DR,gpLV,gnLV,gpRV,gnRV,gpLS,gnLS,gpRS,gnRS):
    """FlexibleSUSY source convention, inputs GeV^-2; rate/capture dimensionless.

    Reject nulls: omission is never equivalent to a zero insertion. Source uses
    overlap factors m_mu^(5/2); D coefficients have source-specific convention.
    """
    vals=(DL,DR,gpLV,gnLV,gpRV,gnRV,gpLS,gnLS,gpRS,gnRS)
    if any(x is None for x in vals): raise ValueError('incomplete Wilson vector')
    m=0.1056583755; scale=m**2.5
    left=scale*(DR*.0357/4-gpLV*.0159-gnLV*.0169-gpRS*.0153-gnRS*.0163)
    right=scale*(DL*.0357/4-gpRV*.0159-gnRV*.0169-gpLS*.0153-gnLS*.0163)
    return left,right,4*(abs(left)**2+abs(right)**2)/4.64079e-19

def source_controls():
    lock=json.loads((ROOT/'research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json').read_text())
    items={x['id']:x for x in lock['artifacts']}
    paths={}
    for name in ('generated','couplings','loops'):
        p=Path(items[name]['path_hint']); assert hashlib.sha256(p.read_bytes()).hexdigest()==items[name]['sha256']; paths[name]=p
    groups=json.loads((ROOT/'validation/module12/d12_benchmarks.json').read_text())['groups']
    controls=[]
    for group in groups:
        w=group['witnesses']['low_joint']; p=w['module2_input']['scalar']['record']['physical']; f=decode(w['yukawas']['F'])
        u=np.diag(np.exp(1j*np.array([.2,-.4,.7])))
        controls.extend([(w['id'],p['mH1'],p['mH2'],p['gamma'],f), (w['id']+'/phase',p['mH1'],p['mH2'],p['gamma'],u@f@u)])
    with tempfile.TemporaryDirectory(dir=HERE) as d:
        work=Path(d); names,driver_hash=generated_box_driver(paths['generated'],paths['couplings'],paths['loops'],work)
        stdin=''.join(f'{a:.17e} {b:.17e} {g:.17e}\n'+''.join(f'{v.real:.17e} {v.imag:.17e}\n' for v in f.flat) for _,a,b,g,f in controls)
        raw=subprocess.check_output([str(work/'box')],input=stdin,text=True)
    rows=np.array([complex(*map(float,line.split())) for line in raw.splitlines()]).reshape(len(controls),len(names))
    out=[]
    for row,(name,a,b,g,f) in zip(rows,controls):
        expected=f[1,2]*f[0,2].conjugate()*np.sum(abs(f[0])**2)*box_kernel(a,b,g)/(64*math.pi**2)
        val=row[names.index('BO4lVLL')]; residual=abs(val-expected)/max(abs(expected),1e-300)
        others=max((abs(v) for n,v in zip(names,row) if n!='BO4lVLL'),default=0)
        assert residual<2e-12 and others==0
        out.append(dict(control=name,source_VLL=pair(val),analytic_VLL=pair(expected),relative_residual=residual,other_source_coefficients_max_abs=others))
    return dict(status='PASS_RESTRICTED_F_ONLY',source_driver_sha256=driver_hash,controls=out,phase_bridge_to_penguins='NOT_VALIDATED')

def produce():
    old=json.loads((HERE/'NUMERICAL.json').read_text()); scope=json.loads((ROOT/'research/full_constraints/lfv_precision_scope_2026/SCOPE_DIAGNOSTICS.json').read_text())
    source=source_controls(); cards=[]; rows=[]
    for c in old['cards']:
        d=c['radiative']['mu_to_e_gamma']; s=next(x for x in scope['cards'] if x['id']==c['id'])
        cards.append(dict(id=c['id'],dipole=dict(status='VALIDATED_SUBSET',CL=d['C_L'],CR=d['C_R'],zgamma_CL_CR=d['neutral_Zgamma_C_LR'],units='GeV^-2'),
          mu3e=dict(tree_scalar=dict(status='VALIDATED_SUBSET',coefficients=c['tree_scalar_contact_GeV_minus2']),F_box=dict(status='VALIDATED_RESTRICTED_SOURCE_CONVENTION',raw_VLL=c['F_only_box_raw_VLL_GeV_minus2'],paper_action_VLL=c['F_only_box_paper_L_PLPL_GeV_minus2']),K1L=None,K1R=None,K2_common_basis=None,Z=None,other_boxes=None,complete_vector=None,rate=None,tree_rate_diagnostic=c['mu3e_tree_only_BR_saved']),
          conversion=dict(K1=None,K2_common_basis=None,Z=None,scalar_quark=None,vector_quark=None,gluon=None,boxes=None,complete_vector=None,rate=None)))
        for obs,partial,limit in [('mu_to_e_gamma',d['BR_subset'],1.5e-13),('mu3e',c['mu3e_tree_only_BR_saved'],1e-12),('muAl_conversion',None,None)]:
            rows.append(dict(card=c['id'],observable=obs,physical_rate=None,partial_diagnostic=partial,diagnostic_group='baseline dipole' if obs=='mu_to_e_gamma' else ('tree only' if obs=='mu3e' else ''),limit_90CL=limit,status='UNKNOWN'))
    ledger=dict(complex_encoding='[real,imag] except imported dipoles {real,imag}',cards=cards,missing_is_null=True)
    (HERE/'WILSON_LEDGER.json').write_text(json.dumps(ledger,indent=2,allow_nan=False)+'\n')
    with (HERE/'BENCHMARK_LFV.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    (HERE/'SOURCE_BOX_CONTROLS.json').write_text(json.dumps(source,indent=2)+'\n')
    material=dict(source='lfv_precision_scope_2026/SCOPE_DIAGNOSTICS.json',cards=[dict(id=x['id'],FdagF_e_mu_abs=x['FdagF_e_mu_abs'],CR_F_only_abs_GeV_minus2=x['CR_F_only_abs_GeV_minus2'],critical_enhancement_factor=x['critical_enhancement_factor_to_mu_gamma_limit_using_F_only']) for x in scope['cards']],interpretation='Diagnostic only; neither an upper bound on unknown amplitudes nor an exclusion.',unresolved=dict(status='UNRESOLVED_POTENTIALLY_LEADING',tensor='mixed F-D charged-current flavor tensors; chirality structure and exact contractions unestablished',topology='mixed charged scalar and W/fermion two-loop structures potentially carrying tau or top chirality enhancement',missing='complete W/Goldstone and wavefunction/scalar-mixing counterterm partners; existence and enhancement not established'))
    (HERE/'MATERIALITY.json').write_text(json.dumps(material,indent=2)+'\n')
    result=dict(status='LEADING_OPERATOR_INCOMPLETE',physical_lfv='UNKNOWN',global_acceptance=None,mu3e_rate=None,muAl_conversion_rate=None,source_controls='SOURCE_BOX_CONTROLS.json',ledger='WILSON_LEDGER.json',reason='Incomplete common signed leading UV vectors and conversion matching; partial quantities are not bounds.')
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Four frozen cards: partial ledger written; restricted source controls:',len(source['controls']))
if __name__=='__main__': produce()

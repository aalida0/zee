"""Bounded h125 source diagnostic. NOT a physical Zgamma width implementation.

Flo21 D.20 is tested both literally in LoopTools ordering and with a proposed
photon-adjacent mass correction. No corrected formula is silently substituted.
Only original D7/F13 and analytic mass/mixing limits are evaluated.
"""
import argparse
import functools
import json
import math
import os
from pathlib import Path
import subprocess

import numpy as np
from scipy.integrate import dblquad

from module1.scalar_constraints import reconstruct
from module4.couplings import rotations, trilinears
from module7.d4_inputs import SM
from research.full_constraints.higgs.sushi_bridge import benchmark, dump, sha, ROOT

HERE = Path(__file__).resolve().parent


@functools.lru_cache(None)
def grid(n):
    u,w=np.polynomial.legendre.leggauss(n); u=(u+1)/2; w=w/2
    x=u[:,None]; y=(1-x)*u[None,:]; z=1-x-y
    return u,w,x,y,z,w[:,None]*w[None,:]*(1-x)


def parameters(s,t,a,b,n=80):
    """a,b are squared masses; real subthreshold domain only, no epsilon hack.

    LoopTools C0(t,0,s,a,b,c): D=ax+by+cz-txy-sxz.
    Hue A1/A3: K=C12+C22+C2=int xz/D for (a,b,b).
    C00=UV/4 - (1/2) int log(D/mu^2), including the d-dimensional
    finite rational term. Omitting that term would spoil the Ward test.
    """
    if not all(math.isfinite(v) for v in (s,t,a,b)) or min(s,t,a,b)<=0 or s<=t:
        raise ValueError('Positive squared masses and s>t required')
    if max(s,t)>=4*min(a,b):
        raise ValueError('Threshold/absorptive domain not validated by this diagnostic')
    u,w,x,y,z,wt=grid(n)
    d=a*x+b*(y+z)-t*x*y-s*x*z
    dp=a*(x+y)+b*z-t*x*y-s*x*z
    dr=b*x+a*(y+z)-t*x*y-s*x*z
    db=-np.dot(w,np.log1p(-(s-t)*u*(1-u)/(a*u+b*(1-u)-t*u*(1-u))))
    return dict(db=float(db),cp=float(-np.sum(wt/dp)),cr=float(-np.sum(wt/dr)),
                k=float(np.sum(wt*x*z/d)),c00=float(-.5*np.sum(wt*np.log(d))),
                bs=float(-np.dot(w,np.log(a*u+b*(1-u)-s*u*(1-u)))))


def adaptive_k(s,t,a,b):
    # Independent adaptive simplex integration, not a second Gauss grid.
    value,error=dblquad(lambda z,x:x*z/(a*x+b*(1-x)-t*x*(1-x-z)-s*x*z),
                        0,1,lambda x:0,lambda x:1-x,epsabs=1e-18,epsrel=2e-12)
    return value,error


def bracket(s,t,a,b,ab,ba,route):
    key={'literal_LoopTools':'cp','photon_mass_correction_candidate':'cr'}[route]
    return t/(s-t)*ab['db']+1+a*ab[key]+b*ba[key]


def i1(s,t,m2):
    # Hue A14/A19, independent elementary equal-mass function.
    a=4*m2/s; b=4*m2/t
    f=lambda u:math.asin(1/math.sqrt(u))**2
    g=lambda u:math.sqrt(u-1)*math.asin(1/math.sqrt(u))
    return a*b/(2*(a-b))+a*a*b*b/(2*(a-b)**2)*(f(a)-f(b))+a*a*b/(a-b)**2*(g(a)-g(b))


def native(probe,requests):
    env=dict(os.environ); env['LD_LIBRARY_PATH']='/tmp/zee-zgamma-native'+(':'+env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
    text=''.join(' '.join(format(v,'.17g') for v in row)+'\n' for row in requests)
    p=subprocess.run([str(probe)],input=text,text=True,capture_output=True,check=True,env=env)
    rows=[]
    for line in p.stdout.splitlines():
        if not line.startswith('PV '): continue
        values=list(map(float,line.split()[1:])); assert len(values)==12
        rows.append(dict(zip(('db','cp','cr','k','c00','bs'),
                            (complex(*values[i:i+2]) for i in range(0,12,2)))))
    if len(rows)!=len(requests): raise ValueError('Missing native PV output')
    return rows,dict(stdin=text,stdout=p.stdout,stderr=p.stderr,executable_sha256=sha(probe))


def physical_width(*args,**kwargs):
    raise ValueError('Zgamma UNKNOWN: literal Flo21/Hue18 mixed routing mismatch; no complete one-loop release')


def materiality_replay():
    """Arithmetic on retained receipts, not a Phase II width calculation."""
    n=json.loads((HERE/'NEUTRAL_WIDTH_EVIDENCE.json').read_text())
    c=json.loads((HERE/'COVERAGE.json').read_text())
    prod=json.loads((HERE/'SUSHI_EVIDENCE.json').read_text())
    sel=next(x for x in c['limits'] if x['id']==200212223)
    path=Path(c['datasets']['HB']['path'])/sel['file']
    if sha(path)!=sel['sha256']:raise ValueError('Selected likelihood source changed')
    raw=json.loads(path.read_text());rows=[]
    for case in n['benchmarks']:
        for st in ('H','A'):
            r=case['states'][st]
            p=next(x for x in prod['records'] if x['name']==case['name'] and x['state']==st)
            k=r['known_disjoint_sum_GeV'];tau=r['partial_widths_GeV']['tau tau'];ratio=tau/k
            rows.append(dict(name=case['name'],state=st,mass_GeV=p['mass_GeV'],known_disjoint_sum_GeV=k,
                retained_tree_tau_width_GeV=tau,formal_tau_over_known=ratio,known_over_mass=k/p['mass_GeV'],
                central_rate_times_formal_ratio_pb={key:v['sigma_pb']*ratio for key,v in p['central']['rates'].items()},
                charged_W_daughter_domains=r['charged_W_daughter_domains'],missing=r['missing'],
                certified_BR_upper=None,certified_signal_upper=None,physical_BR=None,exclusion=None))
    return dict(status='HIGGS_SCOPED_SEARCH_BLOCKED',
        scope='Arithmetic replay of existing evidence only, after the h source mismatch stopping gate; no Phase II width calculations',
        inputs={str((HERE/x).relative_to(ROOT)):sha(HERE/x) for x in
                ['NEUTRAL_WIDTH_EVIDENCE.json','SUSHI_EVIDENCE.json','COVERAGE.json']},
        selected_dataset_sha256=sha(path),selected_dataset_commit=c['datasets']['HB']['git_head'],
        selected_file=sel['file'],massResolution=raw['analysis']['massResolution'],rows=rows,
        missing_width_numerical_bound=None,observable_uncertainty_tolerance=None,
        HiggsTools_predictions_constructed=0,physical_higgs='UNKNOWN',global_acceptance=None)


def serial(x):
    if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v) for v in x]
    if isinstance(x,np.ndarray):return serial(x.tolist())
    if isinstance(x,complex):return dict(real=x.real,imag=x.imag)
    if isinstance(x,np.generic):return x.item()
    return x


def run(probe):
    cases=[]; requests=[]
    for name in ('D7','F13'):
        r,w=benchmark(name); p=r['input']['physical']; s=p['mh1']**2;t=SM['EW']['mZ']**2
        g=trilinears(p,reconstruct(p)[0])['h'][1:,1:]
        zp=rotations(p)[2][1:]; cw=SM['EW']['mW']/SM['EW']['mZ'];sw=math.sqrt(1-cw*cw)
        e=2*SM['EW']['mW']/p['v']*sw
        z=e/(sw*cw)*(.5*zp[:,:2]@zp[:,:2].T-sw*sw*np.eye(2))
        ms=[p['mH1'],p['mH2']]; sq=np.square(ms); a,b=sq
        q=parameters(s,t,a,b);rrev=parameters(s,t,b,a)
        literal=bracket(s,t,a,b,q,rrev,'literal_LoopTools')
        corrected=bracket(s,t,a,b,q,rrev,'photon_mass_correction_candidate')
        expected=-(s-t)*(q['k']+rrev['k'])
        f00=4*(q['c00']+rrev['c00'])-2*q['bs']
        # Reduced pair tensor before overall couplings: F21=4(Kij+Kji).
        # For the bracket representation F21=-4F/delta.
        ward_literal=f00-2*literal; ward_corrected=f00-2*corrected
        independent,error=adaptive_k(s,t,a,b)
        equal=[]
        for m2 in sq:
            x=parameters(s,t,m2,m2)
            equal.append(dict(mass_GeV=math.sqrt(m2),K=x['k'],I1_over_4m2=i1(s,t,m2)/(4*m2)))
        contributions={}
        for route in ('literal_LoopTools','photon_mass_correction_candidate'):
            mat=np.empty((2,2))
            for i in range(2):
                for j in range(2):
                    ab=parameters(s,t,sq[i],sq[j]);ba=parameters(s,t,sq[j],sq[i])
                    # Only Flo21 X convention, not combined with any W/fermion sign.
                    mat[i,j]=2*p['v']/e*g[j,i].real*z[i,j]*bracket(s,t,sq[i],sq[j],ab,ba,route)/(s-t)
            contributions[route]=dict(ordered_X=mat,scalar_X_sum=np.sum(mat),mixed_X=mat[0,1]+mat[1,0])
        heavy=parameters(s,t,100*a,100*b)
        cases.append(dict(name=name,scalar_sha256=benchmark(name)[0]['input_sha256'],yukawa_sha256=w['yukawa_sha256'],
            s_GeV2=s,t_GeV2=t,charged_masses_GeV=ms,G_GeV=g,Z_current=z,photon_e=e,
            ordered_Gij_Zji_GeV=g*z.T,parameters_ab=q,parameters_ba=rrev,
            literal_bracket=literal,photon_corrected_candidate_bracket=corrected,Hue_equivalent_bracket=expected,
            literal_relative_kernel_mismatch=literal/expected-1,corrected_relative_kernel_residual=corrected/expected-1,
            scalar_Ward_reduced_F00=f00,literal_Ward_reduced_residual=ward_literal,
            candidate_Ward_reduced_residual=ward_corrected,adaptive_K=independent,adaptive_error_estimate=error,
            quadrature_relative_K_residual=q['k']/independent-1,equal_mass_controls=equal,
            fixed_coupling_heavy_mass_K_ratio=q['k']/heavy['k'],scalar_X_diagnostics=contributions,
            physical_width_GeV=None,full_one_loop_status='UNKNOWN'))
        for aa,bb in ((a,b),(b,a),(a,a),(b,b)):
            requests.extend([(s,t,aa,bb,0,1),(s,t,aa,bb,7,19)])
    rows,receipt=native(probe,requests)
    checks=[]
    for request,row in zip(requests,rows):
        s,t,a,b,uv,mu=request;ref=parameters(s,t,a,b)
        expected=dict(ref);expected['c00']+=uv/4+math.log(mu)/4;expected['bs']+=uv+math.log(mu)
        checks.append(dict(request=request,LoopTools=row,parameter_reference=expected,
            absolute_residuals={k:abs(row[k]-expected[k]) for k in row}))
    native_wards=[]
    for start in (0,8):
        for offset in (0,1):
            ab,ba=rows[start+offset],rows[start+2+offset];s,t,*_=requests[start+offset]
            native_wards.append(4*(ab['c00']+ba['c00'])-2*ab['bs']+2*(s-t)*(ab['k']+ba['k']))
    pins={str(p.relative_to(ROOT)):sha(p) for p in [HERE/'zgamma_source_audit.py',HERE/'zgamma_pv_probe.cpp',
        HERE/'test_zgamma_source_audit.py',HERE/'ZGAMMA_SOURCE_MANIFEST.json',HERE/'build_zgamma_probe.sh',
        HERE/'NEUTRAL_WIDTH_EVIDENCE.json',HERE/'SOURCE_MANIFEST.json',
        ROOT/'research/full_constraints/HIGGS_VALIDATION.json',
        ROOT/'module4/couplings.py',ROOT/'module7/d4_inputs.py']}
    return serial(dict(status='ZGAMMA_SOURCE_ROUTING_MISMATCH',scope='h125 scalar source comparison only',
        complete_leading_one_loop_validated=False,physical_higgs='UNKNOWN',global_acceptance=None,
        H_A_extension_executed=False,physical_width_GeV=None,theory_sigma=None,
        cases=cases,native_checks=checks,native_Ward_residuals=native_wards,native_receipt=receipt,source_pins=pins))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--probe',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--replay-out',type=Path)
    a=ap.parse_args();dump(a.out,run(a.probe))
    if a.replay_out:dump(a.replay_out,materiality_replay())

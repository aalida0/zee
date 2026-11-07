"""Execute bounded h125 validation and original D7/F13 evidence, no scans."""
import argparse
import gzip
import json
import math
from pathlib import Path

import numpy as np

from module7.d4_inputs import SM
from research.full_constraints.higgs import zgamma as z
from research.full_constraints.higgs import zgamma_source_audit as audit
from research.full_constraints.higgs.zgamma_reference import execute
from research.full_constraints.higgs.sushi_bridge import dump,sha,ROOT

HERE=Path(__file__).resolve().parent


def run(probe):
    manifest=json.loads((HERE/'ZGAMMA_SOURCE_MANIFEST.json').read_text())
    for path,digest in manifest['native']['files'].items():
        if sha(path)!=digest:raise ValueError('Native library changed: '+path)
    for paper in manifest['papers']:
        if paper['id'] in ('Hue18','Fontes14') and sha(paper['local_read_path'])!=paper['pdf_sha256']:
            raise ValueError('Paper bytes changed: '+paper['id'])
    mh=125.;mw=SM['EW']['mW'];mz=SM['EW']['mZ'];v=SM['EW']['v']
    kappas={f:1 for f in z.MASSES if f!='W'}
    sm=z.amplitude(mh,1,kappas);alpha=sm['alpha_em'];e=sm['e']
    cw=mw/mz;sw=math.sqrt(1-cw*cw);s=mh*mh;t=mz*mz;delta=s-t
    reference=execute(mh,mw,mz,v,alpha,z.MASSES)
    six={f:1 if f in reference['SM_fermions'] else 0 for f in kappas}
    matched=z.amplitude(mh,1,six)
    sm_residual=matched['width_GeV']/reference['SM_width_GeV']-1
    assert abs(sm_residual)<2e-12
    requests=[(s,t,m*m,m*m,0,1) for m in z.MASSES.values()]
    requests += [(s,t,m*m,m*m,0,1) for m in (300.,700.)]
    Path('/tmp/zee-zgamma-looptools.log').write_bytes(b'')
    native,receipt=audit.native(probe,requests)
    native_log=Path('/tmp/zee-zgamma-looptools.log').read_bytes()
    (HERE/'ZGAMMA_H125_LOOPTOOLS_LOG.txt.gz').write_bytes(gzip.compress(native_log,mtime=0))
    receipt['runtime_log_sha256']=sha('/tmp/zee-zgamma-looptools.log')
    comparisons={}
    for (f,m),row in zip(z.MASSES.items(),native):
        a,b=z.integrals(mh,mz,m)
        comparisons[f]=dict(C0=row['cr'],K=row['k'],
            C0_relative_residual=abs(row['cr']/(-b/(m*m))-1),
            K_relative_residual=abs(row['k']/(a/(4*m*m))-1))
        assert comparisons[f]['C0_relative_residual']<1e-10
        assert comparisons[f]['K_relative_residual']<1e-10
    w=native[len(z.MASSES)-1];a=mw*mw
    # Hue18 Eq20 uses the opposite tensor sign to Fontes C.1.
    w_direct=-a*cw/sw*(2*(8+(2+s/a)*(2-t/a))*w['k']+4*(4-t/a)*w['cr'])
    assert abs(w_direct/sm['even_terms']['W']-1)<2e-12
    fermion_direct={}
    for (f,m),row in zip(z.MASSES.items(),native):
        if f=='W':continue
        q,t3,nc=z.quantum_numbers(f);gv=t3/2-q*sw*sw
        # Fontes C.3 native PV; C.4 at native b=-Im(k) and Im(k)=1.
        even=-nc*4*gv*q*m*m/(sw*cw)*(2*t/delta**2*row['db']+((4*m*m-s+t)*row['cr']+2)/delta)
        odd=-nc*4*gv*q*m*m/(sw*cw)*row['cr']
        ae=z.amplitude(mh,0,{ff:(1+1j if ff==f else 0) for ff in kappas})
        fermion_direct[f]=dict(even=even,odd_unit_native_imaginary_k=odd,
            even_residual=abs(even-ae['even']),odd_residual=abs(odd-ae['odd']))
        assert abs(even-ae['even'])<1e-11
        assert abs(odd-ae['odd'])<1e-11
    controls=[]
    for index,m in enumerate((300.,700.)):
        zz=e/(sw*cw)*(.5-sw*sw)
        for j,g in enumerate((100.,-100.)):
            calc=z.amplitude(mh,1,six,[m],[[g]],[[zz]])
            native_scalar=2*v/(e*delta)*g*zz*(t/delta*native[-2+index]['db']+1+2*m*m*native[-2+index]['cr'])
            reference_scalar=-g*v/(2*m*m)*reference['scalar_functions'][index]
            expected=reference['one_scalar_widths_GeV'][2*index+j]
            controls.append(dict(mass_GeV=m,G_GeV=g,X=calc['scalar_terms']['H1H1'],
                native_Fontes_C10_X=native_scalar,HEPfit_mapped_X=reference_scalar,
                calculated_width_GeV=calc['width_GeV'],reference_width_GeV=expected,
                width_relative_residual=calc['width_GeV']/expected-1))
            assert abs(calc['scalar_terms']['H1H1']-native_scalar)<1e-11
            assert abs(calc['scalar_terms']['H1H1']-reference_scalar)<1e-10
            assert abs(controls[-1]['width_relative_residual'])<2e-12
    cases=[]
    old=json.loads((HERE/'ZGAMMA_SOURCE_EVIDENCE.json').read_text())
    for name in ('D7','F13'):
        case=z.benchmark(name);fine=z.benchmark(name,120)
        previous=next(x for x in old['cases'] if x['name']==name)
        corrected=previous['scalar_X_diagnostics']['photon_mass_correction_candidate']['scalar_X_sum']
        xscalar=sum(case['full']['scalar_terms'].values())
        assert abs(xscalar-corrected)<1e-11
        case['scalar_routing_preserved_absolute_residual']=abs(xscalar-corrected)
        case['quadrature_width_relative_residual_80_to_120']=abs(case['full']['width_GeV']/fine['full']['width_GeV']-1)
        assert case['quadrature_width_relative_residual_80_to_120']<1e-12
        terms=case['full']['even_terms'];fermions=sum(terms[f] for f in kappas)
        case['component_sums']=dict(W=terms['W'],fermions=fermions,scalars=xscalar,
            mixed_scalars=terms['H1H2']+terms['H2H1'],odd=case['full']['odd'])
        case['even_pair_interference_norm']={
            'W_fermions':2*(terms['W']*fermions.conjugate()).real,
            'W_scalars':2*(terms['W']*xscalar.conjugate()).real,
            'fermions_scalars':2*(fermions*xscalar.conjugate()).real}
        # Conservative numerical allowance, covers quadrature convergence and
        # native/form-factor residuals by orders of magnitude; not theory sigma.
        case['numerical_relative_error_allowance']=1e-10
        cases.append(case)
    pins=[HERE/p for p in ('zgamma.py','zgamma_reference.py','run_zgamma_h125.py',
        'test_zgamma.py','ZGAMMA_SOURCE_EVIDENCE.json','ZGAMMA_SOURCE_MANIFEST.json',
        'NEUTRAL_WIDTH_EVIDENCE.json','SOURCE_MANIFEST.json','diphoton.py',
        'sushi_bridge.py','zgamma_source_audit.py','zgamma_pv_probe.cpp','build_zgamma_probe.sh',
        'ZGAMMA_H125_LOOPTOOLS_LOG.txt.gz')]
    pins += [ROOT/p for p in ('module1/scalar_constraints.py','module2/interface.py',
        'module3/core.py','module4/couplings.py','module7/d4_inputs.py',
        'module13/higgstools.py','module1/d10_benchmarks.json',
        'validation/module12/d12_benchmarks.json','research/full_constraints/HIGGS_VALIDATION.json')]
    return audit.serial(dict(status='H125_ZGAMMA_LEADING_ONE_LOOP_VALIDATED',
        scope='h125 only, original D7/F13 and analytic SM/one-scalar controls',
        inputs=dict(mh_GeV=mh,mw_GeV=mw,mz_GeV=mz,v_GeV=v,alpha_tree=alpha,masses_GeV=z.MASSES),
        SM_all_nine=sm,SM_matched_six=matched,independent_reference=reference,
        SM_reference_relative_residual=sm_residual,
        SM_extra_u_d_e_width_relative_shift=sm['width_GeV']/matched['width_GeV']-1,
        W_Hue20_native_X=w_direct,W_Hue20_relative_residual=abs(w_direct/sm['even_terms']['W']-1),
        native_equal_mass_comparisons=comparisons,native_fermion_tensor_comparisons=fermion_direct,
        native_receipt=receipt,one_scalar_controls=controls,cases=cases,
        source_pins={str(p.relative_to(ROOT)):sha(p) for p in pins},
        paper_sources=json.loads((HERE/'ZGAMMA_SOURCE_MANIFEST.json').read_text())['papers'],
        numerical_relative_error_allowance=1e-10,theory_sigma=None,
        uncertainty='Leading one-loop coefficient only; higher-order QCD/EW/scalar and input covariance not quantified. Alpha(0) comparison is a scheme diagnostic, not a sigma.',
        H_A_extension_executed=False,scans_executed=0,physical_higgs='UNKNOWN',
        global_acceptance=None,exclusion=None,B='B_FULL_RATE_BLOCKED',
        LFV='LFV_FULL_COVERAGE_BLOCKED',Higgs='HIGGS_FULL_COVERAGE_BLOCKED',vacuum='UNKNOWN'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--probe',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=HERE/'ZGAMMA_H125_EVIDENCE.json')
    args=parser.parse_args();dump(args.out,run(args.probe))

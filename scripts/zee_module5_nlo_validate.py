#!/usr/bin/env python3
"""Execute Gate C2 native matching and independent published BMU comparisons.

Requires an existing unmodified v1.0.3 checkout/build. Writes only this
checkout's ignored evidence directory and the requested audit JSON.
"""
import argparse
import json
import math
from pathlib import Path
import re
import shlex
import subprocess
import sys

from zee_module5_hyperiso_runtime import verify_checkout, verify_build, sha, PIN
from zee_module5_hyperiso_bridge import spectrum
from zee_module5_bmu_nlo import matching
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from module5.bsgamma_lo import compute
from module5.bsgamma_matching_accuracy import evaluate, COEFFICIENT_CONVENTION, MATCHING_BASIS
from module5.hyperiso_patch_contract import make_contract

ROOT=Path(__file__).resolve().parents[1]

def run(cmd,cwd):
    r=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=240)
    if r.returncode or r.stderr.strip():
        raise ValueError(f'Execution failed: {cmd}: {r.stderr[-1500:]}')
    return r.stdout

def save(p,obj):
    p.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')

def main():
    if not __debug__:
        raise RuntimeError('Run without -O: all numerical acceptance checks must execute')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=ROOT/'validation/module5/accuracy_2026.json')
    a=ap.parse_args();up=a.upstream.resolve();binary=a.binary.resolve()
    verify_checkout(up);build_info=verify_build(up,binary)
    assert run([str(binary),'--version'],up).strip()=='1.0.3'
    dest=ROOT/'validation/module5/local';dest.mkdir(parents=True,exist_ok=True)
    local=dest/'c2';local.mkdir(exist_ok=True)
    build=Path(build_info['build_directory'])
    source=ROOT/'scripts/zee_module5_nlo_probe.cpp';obj=local/'probe.o';exe=local/'nlo_probe'
    cli=next(c for c in json.loads((build/'compile_commands.json').read_text()) if c['file'].endswith('/UserInterface/main.cpp'))
    cmd=shlex.split(cli['command']);cmd[cmd.index('-o')+1]=str(obj);cmd[cmd.index('-c')+1]=str(source)
    run(cmd,build)
    link=shlex.split(run(['ninja','-C',str(build),'-t','commands','hyperiso-ui'],up).splitlines()[-1])
    link=link[link.index('&&')+1:link.index('&&',link.index('&&')+1)]
    link[link.index('-o')+1]=str(exe)
    link=[str(obj) if x.endswith('/hyperiso-ui.dir/main.cpp.o') else x for x in link]
    run(link,build)
    lha=up/'reproducibility/inputs/thdm_reference.lha';base=lha.read_text()
    c1=json.loads((ROOT/'validation/module5/linear_2026.json').read_text())
    for name,url in [('bmu.html','https://arxiv.org/html/hep-ph/9904413v1'),('bg.html','https://arxiv.org/html/hep-ph/9802391v1'),('misiak.html','https://arxiv.org/html/2608.29863v1')]:
        expected=next(s['download_sha256'] for s in c1['sources'] if s['url']==url)
        assert sha(local/name)==expected, 'Pinned paper differs from C1 source bytes'
    assert sha(lha)==c1['matching_mass_provenance']['lha_sha256']
    phys=c1['reference_run']['input'];tanb=math.tan(phys['beta_rad'])
    # Reconstruct exact C1 bytes, then authenticate against its recorded hash.
    inp=dest/'2026_reference_input.json';save(inp,phys)
    assert sha(inp)==c1['reference_run']['input_sha256'], 'C1 input byte reconstruction differs'
    rows=[];logs=[];artifacts={}
    def artifact(p):artifacts[str(p)]=sha(p);return sha(p)
    points=[(550.,tanb,False),(900.,tanb,False)]
    points += [(m,t,f) for m,t in ((300.,.5),(550.,2.),(900.,50.),(2000.,5.3),(100000.,5.3)) for f in (False,True)]
    for index,(mass,tb,flip) in enumerate(points):
        lp=local/f'state_{index}.lha';lp.write_text(spectrum(base,mass,tb,flip))
        cmd=[str(exe),'--model','THDM','--lha',str(lp),'--spectrum','true']
        raw=run(cmd,up);log=local/f'state_{index}.log';log.write_text(raw);logs.append(raw)
        mt=float(re.search(r'C2 mt (\S+)',raw)[1]);alpha=float(re.search(r'C2 alpha_s (\S+)',raw)[1])
        assert abs(mt-phys['mt_MSbar_GeV'])<2e-11
        assert 0<alpha<1
        coeff={};expansion=[]
        for name,vals in re.findall(r'C2 (C\d) ([^\n]+)',raw):
            z=[complex(float(r),float(i)) for r,i in re.findall(r'\(([^,]+),([^\)]+)\)',vals)]
            assert len(z)==4 and all(v.imag==0 and math.isfinite(v.real) for v in z)
            lo,nlo,flo,fnlo=[v.real for v in z]
            residual=abs(fnlo-flo-alpha/(4*math.pi)*nlo)
            assert residual<3e-15 and abs(flo-lo)<3e-15
            coeff[name]={'LO':lo,'NLO_raw':nlo,'full_LO':flo,'full_NLO':fnlo}
            expansion.append(residual)
        assert set(coeff)=={f'C{i}' for i in range(1,9)}
        assert all(coeff[f'C{i}']['LO']==0 for i in range(1,7))
        assert all(coeff[f'C{i}']['NLO_raw']==0 for i in (1,2,3,5,6))
        assert coeff['C4']['NLO_raw']!=0
        state={'mH_GeV':mass,'C1_to_C6_LO_zero':True,'C4_NLO_raw':coeff['C4']['NLO_raw']}
        for c in ('C7','C8'):
            state[c+'_LO']=coeff[c]['LO'];state[c+'_NLO_raw']=coeff[c]['NLO_raw']
        # Native THDM dipoles include effective-basis -4/9 EH,-1/6 EH.
        # BG 9802391v1 Sec.3 and App.A4; BMU ordinary P4,P7,P8.
        # Preserve raw public API values in coeff; convert witness explicitly.
        state['C7_NLO_raw']+=4/9*state['C4_NLO_raw']
        state['C8_NLO_raw']+=1/6*state['C4_NLO_raw']
        expected=matching(mass,tb,mt,flip=flip)
        residuals={k:state[k]-v for k,v in expected.items()}
        # Numerical comparison tolerances, never a physics error estimate.
        assert all(math.isclose(state[k],v,rel_tol=3e-10,abs_tol=3e-13) for k,v in expected.items()), (index,state,expected,residuals)
        frozen_residual={}
        if not flip:
            frozen=compute(mass,mass,math.atan(tb),0.,mt,160.)
            frozen_residual={c:state[c+'_LO']-frozen[f'delta_{c}_LO_at_matching_scale'] for c in ('C7','C8')}
            assert max(map(abs,frozen_residual.values()))<2e-14
        rows.append({'mass':mass,'tanbeta':tb,'flip_down_Yukawa':flip,'mt':mt,'alpha_s':alpha,
                     'native':coeff,'state':state,'BMU':expected,'BMU_residuals':residuals,
                     'frozen_LO_residuals':frozen_residual,'expansion_max_residual':max(expansion),
                     'command':cmd,'lha_sha256':artifact(lp),'log_sha256':artifact(log)})
    combined=local/'runtime.log';combined.write_text('\n'.join(logs))
    witness={'schema_version':'1.0.0','upstream_commit':PIN,'source_status':'EXECUTED_HYPERISO_UNMODIFIED',
             'normalization':COEFFICIENT_CONVENTION,'matching_basis':MATCHING_BASIS,'binary_sha256':artifact(exe),'source_LHA_sha256':artifact(lha),
             'runtime_log_sha256':artifact(combined),'qmatch_GeV':160.,'mt_MSbar_at_qmatch_GeV':rows[0]['mt'],
             'tan_beta':tanb,'alpha_s_at_qmatch':rows[0]['alpha_s'],
             'unweighted_native_states':[r['state'] for r in rows[:2]]}
    wp=dest/'c2_native_nlo_witness.json';save(wp,witness)
    cp=dest/'c2_contract.json'
    run([sys.executable,'-m','module5.hyperiso_patch_contract','--input',str(inp),'--output',str(cp)],ROOT)
    impact_path=dest/'c2_nlo_impact.json'
    run([sys.executable,'-m','module5.bsgamma_matching_accuracy','--contract',str(cp),'--witness',str(wp),'--output',str(impact_path)],ROOT)
    impact=json.loads(impact_path.read_text())
    # Exercise actual mass-dependent native coefficients through mixing controls.
    controls={}
    def result(p,states):return evaluate(make_contract(p),{**witness,'unweighted_native_states':states})['matching_coefficients']
    states=witness['unweighted_native_states'];reference=result(phys,states)
    swap={**phys,'mH1_GeV':900.,'mH2_GeV':550.,'gamma_rad':math.pi/2-phys['gamma_rad']}
    swapped=result(swap,states[::-1])
    controls['interchange_max_residual']=max(abs(v-swapped[order][k]) for order,d in reference.items() for k,v in d.items())
    assert controls['interchange_max_residual']<2e-15
    for gamma,idx in ((0.,0),(math.pi/2,1)):
        r=result({**phys,'gamma_rad':gamma},states)
        for c in ('C7','C8'):
            assert abs(r['LO_plus_NLO_dipole_only']['Delta'+c]-(rows[idx]['native'][c]['full_NLO']+witness['alpha_s_at_qmatch']/(4*math.pi)*(4/9 if c=='C7' else 1/6)*rows[idx]['state']['C4_NLO_raw']))<2e-15
    equal={**phys,'mH2_GeV':550.}
    eq=result(equal,[states[0],states[0]])
    eq0=result({**equal,'gamma_rad':0.},[states[0],states[0]])
    controls['equal_mass_max_residual']=max(abs(v-eq0[o][k]) for o,d in eq.items() for k,v in d.items())
    assert controls['equal_mass_max_residual']<2e-15
    controls.update(gamma_endpoints='PASS',equal_masses='PASS')
    for f in (False,True):
        heavy=next(r for r in rows if r['mass']==100000 and r['flip_down_Yukawa']==f)
        assert max(abs(heavy['native'][c]['full_NLO']) for c in ('C7','C8'))<1e-4
    beta2=next(r for r in rows if r['mass']==550 and r['tanbeta']==2 and not r['flip_down_Yukawa'])
    for c in ('C7','C8'):
        assert abs(beta2['state'][c+'_LO'])>abs(rows[0]['state'][c+'_LO'])
        assert beta2['state'][c+'_NLO_raw']!=rows[0]['state'][c+'_NLO_raw']
    assert any(r['state']['C7_NLO_raw']>0 for r in rows) and any(r['state']['C7_NLO_raw']<0 for r in rows)
    controls.update(heavy_decoupling='PASS',tanbeta_variation='PASS',positive_negative_Yukawa_controls='PASS',common_scale_GeV=160)
    # Deliberate wrong-basis, extra-alpha_s, and sign falsifiers.
    negative=[]
    for label,alter in (
        ('effective_basis_label',lambda w:w.update(matching_basis='EFFECTIVE_DIPOLES')),
        ('wrong_scale',lambda w:w.update(qmatch_GeV=81.)),
        ('wrong_top_mass',lambda w:w.update(mt_MSbar_at_qmatch_GeV=163.)),
        ('reversed_LO_sign',lambda w:w['unweighted_native_states'][0].update(C7_LO=-states[0]['C7_LO']))):
        w=json.loads(json.dumps(witness));alter(w)
        try:evaluate(make_contract(phys),w)
        except ValueError:negative.append(label)
        else:raise ValueError('Negative control accepted: '+label)
    for r in rows:
        alpha_factor=r['alpha_s']/(4*math.pi)
        for c in ('C7','C8'):
            assert not math.isclose(alpha_factor*r['state'][c+'_NLO_raw'],r['BMU'][c+'_NLO_raw'],rel_tol=1e-3,abs_tol=1e-12)
    controls['extra_alpha_s_factor_detected']='PASS'
    # Numerical falsifiers against independent BMU: passing schema alone is insufficient.
    for r in rows:
        c4=r['state']['C4_NLO_raw']
        for c,factor in (('C7',4/9),('C8',1/6)):
            raw=r['native'][c]['NLO_raw'];ordinary=r['BMU'][c+'_NLO_raw']
            assert math.isclose(ordinary-raw,factor*c4,rel_tol=2e-7,abs_tol=1e-13)
    controls['negative_rejections']=negative
    controls['missing_basis_conversion_detected']='PASS_WITH_NONZERO_C4'
    tests=[]
    for pattern in ('test_module5_matching_accuracy.py','test_module5_bsgamma_2026_linear.py','test_module5_two_state_patch_contract.py'):
        cmd=[sys.executable,'-m','unittest','discover','-s','tests','-p',pattern,'-v']
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);log=local/(pattern+'.log');log.write_text(r.stdout+r.stderr)
        assert r.returncode==0
        tests.append({'command':cmd,'returncode':r.returncode,'tests_run':int(re.search(r'Ran (\d+) tests',r.stderr)[1]),'log_sha256':artifact(log)})
    src=up/'Hyperiso/Hyperiso/core/src'
    for p in (source,Path(__file__),ROOT/'scripts/zee_module5_bmu_nlo.py',ROOT/'module5/bsgamma_matching_accuracy.py',inp,wp,cp,impact_path,
              src/'PhysicalModel/domain/WCoef/BSM/BWilsonTHDM.cpp',src/'Math/domain/special/special_SM.cpp',
              src/'PhysicalModel/domain/Helper/BSM/THDMParametersHelper.cpp',src/'PhysicalModel/domain/Helper/WilsonParametersHelper.cpp',
              src/'Core/infrastructure/QCDHelper.cpp',src/'PhysicalModel/adapters/WilsonInterface.cpp',local/'bmu.html',local/'misiak.html',local/'bg.html',local/'companion.html',src/'PhysicalModel/domain/WGroup/BWilsonGroup.cpp'):
        artifact(p)
    verify_checkout(up)
    # Authenticate actual local bytes, not just a syntactically valid SHA label.
    assert all(sha(Path(p))==h for p,h in artifacts.items())
    payload={'schema_version':'1.0.0','sources':[{'url':url,'sha256':sha(local/name)} for name,url in [('bmu.html','https://arxiv.org/html/hep-ph/9904413v1'),('bg.html','https://arxiv.org/html/hep-ph/9802391v1'),('misiak.html','https://arxiv.org/html/2608.29863v1'),('companion.html','https://arxiv.org/html/2608.29864v1')]],'required_ancestor':'429a9d6de26a072dc0290db6ca1d050a362f5ecf',
             'gates':{'native':'C2_NATIVE_NLO_MATCHING_PASS','independent':'C2_INDEPENDENT_NLO_PASS',
                      'curvature':'QUADRATIC_VALIDITY_UNKNOWN','2026_LINEARIZED_FLAVOR_FILTER_READY':False},
             'upstream':{'commit':PIN,'version':'1.0.3','tracked_clean':True,**build_info},
             'tests':tests,'tests_total':sum(t['tests_run'] for t in tests),
             'basis_conversion':{'native':'effective dipoles as BG 9802391v1 Sec.3/App.A4','witness':'ordinary BMU P4,P7,P8','C7_ordinary_1':'getM(C7,NLO)+4/9*getM(C4,NLO)','C8_ordinary_1':'getM(C8,NLO)+1/6*getM(C4,NLO)'},
             'witness':witness,'impact':impact,'rows':rows,'controls':controls,'verified_artifacts_sha256':artifacts,
             'max_BMU_absolute_residual':max(abs(v) for r in rows for v in r['BMU_residuals'].values()),
             'max_expansion_absolute_residual':max(r['expansion_max_residual'] for r in rows),
             'C1_LO_max_absolute_residual':max(abs(impact['matching_coefficients']['LO']['Delta'+c]-c1['reference_run']['coefficient_components'][c]['real']) for c in ('C7','C8')),
             'sensitivity_status':'NLO_MATCHING_DIPOLE_ONLY_SENSITIVITY','physical_BR':None,'exclusion':None,
             'published_values_1e_minus4':{'SM_central':3.54,'SM_sigma':.14,'experiment_central':3.49,'experiment_sigma':.19},
             'blockers':['No numerical 160-GeV quadratic response implemented/validated from the inspected 2026 sources; the companion gives a low-scale bilinear rate framework, not an authenticated high-scale response matrix.',
                         'C4 NLO running/matrix elements and other operators not propagated to rate.',
                         'NP uncertainty, validity domain, covariance and statistical prescription unvalidated.']}
    save(a.output,payload)
    print(json.dumps({'gates':payload['gates'],'impact':impact['matching_coefficients'],'max_BMU_residual':payload['max_BMU_absolute_residual']}))

if __name__=='__main__':main()

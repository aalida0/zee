"""Bounded new D16 evidence: 2 mixed fixtures + 4 real inverse witnesses.

No D15 rerun, 39-channel replay, scan, source regeneration or global acceptance.
Detailed coefficients and actual command logs stay under ignored local/.
"""
import argparse
import json
from pathlib import Path
import platform
import resource
import subprocess
import time
import numpy as np
import scipy
import sympy
from module1.scalar_constraints import reconstruct,unitarity,ewpo
from module1.bfb import certificate
from module2.interface import canonical_hash
from .external_2hdm import pack,sha,load_reference
from .zee_mixed_hz import scalar_current_tensor,mixed_hz,mixed_hz_kernel,mixed_hz_kernel_bounded
from .test_zee_mixed_hz import fixture
from .external_2hdm_hw_override import ML,REFERENCE
from .zee_two_loop import witness,evaluate
from .w_outer_reduction import reproduce as w_reproduce

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def write(path,data):
    path.write_text(json.dumps(pack(data),indent=2,sort_keys=True,allow_nan=False)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=HERE/'two_loop_evidence.json')
    args=ap.parse_args();start=time.perf_counter();local=HERE/'local'
    old=json.loads((HERE/'hw_generic_evidence.json').read_text())
    load_reference(REFERENCE) # Pin + all five original byte comparisons only.
    for name,expected in old['frozen_hashes'].items():
        if sha(ROOT/name)!=expected:
            raise ValueError('Protected source changed: '+name)
    native=json.loads((HERE/'mixed_hz_sources.json').read_text())
    for name,expected in native['sources_sha256'].items():
        if sha(ROOT/name)!=expected:
            raise ValueError('Mixed source changed: '+name)
    fixtures=[]
    for n in (0,1):
        p,D=fixture(n);lag,inh,closure=reconstruct(p)
        channels={}
        for i,j in ((1,0),(2,0),(2,1)):
            result=mixed_hz(D,p,ML,80.379,91.1876,i,j)
            off=np.zeros(2,complex)
            for neutral,row in result['rows'].items():
                terms=row['terms']
                # Preserve exact per-row normalization even for cancelling A.
                sw2=1-(80.379/91.1876)**2;sw,cw=np.sqrt(sw2),80.379/91.1876
                al=(2*80.379/p['v'])**2*sw2/(4*np.pi)
                M={'h':p['mh1'],'H':p['mh2'],'A':p['ma']}[neutral]
                pref=-al*(-.5+2*sw2)/(sw*cw)/(64*np.pi**3*ML[i]*M*M)
                off+=pref*row['external_LR']*sum(t['weighted_kernel'] for t in terms if t['a']!=t['b'])
            channels[f'{i}_{j}']=dict(C_LR=result['C_LR'],offdiagonal_C_LR=off,
                quadrature_error=result['quadrature_error'],G0_identity_abs_residual=result['G0_identity_abs_residual'])
        # Off-shell longitudinal falsifier and real-photon projected identity.
        ma2,mb2=(p['mH1']/300)**2,(p['mH2']/300)**2
        pp=np.array([.2,.1,-.3,.4]);k=np.array([.4,-.5,.7,1.2])
        offshell=scalar_current_tensor(pp,k,ma2,mb2)
        on=np.array([.2j,0.,0.,.2]);eps=np.array([0.,1.,0.,0.]);J=np.array([.3+.1j,.4-.2j,-.1j,.7+.5j])
        physical=scalar_current_tensor(on,k,ma2,mb2)
        exchange={}
        for xi in (.5,1.,3.,7.):
            prop=(np.eye(4)-(1-xi)*np.outer(k,k)/(k@k+xi*.8))/(k@k+.8)
            exchange[str(xi)]=np.array([eps@physical['tensor']@prop@J,
                                       eps@physical['tensor']@prop@J.conjugate()])
        fixtures.append(dict(physical=p,D=D,input_sha256=canonical_hash(pack(dict(p=p,D=D))),
            channels=channels,source_potential=lag,closure=closure,
            scalar_checks=dict(BFB_sufficient='PASS' if certificate(lag) else 'UNKNOWN',
                unitarity=unitarity(lag,inh)['assessment'],EWPO='NOT_EVALUATED',vacuum='NOT_EVALUATED'),
            tensor_checks=dict(EM_residual=np.linalg.norm(pp@offshell['tensor']),
                Z_longitudinal_norm=np.linalg.norm(offshell['tensor']@k),
                ST_residual=np.linalg.norm(offshell['tensor']@k+(mb2-ma2)*offshell['goldstone_current']),
                projected_G0_norm=abs(eps@physical['goldstone_current']),
                xi_complex_current_exchange=exchange,
                xi_scope='Real-photon current tensor contraction, not independently complete W or full dipole quadrature')))
    master=[]
    for a,b,y in ((2.,7.,.4),(.1,3.,1.),(.9,.9,.53)):
        master.append(dict(ratios=[a,b,y],adaptive=mixed_hz_kernel(a,b,y),
            bounded480=mixed_hz_kernel_bounded(a,b,y,480)))
    samples=[]
    for spectrum in (0,1):
        for ordering in ('NO','IO'):
            data=witness(ordering,spectrum);result=evaluate(data)
            tag=f'zee_{ordering}_{spectrum}'
            path=local/(tag+'.json');write(path,result)
            inp=local/(tag+'_input.json');write(inp,data)
            scalar=data['module3_input']['module2_input']['scalar']['record']
            lag,inh,_=reconstruct(scalar['physical'])
            ew=ewpo(scalar['physical'],scalar['electroweak'],scalar['ew_fit'])
            samples.append(dict(ordering=ordering,spectrum=spectrum,
                input_sha256=canonical_hash(data),detailed_input_file_sha256=sha(inp),
                details=str(path.relative_to(ROOT)),details_sha256=sha(path),
                neutrino_gates=data['module2_output']['gates'],
                scalar_gates=dict(BFB_sufficient='PASS' if certificate(lag) else 'UNKNOWN',
                    tree_unitarity=unitarity(lag,inh)['assessment'],EWPO=ew['assessment'],vacuum='NOT_EVALUATED'),
                channels={k:{key:v[key] for key in ('class_totals','included_only_C_LR',
                    'included_only_two_loop_C_LR','included_only_BR','included_only_quadrature_error',
                    'one_two_loop_interference_norm2','full_C_LR','full_BR')} for k,v in result['channels'].items()},
                F_current_probe=result['F_current_probe']))
    w=w_reproduce();write(local/'w_outer_reduction.json',w)
    logs={str(f.relative_to(ROOT)):sha(f) for f in
        [local/'mixed_hz_extract.log',local/'mixed_hz_source_check.log',local/'new_two_loop_tests.log']}
    evidence=dict(status='BLOCKED_ZEE_TWO_LOOP_COMPLETION',acceptance=False,
        scope='New physical scalar Z radiative-current and common neutral fermion Z classes; no full Zee/W/F² two-loop amplitude',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sympy=sympy.__version__),
        protected_sources_sha256=old['frozen_hashes'],author_pin=old['author_pin'],
        author_files_sha256={name:sha(REFERENCE/name) for name in old['author_files']},
        previous_reference_evidence_sha256=sha(HERE/'hw_generic_evidence.json'),
        new_native_source_sha256=sha(HERE/'mixed_hz_sources.json'),
        code_sha256={f.name:sha(f) for f in sorted(HERE.glob('*.py'))},
        master_checks=master,mixed_fixtures=fixtures,inverse_witnesses=samples,
        W_outer_attempt=dict(status=w['status'],symbolic_residual=w['reduction']['symbolic_residual'],
            details_sha256=sha(local/'w_outer_reduction.json'),
            missing=w['reduction']['remaining']),
        acceptance_matrix=dict(new_native_vertices='64_CHECKS_PASS',
            scalar_current_EM_Ward='PASS',off_shell_Z_G0_current_identity='PASS',
            mixed_HZ_on_shell_current_xi='SCOPED_PASS',
            mixed_HZ_full_reducible_assignment='OPEN',
            neutral_fermion_Z='COMMON_CLASS_PASS',quadratic_FD_massless='ODD_F_SPURION_ZERO',
            F_dagger_F='NONZERO_SUBGRAPH_FULL_SUM_MISSING',W_complete='MISSING',
            all_required_complex_Wilsons='UNAVAILABLE',D14_overlay='NOT_PERMITTED_BEFORE_COMPLETION'),
        command_logs_sha256=logs,focused_tests=14,
        elapsed_seconds=time.perf_counter()-start,peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    write(args.output,evidence)
    print(evidence['status'],len(samples),'inverse witnesses,',len(fixtures),'mixed fixtures;',
          round(evidence['elapsed_seconds'],3),'s')


if __name__=='__main__':
    main()

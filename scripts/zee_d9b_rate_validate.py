#!/usr/bin/env python3
"""Rebuild the pinned local investigative fork and execute bounded D9B gates.
No downloads, D9A writes, scan, rescaling or accepted NNLO prediction.
"""
import argparse
import hashlib
import json
import math
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from zee_module5_bmu_nlo import matching
ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT/'validation/module5/local/d9b'
UP = LOCAL/'SuperIso_v5.0_D9B_patched'
PATCH = ROOT/'module5/patches/d9b_superiso_v5.0.patch'
OUTPUT = ROOT/'validation/module5/d9b_superiso_repair.json'
PIN = '7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f'
EXE = LOCAL/'rate_probe'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd, log, cwd=ROOT):
    r = subprocess.run(list(map(str,cmd)),cwd=cwd,capture_output=True,text=True,timeout=300)
    (LOCAL/log).write_text(r.stdout+r.stderr)
    if r.returncode:
        raise RuntimeError(f'{cmd[0]} returned {r.returncode}: {LOCAL/log}')
    return r.stdout


def parse(raw):
    v = dict((k,float(x)) for k,x in (line.split() for line in raw.splitlines()))
    assert all(math.isfinite(x) for x in v.values())
    return v


def execute(mass,tb,flip,base,label):
    c = matching(mass,tb,base['mt_match'],mu=160.,flip=flip)
    cmd = [EXE,mass,tb,int(flip),*(c[k] for k in ('C7_LO','C8_LO','C4_NLO_raw','C7_NLO_raw','C8_NLO_raw'))]
    out = parse(run(cmd,label+'.log'))
    residual = {order:{str(i):out[f'native_{order}_C{i}']-out[f'SM_{order}_C{i}']-
                      ({7:c['C7_LO'],8:c['C8_LO']} if order=='LO' else
                       {4:c['C4_NLO_raw'],7:c['C7_NLO_raw'],8:c['C8_NLO_raw']}).get(i,0.)
                      for i in range(1,9)} for order in ('LO','NLO')}
    delta = out['injected_BR']-out['native_BR']
    return dict(mass_GeV=mass,tanbeta=tb,opposite_ld=flip,independent_BMU_ordinary=c,
                full_Q1_Q8_matching_residual=residual,BR_absolute_residual=delta,
                BR_relative_residual=delta/out['native_BR'],
                metadata_residual=out['metadata_BR']-out['injected_BR'],
                command=list(map(str,cmd)),output=out,stdout_sha256=sha(LOCAL/(label+'.log')))


def coherent(m1,m2,gamma,tb,flip,mu,base,label):
    weights = (math.cos(gamma)**2,math.sin(gamma)**2)
    parts = [matching(m,tb,base['mt_match'],mu=mu,flip=flip) for m in (m1,m2)]
    total = {k:sum(w*c[k] for w,c in zip(weights,parts)) for k in parts[0]}
    cmd = [EXE,m1,tb,int(flip),*(total[k] for k in ('C7_LO','C8_LO','C4_NLO_raw','C7_NLO_raw','C8_NLO_raw')),mu]
    out = parse(run(cmd,label+'.log'))
    return dict(m1_GeV=m1,m2_GeV=m2,gamma_rad=gamma,tanbeta=tb,opposite_ld=flip,mu0_GeV=mu,
                weights=weights,ordinary_BMU_parts=parts,ordinary_BMU_total=total,
                BR=out['injected_BR'],command=list(map(str,cmd)),output=out,
                stdout_sha256=sha(LOCAL/(label+'.log')))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skip-build',action='store_true')
    ap.add_argument('--tests',action='store_true')
    args = ap.parse_args()
    LOCAL.mkdir(parents=True,exist_ok=True)
    archive = LOCAL/'superiso_v5.0.tgz'
    if not archive.exists():
        shutil.copyfile(ROOT/'validation/module5/local/d9/superiso_v5.0.tgz',archive)
    assert sha(archive)==PIN
    original = {}
    with tarfile.open(archive) as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        original = {m.name:hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in members}
        if not UP.exists():
            tar.extractall(LOCAL, members=members)
            (LOCAL/'SuperIso_v5.0').rename(UP)
            run(['patch','-p1','--batch','-i',PATCH],'patch.log',UP)
    # Gate 0 always precedes patched execution and never rewrites D9A evidence.
    d9 = json.loads((ROOT/'validation/module5/d9_bsgamma_rate.json').read_text())
    old = ROOT/'validation/module5/local/d9/SuperIso_v5.0'
    for name,digest in original.items():
        assert sha(old/Path(name).relative_to('SuperIso_v5.0'))==digest, name
    assert sha(old/'src/libsuperiso.a')==d9['backend']['library_sha256']
    witness = LOCAL/'d9a_witness'
    run(['gcc','-O2','-I',old/'src',ROOT/'scripts/zee_d9_rate_probe.c',
         old/'src/libsuperiso.a','-lm','-o',witness],'gate0_build.log')
    witness_out = parse(run([witness,*d9['rows'][1]['command'][1:]],'gate0_witness.log'))
    assert witness_out==d9['rows'][1]['output'], 'D9A reproduction differs; investigate provenance'
    run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_module5_d9_*.py','-v'],'gate0_tests.log')
    gate0_count = int(re.search(r'Ran (\d+) tests', (LOCAL/'gate0_tests.log').read_text())[1])
    # Replay the complete patch and compare EVERY distributed source byte.
    with tempfile.TemporaryDirectory(dir=LOCAL) as tmp:
        with tarfile.open(archive) as tar:
            tar.extractall(tmp)
        replay = Path(tmp)/'SuperIso_v5.0'
        run(['patch','-p1','--batch','-i',PATCH],'patch_replay.log',replay)
        for name in original:
            relative = Path(name).relative_to('SuperIso_v5.0')
            assert (replay/relative).read_bytes()==(UP/relative).read_bytes(), name
    run(['patch','-p1','--reverse','--dry-run','--batch','-i',PATCH],'patch_reverse_check.log',UP)
    if not args.skip_build:
        run(['make','-B'],'build.log',UP)
    compile_cmd = ['gcc','-O2','-I',UP/'src',ROOT/'scripts/zee_d9b_rate_probe.c',UP/'src/libsuperiso.a','-lm','-o',EXE]
    run(compile_cmd,'client_build.log')
    baseline = parse(run([EXE],'baseline.log'))
    points = [(m,t,False) for t in (5.3,2.) for m in (550.,900.,2000.,10000.,100000.)]
    points += [(550.,5.3,True)]
    rows = [execute(m,t,f,baseline,f'point_{i}') for i,(m,t,f) in enumerate(points)]
    max_coeff = max(abs(v) for r in rows for a in r['full_Q1_Q8_matching_residual'].values() for v in a.values())
    max_rate = max(abs(r['BR_absolute_residual']) for r in rows)
    basis_pass = max_coeff<5e-11
    flow_pass = all(r['metadata_residual']==0. and r['output']['reject_scheme']==1. and
                    r['output']['reject_unsupported_LO']==1. for r in rows)
    consistency = basis_pass and flow_pass and max_rate<5e-13
    record = dict(schema_version='1.0',source_version='official SuperIso v5.0 November 2025; local investigative patched fork',
        archive_sha256=PIN,patch_sha256=sha(PATCH),license='GPL-3.0-or-later',
        status='INTERNAL_CONSISTENCY_PASS' if consistency else 'D9B_ONE_STATE_BLOCKED',
        matching_status='D9B_MATCHING_BASIS_PASS' if basis_pass else 'D9B_MATCHING_BASIS_BLOCKED',
        dataflow_status='D9B_FULL_RATE_DATAFLOW_PASS' if flow_pass else 'D9B_FULL_RATE_DATAFLOW_BLOCKED',
        one_state_status='D9B_ONE_STATE_RATE_PASS' if consistency else 'D9B_ONE_STATE_RATE_BLOCKED',
        independent_physical_accuracy='NOT_CERTIFIED: no independently matched numerical rate benchmark',
        global_zee_acceptance=None,**{'2026_GLOBAL_FLAVOR_FILTER_READY':False},
        accuracy='NLO QCD matching/evolution/numerator; original legacy EM, power corrections and semileptonic normalization; real top-only unprimed charged scalars. Not NNLO or 2026 precision.',
        C2_matching_used_in_accepted_rate=False,physical_full_Zee_BR=None,
        workspace=dict(branch='feature/zee-d9b-superiso-matched-rate',required_D9A_base='5cea65b5a6a90721cb5742e0e71b8d528cfb2341',starting_commit='c965e91a2bdcc64b87ba45d0af9058994a124e87'),
        legacy_default_inputs=d9['baseline'],
        supported_operator_domain='Q1-Q8, real top-only charged-scalar NP; vanishing primed Wilson coefficients; ms retained as original collinear regulator in phi88; no arbitrary LO four-quark NP',
        tolerances=dict(coefficient_absolute=5e-11,rate_absolute=5e-13,meaning='Floating-point implementation comparison, not theory uncertainty'),
        host=platform.platform(),compiler=run(['gcc','--version'],'compiler.log').splitlines()[0],
        build_command=['make','-B'],compiler_flags=(UP/'src/FlagsForMake').read_text(),
        client_build_command=list(map(str,compile_cmd)),
        original_distributed_sha256=original,
        fork_distributed_sha256={name:sha(UP/Path(name).relative_to('SuperIso_v5.0')) for name in original},
        binary_sha256=sha(EXE),library_sha256=sha(UP/'src/libsuperiso.a'),
        sources=[dict(url='https://arxiv.org/html/hep-ph/9904413v1',scope='ordinary NDR matching Eqs.13-29; existing independent 70-digit evaluator',sha256=sha(ROOT/'validation/module5/local/d9/bmu.html')),
                 dict(url='https://arxiv.org/html/hep-ph/9802391v1',scope='effective map Eq.13 and charged-Higgs matching Appendix A4',sha256=sha(LOCAL/'bg.html') if (LOCAL/'bg.html').exists() else None),
                 dict(url='https://superiso.in2p3.fr/superiso4.1.pdf',scope='Eq.343 ordinary/effective map, Eqs.344-346 RG; Appendix E rate')],
        code_paths=dict(native_matching='src/wilson.c:CW_calculator',ordinary_to_effective='src/wilson.c:C_calculator_base1',
                        rate='src/bsgamma.c:d9b_bsgamma -> bsgamma_Ecut_core',
                        internal_high_matching='input->C0 copied to C0w; Kt0 -> N_E0 and Cem[7] -> P_em; no CW_calculator on this path'),
        executable_integration=dict(patched_client_calls=1+len(rows)+(11 if consistency else 0),unmodified_witness_calls=1,D9A_test_backend_calls=11),
        baseline=baseline,rows=rows,max_matching_residual=max_coeff,max_rate_residual=max_rate,
        alpha_s_over_4pi=baseline['alpha_s_match']/(4*math.pi),
        tests={},two_state_executions=0)
    if consistency:
        # Gate 4 is reached only after executed same-order Gate 3 passes.
        controls = [('example',550.,900.,1.09,False),
                    ('gamma_zero',550.,900.,0.,False),
                    ('gamma_half_pi',550.,900.,math.pi/2,False),
                    ('equal_masses',550.,550.,1.09,False),
                    ('interchanged',900.,550.,math.pi/2-1.09,False),
                    ('decoupled',100000.,100000.,1.09,False),
                    ('opposite_ld',550.,900.,1.09,True)]
        two = {name:coherent(m1,m2,g,5.3,f,160.,baseline,'two_'+name)
               for name,m1,m2,g,f in controls}
        for mu in (120.,200.):
            at_scale = parse(run([EXE,mu],f'baseline_{int(mu)}.log'))
            name = f'mu0_{int(mu)}'
            two[name] = coherent(550.,900.,1.09,5.3,False,mu,at_scale,'two_'+name)
        expected = dict(gamma_zero=rows[0]['output']['injected_BR'],
                        gamma_half_pi=rows[1]['output']['injected_BR'],
                        equal_masses=rows[0]['output']['injected_BR'],
                        interchanged=two['example']['BR'])
        endpoint_residuals = {k:two[k]['BR']-v for k,v in expected.items()}
        passed = all(abs(v)<5e-13 for v in endpoint_residuals.values())
        record.update(two_state_status='D9B_TWO_STATE_RATE_PASS' if passed else 'D9B_TWO_STATE_RATE_BLOCKED',
                      two_state=two,two_state_executions=len(two),endpoint_residuals=endpoint_residuals,
                      coupling_orientation='Module5 bsgamma_lo.py:67-76: a=(cos gamma,-sin gamma); XY*=|a|^2',
                      two_state_scope='Backend-conditional NLO QCD top-only unprimed rate, not complete Zee prediction')
    record['dynamic_corrections'] = dict(NLO_P2_explicitly_zero=all(r['output']['native_P2']==0. for r in rows),
        legacy_nnlo_relative=[r['output']['legacy_full_nnlo_relative'] for r in rows],
        legacy_nnlo_dropped=[bool(r['output']['legacy_full_nnlo_dropped']) for r in rows],
        forced_NNLO_branch_exercised=all(r['output']['forced_fallback_nnlo_dropped']==1. and r['output']['forced_fallback_P2']==0. for r in rows),
        legacy_full_NP_status='DIAGNOSTIC_ONLY: NNLO NP matching basis not independently certified',
        cap_policy='Original size caps retained, after LO assignment; inactive for all validated Q7/Q8 matching points',
        NLO_scope='No NP C^(2) needed at NLO; NNLO normalization/alpha_s choices retained as backend prescription')
    record['gate0'] = dict(witness_sha256=sha(LOCAL/'gate0_witness.log'),
        tests_sha256=sha(LOCAL/'gate0_tests.log'),tests_run=gate0_count,
        erased_NLO_dipoles=witness_out['native_NLO_C7']==witness_out['SM_NLO_C7'] and witness_out['native_NLO_C8']==witness_out['SM_NLO_C8'],
        metadata_residual=witness_out['injected_NLOmatching_native_metadata']-witness_out['injected_NLOmatching_SM_metadata'],
        SM_unmodified=witness_out['SM_full'],original_archive_members_checked=len(original))
    record['source_sha256'] = {str(p.relative_to(ROOT)):sha(p) for p in
        [ROOT/'scripts/zee_d9b_rate_probe.c',Path(__file__),ROOT/'scripts/zee_module5_bmu_nlo.py',ROOT/'tests/test_module5_d9b_rate.py']}
    OUTPUT.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n')
    if args.tests:
        run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_module5_d9b_*.py','-v'],'tests.log')
        count = int(re.search(r'Ran (\d+) tests', (LOCAL/'tests.log').read_text())[1])
        record['tests'] = dict(run=count,failures=0,errors=0,skips=0,
                               report_sha256=sha(LOCAL/'tests.log'),live_executable_calls=1+len(rows)+len(record.get('two_state',{})))
        OUTPUT.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n')
    record['log_sha256'] = {p.name:sha(p) for p in LOCAL.glob('*.log') if p.name!='validation_summary.log'}
    OUTPUT.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({k:record[k] for k in ('status','matching_status','dataflow_status','one_state_status','max_matching_residual','max_rate_residual')}))
    for r in rows[:2]:
        print(r['mass_GeV'],r['output']['native_BR'],r['output']['injected_BR'],r['BR_relative_residual'])
    if not consistency:
        raise SystemExit('Gate 3 blocked; no two-state calculation authorized')


if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""Single-run validation with fresh outputs and committed sources.

Run: python3 scripts/zee_sarah_module0.py --publish
Detailed evidence remains in ignored validation/module0/local/runs/.
Only one complete successful invocation can publish concise acceptance.
SPheno/FlavorKit generation, compilation and development are never invoked.
"""
from __future__ import annotations
import argparse
import datetime as dt
import fcntl
import hashlib
import importlib.metadata
import json
import math as numeric
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'validation/module0'
DEPENDENCIES = {
    'gate6_mass_audit':['gate6_fixture'], 'z_vertex_numeric_audit':['gate6_fixture'],
    'fzee_numeric_audit':['gate6_fixture'], 'integrated_lepton_validation':['gate6_fixture'],
    'e3_integrated_validation':['e3_fixture'],
    'e3_independent_selfenergy_audit':['e3_integrated_validation'],
    'majorana_variant':['e3_independent_selfenergy_audit'],
    'e3_majorana_ab_validation':['majorana_variant'],
    'majorana_closure':['e3_majorana_ab_validation'], 'independent_native':['gate6_fixture'],
}
# Every native producer needs fresh artifacts AND its exact terminal status.
CONTRACTS = {
    'gate6_fixture':(None,None,['gate6_fixture.m']),
    'e3_fixture':(None,None,['e3_charged_loop_fixture.m']),
    'independent_numerics':(None,None,['module0_numerics.json']),
    'check':('checkmodel_status.txt','SARAH_CHECKMODEL_COMPLETED_REVIEW_WARNINGS',['checkmodel.log']),
    'gate6_mass_audit':('mass_audit_status.txt','SARAH_GATE6_TREE_MASS_MATRICES_NUMERIC_PASS',
                        ['mass_matrices_raw.txt','mass_matrices_substituted.txt']),
    'z_vertex_numeric_audit':('z_vertex_numeric_status.txt','SARAH_GATE6_CHARGED_GAUGE_VERTEX_NUMERIC_PASS',
                              ['z_vertex_numeric_results.txt']),
    'fzee_numeric_audit':('fzee_numeric_status.txt','SARAH_ZEE_F_COMPLEX_VERTEX_NORMALIZATION_PASS_E3_UNMATCHED',
                          ['fzee_numeric_results.txt']),
    'integrated_lepton_validation':('integrated_lepton_status.txt',
        'SARAH_ZEE_INTEGRATED_TREE_LEPTON_COMPLEX_PASS_E3_LOOP_UNMATCHED',['integrated_lepton_residuals.txt']),
    'e3_integrated_validation':('e3_integrated_status.txt',
        'E3_SARAH_TREE_CONVENTION_AND_CHEN_KERNEL_CONSISTENT_SELFENERGY_UNVALIDATED',['e3_integrated_residuals.txt']),
    'e3_independent_selfenergy_audit':('e3_sarah_selfenergy_status.txt',
        'SARAH_FV_SIGMAS_FE_HM_B0_EXTRACTED_MAJORANA_AMPLITUDE_UNVALIDATED',
        ['e3_sarah_selfenergy_neutrino_raw.txt','e3_sarah_selfenergy_inventory.txt']),
    'majorana_variant':(None,None,['e3_majorana_variant_manifest.json']),
    'e3_majorana_ab_validation':('e3_majorana_ab_status.txt',
        'MAJORANA_AB_SARAH_3X3_FINITE_B0_NEGCONJ_MATCH_PHASE_SIGN_DERIVATION_PENDING',
        ['e3_majorana_ab_numeric_matrix_report.txt','module0_majorana_closure_inputs.m']),
    'majorana_closure':('module0_majorana_status.txt','PHYSICAL_COMPLEX_MAJORANA_MASS_AND_PHASE_CLOSURE_PASS',
                        ['module0_majorana_physical_report.json']),
    'independent_native':('module0_native_status.txt',
        'INDEPENDENT_SCALARS_W_AND_COMPLEX_TYPEII_QUARK_VERTICES_PASS',
        ['module0_native_report.json','module0_native_inputs.m','module0_quark_inputs.m']),
}
SECTORS = {'hessian':6,'goldstone':4,'charged_mix':2,'scalar':434,'W_':32,'TypeII':144,'up_mass':2,'down_mass':2}
FIXTURES = ('gate6_fixture.m','e3_charged_loop_fixture.m','module0_native_inputs.m','module0_quark_inputs.m')
ALLOWED_TERMS = ('{{d, q, conj[H2]}, {d, conj[Splus], conj[u]}, '
                 '{H1, H1, conj[Splus]}, {H1, q, u}, {H2, H2, conj[Splus]}, '
                 '{H1, H1, conj[H1], conj[H2]}, {H1, H2, conj[H1], conj[H1]}, '
                 '{H1, H2, conj[H2], conj[H2]}, {H2, H2, conj[H1], conj[H2]}}.')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def sources():
    paths = list((ROOT/'models/SARAH/ZeeTypeII').glob('*'))
    for pattern in ('zee_sarah_*','gate6_*','gateA1[b-f]_*','gateB[23]_*'):
        paths += list((ROOT/'scripts').glob(pattern))
    paths += [ROOT/'tests'/n for n in ('test_zee_sarah_source.py','test_gate6_benchmark.py')]
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths)) if p.is_file()}


def fresh_workspace(root, run):
    """Preserve old output locally but never import it into a new run."""
    pointer = root/'work/sarah_zee'
    pointer.parent.mkdir(parents=True,exist_ok=True)
    if pointer.exists() or pointer.is_symlink():
        previous = run.parent.parent/'previous_work'/run.name
        previous.parent.mkdir(parents=True,exist_ok=True)
        pointer.rename(previous)
    work = run/'work'
    work.mkdir()
    pointer.symlink_to(work.resolve(),target_is_directory=True)
    return work


def select_stages(requested, available):
    selected = set(available if requested is None else requested)
    if selected-set(available):
        raise ValueError('Unknown stages: '+str(selected-set(available)))
    pending = list(selected)
    while pending:
        for dependency in DEPENDENCIES.get(pending.pop(),[]):
            if dependency not in selected:
                selected.add(dependency)
                pending.append(dependency)
    return selected


def required_outputs(stage):
    status,_,outputs = CONTRACTS.get(stage,(None,None,[]))
    return outputs+([status] if status else [])


def check_stage_outputs(work, stage, started_ns):
    errors = []
    for name in required_outputs(stage):
        path = work/name
        if not path.is_file(): errors.append('Missing output: '+name)
        # Linux may stamp a just-created file from its coarser cached
        # filesystem clock. Absence before the stage + the empty run
        # workspace provide the primary freshness proof; allow one second
        # of timestamp granularity, while rejecting genuinely old files.
        elif path.stat().st_mtime_ns<started_ns-1_000_000_000:
            errors.append('Output predates producer: '+name)
    status,expected,_ = CONTRACTS.get(stage,(None,None,[]))
    if status and (work/status).is_file() and (work/status).read_text().strip()!=expected:
        errors.append('Unaccepted producer status: '+(work/status).read_text().strip())
    return errors


def validate_payload(work, stage):
    errors = []
    if stage=='independent_numerics':
        data = json.loads((work/'module0_numerics.json').read_text())
        rows = data['checks']
        if len(rows)!=31 or data['status']!='PASS_ANALYTIC_NUMERICAL_REGRESSIONS_ONLY':
            errors.append('Incomplete independent numerical regressions')
    elif stage=='independent_native':
        rows = json.loads((work/'module0_native_report.json').read_text())
        if len(rows)!=626 or any(sum(x['label'].startswith(p) for x in rows)!=n for p,n in SECTORS.items()):
            errors.append('Incomplete independent native scalar/current inventory')
    elif stage=='majorana_closure':
        data = json.loads((work/'module0_majorana_physical_report.json').read_text())
        if data['failures'] or len(data['results'])!=2: errors.append('Incomplete physical Majorana closure')
        limits = {'opposite_chirality_residual_GeV':1e-16,'physical_matrix_residual_eV':5e-11,
                  'physical_relative_residual':1e-8,'rephasing_residual_eV':5e-11,
                  'takagi_reference_residual_eV':5e-11,'CP_product_residual_eV4':1e-17}
        for row in data['results']:
            for key,limit in limits.items():
                if not numeric.isfinite(row[key]) or not 0<=row[key]<=limit:
                    errors.append('Physical Majorana residual failure: '+key)
        return errors
    else: return errors
    for row in rows:
        if not numeric.isfinite(row['residual']) or not 0<=row['residual']<=row['tolerance']:
            errors.append('Invalid residual: '+row['label'])
    return errors


def stage_commands(python, math, run):
    stages = [('versions',[math,'-noprompt','-run','Print[$Version]; Exit[]'])]
    for stage,filename in (('static_source','test_zee_sarah_source.py'),('static_benchmark','test_gate6_benchmark.py')):
        stages.append((stage,[python,'-m','unittest','discover','-s','tests','-p',filename,'-v']))
    for stage,filename in (('gate6_fixture','gate6_fixture'),('e3_fixture','e3_convention_fixture'),
                           ('independent_numerics','module0_numerics')):
        stages.append((stage,[python,f'scripts/zee_sarah_{filename}.py']))
    for name in ('gate6_benchmark','gate6_width_inventory','gateA1b_hierarchical_no_seed',
                 'gateA1c_charged_singlet_lfv','gateA1d_neutral_tree_lfv',
                 'gateA1e_neutral_one_loop_dipoles','gateA1f_charged_doublet_y_dipoles'):
        stages.append((name,[python,f'scripts/{name}.py','--output',str(run/(name+'.json'))]))
    stages.append(('vacuum',[python,'scripts/gate6_vacuum_search.py','--nstarts','30',
                             '--seed','123','--output',str(run/'vacuum.json')]))
    for name in ('check','gate6_mass_audit','z_vertex_numeric_audit','fzee_numeric_audit',
                 'integrated_lepton_validation','e3_integrated_validation','e3_independent_selfenergy_audit'):
        stages.append((name,[math,'-script',f'scripts/zee_sarah_{name}.m']))
    stages += [('majorana_variant',[python,'scripts/zee_sarah_majorana_spinor_variant.py']),
               ('e3_majorana_ab_validation',[math,'-script','scripts/zee_sarah_e3_majorana_ab_validation.m']),
               ('majorana_closure',[math,'-script','scripts/zee_sarah_majorana_closure.m']),
               ('independent_native',[math,'-script','scripts/zee_sarah_module0_native.m'])]
    return stages


def publish_report(run, result):
    if not result['full_stage_selection'] or any(result['gates'][str(i)]!='PASS' for i in (1,2,3,4,6)):
        raise ValueError('Only one complete successful invocation can publish acceptance')
    report,fixtures = BASE/'report',BASE/'fixtures'
    report.mkdir(exist_ok=True)
    fixtures.mkdir(exist_ok=True)
    for name in ('inventory.json','trace.jsonl','result.json','checkmodel_diagnostics.json','SHA256SUMS.json'):
        shutil.copy2(run/name,report/name)
    rows = json.loads((run/'work/module0_native_report.json').read_text())
    write_json(report/'native_residuals.json', {prefix:dict(count=len(group),
        max_residual=max(x['residual'] for x in group),tolerance=max(x['tolerance'] for x in group))
        for prefix in SECTORS if (group:=[x for x in rows if x['label'].startswith(prefix)])})
    shutil.copy2(run/'work/module0_majorana_physical_report.json',report/'majorana_physical.json')
    numerical = json.loads((run/'work/module0_numerics.json').read_text())
    write_json(report/'numerics.json',{k:v for k,v in numerical.items() if k!='inputs'})
    write_json(fixtures/'numerics_inputs.json',numerical['inputs'])
    for name in FIXTURES: shutil.copy2(run/'work'/name,fixtures/name)
    names = ['Load / CheckModel','Scalars','Gauge / complex Yukawa vertices',
             'Complex Majorana loop','SPheno / FlavorKit','Regression suites']
    physical = json.loads((report/'majorana_physical.json').read_text())
    worst = max(x['physical_matrix_residual_eV'] for x in physical['results'])
    (BASE/'STATUS.md').write_text('# Module 0 — single complete validation\n\n'+
        f'Run `{run.name}`; committed source `{result["source_commit"]}`.\n'
        'One empty workspace; no prior or partial run contributes acceptance.\n\n'
        '| Gate | Status |\n|---|---|\n'+
        '\n'.join(f'| {i}. {names[int(i)-1]} | **{status}** |' for i,status in result['gates'].items())+
        f'\n\nMathematica {result["versions"]["Mathematica"]}; SARAH {result["versions"]["SARAH"]}. '
        f'{sum(result["unit_test_counts"].values())} unit tests; 31 independent numerical checks.\n'
        f'Maximum complex Majorana residual **{worst:.3e} eV** '
        '(absolute tolerance 5e-11 eV, relative 1e-8).\n\n'
        'Residuals/counts: [report/native_residuals.json](report/native_residuals.json), '
        '[report/majorana_physical.json](report/majorana_physical.json). '
        'All CheckModel diagnostics: [report/checkmodel_diagnostics.json](report/checkmodel_diagnostics.json); '
        'disposition and physical derivation: [CONVENTIONS.md](CONVENTIONS.md). '
        'Commands, SHA256 provenance and local artifact manifest: [report/](report/). '
        'Essential benchmark values: [fixtures/](fixtures/).\n\n'
        f'Detailed evidence stays locally at `validation/module0/local/runs/{run.name}/`. '
        'Legacy detailed runs remain locally ignored.\n\n'
        'Reproduce from this checkout with committed sources:\n\n'
        '```sh\npython3 scripts/zee_sarah_module0.py --publish\n```\n\n'
        'SPheno/FlavorKit was not developed, generated, compiled or run: model-specific '
        '`SPheno.m` is absent and no valid SPheno installation was identified. '
        'The same Zee Lagrangian and Majorana packaging are retained. These passes cover '
        'the stated identities, representative inputs and physical limits; they do not '
        'establish RG closure, a global vacuum, a 309-point archive or full phenomenological '
        'viability. The original `~/zee` repository is untouched.\n')
    write_json(report/'REPORT_SHA256.json',{str(p.relative_to(BASE)):digest(p)
        for folder in (report,fixtures) for p in sorted(folder.iterdir())
        if p.is_file() and p.name!='REPORT_SHA256.json'})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stages',nargs='+',help='Diagnostic subset; fresh prerequisites included')
    ap.add_argument('--publish',action='store_true',help='Publish concise reports only after complete acceptance')
    args = ap.parse_args()
    if args.publish and args.stages: ap.error('Partial selections cannot publish acceptance')
    os.chdir(ROOT)
    source_map = sources()
    if subprocess.check_output(['git','status','--porcelain','--',*source_map],text=True):
        ap.error('Commit the scoped implementation/tests before validation; working sources are dirty')
    local = BASE/'local'
    local.mkdir(parents=True,exist_ok=True)
    lock = open(local/'.runner.lock','w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    run = local/'runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run.mkdir(parents=True)
    stages = stage_commands(shutil.which('python3'),os.environ.get('ZEE_MATH','/usr/local/bin/math'),run)
    selected = select_stages(args.stages,[n for n,_ in stages])
    work = fresh_workspace(ROOT,run)
    sarah = (Path.home()/'.Mathematica/Applications/SARAH').resolve()
    spheno = os.environ.get('SPHENO_ROOT')
    inventory = dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip(),sources=source_map,
        sarah=str(sarah),math=stages[0][1][0],native_dependency_sha256={str(p.relative_to(sarah)):digest(p) for p in
            (sarah/'SARAH.m',sarah/'Package/loopCorrections.m',sarah/'Package/SPheno/SPhenoLoopMasses.m',
             sarah/'SARAH.config',sarah/'Models/parameters.m',sarah/'Models/particles.m') if p.is_file()},
        packages={p:importlib.metadata.version(p) for p in ('numpy','scipy','sympy')},
        spheno_model_support=(ROOT/'models/SARAH/ZeeTypeII/SPheno.m').is_file(),
        spheno_executable=shutil.which('SPheno'),spheno_root=spheno,
        spheno_root_valid=bool(spheno and (Path(spheno)/'src').is_dir() and (Path(spheno)/'Makefile').is_file()),
        spheno_execution='NOT_REQUESTED_NOT_ATTEMPTED',work_initially_empty=not any(work.iterdir()),
        dependency_plan=DEPENDENCIES,full_stage_selection=args.stages is None,
        evidence_policy='fresh run only; every producer creates fresh required outputs and accepted status')
    write_json(run/'inventory.json',inventory)
    outcomes = {}
    for name,command in stages:
        if name not in selected: continue
        print('RUN',name,flush=True)
        started_ns,clock = time.time_ns(),time.monotonic()
        before = {p.name:digest(p) for p in work.iterdir() if p.is_file()}
        errors = ['Failed prerequisite: '+p for p in DEPENDENCIES.get(name,[]) if outcomes.get(p,1)]
        errors += ['Producer output already exists: '+p for p in required_outputs(name) if (work/p).exists()]
        code = 125
        try:
            with (run/(name+'.log')).open('w') as log:
                if errors: log.write('\n'.join(errors)+'\n')
                else: code = subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=2400).returncode
            if not errors and code==0:
                errors += check_stage_outputs(work,name,started_ns)
                if not errors: errors += validate_payload(work,name)
        except subprocess.TimeoutExpired: code = 124
        except (OSError,ValueError,KeyError,TypeError) as exc: errors.append(type(exc).__name__+': '+str(exc))
        if sources()!=source_map: errors.append('Scoped sources changed during invocation')
        text = (run/(name+'.log')).read_text()
        diagnostics = [line for line in text.splitlines() if re.search(r'\w+::\w+:',line)]
        if '-script' in command and name!='check' and diagnostics:
            errors.append('Unreviewed native diagnostic: '+str(diagnostics))
        outputs = {p.name:dict(sha256=digest(p),mtime_ns=p.stat().st_mtime_ns)
            for p in sorted(work.iterdir()) if p.is_file() and before.get(p.name)!=digest(p)}
        record = dict(stage=name,command=command,started_utc=dt.datetime.fromtimestamp(started_ns/1e9,dt.timezone.utc).isoformat(),
            elapsed_seconds=time.monotonic()-clock,exit_code=code,contract_errors=errors,
            source_inventory_sha256=digest(run/'inventory.json'),log_sha256=digest(run/(name+'.log')),
            generated_outputs=outputs)
        with (run/'trace.jsonl').open('a') as trace: trace.write(json.dumps(record,sort_keys=True)+'\n')
        outcomes[name] = code or bool(errors)
        print('DONE',name,'exit',code,'contract_errors',len(errors),flush=True)
    def gate(names):
        if all(n in outcomes and not outcomes[n] for n in names): return 'PASS'
        return 'FAIL' if any(n in outcomes and outcomes[n] for n in names) else 'BLOCKED'
    check_text = (run/'check.log').read_text() if (run/'check.log').is_file() else ''
    diagnostics = [x for x in check_text.splitlines() if re.search(r'\w+::\w+:',x)]
    known = (len(diagnostics)==1 and diagnostics[0].startswith('PossibleTerms::NonSUSY:')
             and diagnostics[0].endswith(ALLOWED_TERMS) and 'ZEE_SARAH_LOADED 4.15.4' in check_text)
    write_json(run/'checkmodel_diagnostics.json',dict(diagnostics=diagnostics,exact_reviewed_list=known,
                                                     review='validation/module0/CONVENTIONS.md'))
    gates = {'1':gate(['versions','check']),'2':gate(['gate6_mass_audit','independent_native']),
        '3':gate(['z_vertex_numeric_audit','fzee_numeric_audit','integrated_lepton_validation','independent_native']),
        '4':gate(['e3_integrated_validation','e3_independent_selfenergy_audit',
                  'e3_majorana_ab_validation','majorana_closure','independent_numerics']),
        '5':'BLOCKED','6':('FAIL' if any(outcomes.values()) else 'PASS') if args.stages is None else 'BLOCKED'}
    if gates['1']=='PASS' and not known: gates['1']='FAIL'
    versions = dict(Mathematica='UNAVAILABLE',SARAH='UNAVAILABLE',SPheno='NOT_RUN')
    for name,pattern,key in (('versions',r'"([\d.]+) for','Mathematica'),('check',r'ZEE_SARAH_LOADED ([\d.]+)','SARAH')):
        if (run/(name+'.log')).is_file():
            match = re.search(pattern,(run/(name+'.log')).read_text())
            if match: versions[key]=match[1]
    tests = {}
    for name in ('static_source','static_benchmark'):
        if (run/(name+'.log')).is_file():
            match = re.search(r'Ran (\d+) tests',(run/(name+'.log')).read_text())
            if match: tests[name]=int(match[1])
    result = dict(run_id=run.name,source_commit=inventory['source_commit'],gates=gates,versions=versions,
        full_stage_selection=args.stages is None,unit_test_counts=tests,failed_stages=[n for n,v in outcomes.items() if v],
        stage_count=len(outcomes),initial_work_empty=inventory['work_initially_empty'],previous_run_inputs_used=False,
        scope='same Zee Lagrangian; finite representative fixtures and physical limits')
    write_json(run/'result.json',result)
    write_json(run/'SHA256SUMS.json',{str(p.relative_to(run)):digest(p) for p in sorted(run.rglob('*'))
        if p.is_file() and p.name!='SHA256SUMS.json'})
    complete = args.stages is None and all(gates[str(i)]=='PASS' for i in (1,2,3,4,6))
    if args.publish and complete: publish_report(run,result)
    print('EVIDENCE',run,flush=True)
    print('GATES',json.dumps(gates),flush=True)
    raise SystemExit(0 if complete or (args.stages and not any(outcomes.values())) else 1)


if __name__=='__main__':
    main()

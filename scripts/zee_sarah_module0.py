#!/usr/bin/env python3
"""Reproducible Module 0 validation; append-only evidence, no external builds.

Run from this checkout: python3 scripts/zee_sarah_module0.py
Each invocation makes a new UTC run directory. Exit 0 means every requested
command succeeded, NOT that every physics gate passed. See STATUS.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'validation/module0'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources():
    paths = list((ROOT / 'models/SARAH/ZeeTypeII').glob('*'))
    for pattern in ('zee_sarah_*', 'gate6_*', 'gateA1[b-f]_*', 'gateB[23]_*'):
        paths += list((ROOT / 'scripts').glob(pattern))
    paths += [ROOT / 'tests' / name for name in
              ('test_zee_sarah_source.py', 'test_gate6_benchmark.py')]
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(paths))
            if p.is_file()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stages', nargs='+', help='Run named stages only (partial rerun)')
    args = ap.parse_args()
    os.chdir(ROOT)
    BASE.mkdir(parents=True, exist_ok=True)
    lock = open(BASE / '.runner.lock', 'w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    run = BASE / (dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    run.mkdir()
    python = shutil.which('python3')
    math = os.environ.get('ZEE_MATH', '/usr/local/bin/math')
    sarah = Path(os.environ.get('ZEE_SARAH', str(Path.home() /
                 '.Mathematica/Applications/SARAH'))).resolve()
    spheno = os.environ.get('SPHENO_ROOT')
    model_support = ROOT / 'models/SARAH/ZeeTypeII/SPheno.m'
    inventory = {
        'math': math, 'sarah': str(sarah),
        'sarah_source_sha256': digest(sarah / 'SARAH.m') if (sarah/'SARAH.m').is_file() else None,
        'native_dependency_sha256': {str(p.relative_to(sarah)):digest(p) for p in
            (sarah/'Package/loopCorrections.m',sarah/'Package/SPheno/SPhenoLoopMasses.m',
             sarah/'SARAH.config',sarah/'Models/parameters.m',sarah/'Models/particles.m') if p.is_file()},
        'spheno_model_support': model_support.is_file(),
        'spheno_path': shutil.which('SPheno'), 'spheno_root': spheno,
        'spheno_root_valid': bool(spheno and (Path(spheno)/'src').is_dir()
                                 and (Path(spheno)/'Makefile').is_file()),
        'gfortran': shutil.which('gfortran'),
        'packages': {p: importlib.metadata.version(p) for p in ('numpy','scipy','sympy')},
        'branch': subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
        'base_commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'sources': sources(),
        'dependency_plan': [
            'static regressions and independent Python finite-loop/benchmark fixtures',
            'native CheckModel, scalar matrices, gauge and complex tree lepton amplitudes',
            'E3 convention -> original loop inventory -> isolated Majorana A/B loop',
            'independent scalar derivatives and physical W/quark vertices',
            'SPheno generation/build only with model support and installed source tree'],
        'spheno_gate': 'BLOCKED' if not model_support.is_file() else 'PARTIAL',
    }
    (run/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    stages = [
        ('versions', [math,'-noprompt','-run','Print[$Version]; Exit[]']),
        ('static_source',[python,'-m','unittest','discover','-s','tests','-p','test_zee_sarah_source.py','-v']),
        ('static_benchmark',[python,'-m','unittest','discover','-s','tests','-p','test_gate6_benchmark.py','-v']),
        ('gate6_fixture',[python,'scripts/zee_sarah_gate6_fixture.py']),
        ('e3_fixture',[python,'scripts/zee_sarah_e3_convention_fixture.py']),
        ('independent_numerics',[python,'scripts/zee_sarah_module0_numerics.py']),
    ]
    for name in ('gate6_benchmark','gate6_width_inventory',
                 'gateA1b_hierarchical_no_seed','gateA1c_charged_singlet_lfv',
                 'gateA1d_neutral_tree_lfv','gateA1e_neutral_one_loop_dipoles',
                 'gateA1f_charged_doublet_y_dipoles'):
        stages.append((name,[python,f'scripts/{name}.py','--output',str(run/(name+'.json'))]))
    stages += [('vacuum',[python,'scripts/gate6_vacuum_search.py','--nstarts','30',
                          '--seed','123','--output',str(run/'vacuum.json')])]
    for name in ('check','gate6_mass_audit','z_vertex_numeric_audit',
                 'fzee_numeric_audit','integrated_lepton_validation',
                 'e3_integrated_validation','e3_independent_selfenergy_audit'):
        stages.append((name,[math,'-script',f'scripts/zee_sarah_{name}.m']))
    stages += [('majorana_variant',[python,'scripts/zee_sarah_majorana_spinor_variant.py']),
               ('e3_majorana_ab_validation',[math,'-script','scripts/zee_sarah_e3_majorana_ab_validation.m']),
               ('majorana_closure',[math,'-script','scripts/zee_sarah_majorana_closure.m'])]
    extra = ROOT/'scripts/zee_sarah_module0_native.m'
    if extra.is_file():
        stages.append(('independent_native',[math,'-script',str(extra)]))
    if args.stages and set(args.stages)-{n for n,_ in stages}:
        ap.error('Unknown stages: '+str(set(args.stages)-{n for n,_ in stages}))
    failures = []
    outcomes = {}
    prerequisites = {
        'gate6_mass_audit':['gate6_fixture'],
        'z_vertex_numeric_audit':['gate6_fixture'],
        'integrated_lepton_validation':['gate6_fixture'],
        'e3_integrated_validation':['e3_fixture'],
        'e3_independent_selfenergy_audit':['e3_integrated_validation'],
        'majorana_variant':['e3_independent_selfenergy_audit'],
        'e3_majorana_ab_validation':['majorana_variant'],
        'majorana_closure':['e3_majorana_ab_validation'],
        'independent_native':['gate6_fixture'],
    }
    for name, command in stages:
        if args.stages and name not in args.stages:
            continue
        print('RUN',name,flush=True)
        start = dt.datetime.now(dt.timezone.utc).isoformat()
        clock = time.monotonic()
        blocked = [p for p in prerequisites.get(name,[]) if p in outcomes and outcomes[p]]
        try:
            with (run/(name+'.log')).open('w') as log:
                if blocked:
                    log.write('SKIPPED: failed prerequisites '+str(blocked)+'\n')
                    code = 125
                else:
                    result = subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                                            timeout=2400)
                    code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
        changed_sources = sources() != inventory['sources']
        record = dict(stage=name,command=command,started_utc=start,
                      elapsed_seconds=time.monotonic()-clock,exit_code=code,
                      source_sha256=inventory['sources'],
                      sources_changed_during_run=changed_sources,
                      log_sha256=digest(run/(name+'.log')))
        # Native machine expressions, fixtures and residuals are evidence;
        # never archive installation output, executables or generated binaries.
        work = ROOT/'work/sarah_zee'
        artifacts = run/'artifacts'/name
        artifacts.mkdir(parents=True)
        record['artifacts'] = {}
        for path in sorted(work.glob('*')):
            if path.is_file() and path.suffix in ('.txt','.json','.m'):
                shutil.copy2(path,artifacts/path.name)
                record['artifacts'][path.name] = dict(sha256=digest(path),
                    mtime_ns=path.stat().st_mtime_ns)
        with (run/'trace.jsonl').open('a') as trace:
            trace.write(json.dumps(record,sort_keys=True)+'\n')
        print('DONE',name,'exit',code,flush=True)
        outcomes[name] = code or int(changed_sources)
        if outcomes[name]:
            failures.append(name)
    gates = {str(i):'PARTIAL' for i in range(1,7)}
    diagnostic_lines = []
    if 'check' in outcomes:
        diagnostic_lines = [line for line in (run/'check.log').read_text().splitlines()
                            if re.search(r'\w+::\w+:',line)]
        (run/'checkmodel_diagnostics.json').write_text(json.dumps(dict(
            diagnostics=diagnostic_lines,review='validation/module0/CONVENTIONS.md'),indent=2)+'\n')
        allowed_terms = ('{{d, q, conj[H2]}, {d, conj[Splus], conj[u]}, '
                         '{H1, H1, conj[Splus]}, {H1, q, u}, {H2, H2, conj[Splus]}, '
                         '{H1, H1, conj[H1], conj[H2]}, {H1, H2, conj[H1], conj[H1]}, '
                         '{H1, H2, conj[H2], conj[H2]}, {H2, H2, conj[H1], conj[H2]}}.')
        known = (len(diagnostic_lines)==1 and diagnostic_lines[0].startswith('PossibleTerms::NonSUSY:')
                 and diagnostic_lines[0].endswith(allowed_terms))
        gates['1']='PASS' if not outcomes['check'] and known else 'PARTIAL'
    def passed(names):
        return all(name in outcomes and outcomes[name]==0 for name in names)
    def status_is(filename, expected):
        path = ROOT/'work/sarah_zee'/filename
        return path.is_file() and path.read_text().strip()==expected
    native_ok = status_is('module0_native_status.txt',
                         'INDEPENDENT_SCALARS_W_AND_COMPLEX_TYPEII_QUARK_VERTICES_PASS')
    if passed(['gate6_mass_audit','independent_native']) and native_ok:
        gates['2']='PASS'
    if passed(['z_vertex_numeric_audit','fzee_numeric_audit',
               'integrated_lepton_validation','independent_native']) and native_ok:
        gates['3']='PASS'
    if passed(['e3_integrated_validation','e3_independent_selfenergy_audit',
               'e3_majorana_ab_validation','majorana_closure','independent_numerics']):
        status = (ROOT/'work/sarah_zee/module0_majorana_status.txt').read_text().strip()
        if status=='PHYSICAL_COMPLEX_MAJORANA_MASS_AND_PHASE_CLOSURE_PASS':
            gates['4']='PASS'
    gates['5']=inventory['spheno_gate']
    if args.stages is None and not failures:
        gates['6']='PASS'
    result = dict(failed_commands=failures,full_stage_selection=args.stages is None,
                  gates=gates,physics_scope='finite representative fixtures; no full model allowed claim',
                  checkmodel_diagnostic_count=len(diagnostic_lines))
    (run/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    # Per-run status is immutable with the rest of this run. The top-level
    # STATUS.md is the reviewed pointer to the final complete run.
    (run/'STATUS.md').write_text('Module 0 run '+run.name+'\n\n'+
        '\n'.join(f'- Gate {gate}: {status}' for gate,status in gates.items())+
        '\n\nSPheno requires models/SARAH/ZeeTypeII/SPheno.m and a valid installation.\n'+
        'Detailed commands, tolerances, inputs and hashes: trace.jsonl and artifacts/.\n')
    print('EVIDENCE',run,flush=True)
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()

"""Fresh native SARAH audit, numerical checks, and concise reproducible evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import unittest
from .native import prepare, ROOT, LOCAL
from .interface import sha
from .amplitudes import MISSING
from .tagged_regression import run as tagged_regression

BASE='48735439f151fb43f2c6d50661abe66f3d440293'
TAG='zee-lfv-module3-components-v1'
PROTECTED=['models/SARAH/ZeeTypeII','module1','module2','module3',
           'validation/module0','validation/module1','validation/module2','validation/module3']


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def write(path,data):
    path.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')


def native_fixture(raw):
    groups={}
    for r in raw['numerical_checks']:
        group=r['vertex'].split('_')[0]
        if group not in groups or r['residual']>groups[group]['residual']:
            groups[group]=dict(r,signed_complex_residual=[a-b for a,b in zip(r['actual'],r['expected'])])
    keys=['photon_Fe','photon_Fu','photon_Fd','lepton_{1, 1, 2}','lepton_{2, 1, 2}','lepton_{3, 1, 2}',
          'charged_minus_{2, 1, 2}','charged_plus_{2, 1, 2}',
          'quark_{1, Fu}','quark_{2, Fu}','quark_{3, Fu}',
          'quark_{1, Fd}','quark_{2, Fd}','quark_{3, Fd}',
          'WW_1','WW_2','WW_A','goldstone_1','goldstone_2',
          'scalar_gauge_{VP, 2, 2}','scalar_gauge_{VP, 2, 3}',
          'scalar_gauge_{VZ, 2, 3}',
          'trilinear_{1, 2, 2}','trilinear_{1, 2, 3}',
          'trilinear_{2, 3, 3}','trilinear_{3, 2, 3}']
    fixture={'status':raw['status'],'mathematica_version':raw['mathematica_version'],
             'sarah_version':raw['sarah_version'],'raw_query_count':raw['query_count'],
             'complex_coefficient_checks':len(raw['numerical_checks']),
             'max_abs_residual':raw['max_abs_residual'],'absolute_tolerance':1e-9,
             'signed_worst_by_sector':groups,'raw_representatives':{k:raw['raw'][k] for k in keys},
             'raw_dump_sha256':sha(LOCAL/'vertices_raw.m'),
             'native_json_sha256':sha(LOCAL/'vertices.json'),
             'witness_records_sha256':sha(LOCAL/'witness_records.json'),
             'scalar_gauge_momentum_tensor_checks':raw['scalar_gauge_momentum_tensor_checks'],
             'field_indices':'Fe/Fv 1=e,2=mu,3=tau; hh1=h,hh2=H; Ah2=A; Hm1=G-,Hm2=H1-,Hm3=H2-',
             'units':'dimensionless Yukawa/gauge coefficients; scalar trilinears in GeV'}
    write(ROOT/'module4/native_evidence.json',fixture)
    return {k:v for k,v in fixture.items() if k not in ('raw_representatives','scalar_gauge_momentum_tensor_checks')}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--all-tests',action='store_true')
    ap.add_argument('--skip-native',action='store_true',help='Offline diagnostic run; reports VERTEX_BLOCKED, never fresh native PASS')
    args=ap.parse_args()
    if git('branch','--show-current')!='feature/zee-barrzee-module4':raise ValueError('Wrong branch')
    pins={'module0':'00bc58869358501bf3f3ef583e2c759a23a4f39a',
          'module1':'687fba61640424406661601e92312b8481673b83',
          'module2':'571046e7dce3b99b60c4aaa6e6cdef2e66a494d4','module3':BASE}
    for commit in pins.values():
        subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=ROOT,check=True)
    if git('rev-parse',TAG+'^{}')!=BASE or git('cat-file','-t',TAG)!='tag':
        raise ValueError('Component freeze annotated tag mismatch')
    if git('rev-parse','zee-sarah-module0-v1^{}')!=pins['module0'] or git('rev-parse','zee-neutrino-module2-physics-v1^{}')!=pins['module2']:
        raise ValueError('Foundation tag mismatch')
    if git('diff','--name-only',BASE,'--',*PROTECTED):raise ValueError('Frozen foundation changed')
    # Check all pre-existing SARAH scripts, including any not listed by foundations().
    scripts=git('ls-tree','-r','--name-only',BASE,'scripts').splitlines()
    if git('diff','--name-only',BASE,'--',*[p for p in scripts if 'sarah' in p.lower()]):
        raise ValueError('Existing SARAH script changed')
    prepare()
    native={'status':'VERTEX_BLOCKED','reason':'Native run explicitly skipped'}
    if not args.skip_native:
        path=LOCAL/'vertices.json'
        if path.exists():path.unlink()
        try:
            with (LOCAL/'native.log').open('w') as log:
                run=subprocess.run(['/usr/local/bin/math','-script','scripts/zee_module4_vertices.m'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
            raw=json.loads(path.read_text())
            if (run.returncode==0 and raw['status']=='VERTEX_COMPONENTS_PASS' and
                raw['sarah_version']=='4.15.4' and raw['mathematica_version'].startswith('15.0.1')):
                native=native_fixture(raw)
            else:native={'status':'VERTEX_BLOCKED','reason':raw.get('status'),'returncode':run.returncode}
        except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
            native={'status':'VERTEX_BLOCKED','reason':str(exc)}
    sys.path.insert(0,str(ROOT/'tests'))
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py' if args.all_tests else 'test_module4_*.py')
    inherited={'status':'NOT_RUN','tests':0,'failures':0,'errors':0,'skipped':0}
    routed=0
    if args.all_tests:
        def cases(node):
            if isinstance(node,unittest.TestSuite):
                for child in node:yield from cases(child)
            else:yield node
        selected=list(cases(suite))
        routed=sum(c.id().startswith('test_module3_') for c in selected)
        suite=unittest.TestSuite(c for c in selected if not c.id().startswith('test_module3_'))
        inherited=tagged_regression()
        if inherited['tests']!=routed:
            raise ValueError('Historical Module3 test routing count changed')
    with (LOCAL/'regression.log').open('w') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    evidence={name:sys.modules[name].EVIDENCE for name in sorted(sys.modules)
              if name.startswith('test_module4_') and hasattr(sys.modules[name],'EVIDENCE')}
    success=(result.wasSuccessful() and result.testsRun>0 and not result.skipped and
             (not args.all_tests or inherited['status']=='PASS'))
    sources=json.loads((ROOT/'module4/sources.json').read_text())
    cache={}
    for label,source in sources.items():
        p=LOCAL/source['local_cache']
        if p.exists() and sha(p)!=source['sha256']:raise ValueError('Primary source hash mismatch: '+label)
        cache[label]='VERIFIED' if p.exists() else 'NOT_CACHED; committed source pin retained'
    paths=sorted(list((ROOT/'module4').glob('*.py'))+list((ROOT/'module4').glob('*.json'))+
                 list((ROOT/'module4').glob('*.md'))+list((ROOT/'tests').glob('test_module4_*.py'))+
                 [ROOT/'scripts/run_module4_validation.sh',ROOT/'scripts/zee_module4_vertices.m'])
    manifest={'schema_version':'1.0.0','foundation_commits':pins,'module4_sources_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},
              'comparison_sources_sha256':{name:sha(ROOT/name) for name in [
                  'module3/core.py','module3/tree.py','scripts/gateA1c_charged_singlet_lfv.py',
                  'scripts/gateA1d_neutral_tree_lfv.py','scripts/gateA1e_neutral_one_loop_dipoles.py',
                  'scripts/gateA1f_charged_doublet_y_dipoles.py',
                  'reference/lfv/scripts/zee_barr_zee_kernels.py',
                  'reference/lfv/scripts/zee_barr_zee_fermion_dipoles.py',
                  'reference/lfv/scripts/zee_gateD4_W_photon_barr_zee_27.py',
                  'reference/barrzee/tests/test_zee_gateD4_W_photon_barr_zee_27.py']},
              'primary_papers':sources,'primary_cached_downloads':cache,
              'native_model_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'models/SARAH/ZeeTypeII').glob('*')) if p.is_file()},
              'installed_SARAH_m_sha256':sha(Path('/home/amine/.Mathematica/Applications/SARAH/SARAH.m')) if Path('/home/amine/.Mathematica/Applications/SARAH/SARAH.m').exists() else None,
              'component_tag':{'name':TAG,'annotated_object':git('rev-parse',TAG),'peeled':BASE},
              'python':sys.version.split()[0],'native_logs':'validation/module4/local (ignored)',
              'inherited_module3_context':inherited}
    gates={
        'A':{'status':'PASS' if native['status']=='VERTEX_COMPONENTS_PASS' else 'BLOCKED','scope':'Native vertices and signed component/contact normalization checks','native':native},
        'B':{'status':'PARTIAL','matching_status':'PASS','scope':'Physical fermion-photon matching derived with outgoing photon crossing and Wick/Dirac projection; three primary diagonal checks; all nine species coherently included; mass/Yukawa scheme nominal'},
        'C':{'status':'PARTIAL','matching_status':'BLOCKED_GAUGE_MATCHING','scope':'Exact CHK-Ilisie-Abe decomposition; off-shell P/pinch Ward identity checked; complete LFV B,C projections and Rxi cancellation unresolved; W excluded'},
        'D':{'status':'PARTIAL','amplitude_status':'UNKNOWN_NOT_IMPLEMENTED','scope':'Native diagonal/off-diagonal trilinears, polynomial derivative, scalar F2, transverse effective tensor checked; general LFV matching not closed'},
        'E':{'status':'PARTIAL','amplitude_status':'NOT_EVALUATED','scope':'CHK Zgamma Eqs12,17,19, set C; Ilisie mixed charged-current topologies inventoried, no amplitudes added'},
        'coherent_combination':{'status':'PARTIAL','included':'Frozen Module3 scalar one-loop plus validated photon-fermion two-loop subset','excluded':'W candidates and other missing topologies','rate_scope':'INCLUDED_TOPOLOGIES_ONLY'}}
    report={'schema_version':'1.0.0','overall_scientific_status':'PARTIAL' if success else 'FAIL',
            'component_validation':'VALIDATION_PASS' if success else 'FAIL',
            'physical_status':'PREDICTION_INCOMPLETE','COMPLETE_LFV':False,'global_zee_acceptance':None,
            'generated_UTC':datetime.now(timezone.utc).isoformat(),'gates':gates,'evidence':evidence,
            'tests':{'run':result.testsRun+inherited['tests'],
                     'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped)+inherited['tests']-inherited['failures']-inherited['errors']-inherited['skipped'],
                     'failures':len(result.failures)+inherited['failures'],
                     'errors':len(result.errors)+inherited['errors'],'skipped':len(result.skipped)+inherited['skipped'],
                     'current_branch':{'branch':git('branch','--show-current'),'run':result.testsRun,
                         'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)},
                     'inherited_module3_tagged_context':inherited,
                     'regression_status':'PASS' if success else 'FAIL','full_repository_regression':args.all_tests},
            'missing_contributions':MISSING,'source_commit_before_validation':git('rev-parse','HEAD'),
            'reproduction':['bash scripts/run_module4_validation.sh --all-tests','python -m module4.interface --input module4/example.json --output validation/module4/local/example_output.json']}
    write(ROOT/'validation/module4/results.json',report)
    write(ROOT/'validation/module4/source_manifest.json',manifest)
    lines=['# Module 4: PARTIAL','',
        'Fermion-photon matching is independently derived and included coherently with the frozen Module3 components. W matching remains blocked and W candidates are excluded. Overall rates remain INCLUDED_TOPOLOGIES_ONLY; no experimental allowance or exclusion is inferred.','',
        '| Gate | Status | Scope |','|---|---|---|']
    lines += [f'| {k} | {v["status"]} | {v.get("scope",v.get("included",""))} |' for k,v in gates.items()]
    lines += ['',f'Current branch: {result.testsRun} tests; failures {len(result.failures)}; errors {len(result.errors)}; skipped {len(result.skipped)}. Full regression: {args.all_tests}.',
        '', f'Inherited Module3: {inherited["tests"]} tests, {inherited["failures"]} failures, {inherited["errors"]} errors, {inherited["skipped"]} skips, in an ephemeral clone of the exact component tag on its original branch name. No branch guard is changed or waived. Current-branch compatibility is tested separately.' if args.all_tests else 'Inherited Module3 tagged-context suite not requested in this selected run.',
        '',f'Native status: {native["status"]}; maximum absolute coefficient residual: {native.get("max_abs_residual","unavailable")}.',
        '', 'Source-to-equation derivation: [MATCHING_AUDIT.md](../../module4/MATCHING_AUDIT.md). Conventions and remaining topologies: [CONVENTIONS.md](../../module4/CONVENTIONS.md). Numerical residuals: [results.json](results.json). Hashes: [source_manifest.json](source_manifest.json).',
        '', 'Reproduce: `bash scripts/run_module4_validation.sh --all-tests`. Logs/raw dumps/PDFs remain in ignored `validation/module4/local/`.',
        '', 'Modules 0–3, including their open NuFIT, global-vacuum, RG and phenomenology limitations, are unchanged. Three-body interference and mu-e conversion are outside this module.']
    (ROOT/'validation/module4/STATUS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'overall_scientific_status':report['overall_scientific_status'],'native':native['status'],'tests':report['tests']}))
    return 0 if success else 1


if __name__=='__main__':sys.exit(main())

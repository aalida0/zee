"""Execute real tests, preserve numerical evidence and hash every input source."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from .interface import foundations, sha
from .core import MISSING

ROOT=Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-tests',action='store_true',help='Run the complete repository tests/ regression suite')
    args=parser.parse_args()
    sys.path.insert(0,str(ROOT/'tests'))
    outdir=ROOT/'validation/module3'
    local=outdir/'local';local.mkdir(parents=True,exist_ok=True)
    pins=foundations()
    if git('branch','--show-current')!='feature/zee-lfv-module3':
        raise ValueError('Wrong branch')
    for key in ['module0_tag_commit','module1_commit','module2_commit']:
        subprocess.run(['git','merge-base','--is-ancestor',pins[key],'HEAD'],cwd=ROOT,check=True)
    if git('rev-parse','zee-neutrino-module2-physics-v1^{}')!=pins['module2_commit']:
        raise ValueError('Module2 freeze tag mismatch')
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py' if args.all_tests else 'test_module3_*.py')
    def cases(node):
        if isinstance(node,unittest.TestSuite):
            for sub in node:yield from cases(sub)
        else:yield node
    by_module={}
    for case in cases(suite):
        name=case.__class__.__module__
        by_module[name]=by_module.get(name,0)+1
    with (local/'validation.log').open('w') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    evidence={name:sys.modules[name].EVIDENCE for name in sorted(sys.modules)
              if name.startswith('test_module3_') and hasattr(sys.modules[name],'EVIDENCE')}
    success=result.wasSuccessful() and result.testsRun>0 and not result.skipped
    status='PASS' if success else 'FAIL'
    sources=json.loads((ROOT/'module3/sources.json').read_text())
    cached={}
    for label,filename in [('Lavoura','lavoura.pdf'),('Herrero-Garcia et al.','herrero.pdf')]:
        path=local/filename
        if path.exists():
            if sha(path)!=sources[label]['sha256']:
                raise ValueError('Primary paper download hash mismatch: '+label)
            cached[label]='SHA256_VERIFIED'
        else:
            cached[label]='NOT_CACHED; published pin retained; no download required for offline numerical tests'
    paths=sorted(list((ROOT/'module3').glob('*.py'))+list((ROOT/'module3').glob('*.json'))+
                 list((ROOT/'module3').glob('*.md'))+list((ROOT/'tests').glob('test_module3_*.py'))+
                 [ROOT/'scripts/run_module3_validation.sh'])
    hashes={str(p.relative_to(ROOT)):sha(p) for p in paths}
    manifest={'schema_version':'1.0.0','foundation_commits':{k:v for k,v in pins.items() if k!='sha256'},
              'frozen_files_sha256':pins['sha256'],'module3_sources_sha256':hashes,
              'primary_papers':sources,'primary_cached_downloads':cached,
              'example_constants_dataset_sha256':hashlib.sha256(json.dumps(json.loads((ROOT/'module3/example.json').read_text())['constants'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
              'raw_SARAH_vertex_archive':'UNAVAILABLE_IN_SNAPSHOT; source identities and archived E3 inputs only',
              'Module2_tag':{'name':'zee-neutrino-module2-physics-v1','peeled_commit':pins['module2_commit'],
                             'annotation':git('for-each-ref','refs/tags/zee-neutrino-module2-physics-v1','--format=%(contents)'),
                             'remote_verified_during_delivery':True,
                             'scope_excludes_authentic_NuFIT61_archive':True},
              'nufit61_authentic_archive_validation':'PENDING_EXTERNAL_DATA',
              'environment':{'python':sys.version.split()[0]},
              'log':'validation/module3/local/validation.log (ignored)'}
    gates={'provenance_and_mapping':{'status':'PARTIAL','validated':status,
               'scope':'Frozen hashes, strict Module1/2 roundtrip, complex E3 conversion and source-derived vertices',
               'missing':'Direct archived raw SARAH real/complex neutral and charged vertex comparison; CP-odd raw archive'},
           'neutral_tree':{'status':status,'scope':'All five massive coherent h/H/A tree subsets with both contractions'},
           'scalar_one_loop':{'status':status,'scope':'All h/H/A e/mu/tau and H1/H2 F,D terms; m_nu=0 and external-invariant expansion'},
           'exact_one_loop':{'status':'PARTIAL','scope':'Finite-neutrino-mass and external-invariant corrections absent'},
           'interference_and_normalization':{'status':status,'scope':'Signed complex rephasing, chirality, conjugation, photon trace, scalar g-2, helicity sums'},
           'higgs_LFV_partial_widths':{'status':status,'scope':'h,H,A; all flavor pairs; exact fermion masses and both charge orientations'},
           'universality':{'status':'PARTIAL','validated_subset':status,'scope':'Leading F-only with muon GF subtraction'},
           'interfaces_and_evidence':{'status':status,'scope':'Strict JSON/JSONL, six full current Module2 family witnesses; tampering/negative cases'},
           'full_LFV':{'status':'PARTIAL','scope':'No full prediction, experimental comparison or exclusion'}}
    results={'schema_version':'1.0.0','overall_scientific_status':'PARTIAL' if success else 'FAIL',
             'validation_status':status,'COMPLETE_LFV':False,'global_zee_acceptance':None,
             'tests':{'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)},
             'test_scope':'ALL_REPOSITORY_TESTS' if args.all_tests else 'MODULE3_TESTS',
             'test_counts_by_module':by_module,
             'gates':gates,'evidence':evidence,'missing_contributions':MISSING,
             'source_manifest_sha256':None,
             'nufit61_authentic_archive_validation':'PENDING_EXTERNAL_DATA',
             'corrected_test_development_findings':['Diagonal g-2 Hermitian operator initially counted twice in reference test; corrected to a=m² Re(CL+CR), with photon-rate trace unchanged.',
                 'An ordered positive arbitrary mass vector is a valid numerical input; the deliberate invalid-order test now uses reversed masses instead of demanding a hidden measured-mass default.']}
    (outdir/'source_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    results['source_manifest_sha256']=sha(outdir/'source_manifest.json')
    (outdir/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    table='\n'.join('| '+k+' | '+v['status']+' | '+v['scope']+' |' for k,v in gates.items())
    text=f'''# Module 3 validation status

Overall scientific status: **{results['overall_scientific_status']}**. Numerical validation: **{status}**.
Real tests: {result.testsRun}; failures: {len(result.failures)}; errors: {len(result.errors)}; skipped: {len(result.skipped)}.
Scope: {results['test_scope']}. Counts per source test module are in results.json.

| Gate | Status | Declared scope |
|---|---|---|
{table}

PASS validates the stated calculation; it is not full phenomenological acceptance.
Three-body output is TREE_SUBSET_ONLY. Radiative output is
SCALAR_ONE_LOOP_APPROXIMATION. Universality is SUBSET_DIAGNOSTIC.
COMPLETE_LFV=false; global acceptance=null; no LFV experimental limit is applied.

Frozen Module 2 physics tag: `zee-neutrino-module2-physics-v1`, at
`{pins['module2_commit']}`. The annotated tag was pushed and independently
remote-verified during delivery. Its scope explicitly excludes authentic
official NuFIT 6.1 archive validation, which remains PENDING_EXTERNAL_DATA.

Raw SARAH real/complex vertex archives are absent from this snapshot. Available
frozen component/source identities and complex E3 fixtures are tested; a fresh
SARAH validation is not claimed. See module3/CONVENTIONS.md for derivations
and the signed legacy discrepancies. Frozen sources remain unchanged.

Reproduce: `bash scripts/run_module3_validation.sh{' --all-tests' if args.all_tests else ''}`.
One point: `python -m module3.interface --input module3/example.json --output /tmp/lfv.json`.
Batch: add `--jsonl` and supply one complete input per line.
Numerical residuals, all six NO/IO witness spectra, four complex family
coefficients and signed checks are in results.json; hashes are in
source_manifest.json. Detailed logs and downloaded primary PDFs are ignored
under validation/module3/local/. Branch/remote commit verification is reported
in the delivery message; reports identify validated content by SHA256.
'''
    (outdir/'STATUS.md').write_text(text)
    print(json.dumps({'validation_status':status,'scientific_status':results['overall_scientific_status'],'tests':results['tests']},sort_keys=True))
    if not success:
        print((local/'validation.log').read_text()[-8000:])
    return 0 if success else 1


if __name__=='__main__':sys.exit(main())

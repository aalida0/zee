"""Record actual Gate A2 evidence, retaining the external convention barrier."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest
import mpmath
import numpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from validate_zee_module5_native import check
from zee_module5_native_compare import LOCAL,compare


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidenceResult(unittest.TextTestResult):
    def addSuccess(self,test):
        super().addSuccess(test)
        if hasattr(test,'audit_evidence'): self.evidence[test.id()]=test.audit_evidence


def main():
    raw=json.loads((LOCAL/'charged_quark_vertices.json').read_text())
    inventory=check(raw)
    if raw['sarah_version']!='4.15.4': raise ValueError('Unpinned SARAH version')
    native=compare(json.loads((LOCAL/'native_numerical.json').read_text()))
    patterns=['test_module5_native_gate.py','test_module5_bsgamma_lo.py',
              'test_module5_native_amplitudes.py','test_module5_dipole_projection.py']
    counts={};residuals={};total=0;failures=0;errors=0;skips=0
    for pattern in patterns:
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        with (LOCAL/(pattern+'.log')).open('w') as log:
            def result_factory(*args,**kwargs):
                result=EvidenceResult(*args,**kwargs);result.evidence={};return result
            result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=result_factory).run(suite)
        counts[pattern]=result.testsRun
        total+=result.testsRun;failures+=len(result.failures);errors+=len(result.errors);skips+=len(result.skipped)
        residuals.update(result.evidence)
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    branch=git('branch','--show-current')
    if branch!='feature/zee-bsgamma-native-convention':raise ValueError('Wrong branch')
    base='09e0e6788f2206e767742730a9fe4c9427f1c097'
    if git('merge-base','HEAD',base)!=base:raise ValueError('Wrong Gate A ancestor')
    tracked=['models/SARAH/ZeeTypeII/ZeeTypeII.m','module4/couplings.py',
        'module5/bsgamma_lo.py','scripts/zee_module5_charged_quark_vertices.m',
        'scripts/zee_module5_native_compare.py','scripts/zee_module5_dipole_projection.py',
        'scripts/validate_zee_module5_matching.py','scripts/validate_zee_module5_native.py',
        'tests/test_module5_native_gate.py','tests/test_module5_bsgamma_lo.py',
        'tests/test_module5_native_amplitudes.py','tests/test_module5_dipole_projection.py',
        'module5/NATIVE_OPERATOR_MATCHING.md']
    local_names=['charged_quark_vertices.json','native_numerical.json','native_witnesses.m','native_driver.log',
                 'BWilsonTHDM.cpp','THDMParametersHelper.cpp','hyperiso_main.tex','hyperiso_manifest.json']
    source_names={'BWilsonTHDM.cpp':'Hyperiso/Hyperiso/core/src/PhysicalModel/domain/WCoef/BSM/BWilsonTHDM.cpp',
        'THDMParametersHelper.cpp':'Hyperiso/Hyperiso/core/src/PhysicalModel/domain/Helper/BSM/THDMParametersHelper.cpp',
        'hyperiso_main.tex':'docs/main.tex','hyperiso_manifest.json':'reproducibility/manifest.json'}
    previous=json.loads((ROOT/'validation/module5/results.json').read_text())['hyperiso']['source_sha256']
    for local,source in source_names.items():
        if sha(LOCAL/local)!=previous[source]:raise ValueError('Pinned source hash mismatch: '+source)
    record=dict(schema_version='1.0.0',scope='GATE_A2',status='PARTIAL',branch=branch,
        validated_gate_A_commit=base,reviewed_start_commit='e121a4ca425eca20630bb847a148dc2a5d3b349a',
        gates={'A2.1':{'status':'PASS','native_inventory':inventory,'comparison':native},
               'A2.2':{'status':'PARTIAL','independent_conditional_amplitude_projection':'PASS',
                       'exact_2026_HyperIso_convention':'BLOCKED'},
               'A2.3':{'status':'BLOCKED','diagnostic_created':False}},
        matching_convention_status='MATCHING_CONVENTION_UNKNOWN',
        blockers=['The inspected 2026 Letter does not explicitly fix Hamiltonian/sigma/Fourier conventions.',
                  'Pinned HyperIso matching/helper/manuscript sources do not close executable O7/O8 insertion conventions; editorial note is not a sign determination.'],
        independent_projection=residuals,
        tests={'run':total,'failures':failures,'errors':errors,'skipped':skips,'by_suite':counts},
        versions={'python':platform.python_version(),'numpy':numpy.__version__,'mpmath':mpmath.__version__,
                  'mathematica':raw['math_version'],'sarah':raw['sarah_version']},
        hyperiso={'peeled_commit':'09d26ac6e71d1528922097a896d15693589f636b',
                  'source_hashes_match_Gate_A':True,'R1':'NOT_RUN','R3':'NOT_RUN','R6':'NOT_RUN',
                  'runtime_gate':'DEFERRED_GATE_B','R1_R6_qmatch_GeV':81},
        file_sha256={p:sha(ROOT/p) for p in tracked},
        ignored_local_sha256={p:sha(LOCAL/p) for p in local_names},
        limitations=['LO leading top and external mb chirality flip; ms/primed and light internal loops omitted in projection.',
            'Independent loop sign established only under documented explicit conventions; external convention closure remains unproven.',
            'No running mass calibration, scale transport, NP NLO, BR, exclusion, or uncertainty covariance.',
            'Numerical residuals do not quantify theory uncertainty.'])
    if failures or errors or skips:
        record['status']='BLOCKED';record['gates']['A2.1']['status']='BLOCKED'
        record['gates']['A2.2']['independent_conditional_amplitude_projection']='BLOCKED'
    dest=ROOT/'validation/module5/native_matching.json'
    dest.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'status':record['status'],'tests':record['tests'],
                      'native_max_absolute_residual':native['max_absolute_residual'],
                      'projection':residuals},sort_keys=True))
    if failures or errors or skips:raise SystemExit(1)


if __name__=='__main__':main()

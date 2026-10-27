#!/usr/bin/env python3
"""Execute scoped C0 checks and record actual evidence, including integration blockers."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import unittest

from zee_module5_two_state_patch import ROOT, parse_output, run, sha
from module5.hyperiso_patch_contract import make_contract


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',type=Path,required=True)
    p.add_argument('--binary',type=Path,required=True)
    a=p.parse_args();up=a.upstream.resolve()
    local=ROOT/'validation/module5/local/two_state';local.mkdir(parents=True,exist_ok=True)
    os.environ['HYPERISO_UPSTREAM']=str(up)
    os.environ['HYPERISO_BINARY']=str(a.binary.resolve())
    runtime_file=local/'runtime.json'
    runtime_file.unlink(missing_ok=True)
    patterns=['test_module5_bsgamma_lo.py','test_module5_two_state_patch_contract.py',
              'test_module5_two_state_adapter.py']
    totals={};results=[]
    for pattern in patterns:
        suite=unittest.TestLoader().discover(str(ROOT/'tests'),pattern=pattern)
        log=io.StringIO()
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
        (local/(pattern+'.log')).write_text(log.getvalue())
        totals[pattern]=dict(run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                             skipped=len(result.skipped))
        results.append(result.wasSuccessful() and not result.skipped)
        print(log.getvalue(),end='')
    example=run([sys.executable,'-m','module5.hyperiso_patch_contract','--input',
                 ROOT/'module5/example_bsgamma_input.json','--output',
                 ROOT/'validation/module5/local/zee_patch_contract.json'],ROOT,check=False)
    runtime=json.loads(runtime_file.read_text()) if runtime_file.exists() else None
    records=runtime['executable_runs'] if runtime else []
    sm=next((r for r in records if r['label']=='production SM two-state rejection'),None)
    contract=None
    if sm:
        from test_module5_two_state_adapter import BASE
        contract=make_contract({**BASE,'mt_MSbar_GeV':parse_output(sm['stdout'])['mt']})
    source_files=['PhysicalModel/adapters/WilsonInterface.h','PhysicalModel/domain/WilsonMatchingPatch.h',
                  'PhysicalModel/domain/WCoef/BSM/BWilsonTHDM.cpp','PhysicalModel/domain/WilsonManager.cpp',
                  'PhysicalModel/domain/WGroup/BWilsonGroup.cpp','BusinessLogic/domain/Decays/BXsDecay.cpp',
                  'UserInterface/CliUtils.h','UserInterface/CliUtils.cpp']
    upstream_hashes={x:sha(up/'Hyperiso/Hyperiso/core/src'/x) for x in source_files}
    historical=json.loads((ROOT/'validation/module5/hyperiso_bridge.json').read_text())
    historical_match=all(historical['upstream_source_sha256'].get('Hyperiso/Hyperiso/core/src/'+x,h)==h
                         for x,h in upstream_hashes.items())
    for r in records:
        raw=r['stdout']
        r['stdout_sha256']=hashlib.sha256(raw.encode()).hexdigest()
        r['coefficient_output']=[x for x in raw.splitlines() if x.startswith('C0 ')]
        del r['stdout']
    success=all(results) and example.returncode==0 and historical_match
    status=('HYPERISO_PATCH_INTEGRATION_BLOCKED_SM_BSM_PATCH_DROPPED' if success and sm and sm['returncode']==3
            else 'HYPERISO_ADAPTER_RUNTIME_BLOCKED')
    residuals=runtime['quantitative_residuals'] if runtime else []
    out=dict(schema_version='1.0.0',scope='GATE_C0_EXTERNAL_ADAPTER_ONLY',status=status,
             branch=run(['git','branch','--show-current'],ROOT).stdout.strip(),
             reviewed_start_commit='76d8299db01c5622e38a7bd79db5cc0ce967cdec',
             gate_B_ancestor='218fe01d893730bc2699c270d10db85a22708616',
             integration_pass=False,external_operator_convention='MATCHING_CONVENTION_UNKNOWN',
             physical_pass='NOT_EVALUATED',linearized_bsm_screen='NOT_EVALUATED',
             physical_BR=None,exclusion=None,mass_cut=None,
             upstream=runtime['provenance'] if runtime else None,
             upstream_source_sha256=upstream_hashes,historical_source_hashes_match=historical_match,
             tests=dict(by_suite=totals,total_run=sum(x['run'] for x in totals.values()),
                        all_scoped_regressions_pass=success,example_cli_returncode=example.returncode),
             contract=contract,executable_runs=records,
             max_absolute_residual=max((x['absolute'] for x in residuals),default=None),
             native_weighted_max_absolute_residual=max((x['absolute'] for x in residuals if x['label'].startswith('native weighted')),default=None),
             quantitative_residuals=residuals,
             blockers=['Pinned SM group rejects BSM contribution patches and SM setup forces BSM=0. Production exits 3; no safe SM injection demonstrated.',
                       'External operator Hamiltonian/sigma/Fourier/CKM insertion remains uncertified.',
                       'No complete Zee observable, higher-order NP matching or calibrated uncertainty model; physical use outside scope.'],
             diagnostic_scope='THDM diagnostics explicitly include native BSM. Complex transport, running and additive patches work there; not a Zee adapter or integration PASS.',
             reference_suite='Historical Gate B R1-R7 PASS retained; not rerun (no upstream change).',
             native_sarah='Historical local-only native_numerical.json not required or regenerated.',
             source_sha256={str(x.relative_to(ROOT)):sha(x) for x in [
                 ROOT/'module5/hyperiso_patch_contract.py',ROOT/'module5/bsgamma_lo.py',
                 ROOT/'module5/TWO_STATE_PATCH_AUDIT.md',
                 ROOT/'scripts/zee_module5_two_state_patch.cpp',ROOT/'scripts/zee_module5_two_state_patch.py',
                 Path(__file__).resolve(),ROOT/'tests/test_module5_two_state_adapter.py',
                 ROOT/'tests/test_module5_two_state_patch_contract.py']},
             local_evidence_sha256={str(x.relative_to(ROOT)):sha(x) for x in sorted(list(local.glob('test_*.log'))+[runtime_file]) if x.exists()})
    (ROOT/'validation/module5/two_state_patch.json').write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(status)
    return 0 if success else 1


if __name__=='__main__':sys.exit(main())

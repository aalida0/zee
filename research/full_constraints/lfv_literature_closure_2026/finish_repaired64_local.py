"""One-command execution of EDM-repaired 64 on user's source-attested native model.

This is intentionally a *local* execution: the original full ZeeTypeII
SARAH/SPheno 4.0.5 source and model-specific binary are not public. The
GitHub Actions synthetic SLHA fixture is never accepted as a physics run.

Example:
  python -m research.full_constraints.lfv_literature_closure_2026.finish_repaired64_local \
    --source ~/Downloads/zee-edm-suppressed-64-new-textures-full.zip

The script knows the previously validated template and corrected SPheno
work paths; both can be overridden explicitly for a relocated installation.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json
from pathlib import Path
from zipfile import ZipFile, is_zipfile

from .stage_edm_repaired_native_64 import build as stage_cards
from .run_repaired64_native_source import execute as run_native
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import (
    EXPECTED_SOURCES, attest_compiled_nuclear_correction, check_source_bundle
)

DEFAULT_WORK=Path('~/zee-lfv64-serial-20261112-094549').expanduser()
DEFAULT_TEMPLATE=Path('~/zee-conditional-cascade-scan/validation/module14/local/runtime/group0/tree.in').expanduser()
ZIP_MEMBER='EDM_SUPPRESSED_64_NEUTRINO_AND_2HDM.json'

def require_file(p,label):
    if not p.is_file():
        raise FileNotFoundError(label+': '+str(p))
    return p

def source_json(inp,outdir):
    require_file(inp,'Repaired 64 JSON/ZIP source')
    if is_zipfile(inp):
        with ZipFile(inp) as z:
            names=[n for n in z.namelist() if n.split('/')[-1]==ZIP_MEMBER]
            if len(names)!=1:
                raise ValueError('Archive must contain exactly one authenticated repaired 64 JSON')
            raw=z.read(names[0])
        dest=outdir/ZIP_MEMBER
        dest.write_bytes(raw)
        result=dest
    else:
        result=inp
    data=json.loads(result.read_text())
    if data.get('n_original_16x4')!=64 or data.get('n_neutrino_exact_perturbative')!=64 or data.get('n_below_MEGII_one_loop')!=64 or data.get('n_below_JILA_pure_2HDM_proxy')!=64:
        raise ValueError('Wrong repaired 64 source status')
    records=data.get('records',[])
    if len(records)!=64 or len({(r['id'],r['ordering'],r['seed']) for r in records})!=64:
        raise ValueError('Missing or duplicated original source identities')
    if len({r['id'] for r in records})!=16:
        raise ValueError('Expected 16 fixed original scalar spectra')
    if any(r.get('full_physical_LFV') is not None or r.get('global_acceptance') is not None for r in records):
        raise ValueError('Source incorrectly claims prior global physics acceptance')
    return result

def preflight(work,template):
    require_file(template,'Original source-validated ZeeTypeII tree-scheme template')
    binary=require_file(work/'SPheno-4.0.5/bin/SPhenoZeeTypeII','Corrected generated-model SPhenoZeeTypeII')
    receipt=require_file(work/'model-rebuild-attestation.json','Actual original forced-build attestation')
    original={name:require_file(work/'original-five'/name, 'Original generated model source') for name in EXPECTED_SOURCES}
    r=json.loads(receipt.read_text())
    if not attest_compiled_nuclear_correction(r,binary):
        raise ValueError('Cannot attest exact two-sign nuclear-corrected SPheno binary')
    verified=check_source_bundle(original)
    if verified!=EXPECTED_SOURCES:
        raise ValueError('Original model hashes differ from the validated generated Fortran source')
    return binary,receipt,original

def finalize(source,work,template,output_root,preflight_only=False):
    binary,receipt,sources=preflight(work,template)
    if output_root.exists(): raise FileExistsError('Refuse overwrite: '+str(output_root))
    output_root.mkdir(parents=True)
    src=source_json(source,output_root)
    if preflight_only:
        print('ORIGINAL_NATIVE_PREFLIGHT_PASS',binary,receipt)
        print('REPAIRED64_SOURCE_PASS',src)
        print('NATIVE_EXECUTION_NOT_REQUESTED; PHYSICAL_LFV_UNKNOWN')
        return None
    card_dir=output_root/'native-source-64-cards'
    result_dir=output_root/'native-source-64-results'
    stage=stage_cards(src,template,card_dir,'VALIDATED_USER_NATIVE')
    if stage.get('n_cards')!=64 or stage.get('template_provenance')!='VALIDATED_USER_NATIVE':
        raise RuntimeError('Cannot trust native card staging')
    result=run_native(src,template,card_dir,binary,receipt,sources,result_dir)
    count=result['all_source1loop_three_bounds']
    report={
        'status':'LFV_SOURCE_ONE_LOOP_SCREEN_COMPLETED' if count==64 else 'LFV_SOURCE_ONE_LOOP_EXCLUSIONS_PRESENT',
        'n_source1loop_three_observables_below_limits':count,
        'n_executed':result['n_new_edm3zero_cases'],
        'max_source_1loop_rates':result['max_1loop_source_observables'],
        'completed_loop_order':'MODEL_SPECIFIC_NATIVE_SOURCE_ONE_LOOP',
        'original_model_source_attested':True,
        'nuclear_scalar_sign_patch_attested':True,
        'matched_native_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
        'source_json_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'full_Zee_two_loop_EDM_and_LFV':'UNKNOWN',
        'modern_LEFT_and_nuclear_conversion':'UNKNOWN',
        'physical_LFV':None,
        'global_zee_acceptance':None,
        'caveat':'No full physical LFV completion or global parameter-space acceptance is inferred from a complete one-loop source screen.',
    }
    (output_root/'SOURCE_ONE_LOOP_FINAL_REPAIR64_RECEIPT.json').write_text(
        json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(report['status'],count,'of 64')
    print('IMPORTANT: FULL_PHYSICAL_ZEE_LFV_UNKNOWN (EDM, two-loop and modern LEFT uncertainties)')
    print('NATIVE_RECEIPT',output_root/'SOURCE_ONE_LOOP_FINAL_REPAIR64_RECEIPT.json')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True,help='Repaired64 complete JSON or GitHub Actions ZIP')
    ap.add_argument('--work',type=Path,default=DEFAULT_WORK)
    ap.add_argument('--template',type=Path,default=DEFAULT_TEMPLATE)
    ap.add_argument('--output-root',type=Path,default=None)
    ap.add_argument('--preflight-only',action='store_true')
    a=ap.parse_args()
    work,template=a.work.expanduser(),a.template.expanduser()
    output=a.output_root or work/('EDM3ZERO_SOURCE64_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    finalize(a.source.expanduser(),work,template,output,a.preflight_only)
if __name__=='__main__':main()

"""Execute native ORIGINAL ZeeTypeII one-loop source on the new EDM-repaired 64.

Needs source-attested nuclear-corrected ORIGINAL SPhenoZeeTypeII executable
and an original USER-VALIDATED, tree-scheme native input template, not the
synthetic CI staging cards. Throws if any part of the mass/Yukawa scheme,
source tree or executable attestation drifts. Does not compute full EDM or
two-loop Zee electroweak LFV.
"""
from __future__ import annotations
import argparse,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
from module2.interface import decode,encode
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import (
    tree_scheme_mass_gate,native_yukawa_gate,parse_observables,
    attest_compiled_nuclear_correction,EXPECTED_SOURCES,check_source_bundle,
)
from .stage_edm_repaired_native_64 import MASS

LIMITS={'mu_to_e_gamma':1.5e-13,'mu_to_3e':1.0e-12,
        'mu_to_e_conversion_Au197':7.0e-13}

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_native_isolated(exe: Path, inp: Path, result_dir: Path, *, timeout=180):
    """Run one genuine model card in a clean directory and preserve SPheno messages.

    SARAH/SPheno may write the default SPheno.spc.ZeeTypeII instead of the
    optional explicit output. Accept default ONLY if isolated and nonempty.
    """
    case = result_dir / inp.stem
    if case.exists():
        raise FileExistsError("SPheno case directory already exists: " + str(case))
    case.mkdir(parents=True)
    # Very long absolute card/output names can exceed fixed-length Fortran
    # filename buffers. Copy exact validated input into a short, isolated path.
    local_input = case / "input.in"
    local_input.write_bytes(inp.read_bytes())
    if digest(local_input) != digest(inp):
        raise ArithmeticError("Native short input copy changed the SLHA source bytes")
    explicit = case / "output.spc"
    default = case / "SPheno.spc.ZeeTypeII"
    runlog = case / "spheno.stdout.stderr.log"
    cmd = [str(exe.resolve()), "input.in", "output.spc"]
    try:
        proc = subprocess.run(cmd, cwd=case, capture_output=True, text=True,
                              timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        runlog.write_text("SPheno timed out; command=" + repr(cmd) + "\n")
        raise RuntimeError("SPheno timeout; log " + str(runlog)) from exc
    runlog.write_text("COMMAND " + repr(cmd) + "\nEXIT_STATUS " +
                      str(proc.returncode) + "\nSTDOUT\n" + proc.stdout +
                      "\nSTDERR\n" + proc.stderr)
    messages = [x for x in sorted(case.iterdir()) if x.is_file()
                and ("message" in x.name.lower() or "error" in x.name.lower())]
    files = [x.name for x in sorted(case.iterdir()) if x.is_file()]
    diagnostics = "\n".join(x.name + ":\n" +
                    x.read_text(errors="replace")[-3500:] for x in messages)
    if proc.returncode != 0:
        raise RuntimeError("SPheno exit %d; log %s; messages %s" %
                           (proc.returncode,runlog,diagnostics[-4000:]))
    outputs = [x for x in (explicit,default) if x.is_file() and x.stat().st_size > 0]
    if len(outputs) > 1:
        raise RuntimeError("Ambiguous two nonempty SPheno outputs in " + str(case))
    if not outputs:
        raise RuntimeError(
            "SPheno exit 0 but NO NONEMPTY SPECTRUM; case %s; files %s; "
            "log %s; stdout tail %r; stderr tail %r; messages %s" %
            (case,files,runlog,proc.stdout[-2400:],proc.stderr[-2400:],diagnostics[-4000:]))
    return outputs[0],runlog,{
        "case_directory":str(case),
        "output_mode":"explicit" if outputs[0]==explicit else "default",
        "original_input_sha256":digest(inp),
        "short_input_copy_sha256":digest(local_input),
        "stdout_log":str(runlog),
        "auxiliary_diagnostics":[str(x) for x in messages],
        "returncode":proc.returncode}


def execute(source,template,staged,exe,receipt,original_sources,output_dir):
    if output_dir.exists():raise FileExistsError('Existing output cannot be overwritten')
    src=json.loads(source.read_text());cards=src['records']
    if len(cards)!=64 or src.get('n_neutrino_exact_perturbative')!=64:
        raise ValueError('Unexpected new neutrino/EDM source family')
    scalar={x['id']:x for x in source_points()}
    old=json.loads((staged/'manifest-new-EDM3zero.json').read_text())
    if old['template_provenance']!='VALIDATED_USER_NATIVE':
        raise ValueError('Synthetic or unknown SPheno template is NOT physics valid')
    if old['template_sha256']!=digest(template) or old['source_file_SHA256']!=digest(source):
        raise ValueError('Model template/source identity mismatch')
    if old['n_cards']!=64:raise ValueError('Incomplete original model card staging')
    build=json.loads(receipt.read_text())
    if not attest_compiled_nuclear_correction(build,exe):
        raise ValueError('Original SPheno binary not rebuilt with two-sign nuclear repair')
    verified=check_source_bundle(original_sources)
    if verified!=EXPECTED_SOURCES:
        raise ValueError('Five original sources have drifted')
    indexes={(r['id'],r['ordering'],r['seed']):r for r in cards}
    out=[]
    output_dir.mkdir(parents=True)
    for row in old['cards']:
        k=tuple(row['id'])
        if k not in indexes:
            raise ValueError('Missing new model source identity')
        card=indexes[k];p=scalar[k[0]]['input_card']['physical']
        if card['source_scalar_sha256']!=row['source_scalar_sha256']:
            raise ValueError('Original physical mass source drift')
        inp=staged/row['SLHA']
        if digest(inp)!=row['sha256_SLHA']:
            raise ValueError('Changed native SLHA source card')
        final,log,native_exec=run_native_isolated(exe,inp,output_dir)
        spectrum=tree_scheme_mass_gate(final.read_text(),p)
        F,D=decode(card['Yukawas']['F']),decode(card['Yukawas']['D'])
        beta=p['beta']
        YeSM=np.sqrt(2)*np.diag(MASS/p['v'])
        Ye2=np.cos(beta)*D+np.sin(beta)*YeSM
        native_lep={'F':encode(F),'D':encode(D),'Ye2':encode(Ye2)}
        try:
            yuk=native_yukawa_gate(final.read_text(),p,native_lep)
        except ValueError as exc:
            # Preserve original model-output mismatch; never loosen tolerance.
            from .diagnose_native_yukawas import inspect_case
            case=Path(native_exec["case_directory"])
            detail=inspect_case(case)
            report=case/"NATIVE_YUKAWA_MISMATCH_DIAGNOSTIC.json"
            if report.exists():
                raise FileExistsError("Refuse overwrite prior mismatch diagnostic") from exc
            report.write_text(json.dumps(detail,indent=2,allow_nan=False)+"\\n")
            fcmp=detail["FZEE"]
            ycmp=detail["YEE2"]
            raise ValueError(
                "Native Zee Yukawa validation failed for %s: %s; "
                "FZEE input/output max-relative=%g, YEE2 max-relative=%g; "
                "best-fit complex F normalization=%s; diagnostics=%s"
                % (k,exc,fcmp["max_relative_to_source_max"],
                   ycmp["max_relative_to_source_max"],
                   fcmp["best_complex_multiplicative_factor"],report)
            ) from exc
        # Also retain the NEW EDM-repaired diagonal electron zero.
        if abs(D[0,0])>1e-10 or max(abs(D[0,1]),abs(D[1,0]))>1e-10:
            raise ValueError('D electron original target broken')
        rates=parse_observables(final.read_text())
        cmp={k:{'BR_or_CR_source1loop':rates[k],'limit_90CL':v,
                'source1loop_below_limit':rates[k]<v} for k,v in LIMITS.items()}
        out.append({'id':list(k),'native_mass_matching':spectrum,'native_yukawa_matching':yuk,
                    'rate_1loop_source':rates,'experiment_comparison':cmp,
                    'native_spectrum_SHA256':digest(final),'native_log_SHA256':digest(log),
                    'native_spheno_execution':native_exec,
                    'original_source_sha256':verified,
                    'full_physical_LFV':None,'global_acceptance':None})
        print('NEW_EDM3ZERO_NATIVE',*k,
              'MUEG',rates['mu_to_e_gamma'],
              'MU3E',rates['mu_to_3e'],
              'AU_HISTORICAL',rates['mu_to_e_conversion_Au197'],
              flush=True)
    if len(out)!=64 or len({tuple(x['id']) for x in out})!=64:
        raise ValueError('Not all 64 new original model solutions were checked')
    result={'status':'NEW_64_ATTTESTED_ORIGINAL_ZEE_NATIVE_ONELOOP_SCREEN',
        'n_new_edm3zero_cases':64,
        'all_source1loop_three_bounds':sum(all(x['experiment_comparison'][name]['source1loop_below_limit'] for name in LIMITS) for x in out),
        'max_1loop_source_observables':{k:max(x['rate_1loop_source'][k] for x in out) for k in LIMITS},
        'source_5_original_hashes':verified,
        'original_pn_patched_binary_SHA256':digest(exe),
        'native_rebuilt_source_receipt_SHA256':digest(receipt),
        'source_scoped_1loop_only':True,
        'physical_LFV':None,'physical_conversion_with_modern_LEFT':None,'physical_electron_EDM':None,
        'global_acceptance':None,'cases':out}
    (output_dir/'NEW_EDM3ZERO_NATIVE_64_SOURCE_ONELOOP.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('NEW_NATIVE_64_ONELOOP_SCREEN',result['all_source1loop_three_bounds'],'OF 64; FULL_PHYSICAL_LFV_UNKNOWN')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--template',type=Path,required=True)
    p.add_argument('--staged-cards',type=Path,required=True)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--build-receipt',type=Path,required=True)
    p.add_argument('--original-fortran-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    original={name:a.original_fortran_dir/name for name in EXPECTED_SOURCES}
    execute(a.source,a.template,a.staged_cards,a.binary,a.build_receipt,original,a.output_dir)

if __name__=='__main__':main()

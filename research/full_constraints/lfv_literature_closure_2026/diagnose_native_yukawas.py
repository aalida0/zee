"""Read-only native Zee FZEE mismatch audit on an existing failed SPheno case.

Never modifies a spectrum or promotes physical LFV. Reads original short input
and native output in latest EDM3ZERO_SOURCE64 run, compares FZEEIN/FZEE,
IMFZEEIN/IMFZEE, YEE2IN/YEE2 and reconstructed D, and diagnoses whether
the disagreement resembles overall normalization/running, complex conjugation,
transpose, missing imaginary parts or entirely ignored input.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import (
    split_slha, block_values, matrix_from_native
)
from module2.interface import decode


def _parse_card_matrix(slha, stem):
    blocks=split_slha(slha,allowed_repeated=("SPHENOINPUT",))
    if stem not in blocks:
        raise ValueError("Required model-specific SLHA block absent: " + stem)
    real=block_values(blocks[stem])
    imag=block_values(blocks["IM"+stem]) if "IM"+stem in blocks else {}
    expected={(i,j) for i in range(1,4) for j in range(1,4)}
    if set(real)!=expected or (imag and set(imag)!=expected):
        raise ValueError("Wrong 3x3 original SLHA matrix shape: " + stem)
    return np.array([[complex(real[i,j],imag.get((i,j),0.))
                      for j in range(1,4)] for i in range(1,4)])


def _comparison(source, actual):
    source=np.asarray(source,complex);actual=np.asarray(actual,complex)
    if source.shape!=(3,3) or actual.shape!=(3,3):
        raise ValueError("Only full 3x3 complex matrices")
    if not np.isfinite(source).all() or not np.isfinite(actual).all():
        raise ValueError("Nonfinite source/observed Yukawa")
    scale=max(float(np.max(np.abs(source))),1e-12)
    a=actual-source
    ix=np.unravel_index(int(np.argmax(np.abs(a))),a.shape)
    source_vec=source.flatten();observed_vec=actual.flatten()
    norm=np.vdot(source_vec,source_vec)
    fit=complex(np.vdot(source_vec,observed_vec)/norm) if abs(norm)>0 else 0j
    fit_remainder=float(np.linalg.norm(actual-fit*source)/(np.linalg.norm(actual)+1e-30))
    def enc(z):return [float(np.real(z)),float(np.imag(z))]
    transformations={
        "direct": source,
        "negative": -source,
        "conjugate":source.conj(),
        "transpose":source.T,
        "conjugate_transpose":source.conj().T,
        "imaginary_parts_discarded":source.real.astype(complex),
    }
    trial={k:float(np.linalg.norm(actual-value)/(np.linalg.norm(actual)+np.linalg.norm(value)+1e-30))
           for k,value in transformations.items()}
    return {
        "source_scale_max_abs":scale,
        "output_max_abs":float(np.max(np.abs(actual))),
        "max_abs_delta":float(np.max(np.abs(a))),
        "max_relative_to_source_max":float(np.max(np.abs(a))/scale),
        "max_difference_entry_one_indexed":[int(ix[0])+1,int(ix[1])+1],
        "source_at_max_difference":enc(source[ix]),
        "output_at_max_difference":enc(actual[ix]),
        "best_complex_multiplicative_factor":enc(fit),
        "residual_after_best_complex_scale":fit_remainder,
        "direction_candidates_normalized_residuals":trial,
        "max_abs_input_imaginary":float(np.max(np.abs(source.imag))),
        "max_abs_output_imaginary":float(np.max(np.abs(actual.imag))),
        "source_antisymmetry_max":float(np.max(np.abs(source+source.T))),
        "output_antisymmetry_max":float(np.max(np.abs(actual+actual.T))),
        "source_rows_complex": [[enc(z) for z in row] for row in source],
        "output_rows_complex": [[enc(z) for z in row] for row in actual],
    }


def inspect_case(case:Path):
    input_file=case/"input.in"
    output_file=case/"output.spc"
    if not output_file.is_file():
        output_file=case/"SPheno.spc.ZeeTypeII"
    if not input_file.is_file() or not output_file.is_file():
        raise FileNotFoundError("Expected saved input.in and SPheno spectrum in "+str(case))
    inp,out=input_file.read_text(),output_file.read_text()
    inp_blocks=split_slha(inp,allowed_repeated=("SPHENOINPUT",))
    out_blocks=split_slha(out)
    fstem=next((x for x in ("FZEEIN","FZEE") if x in inp_blocks),None)
    ystem=next((x for x in ("YEE2IN","YEE2") if x in inp_blocks),None)
    if fstem is None or ystem is None:
        raise ValueError("Input does not contain Zee complex Yukawa blocks")
    actual_f=matrix_from_native(out_blocks,"FZEE")
    actual_y=matrix_from_native(out_blocks,"YEE2")
    expected_f=_parse_card_matrix(inp,fstem)
    expected_y=_parse_card_matrix(inp,ystem)
    controls=[]
    for line in inp.splitlines():
        if line.strip().upper().startswith("BLOCK SPHENOINPUT"):
            controls.append({"block":line.strip(),"settings":[]})
        elif controls and line.strip().upper().startswith("BLOCK "):
            controls.append({"block":line.strip(),"settings":[]})
        elif controls and controls[-1]["block"].upper().startswith("BLOCK SPHENOINPUT"):
            tokens=line.partition("#")[0].split()
            if len(tokens)>=2 and tokens[0] in ("11","12","14","15","57","76"):
                controls[-1]["settings"].append(tokens[:2])
    mass=block_values(out_blocks["MASS"]) if "MASS" in out_blocks else {}
    scales=[]
    for name in ("FZEE","YEE2","GAUGE","HMIX","YU","YE"):
        for line in out.splitlines():
            if line.strip().upper().startswith("BLOCK "+name+" "):
                scales.append(line.strip())
    payload={
        "status":"NATIVE_YUKAWA_MISMATCH_DIAGNOSTIC_ONLY",
        "case_directory":str(case),
        "input_stems":{"F":fstem,"Y":ystem},
        "FZEE":_comparison(expected_f,actual_f),
        "YEE2":_comparison(expected_y,actual_y),
        "SPhenoInput_control_blocks":controls,
        "spectrum_block_scales":scales,
        "source_beta_from_input_tanbeta":math.atan(block_values(inp_blocks["MINPAR"])[(10,)]),
        "output_tanbeta":block_values(out_blocks["MINPAR"]).get((10,)) if "MINPAR" in out_blocks else None,
        "LFV_input_accepted":None,
        "full_physical_LFV":None,
    }
    if "YE" in out_blocks:
        ye=matrix_from_native(out_blocks,"YE")
        beta=math.atan(float(payload["output_tanbeta"]))
        d=-math.sin(beta)*ye+math.cos(beta)*actual_y
        payload["native_reconstructed_D"]={
            "e_mu_abs":float(abs(d[0,1])),"mu_e_abs":float(abs(d[1,0])),
            "e_e_abs":float(abs(d[0,0])),
        }
    return payload


def latest_case(work:Path):
    runs=sorted([p for p in work.glob("EDM3ZERO_SOURCE64_*") if p.is_dir()])
    for root in reversed(runs):
        folder=root/"native-source-64-results"
        if folder.is_dir():
            for case in sorted(folder.iterdir()):
                if case.is_dir() and (case/"input.in").exists() and (
                    (case/"output.spc").exists() or
                    (case/"SPheno.spc.ZeeTypeII").exists()):
                    return case
    raise FileNotFoundError("No saved native case found in "+str(work))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work",type=Path,default=Path("~/zee-lfv64-serial-20261112-094549").expanduser())
    p.add_argument("--case",type=Path,default=None)
    p.add_argument("--output",type=Path,default=None)
    a=p.parse_args()
    case=a.case or latest_case(a.work.expanduser())
    report=inspect_case(case.expanduser())
    data=json.dumps(report,indent=2,allow_nan=False)
    if a.output:
        if a.output.exists():raise FileExistsError("Refuse overwrite prior diagnostic")
        a.output.write_text(data+"\n")
    print("CASE",case)
    for k in ("FZEE","YEE2"):
        x=report[k]
        print(k,"max_abs_source",x["source_scale_max_abs"],
              "max_abs_output",x["output_max_abs"],
              "max_rel_delta",x["max_relative_to_source_max"],
              "relative_residual_after_fit",x["residual_after_best_complex_scale"],
              "best_complex_ratio",x["best_complex_multiplicative_factor"])
        print("    MOST_DIFFERENT_ENTRY",x["max_difference_entry_one_indexed"],
              "expected_complex",x["source_at_max_difference"],
              "native_complex",x["output_at_max_difference"])
        print("    PATTERNS",json.dumps(x["direction_candidates_normalized_residuals"]))
    print("OUTPUT_BLOCK_SCALES",report["spectrum_block_scales"])
    print("SOURCE_CONTROL_FLAGS",report["SPhenoInput_control_blocks"])
    print("FULL_PHYSICAL_LFV_UNKNOWN")
    if a.output:print("DIAGNOSTIC_JSON",a.output)


if __name__=="__main__":main()

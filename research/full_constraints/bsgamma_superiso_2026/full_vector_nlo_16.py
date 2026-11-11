#!/usr/bin/env python3
"""Actually execute the source-pinned SuperIso v5.0 D9B full eight-operator
NLO inclusive B->Xs gamma bridge for 16 fixed Zee charged-scalar spectra.

The compiled SuperIso source must be obtained from the *official v5.0
archive*, byte-pinned to the SHA audited in Nov 2026, with the original
D9B patch applied as-is. Preserves SM Q1..Q8 and separately matches real
top-only NP C7,C8(LO) + C4,C7,C8(NLO). It includes interference, RG,
power/electroweak terms as implemented in the original 2025 backend.

All matched model inputs use the actual MSbar top mass printed by the
compiled backend at the same matching scale. D7/F13 frozen original
benchmark rate snapshots must reproduce; gamma=0 and gamma=pi/2 must
reproduce the *native* 2HDM branch. The h2 mixing contributions are
combined coherently before the inclusive rate is evaluated.

SUPERISO v5.0 != new 2026 Misiak SM/NNLO scheme: never claim these
absolute rates are 2026 rates or derive a physical Zee NP sigma.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from scripts.zee_module5_bmu_nlo import matching
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

ARCHIVE_SHA256="7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f"
SUPERISO_RELEASE="5.0"
SUPPORT_IDS=(15591,15673,2264)
SOURCE_D7_F13={
    "d7_NO_neutral_near_heavy_07":0.00042262508129385407,
    "F13_heavy_0001330":0.0003886651979064471,
}
KEYS=("C7_LO","C8_LO","C4_NLO_raw","C7_NLO_raw","C8_NLO_raw")
MATCH_SCALE=160.

def sha(value:bytes):
    return hashlib.sha256(value).hexdigest()

def parse(out:str):
    vals={}
    for line in out.splitlines():
        words=line.strip().split()
        if len(words)!=2:continue
        k,v=words
        try:
            x=float(v)
        except ValueError:
            continue
        if k in vals:raise ArithmeticError("Duplicate probe stdout scalar: "+k)
        if not math.isfinite(x):raise ArithmeticError("Nonfinite SuperIso rate/wilson: "+k)
        vals[k]=x
    return vals

class Probe:
    def __init__(self, binary:Path, output_dir:Path):
        self.binary=binary.resolve()
        self.logs=(output_dir/"raw_superiso_logs")
        self.logs.mkdir()
        self.k=0

    def call(self, title:str, args:list[float]|None=None):
        self.k+=1
        cmd=[str(self.binary)]
        if args is not None:
            if len(args)!=9:raise ValueError("Exactly nine native D9B probe input fields")
            cmd += [format(float(x),".17g") for x in args]
        else:cmd += ["160"]
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        raw=proc.stdout+proc.stderr
        (self.logs/f"{self.k:03d}_{title}.txt").write_text(
            "COMMAND "+json.dumps(cmd)+"\n"+raw
        )
        if proc.returncode:
            raise RuntimeError(f"{title}: SuperIso subprocess returncode {proc.returncode}")
        vals=parse(proc.stdout)
        if not all(k in vals for k in ("SM_BR","mt_match","zero_NP_max_matching_residual")):
            raise ArithmeticError(f"{title}: unexpected source stdout")
        if vals["zero_NP_max_matching_residual"]>1e-12:
            raise ArithmeticError("Zero-NP source model is not SM")
        if args is not None:
            for k in ("injected_BR","native_BR","metadata_BR","omit_C4_BR",
                      "double_effective_map_BR","reject_scheme","reject_unsupported_LO"):
                if k not in vals:raise ArithmeticError("Missing D9B source value: "+k)
            if vals["reject_scheme"]!=1 or vals["reject_unsupported_LO"]!=1:
                raise ArithmeticError("Nonmatching Wilson basis erroneously accepted")
            if not math.isclose(vals["injected_BR"],vals["metadata_BR"],abs_tol=2e-14,rel_tol=2e-11):
                raise ArithmeticError("Physics depends on injected model metadata")
        return dict(command=cmd,stdout_sha256=sha(proc.stdout.encode()),
                    parsed=vals,raw_log_file=f"{self.k:03d}_{title}.txt")

    def one(self,label,m1,m2,gamma,tanb,scale):
        q=self.call(label+"-SMscale",None if scale==160 else None)
        # For non160 scale, obtain separately with directly supplied matching
        # mu (unsupported as a one-field entry for the original 9-argument
        # CLI). Self-consistent scheme must instead get mt_match from
        # a preliminary matching probe at that mu.
        mt=q["parsed"]["mt_match"]
        if scale!=160:
            seed=matching(m1,tanb,mt,mu=160)
            t=self.call(label+"-mu"+format(scale,"g")+"-probe",
                        [m1,tanb,0,*[seed[k] for k in KEYS],scale])
            mt=t["parsed"]["mt_match"]
        ww=(math.cos(gamma)**2,math.sin(gamma)**2)
        c=[matching(m,tanb,mt,mu=scale) for m in (m1,m2)]
        mix={k:math.fsum(w*z[k] for w,z in zip(ww,c)) for k in KEYS}
        result=self.call(label+"-coherent",[m1,tanb,0,*[mix[k] for k in KEYS],scale])
        z=result["parsed"]
        if not (2e-4<z["SM_BR"]<5e-4 and 2e-4<z["injected_BR"]<7e-4):
            raise ArithmeticError("Unexpected SuperIso finite-cut B rate")
        if scale==160 and not math.isclose(z["SM_BR"],q["parsed"]["SM_BR"],rel_tol=2e-9):
            raise ArithmeticError("Fixed-scale SM baseline changed with model inputs")
        if scale!=160 and not (2e-4<z["SM_BR"]<5e-4):
            raise ArithmeticError("Matching-scale variation has invalid SM normalization")
        return dict(source_label=label,matching_scale_GeV=scale,mt_MSbar_matching_GeV=mt,
                    mH1_GeV=m1,mH2_GeV=m2,tanbeta=tanb,gamma=gamma,
                    matching_ord_NDR=mix,per_state_matching=c,
                    SM_rate=z["SM_BR"],NLO_full_vector_rate=z["injected_BR"],
                    NP_shift_in_same_SuperIso_prescription":z["injected_BR"]-z["SM_BR"],
                    C4_NLO_interference_rate_effect=z["injected_BR"]-z["omit_C4_BR"],
                    incorrect_C4_effective_remap_rate_effect=z["double_effective_map_BR"]-z["injected_BR"],
                    source_stdout_sha256=result["stdout_sha256"],
                    main_probe=result,source_probe=q,
                    full_2026_NNLO_rate_evaluated=False,physical_B="UNKNOWN",
                    NP_theory_sigma=None,global_acceptance=None)

def execute(binary:Path,outdir:Path,source_archive_sha256:str):
    if outdir.exists():
        raise FileExistsError("Never overwrite numerical evidence")
    if source_archive_sha256!=ARCHIVE_SHA256:
        raise ArithmeticError("Official 2025 SuperIso source archive hash changed")
    outdir.mkdir(parents=True)
    test=Probe(binary,outdir)
    probe0=test.call("source-SM-only")
    if not 3e-4<probe0["parsed"]["SM_BR"]<4e-4:
        raise ArithmeticError("NLO SuperIso SM reference outside source paper range")
    # Exact two-source historical D12 controls as a code-provenance falsifier.
    bmarks=json.loads((Path(__file__).resolve().parents[3]/"module1/d10_benchmarks.json").read_text())["records"]
    ctr={}
    for bid,expected in SOURCE_D7_F13.items():
        raw=next(row["input"]["physical"] for row in bmarks if row["input"]["benchmark_id"]==bid)
        data=test.one("historic-"+bid,raw["mH1"],raw["mH2"],raw["gamma"],math.tan(raw["beta"]),160.)
        observed=data["NLO_full_vector_rate"]
        if not math.isclose(observed,expected,rel_tol=1e-8,abs_tol=2e-11):
            raise ArithmeticError(f"Original source control {bid} fails: {observed} vs {expected}")
        ctr[bid]=dict(expected=expected,reproduced=observed,abs_residual=observed-expected)

    cases=[]
    ids={p["id"]:p for p in source_points()}
    if len(ids)!=16:raise ArithmeticError("Original scan source changed")
    for id in sorted(ids):
        p=ids[id]
        if p["gates"]["vacuum"]["assessment"]!="PASS":
            raise ArithmeticError("Original scalar source certificate lost")
        ph=p["input_card"]["physical"]
        q=test.one(f"original-{id}",ph["mH1"],ph["mH2"],ph["gamma"],math.tan(ph["beta"]),160.)
        q["scalar_id"]=id
        q["scalar_sha256"]=p["scalar_sha256"]
        q["source_2026_linear_pull"]=p["conditional_pull"]
        q["new_2026_SM_baseline_shift_transfer_only"]=None
        cases.append(q)
        print("SUPERISO_NLO_TWO_ZEE",id,"NLO_BR",q["NLO_full_vector_rate"],
              "SM",q["SM_rate"],"NP_SHIFT",q["NP_shift_in_same_SuperIso_prescription"],
              "C4_RATE",q["C4_NLO_interference_rate_effect"],
              "FULL_2026_UNKNOWN",flush=True)
    special={}
    for id in SUPPORT_IDS:
        p=ids[id]["input_card"]["physical"]
        for label,m1,m2,g in (("gamma_zero",p["mH1"],p["mH2"],0.),
                              ("gamma_half_pi",p["mH1"],p["mH2"],math.pi/2)):
            s=test.one(f"control-{id}-{label}",m1,m2,g,math.tan(p["beta"]),160.)
            if label=="gamma_zero":
                native=s["main_probe"]["parsed"]["native_BR"]
                if not math.isclose(native,s["NLO_full_vector_rate"],rel_tol=1e-9,abs_tol=5e-12):
                    raise ArithmeticError("One-state native SuperIso/independent BMU bridge mismatch")
            special[f"{id}_{label}"]={"NLO_rate":s["NLO_full_vector_rate"],
                                      "native_one_state_rate":s["main_probe"]["parsed"]["native_BR"]}
    scales={}
    for id in SUPPORT_IDS:
        pp=ids[id]["input_card"]["physical"]
        vals={}
        for mu in (120.,200.):
            z=test.one(f"scale-{id}-{int(mu)}",pp["mH1"],pp["mH2"],pp["gamma"],
                       math.tan(pp["beta"]),mu)
            vals[str(mu)]=dict(
                NLO_full_vector_BR=z["NLO_full_vector_rate"],
                SM_BR=z["SM_rate"],
                same_backend_NP_shift=z["NP_shift_in_same_SuperIso_prescription"],
                beta0_ratio_to_mu160=None,
            )
        scales[str(id)]=vals
    result={
        "schema":"zee-16-scalar-official-SuperIso-v5-audited-D9B-eight-operator-NLO-full-rate-v1",
        "source_release":"SuperIso_v5.0 (23 Nov 2025), official source + pinned D9B patch",
        "official_archive_sha256":source_archive_sha256,
        "declared_calculation_order":"NLO QCD numerator with source native EW/NP HQE prescriptions, real top-only 2 charged state, ms0",
        "SM_rate_provenance":"2025 SuperIso source baseline, NOT Misiak August 2026",
        "old_provenance_controls":ctr,
        "main_source_SM":probe0["parsed"]["SM_BR"],
        "source_verified_n_spectra":len(cases),
        "cases":cases,
        "one_state_controls":special,
        "scale_variation_controls":scales,
        "n_independent_full_vector_NLO_rates":len(cases),
        "2026_SM_plus_SuperIso_NP_rate_transfer":False,
        "physical_2026_B":"UNKNOWN",
        "physical_B_uncertainty_sigma":None,
        "full_2026_2HDM_NNLO_calibrated":False,
        "global_acceptance":None,
        "n_subprocesses":test.k,
    }
    (outdir/"NLO_RATE_EVIDENCE.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("SOURCE_PINNED_SUPERISO_FULL_VECTOR_NLO_REPLAY_DONE",len(cases),
          "SM",result["main_source_SM"],"SUBPROCESSES",test.k,
          "2026_FULL_NNLO_UNKNOWN",flush=True)
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--binary",type=Path,required=True)
    a.add_argument("--output-dir",type=Path,required=True)
    a.add_argument("--source-archive-sha256",required=True)
    args=a.parse_args()
    execute(args.binary,args.output_dir,args.source_archive_sha256)

if __name__=="__main__":
    main()

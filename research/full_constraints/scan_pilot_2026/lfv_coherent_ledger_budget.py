#!/usr/bin/env python3
"""Source-verified coherent LFV composition and missing-amplitude headroom.

The printed limits are *sufficient conditional norm budgets*, NOT bounds
on unknown physical amplitudes. Replays the frozen full neutrino input and
reads every signed, included Module4 scalar one-loop and photon-Barr-Zee term.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from module2.interface import decode, evaluate as neutrino_evaluate
from module3.core import radiative_width
from module4.interface import evaluate as module4_evaluate
from module14.scan import digest, perturbativity
from module12.study import module3_input

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).with_name("2264_fresh_8d_reference.json")
LIMIT = 1.5e-13
ALPHA_MZ = 1 / 127.95
SIN2_W = 0.23129


def parse_pair(row):
    return np.asarray(
        [complex(**row["C_L"]), complex(**row["C_R"])], dtype=complex
    )


def key_group(key):
    if key.startswith("module3_"):
        suffix = key.removeprefix("module3_")
        if suffix.endswith("_F"):
            return "one_loop_singlet_FdagF"
        if suffix.endswith("_D"):
            return "one_loop_doublet_DDdag"
        return "one_loop_neutral_leptons"
    if key.endswith("_scalar_gamma"):
        return "two_loop_charged_scalar_photon"
    if key.endswith("_gamma"):
        return "two_loop_neutral_fermion_photon"
    raise ValueError("Unexpected new ledger row requiring explicit classification: "+key)


def norm(a):
    return float(np.linalg.norm(a))


def evaluate_ledger():
    ref = json.loads(SOURCE.read_text())
    inp = ref["optimized_input"]
    if digest(inp) != ref["optimized_input_sha256"]:
        raise ValueError("Optimized input SHA mismatch")
    nout = neutrino_evaluate(inp)
    if nout["inverse"]["family_relative_residual"] >= 2e-9:
        raise ValueError("Neutrino target closure lost")
    if perturbativity(nout)["overall_max"] >= math.sqrt(4*math.pi):
        raise ValueError("Nonperturbative source card")

    extra = json.loads((ROOT/"module4"/"example.json").read_text())["two_loop_inputs"]
    extra["mW_GeV"] = inp["scalar"]["record"]["electroweak"]["mW"]
    data4 = {
        "schema_version": "1.0.0",
        "kind": "module3_matching_input_v1",
        "module3_input": module3_input(inp),
        "module2_output": nout,
        "two_loop_inputs": extra,
    }
    result = module4_evaluate(data4)
    if result["status"] != "PARTIAL" or result["COMPLETE_LFV"]:
        raise ArithmeticError("Unexpected complete physics status")
    constants = data4["module3_input"]["constants"]
    masses = inp["lepton_masses_GeV"]
    totals = constants["total_lepton_widths_GeV"]
    alpha = constants["alpha_em"]
    grouped_outputs = {}
    for ch,(i,j,limit) in {
        "mu_to_e_gamma":(1,0,LIMIT),
        "tau_to_e_gamma":(2,0,5.6e-8),
        "tau_to_mu_gamma":(2,1,4.2e-8),
    }.items():
        rows=result["channels"][ch]["ledger"]
        groups=defaultdict(lambda: np.zeros(2,dtype=complex))
        group_rows=defaultdict(list)
        each_norm=[]
        for key,row in rows.items():
            if row.get("validation_status")!="VALIDATION_PASS":
                raise ValueError("Unvalidated ledger contribution was added")
            v=parse_pair(row)
            group=key_group(key)
            groups[group]+=v
            group_rows[group].append(key)
            each_norm.append(norm(v))
        sum_pair=sum(groups.values(),start=np.zeros(2,dtype=complex))
        native_pair=parse_pair(result["channels"][ch])
        if not np.allclose(sum_pair,native_pair,rtol=1e-10,atol=1e-25):
            raise ArithmeticError("Signed ledger sum mismatch")
        prefactor = alpha*masses[i]**5/4*(1-(masses[j]/masses[i])**2)**3/totals[i-1]
        br_ledger=prefactor*norm(sum_pair)**2
        br_source=result["channels"][ch]["partial_BR"]
        if not math.isclose(br_ledger,br_source,rel_tol=5e-10,abs_tol=1e-28):
            raise ArithmeticError("Source included BR not reproduced")
        clim=math.sqrt(limit/prefactor)
        grouped={g:{
            "norm_GeV_minus2":norm(v),
            "isolated_BR":prefactor*norm(v)**2,
            "C_L":{"real":v[0].real,"imag":v[0].imag},
            "C_R":{"real":v[1].real,"imag":v[1].imag},
            "n_individual_rows":len(group_rows[g]),
            "contributing_rows":sorted(group_rows[g]),
        } for g,v in sorted(groups.items())}
        def gg(name):return groups.get(name,np.zeros(2,dtype=complex))
        one_loop=gg("one_loop_singlet_FdagF")+gg("one_loop_doublet_DDdag")+gg("one_loop_neutral_leptons")
        dipole_wo_bz=prefactor*norm(one_loop)**2
        sumgroupnorm=sum(norm(v) for v in groups.values())
        sumrownorm=sum(each_norm)
        headroom=clim-norm(sum_pair)
        if headroom <= 0:
            sufficient_conditional_pass=False
        else:
            sufficient_conditional_pass=True
        ew_eps=ALPHA_MZ/(4*math.pi*SIN2_W)
        FF=gg("one_loop_singlet_FdagF")
        kcrit=headroom/(ew_eps*norm(FF)) if norm(FF)>0 else None
        grouped_outputs[ch]={
            "source_included_BR":br_source,
            "signed_ledger_reconstructed_BR":br_ledger,
            "no_barr_zee_one_loop_BR":dipole_wo_bz,
            "experimental_limit_snapshot_BR":limit,
            "limit_coefficient_norm_GeV_minus2":clim,
            "included_coefficient_norm_GeV_minus2":norm(sum_pair),
            "headroom_for_missing_total_vector_GeV_minus2":headroom,
            "sufficient_if_actual_missing_norm_below_headroom":sufficient_conditional_pass,
            "actual_missing_norm_bound":None,
            "included_norm_to_limit_ratio":norm(sum_pair)/clim,
            "largest_group_norm_to_limit":max(norm(v) for v in groups.values())/clim,
            "sum_group_norm_to_limit":sumgroupnorm/clim,
            "signed_group_cancellation_factor":sumgroupnorm/max(norm(sum_pair),1e-300),
            "sum_individual_row_norm_to_limit":sumrownorm/clim,
            "individual_row_cancellation_factor":sumrownorm/max(norm(sum_pair),1e-300),
            "hypothetical_F_gauge_loop_eps":ew_eps,
            "hypothetical_parallel_F_gauge_K_critical":kcrit,
            "hypothetical_K_is_not_a_bound":True,
            "included_groups":grouped,
            "missing_group_names":sorted(result["channels"][ch]["omitted_topologies"]),
        }
    D=decode(nout["D"])
    F=decode(nout["F"])
    p=inp["scalar"]["record"]["physical"]
    return {
        "schema":"zee-fresh-2264-signed-coherent-LFV-ledger-budget-v1",
        "status":"SAVED_SOURCE_INPUT_REPLAYED_INCLUDED_LFV_LEDGER_NOT_PHYSICAL_BOUND",
        "optimized_input_sha256":digest(inp),
        "source_module4_input_sha256":result["provenance"]["input_sha256"],
        "scalar_id":2264,
        "model_gamma":p["gamma"],
        "model_masses_GeV":[p["mH1"],p["mH2"]],
        "max_D_abs":float(np.max(np.abs(D))),
        "max_F_abs":float(np.max(np.abs(F))),
        "direct_D_e_mu_magnitude":float(abs(D[0,1])),
        "direct_D_mu_e_magnitude":float(abs(D[1,0])),
        "FdagF_e_mu_abs":float(abs((F.conj().T@F)[0,1])),
        "neutrino_relative_closure":nout["inverse"]["family_relative_residual"],
        "channels":grouped_outputs,
        "full_physical_lfv":"UNKNOWN",
        "full_mu3e":"UNKNOWN","full_conversion":"UNKNOWN",
        "physical_B":"UNKNOWN","physical_Higgs":"UNKNOWN",
        "global_acceptance":None,
        "source_retained_ledger_only":True,
        "interpretation":"One-loop and selected photon Barr-Zee terms source-replayed with full signs. Headroom is a sufficient geometric budget; not a bound on omitted actual amplitudes; K is strictly hypothetical F gauge dressing.",
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    if args.output.exists():raise FileExistsError("No overwrite")
    out=evaluate_ledger()
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("LFV_LEDGER_HEADROOM",out["optimized_input_sha256"])
    print("YUKAWA_DIRECT",out["direct_D_e_mu_magnitude"],out["direct_D_mu_e_magnitude"],
          "FdagF",out["FdagF_e_mu_abs"])
    for ch,v in out["channels"].items():
        print("CHANNEL",ch,
              "INCLUDED",f'{v["source_included_BR"]:.12e}',
              "ONELOOP",f'{v["no_barr_zee_one_loop_BR"]:.12e}',
              "C_HEADROOM",f'{v["headroom_for_missing_total_vector_GeV_minus2"]:.12e}',
              "GROUP_CANCELLATION_FACTOR",f'{v["signed_group_cancellation_factor"]:.12e}',
              "KCRIT_F_ONLY",v["hypothetical_parallel_F_gauge_K_critical"])
        for g,z in v["included_groups"].items():
            print("LEDGER_GROUP",ch,g,"NORM",f'{z["norm_GeV_minus2"]:.12e}',"ISOLATED_BR",f'{z["isolated_BR"]:.12e}')
    print("FULL_PHYSICAL_LFV_UNKNOWN / NO_OMISSION_BOUNDS",flush=True)


if __name__=="__main__":
    main()

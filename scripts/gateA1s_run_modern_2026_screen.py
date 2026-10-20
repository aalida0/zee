#!/usr/bin/env python3
"""Gate A1S: screen two mixed Zee-type charged scalars with 2026 B->Xsγ.

The 2026 collaboration's independent Eq.(4) (arXiv:2608.29863) is
  BR*1e4 = (3.54 ± 0.14) - 8.51*DeltaC7(mu0) - 2.16*DeltaC8(mu0)
at mu0=160 GeV and Egamma>1.6 GeV; quadratic NP terms neglected.

We get LO dC7,dC8 directly from the existing A1M source-hashed
SuperIso v5 library at exactly mu0=160 GeV (not from the legacy
full-BR calculation and not from mu0=2MW ~160.7384 GeV).

At Type-II quark Yukawas, two-state leading coefficients are
  dCi = cos(gamma)^2*dCi(mH1) + sin(gamma)^2*dCi(mH2).
NO weighted average of BRs is used.

This is a published, modern LO, linearized, operator-specific SCREEN,
not the full 2026 2HDM NNLO fit/likelihood. Do not label any Zee point
excluded/allowed by this result. No full-neutrino Zee claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

from gateA1r_run_br_pilot import check_superiso_source,compile_pilot

SOURCE="arXiv:2608.29863v1 (2026-08-30) Section IV Eq.(4)"
PDG_EXP={"central_times_1e4":3.49,"sigma_times_1e4":0.19,
         "photon_cut_GeV":1.6}
MODERN_SM={"central_times_1e4":3.54,"sigma_times_1e4":0.14,
           "photon_cut_GeV":1.6}
K7=-8.51
K8=-2.16
MU0_GEV=160.
REFERENCE_MASSES=(300.,670.,700.,1000.,2000.)
INPUT=re.compile(
    r"^INPUT mH_GeV=([-+eE0-9.]+) tanbeta=([-+eE0-9.]+) "
    r"mu0_GeV=([-+eE0-9.]+) running_mt_mu0_GeV=([-+eE0-9.]+)$")
DELTA7=re.compile(r"^DELTA_C7_LO=([-+eE0-9.]+)$")
DELTA8=re.compile(r"^DELTA_C8_LO=([-+eE0-9.]+)$")
STATUS="STATUS A1S_SOURCE_PINNED_LO_MATCHING_NO_BR_OR_EXCLUSION"

def weights(gamma):
    if not (math.isfinite(gamma) and 0.<=gamma<=math.pi/2+1e-12):
        raise ValueError("Require physical 0<=gamma<=pi/2")
    # Map the trivial numerical upper boundary back onto pi/2.
    gamma=min(gamma,math.pi/2)
    c=math.cos(gamma)
    s=math.sin(gamma)
    w1,w2=c*c,s*s
    if abs(w1+w2-1.)>1.e-14:
        raise ValueError("Mixing unitarity violated")
    return w1,w2

def linearized_2026(d7,d8):
    if not all(math.isfinite(v) for v in (d7,d8)):
        raise ValueError("Nonfinite new-physics LO coefficient")
    shift=K7*d7+K8*d8
    return {
        "LO_delta_C7_mu0_160":d7,
        "LO_delta_C8_mu0_160":d8,
        "linearized_shift_times_1e4":shift,
        "linearized_predicted_central_times_1e4":MODERN_SM["central_times_1e4"]+shift,
        "SM_theory_sigma_times_1e4_NOT_a_complete_NP_error":
            MODERN_SM["sigma_times_1e4"],
        "quadratic_NP_terms_omitted":True,
        "NLO_NNLO_NP_matching_omitted":True,
    }

def combine(source1,source2,gamma):
    w1,w2=weights(gamma)
    c1=source1["delta_C7_LO"],source1["delta_C8_LO"]
    c2=source2["delta_C7_LO"],source2["delta_C8_LO"]
    d7=w1*c1[0]+w2*c2[0]
    d8=w1*c1[1]+w2*c2[1]
    br=linearized_2026(d7,d8)
    br.update({
        "gamma_rad":gamma,"w_light_cos2":w1,"w_heavy_sin2":w2,
        "mH1_GeV":source1["mass_GeV"],
        "mH2_GeV":source2["mass_GeV"],
        "single_state_1_linearized":linearized_2026(*c1),
        "single_state_2_linearized":linearized_2026(*c2),
        "coefficient_level_superposition":True,
        "weighted_BR_of_single_Higgs_states":False,
    })
    return br

def parse_probe(raw,mH,tanbeta):
    lines=raw.strip().splitlines()
    if lines.count(STATUS)!=1 or lines.count(
            "NO_THEORY_LIKELIHOOD_VALIDATED true")!=1:
        raise ValueError("Missing expected source-pinned C-driver status")
    def match_unique(regex):
        rows=[m for line in lines if (m:=regex.fullmatch(line))]
        if len(rows)!=1: raise ValueError("Missing/duplicate numeric matching probe field")
        return rows[0]
    inp=match_unique(INPUT)
    if not math.isclose(float(inp[1]),mH,rel_tol=0.,abs_tol=1e-9) \
       or not math.isclose(float(inp[2]),tanbeta,rel_tol=1e-13) \
       or float(inp[3])!=MU0_GEV or not 100.<float(inp[4])<250.:
        raise ValueError("Matching parameters differ from 2026 Eq4 contract")
    d7=float(match_unique(DELTA7)[1])
    d8=float(match_unique(DELTA8)[1])
    if not all(math.isfinite(x) for x in (d7,d8)):
        raise ValueError("Nonfinite source-pinned matching")
    return {
        "mass_GeV":mH,"tanbeta":tanbeta,
        "matching_scale_GeV":MU0_GEV,
        "running_mt_mu0_GeV":float(inp[4]),
        "delta_C7_LO":d7,
        "delta_C8_LO":d8,
    }

def report(probes,m1,m2,gamma,tanbeta,prov):
    if not (200.<=m1<m2<=10000. and
            math.isfinite(tanbeta) and .25<=tanbeta<=100.):
        raise ValueError("Physical ordered input required: 200<=m1<m2<=10000")
    if m1 not in probes or m2 not in probes or 670. not in probes:
        raise ValueError("Missing current benchmark matching probe")
    zee=combine(probes[m1],probes[m2],gamma)
    check_lo=lambda p: math.isclose(p["matching_scale_GeV"],MU0_GEV)
    if not all(check_lo(p) for p in probes.values()):
        raise ValueError("A1S requires exact 160GeV matching")
    return {
        "status":"GATE_A1S_2026_MODERN_EQ4_LO_LINEARIZED_ZEE_SCREEN_NOT_EXCLUSION",
        "reference_paper":SOURCE,
        "Eq4_coefficients":{"constant":3.54,"coefficient_delta_C7":K7,
                            "coefficient_delta_C8":K8,
                            "matching_scale_GeV":MU0_GEV},
        "SM_2026":MODERN_SM,
        "experimental_PDG_2026":PDG_EXP,
        "full_2026_single_TypeII_95CL_lower_mass_GeV":670.,
        "full_2026_bound_not_derived_by_linearized_Eq4":True,
        "physical_photon_cut_GeV":1.6,
        "tanbeta":tanbeta,
        "source_pinned_LO_coefficients":{
            str(m):p for m,p in sorted(probes.items())},
        "selected_Zee_scalar_sector_benchmark":zee,
        "full_2026_NNLO_observable_kernel_reimplemented":False,
        "linearized_approximation_assessed_for_LARGE_NP":False,
        "matching_and_high_order_scale_envelope_validated":False,
        "charged_singlet_fermion_couplings_assumed_zero_in_quark_sector":True,
        "Zee_two_state_full_BR_validated":False,
        "experimental_95CL_likelihood_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
        "provenance":prov,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vendor-root",required=True,type=Path)
    p.add_argument("--a1m-provenance",required=True,type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--mH1",type=float,default=300.)
    p.add_argument("--mH2",type=float,default=700.)
    p.add_argument("--gamma",type=float,default=1.089)
    p.add_argument("--tanbeta",type=float,default=5.597170833164245)
    args=p.parse_args()
    m1,m2,g,t=args.mH1,args.mH2,args.gamma,args.tanbeta
    if not all(math.isfinite(v) for v in (m1,m2,g,t)) \
       or not (200.<=m1<m2<=10000. and .25<=t<=100.):
        raise SystemExit("Gate A1S input must satisfy 200<=m1<m2<=10000, 0.25<=tanbeta<=100")
    weights(g)
    pinned=check_superiso_source(args.vendor_root,args.a1m_provenance)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    driver=Path(__file__).with_name("gateA1s_probe_modern_2026_lo.c")
    binary=args.output_dir/"gateA1s_probe_lo"
    compiled=compile_pilot(args.vendor_root,binary,driver,False)
    masses=sorted(set(REFERENCE_MASSES)|{m1,m2})
    probes={}
    all_raw=[]
    for mass in masses:
        proc=subprocess.run(
            [str(binary.resolve()),f"{mass:.17g}",f"{t:.17g}"],
            capture_output=True,text=True,timeout=90,check=False)
        if proc.returncode:
            raise ValueError(
                f"LO matching probe failed at mH={mass}, exit={proc.returncode}: "
                f"STDERR={proc.stderr[-1500:]} STDOUT={proc.stdout[-1500:]}")
        probes[mass]=parse_probe(proc.stdout,mass,t)
        all_raw.append(f"CASE mass={mass}\n{proc.stdout}")
    provenance={
        "vendor":pinned,
        "compiled_probe":compiled,
    }
    out=report(probes,m1,m2,g,t,provenance)
    (args.output_dir/"matching_raw.log").write_text("\n".join(all_raw))
    target=args.output_dir/"modern_2026_LO_Zee_screen.json"
    target.write_text(json.dumps(out,indent=2)+"\n")
    z=out["selected_Zee_scalar_sector_benchmark"]
    print("STATUS",out["status"])
    print("REFERENCE_2026 SM_BR_1e4",MODERN_SM["central_times_1e4"],
          "SM_SIGMA_1e4",MODERN_SM["sigma_times_1e4"],
          "EXP_BR_1e4",PDG_EXP["central_times_1e4"],
          "PUBLISHED_FULL_TYPEII_BOUND_GE_V",670)
    for m in masses:
        h=probes[m]
        b=linearized_2026(h["delta_C7_LO"],h["delta_C8_LO"])
        print(f"mH={m:g} DELTA_C7_LO={h['delta_C7_LO']:.12g} "
              f"DELTA_C8_LO={h['delta_C8_LO']:.12g} "
              f"BR26_LO_LINEARIZED_1e4={b['linearized_predicted_central_times_1e4']:.12g}")
    print(f"ZEE mH1={m1:g} mH2={m2:g} gamma={g:.9g} "
          f"w1={z['w_light_cos2']:.10g} w2={z['w_heavy_sin2']:.10g}")
    print("ZEE DELTA_C7_LO",f"{z['LO_delta_C7_mu0_160']:.12g}",
          "DELTA_C8_LO",f"{z['LO_delta_C8_mu0_160']:.12g}")
    print("ZEE_BR26_LO_LINEARIZED_1e4",
          f"{z['linearized_predicted_central_times_1e4']:.12g}")
    print("FULL_2026_NNLO_BR_VALIDATED",False)
    print("ZEE_EXCLUSION_CALCULATED",False)
    print("Wrote",target)

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Gate A1U: physical LEGACY v5 two-state inclusive BR, no 2026 exclusion.

Uses compiled SuperIso v5 physics kernel with charged-Higgs contributions
combined in Wilson coefficients at muW=2MW, including LO/NLO/NNLO and
primed coefficients. The bsgamma() internal LO C7/C8 matching reload
is treated by separate SM/light/heavy evaluations of the same LOW-scale
Wilson vectors and affine superposition. This is legitimate only
when the ACTUAL pinned source supports the linear internal dependence.

Critical numerical gates: gamma=0, pi/2 reproduce independent
single-state A1R BRs; mH1=mH2 agrees for ANY gamma; full single-state
values reproduce the real AF Gate A1R physical observable.
This cannot reproduce the 2026 SM theoretical upgrade or a Zee
95%-CL likelihood. Do not perform any exclusion.
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

STATUS="GATE_A1U_LEGACY_TWO_STATE_BR_PILOT_NOT_2026_EXCLUSION"
FNUM=r"([-+0-9.eE]+)"
INPUT=re.compile(
    rf"^INPUT mH1_GeV={FNUM} mH2_GeV={FNUM} gamma_rad={FNUM} "
    rf"tanbeta={FNUM} muW_GeV={FNUM} mu_b_GeV={FNUM}$")
WEIGHTS=re.compile(rf"^WEIGHTS w1={FNUM} w2={FNUM}$")
MATCH=re.compile(rf"^MATCH op=(7|8) sm_LO={FNUM} "
                 rf"delta1_LO={FNUM} delta2_LO={FNUM} zee_LO={FNUM}$")
MODE=re.compile(r"^INTERNAL_CW_MODE=(none|reload)$")
DIAGNOSTIC=re.compile(
    rf"^A1U_CONTEXT_DIAGNOSTIC RG_MAX_ABS_DELTA_H1={FNUM} "
    rf"RG_MAX_ABS_DELTA_H2={FNUM} "
    rf"FIXED_LOW_BR_SM={FNUM} FIXED_LOW_BR_H1={FNUM} "
    rf"FIXED_LOW_BR_H2={FNUM}$")
INTERNAL=re.compile(
    rf"^INTERNAL_FIXED_LOW BR_SM_CONTEXT={FNUM} "
    rf"BR_H1_CONTEXT={FNUM} BR_H2_CONTEXT={FNUM}$")
SINGLE=re.compile(
    rf"^FULL_SINGLE_REFERENCE br_H1={FNUM} br_H2={FNUM} br_SM={FNUM}$")
COMBINED=re.compile(rf"^FULL_LEGACY_ZEE_TWO_STATE_BR={FNUM}$")
REFERENCE_MASSES=(300,700,1000,2000)

def finite(s):
    x=float(s)
    if not math.isfinite(x): raise ValueError("Nonfinite A1U value")
    return x

def audit_affine_internal_matching(vendor_root):
    """Classify *actual pinned* bsgamma() internal matching dependence.

    This must not assume the v3-era implementation is present in the
    isolated SuperIso v5 tree. If there is NO internal CW_calculator()
    reload, no affine interpolation is needed; require actual numerical
    independence under three model-parameter contexts with *identical*
    mixed low-scale coefficients. If an internal reload exists, require
    the documented affine C7/C8 source pattern before interpolating.
    Both cases are subject to A1R physical endpoint closure.
    """
    path=Path(vendor_root)/"src"/"bsgamma.c"
    raw=path.read_bytes()
    code=raw.decode()
    clean=re.sub(r"/\*.*?\*/|//[^\n]*"," ",code,flags=re.S)
    a=re.search(r"\bdouble\s+bsgamma\s*\(",clean)
    b=re.search(r"\bdouble\s+bsgamma_calculator\s*\(",clean)
    if a is None or b is None or a.end()>=b.start():
        raise ValueError("Cannot locate source-pinned bsgamma body")
    body=clean[a.end():b.start()]
    calls=re.findall(r"\bCW_calculator\s*\(",body)
    if len(calls)>1:
        raise ValueError("More than one internal CW_calculator() call: unsupported")
    if re.search(r"param\s*->\s*(?:SM|mass_H)\b",body):
        raise ValueError(
            "Direct model mass/SM dependence inside bsgamma outside reload; "
            "internal-context independence/affinity is unsafe")
    # Local array declarations are NOT indexed operator uses.
    expressions=re.sub(
        r"\b(?:double\s+complex|double)\s+[^;]*"
        r"\bC0w\s*\[\s*\d+\s*\][^;]*;",
        " ",body)
    refs=re.findall(r"\bC0w\s*\[\s*([^\]]+)\s*\]",expressions)
    refs=[r.strip() for r in refs]
    common={
        "superiso_v5_bsgamma_sha256":hashlib.sha256(raw).hexdigest(),
        "internal_CW_call_count":len(calls),
        "source_scan_not_formal_semantic_proof":True,
        "two_state_modern_2026_BR_validated":False,
        "numerical_fixed_low_context_test_required":True,
    }
    if not calls:
        if refs or re.search(r"\bC0w\b",expressions):
            raise ValueError(
                "bsgamma uses internal C0w without CW reload: manual source review required")
        return {
            **common,
            "status":"A1U_SUPERISO_BSGAMMA_NO_INTERNAL_CW_RELOAD_REQUIRES_CONTEXT_INVARIANCE",
            "internal_CW_mode":"none",
            "reloaded_indices":[],
            "affine_interpolation_needed":False,
        }
    if not refs or set(refs)!={"7","8"}:
        raise ValueError(f"Unsupported bsgamma reloaded C0w indices {set(refs)}")
    if "Kt0" not in body or "Cem" not in body:
        raise ValueError("Cannot identify legacy nonperturbative/EM terms")
    if re.search(r"pow\s*\(\s*C0w\s*\[",body):
        raise ValueError("Nonlinear power of internal high-scale Wilson")
    if re.search(r"C0w\s*\[[78]\]\s*\*\s*C0w\s*\[[78]\]",body):
        raise ValueError("Product of internal high-scale Wilson coefficients")
    if not re.search(r"\bKt0\s*=",body):
        raise ValueError("Missing Kt0 definition in pinned bsgamma")
    return {
        **common,
        "status":"A1U_PINNED_SUPERISO_BSGAMMA_INTERNAL_AFFINE_PREFLIGHT",
        "internal_CW_mode":"reload",
        "reloaded_indices":sorted(set(refs)),
        "affine_interpolation_needed":True,
        "nonperturbative_Kt0_seen":True,
        "electromagnetic_Cem_seen":True,
        "no_obvious_quadratic_reloaded_LO_terms":True,
    }

def parse_driver(raw,expected_m1,expected_m2,expected_gamma,tanbeta,expected_mode=None):
    lines=raw.splitlines()
    if lines.count("STATUS "+STATUS)!=1:
        raise ValueError("Missing exact A1U executable status")
    def one(regex):
        matches=[m for line in lines if (m:=regex.fullmatch(line))]
        if len(matches)!=1: raise ValueError(f"Missing/duplicate A1U field {regex.pattern[:28]}")
        return matches[0]
    inp=one(INPUT)
    m1,m2,g,t,mu,mub=[finite(v) for v in inp.groups()]
    for tag,val,expected in (
        ("mH1",m1,expected_m1),
        ("mH2",m2,expected_m2),
        ("gamma",g,expected_gamma),
        ("tanbeta",t,tanbeta),
    ):
        if not math.isclose(val,expected,rel_tol=1e-13,abs_tol=1e-12):
            raise ValueError(f"Unexpected {tag} input in C driver")
    if not (100.<mu<300. and 0.<mub<20.):
        raise ValueError("Unexpected RG scale")
    wm=one(WEIGHTS)
    w1,w2=finite(wm[1]),finite(wm[2])
    if not math.isclose(w1+w2,1.,abs_tol=1.e-13,rel_tol=0.):
        raise ValueError("Charged mass-eigenstate mixing nonunitarity")
    match={}
    for line in lines:
        m=MATCH.fullmatch(line)
        if m:
            op=int(m[1])
            if op in match: raise ValueError("Duplicate C7/C8 high-scale matching")
            sm,d1,d2,z=(finite(v) for v in m.groups()[1:])
            if not math.isclose(z,sm+w1*d1+w2*d2,
                                abs_tol=1e-12,rel_tol=2.e-13):
                raise ValueError("High-scale Wilson mixing closure failed")
            match[op]={"SM":sm,"delta_light":d1,"delta_heavy":d2,"Zee":z}
    if set(match)!={7,8}:
        raise ValueError("Missing C7/C8 high-scale matching")
    mode=one(MODE)[1]
    if expected_mode is not None and mode!=expected_mode:
        raise ValueError("A1U C-driver internal matching mode differs from audited source")
    diag=one(DIAGNOSTIC)
    rg1,rg2,db0,db1,db2=[finite(v) for v in diag.groups()]
    if not (0.<=rg1<=1.e-10 and 0.<=rg2<=1.e-10):
        raise ValueError("A1U fixed-high-scale RG context invariance FAILED")
    internal=one(INTERNAL)
    b0,b1,b2=[finite(x) for x in internal.groups()]
    if max(abs(db0-b0),abs(db1-b1),abs(db2-b2))>1.e-15:
        raise ValueError("A1U C-driver fixed-low diagnostics disagree with final output")
    if mode=="none" and max(abs(b0-b1),abs(b0-b2))>2e-12:
        raise ValueError(
            "No-reload bsgamma() changed with SM/H1/H2 context "
            "despite identical mixed low-scale Wilson vectors")
    singles=one(SINGLE)
    r1,r2,rsm=[finite(x) for x in singles.groups()]
    br=finite(one(COMBINED)[1])
    if not all(0.<v<.01 for v in (b0,b1,b2,r1,r2,rsm,br)):
        raise ValueError("Unphysical A1U full BR")
    should=(b0+w1*(b1-b0)+w2*(b2-b0) if mode=="reload" else b0)
    if abs(br-should)>1e-13:
        raise ValueError("Internal high-scale affine combination did not close")
    for key in ("EXPERIMENTAL_LIKELIHOOD_VALIDATED false",
                "MODERN_2026_FULL_NNLO_VALIDATED false",
                "ZEE_BENCHMARK_ALLOWED_OR_EXCLUDED undetermined"):
        if key not in lines: raise ValueError("A1U exclusion safety marker absent")
    return {
        "mH1_GeV":m1,"mH2_GeV":m2,"gamma_rad":g,
        "tanbeta":t,"muW_GeV":mu,"mu_b_GeV":mub,
        "w_light":w1,"w_heavy":w2,
        "full_legacy_Zee_BR":br,
        "internal_CW_mode":mode,
        "fixed_low_context_invariance_verified":mode=="none",
        "high_scale_fixed_RG_context_max_abs_delta_H1":rg1,
        "high_scale_fixed_RG_context_max_abs_delta_H2":rg2,
        "fixed_low_context_numeric_separation":{
            "SM_minus_H1":b0-b1,"SM_minus_H2":b0-b2,
        },
        "internal_high_scale_eval_fixed_low":{
            "SM":b0,"H1":b1,"H2":b2,
        },
        "full_single_state_BR":{
            "H1":r1,"H2":r2,"SM":rsm,
        },
        "C7_C8_high_scale":match,
    }

def closeness(x,y,name,atol=4.e-11,rtol=2.e-8):
    if not math.isclose(x,y,rel_tol=rtol,abs_tol=atol):
        raise ValueError(f"{name} physical BR closure failure: {x} vs {y}")
    return x-y

def finalize(point,zero,pi2,deg,legacy,source,build,logs):
    input_m1=point["mH1_GeV"]
    input_m2=point["mH2_GeV"]
    if zero["mH1_GeV"]!=input_m1 or pi2["mH2_GeV"]!=input_m2:
        raise ValueError("Endpoint mass grid inconsistent")
    if deg["mH1_GeV"]!=input_m2 or deg["mH2_GeV"]!=input_m2:
        raise ValueError("Wrong equal-mass audit")
    if legacy.get("status")!=(
        "GATE_A1R_SINGLE_TYPEII_OBSERVABLE_BR_PILOT_"
        "AWAITING_INDEPENDENT_ERROR_BUDGET"):
        raise ValueError("Prior AF A1R actual BR unavailable")
    old=legacy["TypeII_control_points"]
    if input_m1 not in REFERENCE_MASSES or input_m2 not in REFERENCE_MASSES:
        raise ValueError("Require A1R reference masses for endpoint validation")
    x1=finite(old[f"TypeII{int(input_m1)}"]["BR_B_to_Xs_gamma"])
    x2=finite(old[f"TypeII{int(input_m2)}"]["BR_B_to_Xs_gamma"])
    sm=finite(legacy["SM_model_BR"])
    for run,ref,label in (
        (zero,x1,"gamma=0_vs_A1R_H1"),
        (pi2,x2,"gamma=pi2_vs_A1R_H2"),
        (deg,x2,"mass_degenerate_vs_A1R_single"),
        (point["full_single_state_BR"]["H1"],x1,"independent_H1_single"),
        (point["full_single_state_BR"]["H2"],x2,"independent_H2_single"),
        (point["full_single_state_BR"]["SM"],sm,"SM"),
    ):
        value=run["full_legacy_Zee_BR"] if isinstance(run,dict) else run
        closeness(value,ref,label)
    # Establish high-scale identical coefficient identities at endpoints.
    for op in (7,8):
        for label,run,kind in (
            ("gamma=0",zero,"delta_light"),
            ("gamma=pi2",pi2,"delta_heavy"),
            ("mass_degenerate",deg,"delta_light"),
        ):
            w=run["C7_C8_high_scale"][op]
            if not math.isclose(w["Zee"],w["SM"]+w[kind],
                                abs_tol=1e-12,rel_tol=1e-11):
                raise ValueError(f"{label} LO operator C{op} failed")
    if abs(point["w_light"]+point["w_heavy"]-1.)>1e-13:
        raise ValueError("Bad mass-eigenstate normalization")
    return {
        "status":"GATE_A1U_FULL_LEGACY_SUPERISO_TWO_STATE_BR_ENDPOINT_CLOSED_NOT_2026_EXCLUSION",
        "scope":"Physical legacy SuperIso v5 inclusive BR with matched "
                "LO/NLO/NNLO Wilson arrays and primed coefficients",
        "benchmark":point,
        "SM_BR_legacy":sm,
        "A1R_pinned_single_controls":{
            "mH1":x1,"mH2":x2,
        },
        "gamma_0_endpoint":zero,
        "gamma_pi2_endpoint":pi2,
        "equal_mass_gamma_endpoint":deg,
        "all_A1R_physical_endpoint_checks_pass":True,
        "affine_internal_CW_source_contract":source,
        "compiled_static_vendor":build,
        "raw_logs":str(logs),
        "full_legacy_two_state_BR_calculated":True,
        "MODERN_2026_full_NNLO_two_state_BR_validated":False,
        "flavour_error_budget_validated":False,
        "quadratic_NP_terms_present_in_legacy_vendor_observable":True,
        "Zee_model_allowed":None,
        "Zee_model_excluded":None,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vendor-root",required=True,type=Path)
    ap.add_argument("--a1m-provenance",required=True,type=Path)
    ap.add_argument("--a1r-result",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    ap.add_argument("--mH1",type=float,default=300.)
    ap.add_argument("--mH2",type=float,default=700.)
    ap.add_argument("--gamma",type=float,default=1.089)
    ap.add_argument("--tanbeta",type=float,default=5.597170833164245)
    args=ap.parse_args()
    m1,m2,g,t=args.mH1,args.mH2,args.gamma,args.tanbeta
    if not all(math.isfinite(v) for v in (m1,m2,g,t)) or not (
        200.<=m1<m2<=10000. and 0.<=g<=math.pi/2 and
        .25<=t<=100.):
        raise SystemExit("A1U invalid ordered physical mass/mixing/Yukawa input")
    src_checks=check_superiso_source(args.vendor_root,args.a1m_provenance)
    affine=audit_affine_internal_matching(args.vendor_root)
    mode=affine["internal_CW_mode"]
    if src_checks["bsgamma_internal_CW_reload_detected"] != (mode=="reload"):
        raise ValueError("Conflicting independent source audits of internal CW reload")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    exe=args.output_dir/"gateA1u_legacy_two_state_br"
    built=compile_pilot(
        args.vendor_root,exe,
        Path(__file__).with_name("gateA1u_legacy_two_state_br.c"),False)
    controls={
        "zee":(m1,m2,g),
        "gamma0":(m1,m2,0.),
        "gamma_pi2":(m1,m2,math.pi/2),
        "degenerate":(m2,m2,g),
    }
    parsed={}
    logs=[]
    for label,(a,b,gg) in controls.items():
        proc=subprocess.run(
            [str(exe.resolve()),f"{a:.17g}",f"{b:.17g}",
             f"{gg:.17g}",f"{t:.17g}",mode],
            capture_output=True,text=True,timeout=90,check=False)
        if proc.returncode:
            raise ValueError(
                f"A1U {label} vendor observable failed code={proc.returncode} "
                f"stdout={proc.stdout[-1400:]} stderr={proc.stderr[-1400:]}")
        parsed[label]=parse_driver(proc.stdout,a,b,gg,t,expected_mode=mode)
        logs.append("CASE "+label+"\n"+proc.stdout)
        if proc.stderr:logs.append("STDERR "+label+"\n"+proc.stderr)
    log=args.output_dir/"a1u_raw_vendor_output.log"
    log.write_text("\n".join(logs))
    report=finalize(
        parsed["zee"],parsed["gamma0"],parsed["gamma_pi2"],
        parsed["degenerate"],
        json.loads(args.a1r_result.read_text()),affine,
        {"source_pinned_vendor":src_checks,"build":built},log)
    target=args.output_dir/"legacy_two_state_br.json"
    target.write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",report["status"])
    print("ZEE_LEGACY_FULL_BR",
          f"{report['benchmark']['full_legacy_Zee_BR']:.13g}")
    print("GAMMA_0_ENDPOINT",
          f"{report['gamma_0_endpoint']['full_legacy_Zee_BR']:.13g}")
    print("GAMMA_PI2_ENDPOINT",
          f"{report['gamma_pi2_endpoint']['full_legacy_Zee_BR']:.13g}")
    print("DEGENERATE_MASSES",
          f"{report['equal_mass_gamma_endpoint']['full_legacy_Zee_BR']:.13g}")
    print("FULL_2026_NNLO_BR_VALIDATED False")
    print("ZEE_EXCLUSION_CALCULATED False")
    print("Wrote",target)

if __name__=="__main__":
    main()

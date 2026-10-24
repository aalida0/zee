#!/usr/bin/env python3
"""F19: evaluate *actual* scalar BFB/unitarity and correlated scalar S,T,U
on exactly the three completed F18 full-MadWidth benchmarks.

Reads the immutable F16/F17f source bundle transferred to CERN and the
completed source-hash-validated F18 three-case merge. Reconstructs the exact
Zee scalar potential independently with Gate6, evaluates Gate A1H scalar
S,T,U against its two published 3D covariances. This is not the complete
experimental/theoretical Zee-model likelihood or a publication scan.

Rejects broken source joins; NEVER upgrades partial flavor/neutrino gates
to passes or asserts a fully allowed benchmark. Output is immutable.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,tarfile
from pathlib import Path
from gate6_benchmark import benchmark
from gateA1h_correlated_stu_ewpo import report as compute_stu

CASES=("F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003")
F18_MERGE_STATUS="F18_THREE_CASES_CONDOR_OR_LOCAL_MERGED_TREE_LO_NOT_ALLOWED"
F19_STATUS="F19_REAL_F18_THREE_SCALAR_BFB_UNITARITY_STU_SCREENS_NOT_FULL_ZEE_ALLOWED"
F16_FILE="F16_three_exact_F13_Zee_input_reconstruction.json"
F17F_SUBDIR="F17f_real_UFO_unitary_complex_CKM_20261023T120345Z"
F17F_FILE=F17F_SUBDIR+"/report.json"
REQUIRED_BLOCKERS={
    "global_charge_breaking_and_neutral_vacuum":"NOT_EVALUATED",
    "neutrino_NO_IO_oscillation_likelihood":"NOT_EVALUATED",
    "general_Zee_complete_LFV_BarrZee_conversion_EDMs":"NOT_EVALUATED",
    "modern_two_charged_b_to_s_gamma_full_precision_likelihood":"NOT_EVALUATED",
    "remaining_quark_flavor_and_alignment_RGE":"NOT_EVALUATED",
    "complete_HiggsTools_HB_HS_five_state":"NOT_EVALUATED",
    "charged_Higgs_direct_LHC_search_coverage":"NOT_EVALUATED",
    "nonoblique_EWPO_and_precision_vertices":"NOT_EVALUATED",
    "QCD_improved_hadronic_widths_and_signal_rates":"NOT_EVALUATED",
}
def sha(data):
    return hashlib.sha256(data).hexdigest()

def finite(x,label):
    if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x):
        raise ValueError("Invalid/nonfinite "+label)
    return float(x)

def get_bundle_bytes(archive,path,maxbytes=64_000_000):
    try: member=archive.getmember(path)
    except KeyError as exc:
        raise ValueError("Missing F16/F17f original source "+path) from exc
    if not member.isfile() or not 0<member.size<=maxbytes:
        raise ValueError("Bad original source member size/type "+path)
    stream=archive.extractfile(member)
    if stream is None:raise ValueError("Unreadable original source "+path)
    return stream.read()

def source_cards(bundle):
    with tarfile.open(bundle,"r:gz") as tar:
        raw16=get_bundle_bytes(tar,F16_FILE)
        rawf17=get_bundle_bytes(tar,F17F_FILE)
        f16=json.loads(raw16)
        f17f=json.loads(rawf17)
        if set(f16)!=set(CASES) or not f17f.get("CKM_numerical_3_of_3") or (
            not f17f.get("full_complex_lepton_physical_widths_validated")):
            raise ValueError("F16 or F17f physical source cohort incomplete")
        entries=f17f.get("CKM_candidate_cards")
        if not isinstance(entries,list) or len(entries)!=3 or (
            {r["candidate_id"] for r in entries}!=set(CASES)):
            raise ValueError("F17f original source card inventory incomplete")
        cards={}
        for row in entries:
            basename=row["file"]
            if Path(basename).name!=basename:
                raise ValueError("Unsafe original F17f card basename")
            data=get_bundle_bytes(tar,F17F_SUBDIR+"/"+basename)
            if sha(data)!=row["sha256"]:
                raise ValueError("Actual source F17f SLHA hash mismatch")
            cards[row["candidate_id"]]=(row,data)
    return f16,raw16,rawf17,cards

def masses_from_original_slha(data):
    masses={};block=None
    for line in data.decode("utf-8").splitlines():
        s=line.split("#",1)[0].strip()
        if not s:continue
        t=s.split()
        if t[0].upper()=="BLOCK":
            block=t[1].upper()
            continue
        if t[0].upper() in ("DECAY","QNUMBERS"):
            block=None
            continue
        if block=="MASS":
            if len(t)!=2:raise ValueError("Malformed source SLHA MASS row")
            pdg=int(t[0]);value=float(t[1].replace("D","E"))
            if pdg in masses or not math.isfinite(value):
                raise ValueError("Duplicate/unphysical source mass")
            masses[pdg]=value
    return masses

def scalar_input(case,source,f18,card):
    scalar=source.get("scalar")
    if not isinstance(scalar,dict):raise ValueError("Missing original F16 Zee scalar inputs")
    keys=("mH1","mH2","mh2","ma","beta","alpha","gamma",
          "m12sq","lc","k1","k2","k12")
    args={k:finite(scalar[k],k) for k in keys}
    if not source.get("complex_Y_and_f_reconstructed_from_exact_F13"):
        raise ValueError("F16 original complex neutrino Yukawa mapping not certified")
    masses=masses_from_original_slha(card)
    for pdg,key in ((25,None),(35,"mh2"),(36,"ma"),
                    (37,"mH1"),(9000037,"mH2")):
        expected=125. if key is None else args[key]
        if pdg not in masses or not math.isclose(masses[pdg],expected,rel_tol=3e-7,abs_tol=0.0002):
            raise ValueError("Original UFO card/physical F16 spectrum mismatch "+str(pdg))
    if f18["provenance"].get("source_F17f_card_SHA256")!=sha(card):
        raise ValueError("F18 completed result not tied to same original F17f candidate card")
    doublet=f18.get("H2_doublet_weight_sin2gamma")
    if doublet is not None and not math.isclose(
        finite(doublet,"H2_doublet_weight"),math.sin(args["gamma"])**2,
        rel_tol=1e-9,abs_tol=1e-9):
        raise ValueError("H2 charged-doublet production mixing weight changed")
    return args

def calc_one(name,source,f18,card,*,quadrature):
    p=scalar_input(name,source,f18,card)
    gate6=benchmark(beta=p["beta"],alpha=p["alpha"],gamma=p["gamma"],
                    mH1=p["mH1"],mH2=p["mH2"],mh2=p["mh2"],ma=p["ma"],
                    m12sq=p["m12sq"],lc=p["lc"],k1=p["k1"],
                    k2=p["k2"],k12=p["k12"])
    # Source Gate6 mass identities must reconstruct the exact original F16
    # physical spectrum; a scalar theory screen is invalid if the spectrum
    # itself is mismatched.
    for got,expected in zip(gate6["rebuilt_charged_masses_GeV"],
                            (p["mH1"],p["mH2"])):
        if not math.isclose(got,expected,rel_tol=1e-8,abs_tol=2e-5):
            raise ValueError("Independent Zee charged mass spectrum did not close "+name)
    for got,expected in zip(gate6["rebuilt_neutral_masses_GeV"],
                            (125.,p["mh2"])):
        if not math.isclose(got,expected,rel_tol=1e-8,abs_tol=2e-5):
            raise ValueError("Independent Zee neutral mass spectrum did not close "+name)
    ew=compute_stu(m1=p["mH1"],m2=p["mH2"],mh=125.,mH=p["mh2"],
                   mA=p["ma"],alpha=p["alpha"],beta=p["beta"],
                   gamma=p["gamma"],n=quadrature)
    fit=ew["correlated_fit_screens"]
    primary=fit["Gfitter_2026_U_floating"]
    bfb=gate6["sufficient_global_quartic_BFB"]
    uni=gate6["tree_unitarity_pass"]
    if type(bfb)!=bool or type(uni)!=bool:
        raise ValueError("Invalid Gate6 screen decisions")
    br=f18["BR_H2_H1_Z_model_LO_2plus3"]
    brtb=f18["BR_H1_tb_model_LO_2plus3"]
    prod=f18["cascade_BR_product_model_LO_2plus3"]
    for value,label in ((br,"BRH2H1Z"),(brtb,"BRH1tb"),(prod,"cascadeBR")):
        if not 0<finite(value,label)<=1:raise ValueError("Invalid validated MadWidth BR")
    if not math.isclose(br*brtb,prod,rel_tol=1e-10,abs_tol=1e-12):
        raise ValueError("Completed MadWidth cascade BR arithmetic mismatch")
    states=f18["charged_H_decay_tables"]
    widths={k:finite(states[k]["total_GeV"],k+" width") for k in ("37","9000037")}
    gate_status={
        "exact_F16_F17f_F18_model_source_and_MadWidth":"VALIDATED_INPUT",
        "Zee_tree_BFB_sufficient_not_necessary":
           "SCREEN_PASS" if bfb else "NOT_CERTIFIED_BY_SUFFICIENT_TEST",
        "Zee_scalar_2to2_tree_unitarity_8pi":
           "SCREEN_PASS" if uni else "SCREEN_FAIL",
        "scalar_STU_Gfitter_2026_3D_Gaussian":
           "SCREEN_PASS" if primary["inside_95percent_3D_gaussian_ellipsoid"]
           else "SCREEN_OUTSIDE_95PCT_REGION",
        "scalar_STU_PDG_2025_3D_Gaussian_robustness":
           "SCREEN_PASS" if fit["PDG_2025_U_floating"][
             "inside_95percent_3D_gaussian_ellipsoid"]
           else "SCREEN_OUTSIDE_95PCT_REGION",
        "F17f_complex_source_amplitudes_not_full_LFV":"SOURCE_VALIDATED_NOT_LIKELIHOOD",
        "F18_model_tree_2plus3_body_MadWidth":"EVALUATED_MODEL_TREE_ONLY",
        **REQUIRED_BLOCKERS,
    }
    has_screen_flag=any(v in ("SCREEN_FAIL","SCREEN_OUTSIDE_95PCT_REGION",
                            "NOT_CERTIFIED_BY_SUFFICIENT_TEST") for v in gate_status.values())
    return {
        "candidate_id":name,
        "physics_convention":"general_Zee_two_charged_states_TypeII_like_quark_ansatz",
        "scalar_original_F16_inputs":p,
        "scalar_theory_gate6":gate6,
        "EWPO_correlated_scalar_STU_A1H":ew,
        "widths_GeV":{"H1":widths["37"],"H2":widths["9000037"]},
        "BR_H2_H1Z_tree_MadWidth":br,"BR_H1_tb_tree_MadWidth":brtb,
        "BR_cascade_tree_MadWidth":prod,
        "constraint_gates":gate_status,
        "has_any_screen_red_flag":has_screen_flag,
        "physical_Zee_fully_allowed_or_excluded":None,
        "global_95pct_model_exclusion_or_acceptance":None,
    }

def run(merged_path,bundle_path,out,*,quadrature=160):
    merged_path=Path(merged_path).expanduser().resolve()
    bundle_path=Path(bundle_path).expanduser().resolve()
    out=Path(out).expanduser().resolve()
    if out.exists():raise FileExistsError("Never overwrite an F19 completed or partial run")
    source=json.loads(merged_path.read_text())
    if source.get("status")!=F18_MERGE_STATUS or (
        source.get("three_original_benchmarks_LO_MadWidth_completed") is not True) or (
        source.get("QCD_NLO_or_loop_corrected") is not False) or (
        source.get("physical_Zee_model_allowed_or_excluded") is not None):
        raise ValueError("Not the complete original F18 source-constrained 3-case tree campaign")
    if quadrature<32 or quadrature>1000:raise ValueError("Unphysical STU quadrature setting")
    f16,raw16,rawf17,cards=source_cards(bundle_path)
    provenance=source.get("software_and_flavor_source_provenance",{})
    if sha(rawf17)!=provenance.get("original_F17f_report_SHA256"):
        raise ValueError("F18 output does not belong to the original F16 source bundle")
    rows=source.get("benchmarks")
    if not isinstance(rows,list) or len(rows)!=3 or (
        {r["candidate_id"] for r in rows}!=set(CASES)):
        raise ValueError("Original F18 three benchmark cohort mismatch")
    by_id={r["candidate_id"]:r for r in rows}
    results=[calc_one(n,f16[n],by_id[n],cards[n][1],quadrature=quadrature)
             for n in CASES]
    metadata={
        "status":F19_STATUS,
        "observational_allowance_or_exclusion":None,
        "all_three_exact_source_matched":True,
        "three_complete_F18_MadWidth_tree_widths_reused":True,
        "new_evaluations":"Exact-source Gate6 quartic BFB+unitarity and GateA1H scalar STU 3D covariance",
        "F18_merged_JSON_SHA256":sha(merged_path.read_bytes()),
        "F16_original_source_bundle_SHA256":sha(bundle_path.read_bytes()),
        "F16_reconstructed_scalar_JSON_SHA256":sha(raw16),
        "F17f_original_report_SHA256":sha(rawf17),
        "quadrature_nodes":quadrature,
        "every_required_full_model_constraint_evaluated":False,
        "missing_blockers":list(REQUIRED_BLOCKERS),
        "benchmarks":results,
    }
    out.mkdir(parents=True,exist_ok=False)
    (out/"F19_integrated_three_constraint_ledger_NOT_ALLOWED.json").write_text(
        json.dumps(metadata,indent=2,sort_keys=True,allow_nan=False)+"\n")
    with (out/"F19_three_scalar_EWPO_vs_cascade_NOT_ALLOWED.csv").open("w",newline="") as handle:
        cols=("candidate_id","mH1_GeV","mH2_GeV","gamma_rad",
              "Gamma_H1_GeV","Gamma_H2_GeV","BR_H2_H1Z","BR_H1_tb","BR_cascade",
              "BFB_sufficient","tree_unitarity","max_abs_unitarity_eigenvalue",
              "S","T","U","Gfitter_chi2","Gfitter_95region",
              "PDG2025_chi2","PDG2025_95region","model_fully_allowed")
        writer=csv.DictWriter(handle,fieldnames=cols);writer.writeheader()
        for r in results:
            t=r["scalar_theory_gate6"]
            e=r["EWPO_correlated_scalar_STU_A1H"]
            f=e["correlated_fit_screens"]
            writer.writerow(dict(
                candidate_id=r["candidate_id"],
                mH1_GeV=r["scalar_original_F16_inputs"]["mH1"],
                mH2_GeV=r["scalar_original_F16_inputs"]["mH2"],
                gamma_rad=r["scalar_original_F16_inputs"]["gamma"],
                Gamma_H1_GeV=r["widths_GeV"]["H1"],
                Gamma_H2_GeV=r["widths_GeV"]["H2"],
                BR_H2_H1Z=r["BR_H2_H1Z_tree_MadWidth"],
                BR_H1_tb=r["BR_H1_tb_tree_MadWidth"],
                BR_cascade=r["BR_cascade_tree_MadWidth"],
                BFB_sufficient=t["sufficient_global_quartic_BFB"],
                tree_unitarity=t["tree_unitarity_pass"],
                max_abs_unitarity_eigenvalue=t["max_abs_unitarity_eigenvalue"],
                S=e["scalar_STU"]["S"],T=e["scalar_STU"]["T"],U=e["scalar_STU"]["U"],
                Gfitter_chi2=f["Gfitter_2026_U_floating"]["chi2_relative_to_fit_minimum"],
                Gfitter_95region=f["Gfitter_2026_U_floating"][
                    "inside_95percent_3D_gaussian_ellipsoid"],
                PDG2025_chi2=f["PDG_2025_U_floating"]["chi2_relative_to_fit_minimum"],
                PDG2025_95region=f["PDG_2025_U_floating"][
                    "inside_95percent_3D_gaussian_ellipsoid"],
                model_fully_allowed="UNKNOWN_NOT_EVALUATED"))
    for r in results:
        fits=r["EWPO_correlated_scalar_STU_A1H"]["correlated_fit_screens"]
        print("F19_CASE",r["candidate_id"],
              "BFB_SUFFICIENT",r["scalar_theory_gate6"]["sufficient_global_quartic_BFB"],
              "UNITARITY",r["scalar_theory_gate6"]["tree_unitarity_pass"],
              "GFITTER_CHI2",format(fits["Gfitter_2026_U_floating"][
                  "chi2_relative_to_fit_minimum"],".7g"),
              "GFITTER_SCREEN",fits["Gfitter_2026_U_floating"][
                  "inside_95percent_3D_gaussian_ellipsoid"],
              "PDG_SCREEN",fits["PDG_2025_U_floating"][
                  "inside_95percent_3D_gaussian_ellipsoid"],
              "CASCADE_BR",format(r["BR_cascade_tree_MadWidth"],".8f"),
              "MODEL_ALLOWED","UNKNOWN")
    print("F19_STATUS",F19_STATUS,"SOURCE_CASES",len(results),
          "FULL_MODEL_ALLOWED",False,"EVALUATION_COMPLETE_ONLY_FOR_SCALAR_EWPO",True)
    print("F19_OUTPUT",out)
    return metadata

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--f18-merged",type=Path,required=True)
    p.add_argument("--f16-source-bundle",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--quadrature-nodes",type=int,default=160)
    a=p.parse_args(argv)
    run(a.f18_merged,a.f16_source_bundle,a.output_dir,quadrature=a.quadrature_nodes)

if __name__=="__main__":main()

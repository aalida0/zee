#!/usr/bin/env python3
"""Joint B4+B2+B3+A1V candidate audit; NOT a physical allowed-point classifier.

Matches B4 scalar candidates to B2 neutrino-closed Yukawa solutions, B3
leptonic width replacement, and legacy A1V SuperIso scans. Strictly
checks 4-component charged-spectrum provenance since A1V grid has no
candidate ID. No statistical likelihoods or full LFV are inferred.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import statistics
from collections import Counter,defaultdict
from pathlib import Path

STATUS="GATE_B4C_JOINED_SCREEN_AUDIT_ONLY_NOT_ALLOWED"
SCALAR_MATCH_FIELDS=("mH1","mH2","gamma","tanbeta")
B3_MATCH_FIELDS=("mH1","mH2","gamma")
B3_FIELDS=("BR_H2_H1Z_included_general_Zee",
           "BR_H1_tb_included_general_Zee",
           "production_weighted_partial_cascade_proxy")
COLS=(
    "candidate_id","seed_id","mH1","mH2","mh2","ma","gamma",
    "tanbeta","S","T","U","chi2_Gfitter","chi2_PDG",
    "max_unitarity","b4_nonleptonic_cascade_proxy",
    "n_B2_flavour_solutions","n_B3_width_solutions",
    "min_partial_LFV_score_NOT_EXCLUSION",
    "best_LFV_max_abs_f","best_LFV_max_abs_Y",
    "best_LFV_neutrino_closure_eV",
    "leading_partial_LFV_channel",
    "leading_partial_LFV_ratio_NOT_EXCLUSION",
    "B3_BR_H2_H1Z_min","B3_BR_H2_H1Z_median",
    "B3_BR_H2_H1Z_max",
    "B3_BR_H1_tb_min","B3_BR_H1_tb_median",
    "B3_BR_H1_tb_max",
    "B3_cascade_proxy_min","B3_cascade_proxy_median",
    "B3_cascade_proxy_max",
    "B3_cascade_proxy_delta_vs_B4_nonleptonic",
    "legacy_SuperIso_SM_BR","legacy_SuperIso_full_Zee_BR",
    "legacy_SuperIso_linear_delta_BR","legacy_SuperIso_quadratic_delta_BR",
    "status",
)


def get_rows(path):
    with Path(path).open(newline="") as fh:
        rd=csv.DictReader(fh)
        if rd.fieldnames is None:raise ValueError(f"No CSV header: {path}")
        rows=list(rd)
        if not rows:raise ValueError(f"Empty CSV: {path}")
    return rows


def finite_value(row,k):
    try:v=float(row[k])
    except (TypeError,ValueError,KeyError) as exc:
        raise ValueError(f"Missing/invalid {k}") from exc
    if not math.isfinite(v):raise ValueError(f"Nonfinite {k}")
    return v


def ensure_close(a,b,k):
    x=finite_value(a,k);y=finite_value(b,k)
    if not math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-8):
        raise ValueError(f"Mismatch {k}: {x} versus {y}")


def ensure_identical_ids(rows,key,what):
    ids=[r.get(key) for r in rows]
    if any(not x for x in ids) or len(set(ids))!=len(ids):
        raise ValueError(f"{what} has duplicate/empty IDs")
    return set(ids)


def index_superiso(spectra,flavor):
    """One-to-one join on the four physical parameters, not row order."""
    matches={}
    used=set()
    for p in spectra:
        candidate_id=p["id"]
        good=[]
        for i,r in enumerate(flavor):
            if all(math.isclose(finite_value(p,k),finite_value(r,k),
                                rel_tol=1e-9,abs_tol=1e-8)
                   for k in SCALAR_MATCH_FIELDS):
                good.append(i)
        if len(good)!=1:
            raise ValueError(f"SuperIso join for {candidate_id}: "
                             f"expected one match; got {len(good)}")
        j=good[0]
        if j in used:
            raise ValueError("SuperIso spectrum matches multiple candidates")
        used.add(j)
        matches[candidate_id]=flavor[j]
    if len(used)!=len(flavor):
        raise ValueError("Unmatched extra A1V results")
    return matches


def make_join(spectra,b2,b3,flavor):
    ids=ensure_identical_ids(spectra,"id","B4 spectra")
    if set(b2)!=ids:raise ValueError("B2 JSON candidate IDs mismatch B4")
    if any(not isinstance(v,list) or not v for v in b2.values()):
        raise ValueError("B2 JSON has no Yukawa solutions")
    b3map=defaultdict(list)
    for row in b3:
        if row.get("candidate_id") not in ids:
            raise ValueError("B3 contains candidate absent from B4")
        b3map[row["candidate_id"]].append(row)
    if set(b3map)!=ids:raise ValueError("Missing B3 candidate rows")
    flavor_by_id=index_superiso(spectra,flavor)
    result=[]
    for p in spectra:
        ident=p["id"]
        b2sol=b2[ident]
        b3sol=b3map[ident]
        # The B3 script stores one row for each rank 1..N of B2 JSON.
        ranks=[int(row["b2_solution_rank"]) for row in b3sol]
        if len(ranks)!=len(set(ranks)) or sorted(ranks)!=list(
                range(1,len(ranks)+1)):
            raise ValueError("Missing/duplicate B3 rank for "+ident)
        if len(b3sol)!=len(b2sol):
            raise ValueError("B2/B3 Yukawa selection count differs for "+ident)
        for row in b3sol:
            for k in B3_MATCH_FIELDS:
                ensure_close(p,row,k)
            j=int(row["b2_solution_rank"])-1
            sol=b2sol[j]
            if str(sol["candidate_id"])!=ident:
                raise ValueError("Mismatched B2 candidate rank")
            for k in B3_MATCH_FIELDS:
                ensure_close(row,sol,k)
            ensure_close({"lfv":row["b2_partial_LFV_score_NOT_EXCLUSION"]},
                         {"lfv":sol["partial_LFV_score_NOT_EXCLUSION"]},
                         "lfv")
            ensure_close({"closure":row["neutrino_matrix_closure_eV"]},
                         {"closure":sol["neutrino_matrix_closure_eV"]},
                         "closure")
            if "NOT_ALLOWED" not in row.get("candidate_id","") and (
                not all(0<=finite_value(row,k)<=1 for k in B3_FIELDS)):
                raise ValueError("B3 fractions outside [0,1]")
            if "NOT_ALLOWED" not in str(sol["status"]):
                raise ValueError("B2 solution not explicitly unclassified")
        scored=sorted(b2sol,key=lambda row:finite_value(
            row,"partial_LFV_score_NOT_EXCLUSION"))
        best=scored[0]
        lfvratios=best["partial_LFV_ratios_NOT_EXCLUSION"]
        if not lfvratios:raise ValueError("B2 LFV ratios empty")
        leading=max(lfvratios,key=lambda k:float(lfvratios[k]))
        if not math.isclose(float(lfvratios[leading]),
                            float(best["partial_LFV_score_NOT_EXCLUSION"]),
                            rel_tol=1e-10,abs_tol=1e-15):
            raise ValueError("B2 best LFV score disagrees with channels")
        value={}
        for k in ("seed_id","mH1","mH2","mh2","ma","gamma","tanbeta",
                  "S","T","U","chi2_Gfitter","chi2_PDG",
                  "max_unitarity"):
            value[k]=p[k]
        value["candidate_id"]=ident
        value["b4_nonleptonic_cascade_proxy"]=finite_value(
            p,"production_weighted_nonleptonic_cascade_upper_proxy")
        value["n_B2_flavour_solutions"]=len(b2sol)
        value["n_B3_width_solutions"]=len(b3sol)
        value["min_partial_LFV_score_NOT_EXCLUSION"]=float(
            best["partial_LFV_score_NOT_EXCLUSION"])
        value["best_LFV_max_abs_f"]=float(best["max_abs_f"])
        value["best_LFV_max_abs_Y"]=float(best["max_abs_Y"])
        value["best_LFV_neutrino_closure_eV"]=float(
            best["neutrino_matrix_closure_eV"])
        value["leading_partial_LFV_channel"]=leading
        value["leading_partial_LFV_ratio_NOT_EXCLUSION"]=float(
            lfvratios[leading])
        for field,stem in zip(B3_FIELDS,(
                "B3_BR_H2_H1Z","B3_BR_H1_tb","B3_cascade_proxy")):
            vals=[finite_value(row,field) for row in b3sol]
            value[stem+"_min"]=min(vals)
            value[stem+"_median"]=statistics.median(vals)
            value[stem+"_max"]=max(vals)
        upper=value["b4_nonleptonic_cascade_proxy"]
        if value["B3_cascade_proxy_max"]>upper+5e-10:
            raise ValueError("Adding physical lepton widths cannot "
                             "increase the B4 nonleptonic proxy")
        value["B3_cascade_proxy_delta_vs_B4_nonleptonic"]=(
            value["B3_cascade_proxy_median"]-upper)
        f=flavor_by_id[ident]
        for name,key in (
                ("legacy_SuperIso_SM_BR","SM_BR"),
                ("legacy_SuperIso_full_Zee_BR","full_Zee_BR"),
                ("legacy_SuperIso_linear_delta_BR","linear_delta_BR"),
                ("legacy_SuperIso_quadratic_delta_BR","quadratic_delta_BR")):
            value[name]=finite_value(f,key)
        if not math.isclose(
                value["legacy_SuperIso_SM_BR"]+
                value["legacy_SuperIso_linear_delta_BR"]+
                value["legacy_SuperIso_quadratic_delta_BR"],
                value["legacy_SuperIso_full_Zee_BR"],
                rel_tol=1e-7,abs_tol=2e-10):
            raise ValueError("A1V full BR fails legacy SM+NP decomposition")
        value["status"]="JOINED_THEORY_EWPO_ALGEBRA_PARTIAL_LFV_ONLY_NOT_ALLOWED"
        result.append(value)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b4-csv",type=Path,required=True)
    ap.add_argument("--b2-json",type=Path,required=True)
    ap.add_argument("--b3-csv",type=Path,required=True)
    ap.add_argument("--a1v-csv",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,
                    default=Path("work/gateB4c_joined_candidate_audit"))
    args=ap.parse_args()
    b4=get_rows(args.b4_csv)
    b2=json.loads(args.b2_json.read_text())
    b3=get_rows(args.b3_csv)
    a1v=get_rows(args.a1v_csv)
    table=make_join(b4,b2,b3,a1v)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    dest=args.output_dir/"joint_scalar_neutrino_width_flavour_NOT_ALLOWED.csv"
    with dest.open("w",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=COLS)
        writer.writeheader()
        writer.writerows(sorted(table,key=lambda row:
            row["B3_cascade_proxy_median"],reverse=True))
    ancestry=dict(Counter(r["seed_id"] for r in table))
    summary={
        "status":STATUS,
        "n_joined_scalar_spectra":len(table),
        "n_B2_neutrino_Yukawa_families":sum(
            r["n_B2_flavour_solutions"] for r in table),
        "n_B3_width_solutions":sum(
            r["n_B3_width_solutions"] for r in table),
        "n_A1V_legacy_flavor_points":len(a1v),
        "seed_ancestry":ancestry,
        "leading_partial_LFV_channels":dict(Counter(
            r["leading_partial_LFV_channel"] for r in table)),
        "ranges":{
            k:{"min":min(float(r[k]) for r in table),
               "median":statistics.median(float(r[k]) for r in table),
               "max":max(float(r[k]) for r in table)}
            for k in ("B3_BR_H2_H1Z_median","B3_BR_H1_tb_median",
                      "B3_cascade_proxy_median",
                      "min_partial_LFV_score_NOT_EXCLUSION",
                      "legacy_SuperIso_full_Zee_BR")},
        "physically_allowed":None,
        "neutrino_likelihood_fit":False,
        "complete_LFV_amplitudes":False,
        "HiggsTools_applied":False,
        "modern_BtoXsGamma_exclusion":False,
        "true_collider_production_cross_section":False,
        "message":"Joint scalar/EWPO screen + one neutrino central target "
                  "+ partial LFV rates + included LO widths "
                  "+ legacy flavor predictions. None is an exclusion.",
        "output_csv":str(dest),
    }
    (args.output_dir/"summary.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print("STATUS",STATUS)
    print("SCALAR_CANDIDATES",len(table))
    print("NEUTRINO_YUKAWA_SOLUTIONS",
          summary["n_B2_neutrino_Yukawa_families"])
    print("LEPTON_WIDTH_SOLUTIONS",summary["n_B3_width_solutions"])
    print("LEGACY_FLAVOR_POINTS",len(a1v))
    print("SEED_ANCESTRY",ancestry)
    print("FULL_MODEL_ALLOWED unknown")
    print("TOP_CASCADE_PROXY_CANDIDATES")
    for r in sorted(table,key=lambda p:p[
            "B3_cascade_proxy_median"],reverse=True)[:5]:
        print(r["candidate_id"],
              "proxy",format(r["B3_cascade_proxy_median"],".6g"),
              "BR_H2_H1Z",format(r["B3_BR_H2_H1Z_median"],".6g"),
              "legacy_BtoXs_gamma",
              format(r["legacy_SuperIso_full_Zee_BR"],".8g"),
              "min_partial_LFV",
              format(r["min_partial_LFV_score_NOT_EXCLUSION"],".5g"))
    print("OUTPUT",dest)

if __name__=="__main__":
    main()

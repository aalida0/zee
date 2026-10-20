#!/usr/bin/env python3
"""Paper2: rank neutrino-closed Zee Yukawas by muon-column invariants.

An intentionally model-convention-conservative screening tool.
Yang/Wu Lagrangian.fr charged-doublet term:
    -ylz[i,j] bar(L_i) mu_R(j) H2
so H2 doublet muon couplings involve the entire Y[:, mu] COLUMN,
not Y[mu, :]. Antisymmetric f[:, mu] likewise connects mu_L with
neutrino flavors, but its vertex normalization must be checked from
the exported UFO before amplitudes are predicted.

For Hlight = cos(gamma) HD + sin(gamma) chi,
Hheavy = -sin(gamma) HD + cos(gamma) chi,
the two same-chirality flavor-summed t-channel coupling products
are proportional to (-sin cos gamma)*||Y[:,mu]||² and
(+sin cos gamma)*||f[:,mu]||², respectively (normalization convention
for f deliberately NOT fixed here).

The script evaluates no t-channel propagators/helicity amplitudes,
cross sections, interference, LFV pass/fail, or allowed parameter space.
It is meant to identify which B2 Yukawa samples could merit re-export
of a complex-coupling UFO. B2 originally selected the lowest PARTIAL
LFV scores; do not call its top 5 a representative allowed sample.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np

STATUS="PAPER2_MUON_COLUMN_YUKAWA_SCREEN_NOT_TCHANNEL_RATE_OR_ALLOWED"
COLS=("candidate_id","b2_solution_rank","mH1","mH2","gamma",
      "Y_muon_column_norm","f_muon_column_norm",
      "Y_muon_column_norm_squared","f_muon_column_norm_squared",
      "abs_mixing_overlap_Y_Y","abs_mixing_overlap_f_f",
      "Y_muon_ROW_norm_CONTROL","partial_LFV_score_NOT_EXCLUSION",
      "max_abs_f","max_abs_Y","neutrino_matrix_closure_eV",
      "status")


def matrix(encoded,name):
    if not isinstance(encoded,dict) or (
        "real" not in encoded or "imag" not in encoded):
        raise ValueError("Missing complex "+name+" matrix")
    a=np.asarray(encoded["real"],dtype=float)
    b=np.asarray(encoded["imag"],dtype=float)
    if a.shape!=(3,3) or b.shape!=(3,3) or (
        not np.isfinite(a).all() or not np.isfinite(b).all()):
        raise ValueError("Invalid complex "+name+" shape/values")
    return a+1j*b


def evaluate(solution,rank):
    Y=matrix(solution["Y"],"Y")
    f=matrix(solution["f"],"f")
    if np.max(np.abs(f+f.T))>1e-10:
        raise ValueError("Non-antisymmetric Zee f")
    gamma=float(solution["gamma"])
    if not math.isfinite(gamma) or not 0<gamma<math.pi/2:
        raise ValueError("Invalid gamma")
    s=abs(math.sin(gamma)*math.cos(gamma))
    y2=float(np.vdot(Y[:,1],Y[:,1]).real)
    f2=float(np.vdot(f[:,1],f[:,1]).real)
    row_norm=float(np.linalg.norm(Y[1,:]))
    score=float(solution["partial_LFV_score_NOT_EXCLUSION"])
    closure=float(solution["neutrino_matrix_closure_eV"])
    if not (all(math.isfinite(q) and q>=0 for q in
            (y2,f2,row_norm,score,closure)) and closure<1e-9):
        raise ValueError("Invalid B2 neutrino/LFV diagnostic")
    return {
        "candidate_id":str(solution["candidate_id"]),
        "b2_solution_rank":rank,
        "mH1":solution["mH1"],"mH2":solution["mH2"],
        "gamma":gamma,
        "Y_muon_column_norm":math.sqrt(y2),
        "f_muon_column_norm":math.sqrt(f2),
        "Y_muon_column_norm_squared":y2,
        "f_muon_column_norm_squared":f2,
        "abs_mixing_overlap_Y_Y":s*y2,
        "abs_mixing_overlap_f_f":s*f2,
        "Y_muon_ROW_norm_CONTROL":row_norm,
        "partial_LFV_score_NOT_EXCLUSION":score,
        "max_abs_f":solution["max_abs_f"],
        "max_abs_Y":solution["max_abs_Y"],
        "neutrino_matrix_closure_eV":closure,
        "status":"NEUTRINO_CLOSED_MUON_COLUMN_ONLY_NOT_RATE_OR_ALLOWED",
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b2-json",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    data=json.loads(args.b2_json.read_text())
    if not isinstance(data,dict) or not data:
        raise ValueError("Expected nonempty B2 candidate dictionary")
    rows=[]
    for ident,solutions in data.items():
        if not isinstance(solutions,list) or not solutions:
            raise ValueError("Missing B2 family for "+str(ident))
        for rank,sol in enumerate(solutions,1):
            if str(sol["candidate_id"])!=ident:
                raise ValueError("B2 candidate ID mismatch")
            rows.append(evaluate(sol,rank))
    # Ranking emphasizes both types of muon charged-Higgs couplings,
    # without pretending their field-theory normalization is identical.
    by_Y=sorted(rows,key=lambda r:r["abs_mixing_overlap_Y_Y"],reverse=True)
    by_f=sorted(rows,key=lambda r:r["abs_mixing_overlap_f_f"],reverse=True)
    out=args.output_dir
    if out.exists() and any(out.iterdir()):
        raise ValueError("Use a NEW empty output directory")
    out.mkdir(parents=True,exist_ok=True)
    file=out/"muon_yukawa_column_proxies_NOT_CROSS_SECTION.csv"
    with file.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLS)
        w.writeheader()
        w.writerows(by_Y)
    summary={
        "status":STATUS,
        "n_scalar_candidates":len(data),
        "n_B2_flavour_solutions":len(rows),
        "max_abs_mixing_Y_Y":by_Y[0]["abs_mixing_overlap_Y_Y"],
        "max_abs_mixing_f_f":by_f[0]["abs_mixing_overlap_f_f"],
        "top_5_Y_muon_column":by_Y[:5],
        "top_5_f_muon_column":by_f[:5],
        "all_150_B2_selected_by_low_PARTIAL_LFV":True,
        "does_not_include_tchannel_propagator":True,
        "uses_unfixed_f_vertex_normalization":True,
        "muon_specific_cross_section_calculated":False,
        "physical_LFV_exclusion_calculated":False,
        "note":"For future MG5 muon-collider amplitudes, validate Yang/Wu "
               "muon COLUMN flavor conventions, complex f/Y UFO support, "
               "neutrino propagator/chirality and B2 source matrix closure.",
        "output_csv":str(file),
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("STATUS",STATUS)
    print("B2_YUKAWA_SOLUTIONS",len(rows))
    print("MAX_MIXING_ABS_Y_Y",format(summary["max_abs_mixing_Y_Y"],".8g"))
    print("MAX_MIXING_ABS_f_f",format(summary["max_abs_mixing_f_f"],".8g"))
    print("TOP_MUON_COLUMN_Y_CANDIDATES")
    for r in by_Y[:5]:
        print(r["candidate_id"],"rank",r["b2_solution_rank"],
              "overlap_Y",format(r["abs_mixing_overlap_Y_Y"],".7g"),
              "partial_LFV",format(
                  r["partial_LFV_score_NOT_EXCLUSION"],".6g"))
    print("TCHANNEL_CROSS_SECTION_COMPUTED False")
    print("OUTPUT",file)


if __name__=="__main__":
    main()

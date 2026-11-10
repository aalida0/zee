#!/usr/bin/env python3
"""Complete *restricted* LFV/tree-D4 reevaluation of original Zee 400 scalar points,
using explicitly texture-biased homogeneous neutrino inverses.

No full Zee LFV/global acceptance. This is a source-locked candidate audit,
not an experimental exclusion or discovery forecast.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

from module2.interface import decode, evaluate as neutrino_evaluate
from module14.decays import DecayCalculation
from module14.lfv import evaluate_family as lfv_evaluate
from module14.scan import neutrino_input,perturbativity,digest
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs
from research.full_constraints.scan_pilot_2026.homogeneous_texture_lfv import evaluate_texture,SEED,MEG_II

CASES=((284,"IO",4,0.0),(284,"NO",4,0.0),(284,"NO",11,0.001),(112,"IO",6,0.0))
ORIGINAL_VACUUM={284:"UNKNOWN",112:"PASS"}
ORIGINAL_B={284:{"pull":1.7690327380223143,"class":"APPROX_COMPATIBLE"},
             112:{"pull":6.7892789625350485,"class":"APPROX_DISFAVORED"}}

def detailed(case,scalar):
    id,ordering,index,eta=case
    first=evaluate_texture(scalar,ordering,index,eta)
    if first["status"]!="NEUTRINO_PASS_LFV_PARTIAL":
        raise ValueError(f"Texture candidate not validated: {first.get('error')}")
    input=first["nu_input"]
    n=neutrino_evaluate(input)
    metrics=perturbativity(n)
    if not metrics["overall_max"]<math.sqrt(4*math.pi):
        raise ArithmeticError("New texture violates perturbativity")
    neures=n["inverse"]["family_relative_residual"]
    if neures>=2e-9:raise ArithmeticError("New texture lost neutrino mass closure")
    family={k:n[k] for k in ("F","D","Ye","Ye2","Mnu")}
    family.update(input=input,input_sha256=digest(input))
    l=lfv_evaluate(family,True)
    if l["status"]!="PARTIAL" or l["complete_lfv"]:
        raise ArithmeticError("Unexpected physical LFV promotion")
    measured=l["channels"]["mu_to_e_gamma"]["partial_BR"]
    if not math.isclose(measured,first["partial_lfv"]["mu_to_e_gamma_BR"],rel_tol=1e-12,abs_tol=1e-24):
        raise ArithmeticError("Independent restricted LFV replay mismatch")
    widths=DecayCalculation(scalar["scalar"],family).evaluate(family)
    if widths["status"]!="PASS":
        raise ArithmeticError("New D4 width inventory incomplete")
    h2=widths["mothers"]["H2"]
    h1=widths["mothers"]["H1"]
    # One scalar-matched, neutrino-aligned source. D4 full tree two-body only.
    p=scalar["scalar"]["physical"]
    D=decode(n["D"])
    F=decode(n["F"])
    return {
       "scalar_id":id,"ordering":ordering,"family":index,"eta":eta,
       "scalar_sha256":scalar["scalar_sha256"],
       "original_scalar_masses_GeV":{"H1":p["mH1"],"H2":p["mH2"]},
       "tanbeta":math.tan(p["beta"]),"gamma_rad":p["gamma"],
       "original_vacuum_status":ORIGINAL_VACUUM[id],
       "original_B_approx_diagnostic":ORIGINAL_B[id],
       "neutrino_input_sha256":digest(input),
       "neutrino_residual":neures,
       "max_perturbative_yukawa":metrics["overall_max"],
       "F_max":float(np.max(np.abs(F))),"D_max":float(np.max(np.abs(D))),
       "D_em":abs(D[0,1]),"D_me":abs(D[1,0]),
       "partial_mu_to_e_gamma_BR":measured,
       "ratio_partial_mu_e_gamma_to_limit":measured/MEG_II,
       "partial_tau_radiative_BRs":{k: v["partial_BR"] for k,v in l["channels"].items()
                                  if k!="mu_to_e_gamma"},
       "partial_mu_to_3e_tree_BR":l["mu_to_3e"]["tree_subset_BR"],
       "partial_mu_to_3e_tree_scope":l["mu_to_3e"]["status"],
       "mu_to_3e_tree_relative_quadrature_change":l["mu_to_3e"]["quadrature_relative_change"],
       "H1_total_tree_width_GeV":h1["total"]["total_width_GeV"],
       "H2_total_tree_width_GeV":h2["total"]["total_width_GeV"],
       "BR_H2_H1Z_tree":h2["br_H1_Z"],
       "BR_H1_tb_tree":h1["br_tb"],
       "tree_cascade_product":widths["cascade_product"],
       "full_tree_D4_provenance_sha256":digest(widths["source_sha256"]),
       "physical_B":"UNKNOWN","physical_LFV":"UNKNOWN","physical_Higgs":"UNKNOWN",
       "globally_allowed":None,
       "full_Zee_LFV":False,
       "production_cross_section_pb":None,
       "physical_search_acceptance":None,
       "source_replay":{"module4_output_sha256":l["module4_output_sha256"],
                        "module2_input_sha256":digest(input),"decay_scalar_sha256":widths["scalar_sha256"]},
    }

def run(path:Path):
    if path.exists():raise FileExistsError("Refuse overwrite")
    scalars={s["id"]:s for s in strict_inputs()}
    res=[]
    for case in CASES:
        row=detailed(case,scalars[case[0]])
        res.append(row)
        print("TEXTURE_CANDIDATE_DETAIL",row["scalar_id"],row["ordering"],row["family"],row["eta"],
              "BR_MUE_PARTIAL",f'{row["partial_mu_to_e_gamma_BR"]:.11e}',
              "BR_MU3E_TREE",f'{row["partial_mu_to_3e_tree_BR"]:.11e}',
              "BR_H2_H1Z",f'{row["BR_H2_H1Z_tree"]:.9g}',
              "CASCADE_PRODUCT",f'{row["tree_cascade_product"]:.9g}',
              "VAC",row["original_vacuum_status"],
              "B_REF",row["original_B_approx_diagnostic"]["class"],flush=True)
    final={"schema":"zee-original-400-post-texture-d4-lfv-detailed-1",
       "status":"PARTIAL_LFV_AND_D4_TREE_CANDIDATE_DETAIL_COMPLETE",
       "selection":"Prior predeclared eta=0 and eta=0.001 families from independent 448-row scan; strong LFV selection bias, not flat-scan efficiency.",
       "cases":res,
       "MEGII_limit":MEG_II,
       "SINDRUM_mu3e_tree_reference_limit":1e-12,
       "n_cases":len(res),
       "physics_gate":"LEADING_LFV_PARTIAL_ONLY; HIGGS/B/VACUUM_FULL_UNKNOWN",
       "any_global_acceptance":None}
    path.write_text(json.dumps(final,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return final

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();run(a.output)

if __name__=="__main__":
    main()

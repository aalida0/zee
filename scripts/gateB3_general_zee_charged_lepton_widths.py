#!/usr/bin/env python3
"""Gate B3: general-Zee leptonic charged-scalar widths for B2 Yukawa families.

Zee Higgs basis from Chen, arXiv:2508.18757, Eq.(3)-(6):
  -L contains sqrt(2) bar(ell_R) Y^ell nu_L H_D^- +
  2 nu_L^T C f ell_L chi^+ + h.c.
  H1 = cos(gamma) H_D + sin(gamma) chi,
  H2 = -sin(gamma) H_D + cos(gamma) chi.

Ignoring negligible neutrino masses and tiny outgoing charged-lepton
mass interference, the partial two-body width for charged lepton ell is
  M/(16*pi) (2 * doublet_weight * sum_nu |Y[ell,nu]|^2
           + 4 * singlet_weight * sum_nu |f[nu,ell]|^2)
  * (1-m_ell^2/M^2)^2.

We DELETE the older Type-II tau-nu width from the scalar-only Gate6
inventory and REPLACE it with lepton-family-specific widths. This is a
consistent Higgs-basis choice, not an additional lepton term.

Still NOT full model BR: possible extra scalar/fermion channels,
higher-order QCD, off-shell modes and all experimental likelihood
requirements are absent. No point is certified allowed.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
from gate6_width_inventory import inventory, tau_width
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix, reconstruct_neutrino, scalar_kappa,
    ME, MMU, MTAU,
)

STATUS="GATE_B3_LEPTON_WIDTH_REPLACEMENT_ONLY_NOT_PHYSICAL_BR_OR_ALLOWED"
LEPTONS=("e","mu","tau")
MASSES=(ME,MMU,MTAU)
NUMERIC_ATOL=1e-9


def complex_matrix(payload, name):
    try:
        re=np.asarray(payload["real"],float)
        im=np.asarray(payload["imag"],float)
    except (KeyError,TypeError,ValueError) as exc:
        raise ValueError(f"Invalid complex {name} matrix") from exc
    if re.shape!=(3,3) or im.shape!=(3,3):
        raise ValueError(f"{name} must be a complex 3x3 matrix")
    z=re+1j*im
    if not np.all(np.isfinite(z)):
        raise ValueError(f"Nonfinite {name}")
    return z


def general_zee_lepton_widths(M,gamma,f,Y):
    """Return massless-neutrino LO per-flavor rates [GeV].

    f indices are neutrino,charged-lepton and Y rows are charged
    lepton. No cross-chirality interference at m_nu=0.
    """
    if not (math.isfinite(M) and M>0 and math.isfinite(gamma)
            and 0<=gamma<=math.pi/2):
        raise ValueError("Invalid mass or gamma")
    if f.shape!=(3,3) or Y.shape!=(3,3):
        raise ValueError("Expected 3x3 f and Y")
    if not np.all(np.isfinite(f)) or not np.all(np.isfinite(Y)):
        raise ValueError("Nonfinite Yukawas")
    if np.max(abs(f+f.T))>1.e-10:
        raise ValueError("f is not antisymmetric")
    cd2=math.cos(gamma)**2
    sd2=math.sin(gamma)**2
    out={}
    for i,name in enumerate(LEPTONS):
        suppression=max(0.,1-(MASSES[i]/M)**2)**2
        yy=float(np.sum(abs(Y[i,:])**2))
        ff=float(np.sum(abs(f[:,i])**2))
        rates=[]
        for md,dweight,sweight in ((M,cd2,sd2),(M,sd2,cd2)):
            val=md/(16*math.pi)*(2*dweight*yy+4*sweight*ff)*suppression
            if not math.isfinite(val) or val<0:raise ValueError("Invalid lepton rate")
            rates.append(val)
        out[name]={"H1":rates[0],"H2":rates[1],
                   "Y_row_norm_squared":yy,"f_column_norm_squared":ff}
    return out


def charged_lepton_widths(m1,m2,gamma,f,Y):
    # Above single-mass helper computes BOTH mixing weights at its given
    # mass; use the H1 component at m1 and the H2 component at m2.
    low=general_zee_lepton_widths(m1,gamma,f,Y)
    high=general_zee_lepton_widths(m2,gamma,f,Y)
    return {
        "H1":{ell:low[ell]["H1"] for ell in LEPTONS},
        "H2":{ell:high[ell]["H2"] for ell in LEPTONS},
    }


def ensure_neutrino_closure(row,f,Y,target):
    k=scalar_kappa(row["mH1"],row["mH2"],row["gamma"])
    err=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=k)-target)))
    if not math.isfinite(err) or err>NUMERIC_ATOL:
        raise ValueError("Saved f/Y do not reconstruct requested neutrino matrix")
    return err


def inventory_without_typeii_tau(row):
    """Keep existing bosonic and quark channels; replace lepton sector."""
    p=inventory(
        beta=row["beta"],mH1=row["mH1"],mH2=row["mH2"],
        alpha=row["alpha"],gamma=row["gamma"],
        m12sq=row["m12sq"],mh2=row["mh2"],ma=row["ma"],
        lc=row["lc"],k1=row["k1"],k2=row["k2"],k12=row["k12"])
    widths=p["partial_widths_GeV"]
    out={}
    for state in ("H1","H2"):
        if "tau_nu_TypeII" not in widths[state]:
            raise ValueError("Expected legacy Type-II tau-nu width missing")
        out[state]={k:float(v) for k,v in widths[state].items()
                    if k!="tau_nu_TypeII"}
    return out,p


def evaluate(row,f,Y,target):
    err=ensure_neutrino_closure(row,f,Y,target)
    widths,original=inventory_without_typeii_tau(row)
    leptons=charged_lepton_widths(row["mH1"],row["mH2"],
                                 row["gamma"],f,Y)
    totals={}
    fractions={}
    for state in ("H1","H2"):
        for ell,val in leptons[state].items():
            widths[state][f"{ell}_nu_generalZee"]=val
        totals[state]=sum(widths[state].values())
        if totals[state]<=0 or not math.isfinite(totals[state]):
            raise ValueError("Invalid total included width")
        fractions[state]={k:v/totals[state] for k,v in widths[state].items()}
    br2=fractions["H2"]["H1_Z"]
    br1=fractions["H1"]["tb"]
    proxy=math.sin(row["gamma"])**2*br2*br1
    return {
        "candidate_id":str(row["id"]), "mH1":row["mH1"],
        "mH2":row["mH2"],"gamma":row["gamma"],
        "neutrino_matrix_closure_eV":err,
        "leptonic_widths_GeV":leptons,
        "partial_widths_included_GeV":widths,
        "totals_included_GeV":totals,
        "BR_H2_H1Z_included_general_Zee":br2,
        "BR_H1_tb_included_general_Zee":br1,
        "production_weighted_partial_cascade_proxy":proxy,
        "legacy_B1_BR_H2_H1Z_TypeII_tau":
            original["conditional_fractions_included_channels_only"]["H2"]["H1_Z"],
        "legacy_B1_BR_H1_tb_TypeII_tau":
            original["conditional_fractions_included_channels_only"]["H1"]["tb"],
        "status":"GENERAL_ZEE_LEPTON_WIDTHS_LO_INCLUDED_ONLY_NOT_ALLOWED",
    }


def read_b1(path):
    needed=("id","mH1","mH2","mh2","ma","alpha","beta",
            "gamma","m12sq")
    original=None
    with Path(path).open(newline="") as fh:
        reader=csv.DictReader(fh)
        if reader.fieldnames is None or any(k not in reader.fieldnames for k in needed):
            raise ValueError("B1 complete candidate CSV required")
        result={}
        for row in reader:
            p={}
            for k in needed:
                if k=="id": p[k]=str(row[k]);continue
                p[k]=float(row[k])
            for k,d in (("lc",4.473),("k1",1.082),
                        ("k2",0.00398),("k12",-0.001266)):
                # B1 fixed these values; B4 varies and SERIALIZES them.
                # Never overwrite an explicitly scanned Zee quartic.
                supplied=row.get(k)
                p[k]=float(supplied) if supplied not in (None,"") else d
            if not all(math.isfinite(v) for k,v in p.items() if k!="id"):
                raise ValueError("Nonfinite scalar or Zee singlet input")
            if p["id"] in result:raise ValueError("Duplicate B1 ID")
            result[p["id"]]=p
    if not result:raise ValueError("B1 CSV empty")
    return result


def run(b1,b2,top):
    points=read_b1(b1)
    data=json.loads(Path(b2).read_text())
    if set(data)!=set(points):
        raise ValueError("Saved B2 Yukawa families do not cover EXACT B1 candidate set")
    target,_=target_neutrino_matrix()
    reports=[]
    for id_,solutions in data.items():
        if not isinstance(solutions,list) or not solutions:
            raise ValueError("Empty B2 Yukawa family")
        for j,solution in enumerate(solutions[:top],start=1):
            if str(solution.get("candidate_id"))!=id_:
                raise ValueError("Mismatched B2 candidate identifier")
            f=complex_matrix(solution["f"],"f")
            Y=complex_matrix(solution["Y"],"Y")
            x=evaluate(points[id_],f,Y,target)
            x["b2_solution_rank"]=j
            x["b2_partial_LFV_score_NOT_EXCLUSION"]=float(
                solution["partial_LFV_score_NOT_EXCLUSION"])
            reports.append(x)
    return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b1-csv",type=Path,required=True)
    ap.add_argument("--b2-json",type=Path,required=True)
    ap.add_argument("--top",type=int,default=10)
    ap.add_argument("--output-dir",type=Path,
                    default=Path("work/gateB3_zee_leptonic_widths"))
    a=ap.parse_args()
    if not 1<=a.top<=1000: ap.error("top must be 1..1000")
    rows=run(a.b1_csv,a.b2_json,a.top)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    cols=("candidate_id","b2_solution_rank","mH1","mH2","gamma",
          "BR_H2_H1Z_included_general_Zee",
          "BR_H1_tb_included_general_Zee",
          "production_weighted_partial_cascade_proxy",
          "legacy_B1_BR_H2_H1Z_TypeII_tau",
          "legacy_B1_BR_H1_tb_TypeII_tau",
          "b2_partial_LFV_score_NOT_EXCLUSION","neutrino_matrix_closure_eV")
    csvfile=a.output_dir/"cascade_width_corrected_NOT_ALLOWED.csv"
    with csvfile.open("w",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols)
        writer.writeheader()
        for row in sorted(rows,key=lambda x:x[
                "production_weighted_partial_cascade_proxy"],reverse=True):
            writer.writerow({k:row[k] for k in cols})
    full=a.output_dir/"all_width_details_NOT_ALLOWED.json"
    full.write_text(json.dumps(rows,indent=2)+"\n")
    print("STATUS",STATUS)
    print("CHARGED_LEPTON_TYPEII_WIDTH_REPLACED True")
    print("FULL_LEPTON_FLAVOUR_FIT False")
    print("HIGGSTOOLS_VALIDATED False")
    print("FULL_ZEE_PHYSICAL_BR_VALIDATED False")
    print("ALLOWED_BENCHMARKS False")
    print("N_YUKAWA_SOLUTIONS",len(rows))
    print("Wrote",csvfile)


if __name__=="__main__":
    main()

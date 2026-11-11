#!/usr/bin/env python3
"""13 TeV source Zee H1/H2 matched tb-associated production in HiggsTools.

The published HiggsTools effective-coupling parametrization returns an
interpolated 4FS/5FS matched 13 TeV charged Higgs cross section, not an LO
MadGraph result; its range 145--2000 GeV is enforced explicitly.

The Zee doublet fractions in the charged mass eigenstates follow native
ZP rows: H1=(-s_beta*c_gamma,c_beta*c_gamma,s_gamma),
H2=(s_beta*s_gamma,-c_beta*s_gamma,c_gamma). Thus Type-II charged
quark Yukawas are the doublet fractions c_gamma and -s_gamma times
(cot(beta),tan(beta)); source F/D lepton couplings do not enter tbH.

Use D4 genuine on-shell two-body widths with the exotic H2->H1Z
included in its denominator. This remains a *scoped observed-limit
diagnostic*, not globally accepted parameter space, until width/shape,
production uncertainties and additional signals are validated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from module14.scan import digest
from module14.decays import DecayCalculation
from module2.interface import evaluate as neutrino_evaluate
from module7.d4_inputs import rotations
from research.full_constraints.pheno_paper_2026.H2_charged_higgsbounds_probe import TOOL_DECAYS
from research.full_constraints.pheno_paper_2026.paper_gate import load_sources


def normalized_tb_couplings(p,k):
    if k not in (1,2): raise ValueError("Only Zee H1/H2 supported")
    beta=float(p["beta"]);g=float(p["gamma"])
    tanbeta=math.tan(beta)
    if not math.isfinite(tanbeta) or tanbeta<=0:
        raise ValueError("Invalid charged quark Type-II tanbeta")
    doublet=math.cos(g) if k==1 else -math.sin(g)
    zp=rotations(p)[0][k]
    expected=[-math.sin(beta)*doublet,math.cos(beta)*doublet]
    if any(not math.isclose(float(a),b,rel_tol=1e-12,abs_tol=1e-13)
           for a,b in zip(zp[:2],expected)):
        raise ArithmeticError("Native physical charged ZP row inconsistency")
    if not math.isclose(sum(float(x)**2 for x in zp),1.,rel_tol=1e-12):
        raise ArithmeticError("Charged mixing rotation not orthonormal")
    return {"kappa_t":doublet/tanbeta,"kappa_b":doublet*tanbeta,
            "doublet_amplitude":doublet}


def physical_two_body(h,require_h2=False):
    total=h["total"]
    if total.get("status")!="D4_COMPLETE_TWO_BODY_BR_PASS":
        raise ValueError("Native D4 on-shell two-body decay inventory invalid")
    width=float(total["total_width_GeV"])
    if not math.isfinite(width) or width<=0:
        raise ValueError("Invalid charged total two-body width")
    channels={x["channel"]:float(x["width_GeV"]) for x in h["channels"]}
    if len(channels)!=len(h["channels"]) or any(not math.isfinite(v) or v<0 for v in channels.values()):
        raise ValueError("Repeated or unphysical charged decay channel")
    if not math.isclose(math.fsum(channels.values()),width,rel_tol=1e-9):
        raise ValueError("Two-body decay sum mismatch")
    br={}
    for enum,source in TOOL_DECAYS:
        if source not in channels:
            raise KeyError("Missing D4 charged observed-search channel "+source)
        br[enum]=channels[source]/width
    cascade=channels.get("H1 Z") if require_h2 else None
    if require_h2 and cascade is None:
        raise ValueError("Heavy Zee H2 must include its H1Z channel")
    if math.fsum(br.values())>1+1e-10:
        raise ValueError("SM charged BR exceeds physically computed width")
    return {"total_width_D4_GeV":width,"SM_final_state_BRs":br,
            "BR_H1Z":cascade/width if cascade is not None else None,
            "n_known_D4_channels":len(channels),
            "missing_offshell_and_loops":True}


def matched_13tb(p,k,HP):
    coeff=normalized_tb_couplings(p,k)
    mass=float(p[f"mH{k}"])
    if not 145.0<=mass<=2000.0:
        return None,coeff,"MISSING_PRODUCTION_OUTSIDE_PUBLIC_TABLE_RANGE"
    rate=float(HP.EffectiveCouplingCxns.ppHpmtb(
        HP.Collider.LHC13,mass,coeff["kappa_t"],coeff["kappa_b"],0.0))
    if not math.isfinite(rate) or rate<=0:
        raise ValueError("Published charged-Higgs 4FS/5FS matched rate invalid")
    return rate,coeff,"PUBLIC_4FS_5FS_MATCHED_INTERPOLATION_13TEV"


def applied_value(value):
    x=value.limit()
    return {"analysis_id":int(x.id()),"process":str(x),
            "reference":str(x.reference()),
            "observed_ratio":float(value.obsRatio()),"expected_ratio":float(value.expRatio()),
            "contributing_particles":[str(z) for z in value.contributingParticles()]}


def run(source:Path,dataset:Path,output:Path):
    if output.exists():raise FileExistsError("Do not overwrite 64-card observed-search evidence")
    if not dataset.is_dir():raise FileNotFoundError("Pinned HiggsBounds observed dataset missing")
    import Higgs.predictions as HP
    import Higgs.bounds as HB
    data=json.loads(source.read_text())
    if (data.get("new_neutrino_family_count")!=64 or len(data.get("families",[]))!=64
        or data.get("global_acceptance") is not None):
        raise ValueError("Expected original exactly 64 constructed neutrino family cards")
    _,original,rates,_,_,_,_,_=load_sources()
    byid={s["scalar_id"]:s for s in data["scalars"]}
    if set(byid)!=set(original):
        raise ValueError("16 scalar source identity mismatch")
    hb=HB.Bounds(str(dataset),HB.LimitOptions(minExpRatio=0.))
    cases=[]
    for f in data["families"]:
        sid=int(f["id"])
        if f["scalar_sha256"]!=original[sid]["scalar_sha256"]:
            raise ValueError("Family and original scalar identity not matched")
        scalar=byid[sid]["scalar_input"]
        if digest(scalar)!=f["scalar_sha256"]:
            raise ValueError("Original scalar input has been modified")
        p=scalar["physical"]
        n=neutrino_evaluate(f["algebraic_texture_input"])
        if n["inverse"]["family_relative_residual"]>=2e-9:
            raise ValueError("Exact source neutrino target does not close")
        fields={key:n[key] for key in ("F","D","Ye","Ye2","Mnu")}
        fields.update(input=f["algebraic_texture_input"],input_sha256=f["algebraic_texture_input_sha256"])
        widths=DecayCalculation(scalar,fields).evaluate(fields)
        if widths.get("status")!="PASS" or widths["scalar_sha256"]!=f["scalar_sha256"]:
            raise ValueError("Charged scalar source D4 width evaluation invalid")
        pred=HP.Predictions()
        charged={}
        for k in (1,2):
            w=physical_two_body(widths["mothers"][f"H{k}"],require_h2=(k==2))
            if k==2 and not math.isclose(w["BR_H1Z"],f["D4_BR_H2_H1Z"],rel_tol=2e-8,abs_tol=1e-12):
                raise ValueError("H2 exotic cascade width mismatches native family source")
            rate,c,status=matched_13tb(p,k,HP)
            particle=pred.addParticle(HP.ChargedScalar(f"H{k}"))
            particle.setMass(float(p[f"mH{k}"]))
            particle.setTotalWidth(w["total_width_D4_GeV"])
            if rate is not None:particle.setCxn(HP.Collider.LHC13,HP.Production.Hpmtb,rate)
            for decay,br in w["SM_final_state_BRs"].items():
                particle.setBr(getattr(HP.Decay,decay),br)
            charged[f"H{k}"]={"mass_GeV":float(p[f"mH{k}"]),
                  "width_D4_GeV":w["total_width_D4_GeV"],
                  "width_over_mass":w["total_width_D4_GeV"]/float(p[f"mH{k}"]),
                  "matched_rate_13TeV_pb":rate,"rate_status":status,
                  "quark_primitive_couplings":c,"D4":w}
        source_lo=float(rates[(sid,13)]["sigma_pb"])
        if source_lo<=0:raise ValueError("Source matched H2 MadGraph LO rate missing")
        public=charged["H2"]["matched_rate_13TeV_pb"]
        compare=public/source_lo if public is not None else None
        obs=hb(pred)
        applied=[applied_value(z) for z in obs.appliedLimits]
        selected={str(k):applied_value(z) for k,z in obs.selectedLimits.items()}
        cases.append({
            "scalar_id":sid,"ordering":f["ordering"],"seed":f["seed"],
            "scalar_sha256":f["scalar_sha256"],"charged":charged,
            "H2_public_matched_to_original_MG5_LO_ratio_DIAGNOSTIC":compare,
            "original_13TeV_MG5_H2_LO_pb":source_lo,
            "selected_limits":selected,"applied_limits":applied,
            "scoped_13TeV_public_model_excluded":bool(applied and not obs.allowed),
            "full_Zee_Higgs_exclusion":None,"global_acceptance":None,
            "missing":["8 TeV charged production","signal finite-width and interference",
                        "QCD/PDF/scale uncertainty and shape transfer",
                        "all neutral states and non-tb production",
                        "H2->H1Z dedicated experimental search topology"]
        })
        if sid in (15673,15591,2264) and f["ordering"]=="NO" and f["seed"]==20261111:
            print("ZEE_CHARGED_PUBLIC_BOTH",sid,
                  "H1_RATE_pb",charged["H1"]["matched_rate_13TeV_pb"],
                  "H2_RATE_pb",charged["H2"]["matched_rate_13TeV_pb"],
                  "H2_PUBLIC_OVER_MG5LO",compare,
                  "HB_SELECTED_OBS",[(x["analysis_id"],x["observed_ratio"]) for x in selected.values()],
                  "SCOPED_EXCLUDED",bool(applied and not obs.allowed),"GLOBAL_UNKNOWN",flush=True)
    if len(cases)!=64 or len({(c["scalar_id"],c["ordering"],c["seed"]) for c in cases})!=64:
        raise ValueError("Incomplete 64 family search sample")
    report={
        "schema":"zee-64-families-H1-H2-13TeV-published-matched-tb-production-higgsbounds-v1",
        "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_spectra":16,"source_families":64,
        "production_version":"HiggsTools 1.1.3 effective coupling matched 4FS/5FS tbH",
        "public_table_domain_GeV":[145.,2000.],
        "all_scalar_rates_physical_global_status":"UNKNOWN",
        "n_scoped_13TeV_excluded":sum(x["scoped_13TeV_public_model_excluded"] for x in cases),
        "n_missing_H1_public_tb":sum(x["charged"]["H1"]["matched_rate_13TeV_pb"] is None for x in cases),
        "n_missing_H2_public_tb":sum(x["charged"]["H2"]["matched_rate_13TeV_pb"] is None for x in cases),
        "global_acceptance":None,"cases":cases}
    output.write_text(json.dumps(report,allow_nan=False,indent=2,sort_keys=True)+"\n")
    print("ZEE_BOTH_CHARGED_PUBLIC_TB_64_DONE",len(cases),"SELECTED_EXCLUDED",report["n_scoped_13TeV_excluded"],
          "FULL_MODEL_UNKNOWN",flush=True)
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--dataset",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    run(a.source,a.dataset,a.output)

if __name__=="__main__":
    main()

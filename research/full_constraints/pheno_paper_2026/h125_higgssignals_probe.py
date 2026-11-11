#!/usr/bin/env python3
"""HiggsSignals h125-only effective-coupling consistency probe for Zee families.

This is explicitly a *restricted h125 single-resonance* HiggsSignals check,
NOT a physical all-Higgs-sector scan verdict, because additional H/A charged
states are excluded from this HiggsSignals prediction and HiggsBounds searches
are not evaluated. The supplied h125 loop gg/gammagamma couplings are explicit.

The matched h125 64-family input is SHA-provenanced from the validated
native source-output pipeline; no incomplete h125 known-channel width is ever
fed to the experimental precision likelihood.
"""
import argparse, hashlib, json, math
from pathlib import Path

def add_native_zee_h125_lfv(h_particle, h_source):
    """Add the source-computed on-shell h->different-flavor leptons once.

    HiggsPredictions' effective-coupling reference only knows flavor-diagonal
    lepton modes. setDecayWidth adds each LFV mode to the reference-derived
    denominator and correspondingly renormalizes all existing BRs. The result
    remains an effective-coupling approximation, NOT a certified full Zee width.
    """
    widths=h_source["known_partial_widths_GeV"]
    baseline=float(h_particle.totalWidth())
    if not math.isfinite(baseline) or baseline<=0:
        raise ValueError("HiggsTools h125 reference total width invalid")
    added={}
    for mode,source_key in (("emu","ll_e_mu"),("etau","ll_e_tau"),("mutau","ll_mu_tau")):
        val=float(widths[source_key])
        if not math.isfinite(val) or val<0:
            raise ValueError("Unphysical native Zee h125 LFV partial width")
        # Each native off-diagonal source width already sums charge conjugates.
        # Do not multiply by two a second time.
        h_particle.setDecayWidth(mode,val)
        added[mode]=val
    actual=float(h_particle.totalWidth())
    expected=math.fsum((baseline,*added.values()))
    if not math.isclose(actual,expected,rel_tol=5e-10,abs_tol=1e-13):
        raise ArithmeticError("LFV width double counting or reference normalization drift")
    return {"reference_before_LFV_width_GeV":baseline,
            "native_LFV_partial_widths_GeV":added,
            "effective_after_LFV_width_GeV":actual,
            "width_is_full_physical_Zee":False}


def run(source:Path, dataset:Path, output:Path):
    if output.exists():raise FileExistsError("No overwriting evidence")
    if not dataset.is_dir():raise FileNotFoundError("HiggsSignals dataset not installed")
    import Higgs.predictions as HP
    import Higgs.signals as HS
    d=json.loads(source.read_text())
    if d.get("n_evaluated")!=64 or d.get("global_acceptance") is not None:
        raise RuntimeError("Incomplete or improperly accepted 64 family input")
    allrows=d["families"]
    sm_ledger=json.loads((Path(__file__).resolve().parents[3]/
        "research/full_constraints/higgs/H125_SIGNAL_STRENGTH_EVIDENCE.json").read_text()
        )["matched_SM_ledger_GeV"]
    # Demand two datasets of identically configured genuine HiggsSignals
    # measurements. Never infer 95% CL from a raw delta chi2 without NDF.
    hs=HS.Signals(str(dataset))
    smp=HP.Predictions()
    smh=smp.addParticle(HP.BsmParticle("h","neutral","even"))
    smh.setMass(125.0)
    HP.effectiveCouplingInput(smh,HP.smLikeEffCouplings)
    smres=hs(smp)
    if not math.isfinite(float(smres)):
        raise RuntimeError("SM HiggsSignals chi2 not finite")
    cases=[]
    for row in allrows:
        h=row["h125"]
        if h["full_model_total_width_GeV"] is not None:
            raise RuntimeError("A known-channel sum was promoted to total width")
        # Native HiggsPredictions effective-coupling API provides the
        # *reference-model inferred* h125 width, avoiding the Input parser's
        # mandatory w_h requirement. This is a declared effective-coupling
        # approximation, NOT our unknown full physical Zee width.
        pred=HP.Predictions()
        hp=pred.addParticle(HP.BsmParticle("h","neutral","even"))
        hp.setMass(125.0)
        k=HP.NeutralEffectiveCouplings()
        ku=float(h["kappa_top"])
        kd=float(h["kappa_bottom"])
        kv=float(h["kappaV"])
        for name in ("uu","cc","tt"):
            setattr(k,name,complex(ku,0.0))
        for name in ("dd","ss","bb"):
            setattr(k,name,complex(kd,0.0))
        k.WW=kv
        k.ZZ=kv
        def width_ratio(channel):
            model=float(h["known_partial_widths_GeV"][channel])
            sm=float(sm_ledger[channel])
            if not (math.isfinite(model) and model>=0 and math.isfinite(sm) and sm>0):
                raise ValueError("Invalid source partial-width ratio: "+channel)
            return math.sqrt(model/sm)
        gg_ratio=float(h["matched_independent_quark_lo_gg_ratio"])
        if not math.isfinite(gg_ratio) or gg_ratio<0:
            raise ValueError("Invalid source coherent gg-production ratio")
        k.gg=math.sqrt(gg_ratio)
        k.gamgam=width_ratio("gammagamma")
        k.Zgam=width_ratio("Zgamma")
        # The general Zee lepton Yukawa sector is not Type-II NFC.
        # Retain both signed scalar and pseudoscalar components explicitly.
        for name,flavor in (("ee","e"),("mumu","mu"),("tautau","tau")):
            d=h["Zee_lepton_diagonal_kappas_complex"][flavor]
            sc=float(d["scalar"])
            ps=float(d["pseudoscalar"])
            if not math.isfinite(sc) or not math.isfinite(ps):
                raise ValueError("Nonfinite Zee lepton effective coupling")
            setattr(k,name,complex(sc,ps))
        # The native Zee photon and gg amplitude ratios include physics
        # absent from the generic 2HDM formulas. Never recalculate/override
        # them from quark/W loops, and never insert the partial-width sum.
        HP.effectiveCouplingInput(
            hp,k,calcggH=False,calcHgamgam=False)
        width_record=add_native_zee_h125_lfv(hp,h)
        x=float(hs(pred))
        if not math.isfinite(x):
            raise ValueError("Nonfinite h125-only HiggsSignals prediction")
        cases.append({
            "scalar_id":row["scalar_id"],"ordering":row["ordering"],"seed":row["seed"],
            "chi2_h125_restricted":x,"chi2_SM_same_dataset":float(smres),
            "delta_chi2_h125_restricted":x-float(smres),
            "has_model_diagonal_lepton_effcoupling":True,
            "h125_width_prescription":"SM_reference_effective_coupling_plus_exact_native_LFV_NOT_complete_Zee",
            "h125_effective_width_record":width_record,
            "includes_h125_offdiagonal_LFV_decays":True,
            "includes_all_H_A_other_states":False,
            "has_declared_NDF_or_chi2_threshold":False,
            "full_Higgs_acceptance":None,"global_acceptance":None,
        })
        print("H125_HS_ONLY",row["scalar_id"],row["ordering"],row["seed"],
              "DELTACHI2",x-float(smres),"FULL_HIGGS_UNKNOWN",flush=True)
    result={"schema":"zee-2026-h125-only-higgssignals-test-not-a-full-Higgs-exclusion",
        "HiggsTools_dataset":str(dataset),"HiggsTools_package":"source-pinned-v1.1.3",
        "source_64_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "n_h125_cases":len(cases),"chi2_SM":float(smres),
        "diagonal_zee_lepton_yukawa_inputs_incomplete":False,
        "heavy_H_A_and_charged_excluded_from_input":True,
        "h125_width_prescription":"SM_reference_effective_coupling_plus_exact_native_LFV_NOT_complete_Zee",
        "physical_Higgs":"UNKNOWN","global_acceptance":None,"cases":cases}
    output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True,type=Path)
    a.add_argument("--dataset",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    run(args.source,args.dataset,args.output)

if __name__=="__main__":main()

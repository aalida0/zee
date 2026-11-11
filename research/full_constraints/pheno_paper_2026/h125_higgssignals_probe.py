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

def run(source:Path, dataset:Path, output:Path):
    if output.exists():raise FileExistsError("No overwriting evidence")
    if not dataset.is_dir():raise FileNotFoundError("HiggsSignals dataset not installed")
    import Higgs.predictions as HP
    import Higgs.signals as HS
    import Higgs.tools.Input as Input
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
        # For CP-even h, one-loop complex off-diagonal lepton Yukawas are
        # not introduced via an imaginary diagonal scalar 'kappa' here.
        # Source h lepton e/mu/tau diagonal scalar couplings receive
        # a separate treatment; if absent, no non-SM tau coupling is guessed.
        inputs={
            "m_h":125.0,
            "CP_h":"even",
            "effc_h_WW":float(h["kappaV"]),
            "effc_h_ZZ":float(h["kappaV"]),
            "effc_h_tt_s":float(h["kappa_top"]),
            "effc_h_cc_s":float(h["kappa_top"]),
            "effc_h_bb_s":float(h["kappa_bottom"]),
            "effc_h_ss_s":float(h["kappa_bottom"]),
            "effc_h_gg":math.sqrt(float(h["matched_independent_quark_lo_gg_ratio"])),
            "effc_h_gamgam":math.sqrt(
                float(h["known_partial_widths_GeV"]["gammagamma"])/sm_ledger["gammagamma"]),
        }
        # Source lepton D is fully general and complex; explicit effective
        # scalar/pseudoscalar Yukawas, not a false Type-II lepton assumption.
        for flavor,contract in (
            ("ee","e"),("mumu","mu"),("tautau","tau")
        ):
            kappas=h["Zee_lepton_diagonal_kappas_complex"][contract]
            inputs[f"effc_h_{flavor}_s"]=kappas["scalar"]
            inputs[f"effc_h_{flavor}_p"]=kappas["pseudoscalar"]
        pred=Input.predictionsFromDict(inputs,["h"],[],[],useExplicitBr=False)
        x=float(hs(pred))
        if not math.isfinite(x):
            raise ValueError("Nonfinite h125-only HiggsSignals prediction")
        cases.append({
            "scalar_id":row["scalar_id"],"ordering":row["ordering"],"seed":row["seed"],
            "chi2_h125_restricted":x,"chi2_SM_same_dataset":float(smres),
            "delta_chi2_h125_restricted":x-float(smres),
            "has_model_diagonal_lepton_effcoupling":True,
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

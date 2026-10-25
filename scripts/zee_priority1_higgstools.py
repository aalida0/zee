#!/usr/bin/env python3
"""Minimal real HiggsTools API adapter, only with complete rate exports.

Invokes Higgs.tools.Input.predictionsFromDict(), Higgs.bounds.Bounds() and
Higgs.signals.Signals() on a five-particle Zee prediction. This module
does NOT invent decay channels, width remainders, SM approximations,
cross sections, CP or interference assumptions. Fails closed on input
or API mismatch. No claim about full model acceptance is returned.
"""
from __future__ import annotations
import math
from zee_priority1_contracts import (
 IDS, validate_decays,validate_production,numeric)

NEUTRAL=("h","H","A")
CHARGED=("H1","H2")

def predictions_dict(spectrum,decays,production):
    if validate_decays(decays,spectrum)!="EVALUATED_FIVE_STATE_DECAY_INPUT":
        raise ValueError("Incomplete Zee 5-state decay model")
    if validate_production(production,spectrum)!="EVALUATED_FIVE_STATE_PRODUCTION_INPUT":
        raise ValueError("Incomplete Zee hadronic production model")
    if (decays.get("higgstools_decay_mode_mapping_validated") is not True
        or production.get("higgstools_production_mode_mapping_validated") is not True):
        raise ValueError("Cannot translate unchecked Zee modes to HiggsTools")
    data={"CP_h":"even","CP_H":"even","CP_A":"odd"}
    for pid in IDS:
        row=decays["particles"][pid]
        total=numeric(row["total_width_GeV"],"width",positive=True)
        data["m_"+pid]=numeric(row["mass_GeV"],pid+" mass",positive=True)
        data["w_"+pid]=total
        for mode,partial in row["partial_widths_GeV"].items():
            if not isinstance(mode,str) or not mode:
                raise ValueError("Invalid HiggsTools decay-mode name")
            data[f"br_{pid}_{mode}"]=numeric(partial,mode,nonnegative=True)/total
        for mode,entry in production["particles"][pid].items():
            coll=entry["collider"]
            data[f"cxn_{pid}_{mode}_{coll}"]=numeric(
                entry["sigma_pb"],pid+" "+mode,nonnegative=True)
    return data

def run(spectrum,decays,production,hb_data,hs_data,
        *,conversion=None,bounds_constructor=None,signals_constructor=None):
    """Initialize datasets once via callers if running many points."""
    if conversion is None or bounds_constructor is None or signals_constructor is None:
        try:
            import Higgs.tools.Input as hinput
            import Higgs.bounds as HB
            import Higgs.signals as HS
        except ImportError as exc:
            raise RuntimeError("HiggsTools Python bindings not installed") from exc
        conversion=conversion or hinput.predictionsFromDict
        bounds_constructor=bounds_constructor or HB.Bounds
        signals_constructor=signals_constructor or HS.Signals
    if not hb_data or not hs_data:
        raise ValueError("Both official HiggsTools datasets required")
    data=predictions_dict(spectrum,decays,production)
    try:
        pred=conversion(data,neutralIds=list(NEUTRAL),
                        singleChargedIds=list(CHARGED),
                        doubleChargedIds=[],useExplicitBr=True)
        bounds=(hb_data if callable(hb_data) else bounds_constructor(str(hb_data)))
        signals=(hs_data if callable(hs_data) else signals_constructor(str(hs_data)))
        result=bounds(pred)
        chi2=numeric(signals(pred),"HiggsSignals chi2",nonnegative=True)
    except Exception as exc:
        raise RuntimeError("HiggsTools full-five-state API evaluation failed") from exc
    return {
        "status":"FIVE_STATE_HIGGSTOOLS_API_EVALUATED_INPUT_CONDITIONAL",
        "HiggsSignals_chi2":chi2,
        "HiggsBounds_result_repr":str(result),
        "all_physical_model_constraints_tested":False,
        "source_inputs_validated_by_API_not_independent_physics":True,
        "full_Zee_allowed_or_excluded":None,
    }

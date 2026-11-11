#!/usr/bin/env python3
"""Create paper-reviewable collider/constraint tables from *existing actual* data.

No external dependencies. Does not generate invented confidence intervals,
recast detector efficiencies, or extrapolate 13->14 TeV production.

Sources (all from this repository's original frozen research branch):
- D14D MG5 actual 13 TeV for 16 scalars, actual 14 TeV for 3
- D14 original scalar and neutrino-family source bindings
- Misiak 2026 one/two sided scalar leading-NP B gate and independent
  SuperIso/HEPfit/flavio stress diagnostics, uncalibrated
- H125/LFV all-64 summary gated on named source approximations
Optional --fresh-json: newly constructed 64 one-loop-neutrino families,
needed for *new flavor* cascade branching products; without it all
physical-rate products are clearly labelled historical families.

NEVER classifies globally allowed models, h125/heavy Higgs physical passes,
complete LFV passes or LHC discovery/exclusion reach.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SOURCE_PRODUCTION=ROOT/"module14/conditional_scan/production_map_13_14.json"
SOURCE_ORIGINAL=ROOT/"module14/conditional_scan/candidate_followup.json"
SOURCE_B=ROOT/"research/full_constraints/bsgamma_nnlo_hepfit_2026/16_scalar_adversarial_three_method_B_stress.json"
SOURCE_B_NNLO=ROOT/"research/full_constraints/bsgamma_nnlo_hepfit_2026/16_scalar_three_loop_source_matched_evidence.json"
SOURCE_HL=ROOT/"research/full_constraints/higgs_lfv_2026/HIGGS_LFV_64_SCOPE_GATE_2026-11-11.json"
SOURCE_APPROX=Path(__file__).with_name("APPROXIMATIONS_REVIEW_REGISTRY.json")
SCALAR_COUNT=16
ORIGINAL_FAMILY_PER_SCALAR=4
LUMI_PAPER_FB=3000.0
TARGET_SELECTED=(10.0,100.0)


def read(path):
    return json.loads(Path(path).read_text())


def finite_positive(x, field):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0:
        raise ValueError(f"{field}: expected positive finite source number")
    return float(x)


def band(vals):
    if not vals: return None
    return [min(vals),max(vals)]


def safe_yield(rate_fb,luminosity_fb=LUMI_PAPER_FB):
    if rate_fb is None:return None
    return rate_fb*luminosity_fb


def required_efficiency_for_n(rate_fb,n):
    count=safe_yield(rate_fb)
    if count is None or count<=0:return None
    return n/count


def load_sources():
    prod=read(SOURCE_PRODUCTION)
    orig=read(SOURCE_ORIGINAL)
    b=read(SOURCE_B)
    bn=read(SOURCE_B_NNLO)
    hl=read(SOURCE_HL)
    reg=read(SOURCE_APPROX)
    if (prod["production_13TeV_gate"]!="PRODUCTION_MAP_13TEV_COMPLETE"
        or prod["production_14TeV_gate"]!="PRODUCTION_14TEV_PILOT_COMPLETE"):
        raise ValueError("Original actual 13/14 TeV MG5 source no longer validated")
    if prod["global_acceptance"] is not None:raise ValueError("Original collider source improperly promoted")
    origrows=orig["tables"]["CERTIFIED_VACUUM_APPROX_BSG_16"]
    if len(origrows)!=SCALAR_COUNT:raise ValueError("Unexpected source scalar count")
    ids={p["id"]:p for p in origrows}
    if len(ids)!=SCALAR_COUNT:raise ValueError("Duplicate original scalar identity")
    rates={}
    for item in prod["rates"]:
        ident=(item["id"],item["energy_TeV"])
        if ident in rates:raise ValueError("Duplicate actual generator rate")
        if item["status"] not in ("D14C_NATIVE_RUN_PASS","D14D_NATIVE_RUN_PASS"):
            raise ValueError("Generator did not pass source receipt")
        if item["order"]!="LO_QCD":
            raise ValueError("Generator accuracy changed")
        finite_positive(item["sigma_pb"],"sigma_pb")
        finite_positive(item["integration_error_pb"],"MC integration error")
        if item.get("theory_sigma_pb") is not None:
            raise ValueError("Source unexpectedly provides production theory uncertainty")
        rates[ident]=item
    expected={(i,13) for i in ids}|{(i,14) for i in (15591,2264,15673)}
    if set(rates)!=expected:
        raise ValueError(f"Energy coverage changed: missing {expected-set(rates)}, extra {set(rates)-expected}")
    families={}
    for f in prod["families"]:
        key=(f["id"],f["energy_TeV"],f["ordering"],f["family"])
        if key in families:raise ValueError("Duplicate source original family")
        if f["closure_status"]!="PASS" or f["width_status"]!="PASS":
            raise ValueError("Original production-family neutrino/width gate changed")
        if f["global_acceptance"] is not None:raise ValueError("Unjustified global acceptance")
        families[key]=f
    if len(families)!=(SCALAR_COUNT+3)*ORIGINAL_FAMILY_PER_SCALAR:
        raise ValueError("Unexpected 16x4 + 3x4 historical MG5 family count")
    bmap={x["id"]:x for x in b["entries"]}
    nnmap={x["id"]:x for x in bn["cases"]}
    if set(ids)!=set(bmap) or set(ids)!=set(nnmap):
        raise ValueError("B matching must cover the same sixteen source scalar identities")
    if (b["one_sided_95_stress_surviving"]!=3
       or bn["one_sided_95_LO_NP_n"]!=10
       or bn["two_sided_95_LO_NP_n"]!=16):
        raise ValueError("Published B screens changed; update the scientific review")
    for ident,row in ids.items():
        if row["scalar_sha256"] not in (
            bmap[ident]["original_scalar_sha256"],
            nnmap[ident]["scalar_sha256"],
        ):
            raise ValueError("Source scalar SHA mismatch")
        if any(v["assessment"]!="PASS" for v in row["gates"].values()):
            raise ValueError("Original 16 scalar theory/EWPO/vacuum certificate invalid")
        if row["global_acceptance"] is not None:
            raise ValueError("Original source global acceptance promoted")
    if (hl["number_new_constructed_neutrino_families"]!=64
        or hl["one_loop_radiative_MEGII_below_90CL_count"]!=64
        or hl["uncertified_full_constraints"]["globally_allowed_model_points"] is not None):
        raise ValueError("New-flavor source Higgs/LFV scoped gate changed")
    if len(reg["entries"])<15: raise ValueError("Missing approximation audit")
    return prod,ids,rates,families,bmap,nnmap,hl,reg


def verify_new_family(fresh,origids):
    if fresh is None:return None
    if fresh["new_neutrino_family_count"]!=64 or len(fresh["families"])!=64:
        raise ValueError("Not a 64-family original rebuilt neutrino source")
    if set(fresh["source_16_certified_original_scalar_IDs"])!=set(origids):
        raise ValueError("New and original scalar sets differ")
    got={}
    for family in fresh["families"]:
        i=family["id"]
        if family["scalar_sha256"]!=origids[i]["scalar_sha256"]:
            raise ValueError("Fresh neutrino source card scalar SHA mismatch")
        key=(i,family["ordering"],family["seed"])
        if key in got:raise ValueError("Duplicate new neutrino card")
        if family["perturbativity_status"]!="NEUTRINO_PERTURBATIVE":
            raise ValueError("New family perturbativity now fails")
        if family["neutrino_closure"]>=2e-9:
            raise ValueError("New family neutrino target now fails")
        if family["physical_LFV"]!="UNKNOWN" or family["global_acceptance"] is not None:
            raise ValueError("Physical new LFV improperly accepted")
        for k in ("D4_cascade_product","D4_BR_H2_H1Z","D4_BR_H1_tb"):
            y=family[k]
            if y is None or not 0.0<=y<=1.0:
                raise ValueError("Missing/out-of-range new D4 tree branching fraction")
        if not math.isclose(family["D4_cascade_product"],
                            family["D4_BR_H2_H1Z"]*family["D4_BR_H1_tb"],
                            rel_tol=1e-10,abs_tol=1e-14):
            raise ValueError("New cascade product inconsistent with native two-body widths")
        got[key]=family
    if len(got)!=64:raise ValueError("Incomplete new family input coverage")
    return got


def build(fresh=None):
    prod, orig, rates, fams, bgate, bn, hl, reg=load_sources()
    latest=verify_new_family(fresh,orig)
    rows=[]
    for ident,p in sorted(orig.items()):
        old=[fams[(ident,13,ordering,family)] for ordering in ("NO","IO")
             for family in (0,1)]
        on14=[fams[(ident,14,ordering,family)] for ordering in ("NO","IO")
              for family in (0,1)] if (ident,14) in rates else []
        for a,b in zip(old,on14):
            if (a["scalar_sha256"]!=b["scalar_sha256"]
                or a["ordering"]!=b["ordering"] or a["family"]!=b["family"]):
                raise ValueError("13/14 TeV underlying scalar/family card mismatch")
            if not math.isclose(a["BR_H2_H1Z"],b["BR_H2_H1Z"],rel_tol=1e-13):
                raise ValueError("Production energy spuriously changed same-input BR")
        sigma13=1000.0*rates[(ident,13)]["sigma_pb"]
        sigma14=1000.0*rates[(ident,14)]["sigma_pb"] if (ident,14) in rates else None
        original_h2=[f["BR_H2_H1Z"] for f in old]
        original_tb=[f["BR_H2_H1Z"]*f["H1_decay_BR_separate"]["t anti-b"] for f in old]
        if latest is not None:
            new=[f for (i,_,_),f in latest.items() if i==ident]
            if len(new)!=4:raise ValueError("Missing new neutrino family")
            h2=[f["D4_BR_H2_H1Z"] for f in new]
            cascade=[f["D4_cascade_product"] for f in new]
            selection="new_64_constructed_neutrino_families"
            max_retained=max(f["partial_mu_to_e_gamma_BR"] for f in new)
            if not max_retained<1.5e-13:raise ValueError("A newly reconstructed partial LFV screen failed")
        else:
            h2=original_h2
            cascade=original_tb
            selection="original_D14D_four_neutrino_families__new_64_not_merged"
            max_retained=None
        for v in h2+cascade:
            if not 0.0<=v<=1.0:raise ValueError("BR outside probability range")
        if not h2 or not cascade: raise ValueError("No source charged Higgs BR")
        b=bgate[ident];n=bn[ident]
        if b["LO2026_B_rate"]!=n["LO_NP_Misiak2026_rate"]:
            raise ValueError("Two independent source B rates disagree")
        psrc=p["input_card"]["physical"]
        row={
            "scalar_id":ident,
            "scalar_sha256":p["scalar_sha256"],
            "mH1_GeV":psrc["mH1"],
            "mH2_GeV":psrc["mH2"],
            "tanbeta":math.tan(psrc["beta"]),
            "gamma_rad":psrc["gamma"],
            "original_scalar_reconstruction_bfb_unitarity_ewpo_vacuum":"PASS_original_theory_scope",
            "nu_family_basis":selection,
            "nu_64_families_partial_mu_e_gamma_max_BR":max_retained,
            "BR_H2_to_H1_Z_range":band(h2),
            "BR_H2_H1Z_H1_tb_product_range":band(cascade),
            "B_2026_Misiak_Eq4_BR":b["LO2026_B_rate"],
            "B_one_sided_Gaussian_LO_NP_screen":n["one_sided_95_LO_NP_screen"],
            "B_two_sided_Gaussian_LO_NP_screen":n["two_sided_95_LO_NP_screen"],
            "B_one_sided_nonprobabilistic_stress_survival":b["one_sided_stress_survival"],
            "B_method_stress_is_not_theory_sigma":True,
            "B_physical_NNLO_exclusion":None,
            "sigma13_actual_LO_5FS_fb":sigma13,
            "sigma13_MC_integration_error_fb":1000.0*rates[(ident,13)]["integration_error_pb"],
            "sigma14_actual_LO_5FS_fb":sigma14,
            "sigma14_MC_integration_error_fb":1000.0*rates[(ident,14)]["integration_error_pb"] if sigma14 is not None else None,
            "sigma14_over_sigma13_ACTUAL_ONLY":sigma14/sigma13 if sigma14 is not None else None,
            "sigma13_H2_H1Z_tb_product_range_fb":band([sigma13*z for z in cascade]),
            "sigma14_H2_H1Z_tb_product_range_fb":band([sigma14*z for z in cascade]) if sigma14 is not None else None,
            "events13_3000fb_minus1_before_Z_top_decays_and_selection":band([safe_yield(sigma13*z) for z in cascade]),
            "events14_3000fb_minus1_before_Z_top_decays_and_selection":band([safe_yield(sigma14*z) for z in cascade]) if sigma14 is not None else None,
            "epsilon_for_10_selected_at_14TeV_using_min_rate":required_efficiency_for_n(sigma14*min(cascade),10.) if sigma14 is not None else None,
            "epsilon_for_100_selected_at_14TeV_using_min_rate":required_efficiency_for_n(sigma14*min(cascade),100.) if sigma14 is not None else None,
            "production_scale_uncertainty":None,
            "production_PDF_uncertainty":None,
            "total_h125_and_H_A_widths_physical":None,
            "full_mu_to_3e_and_conversion_new_family":None,
            "full_LFV_gauge_complete":None,
            "LHC_95CL_exclusion_or_discovery":None,
            "global_acceptance":None,
        }
        rows.append(row)
    assert len(rows)==16
    result={
        "schema":"zee-pheno-paper-source-replay-scoped-collider-constraints-v1",
        "source_production_gate_13TeV":prod["production_13TeV_gate"],
        "source_production_gate_14TeV":prod["production_14TeV_gate"],
        "n_original_certified_scalar_spectra":16,
        "n_actual_13TeV_scalar_production_rates":sum(r["sigma13_actual_LO_5FS_fb"] is not None for r in rows),
        "n_actual_14TeV_scalar_production_rates":sum(r["sigma14_actual_LO_5FS_fb"] is not None for r in rows),
        "n_B_one_sided_source_LO_NP_screen":sum(r["B_one_sided_Gaussian_LO_NP_screen"] for r in rows),
        "n_B_two_sided_source_LO_NP_screen":sum(r["B_two_sided_Gaussian_LO_NP_screen"] for r in rows),
        "n_B_one_sided_adversarial_stress_screen":sum(r["B_one_sided_nonprobabilistic_stress_survival"] for r in rows),
        "all_64_new_neutrino_families_screened_retained_LFV_in_separate_evidence":hl["one_loop_radiative_MEGII_below_90CL_count"],
        "fresh_64_source_cards_consumed_in_this_replay":latest is not None,
        "BR_input_family_scope":rows[0]["nu_family_basis"],
        "HL_luminosity_fb_minus1_assumed":LUMI_PAPER_FB,
        "HL_yields_are_14TeV_LO_only_without_Z_top_decay_efficiency_or_background":True,
        "is_unbiased_parameter_space_scan":False,
        "model_fully_allowed_count":None,
        "paper_claim":"Conditional leading-order collider and specified leading-NP screening results; not detector reach or global acceptance",
        "rows":rows,
    }
    if (result["n_actual_13TeV_scalar_production_rates"]!=16
        or result["n_actual_14TeV_scalar_production_rates"]!=3
        or result["n_B_one_sided_source_LO_NP_screen"]!=10
        or result["n_B_one_sided_adversarial_stress_screen"]!=3):
        raise ValueError("Regression on original source coverage or B screen")
    return result


def outputs(report,out:Path):
    if out.exists():raise FileExistsError("Refusing to overwrite a paper evidence directory")
    out.mkdir(parents=True)
    (out/"SOURCE_LOCKED_PAPER_GATE.json").write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    columns=[
        "scalar_id","mH1_GeV","mH2_GeV","tanbeta","gamma_rad",
        "B_one_sided_Gaussian_LO_NP_screen","B_two_sided_Gaussian_LO_NP_screen",
        "B_one_sided_nonprobabilistic_stress_survival",
        "sigma13_actual_LO_5FS_fb","sigma14_actual_LO_5FS_fb",
        "BR_H2_to_H1_Z_range","BR_H2_H1Z_H1_tb_product_range",
        "sigma13_H2_H1Z_tb_product_range_fb","sigma14_H2_H1Z_tb_product_range_fb",
        "events14_3000fb_minus1_before_Z_top_decays_and_selection",
        "epsilon_for_10_selected_at_14TeV_using_min_rate",
        "epsilon_for_100_selected_at_14TeV_using_min_rate",
        "nu_family_basis","global_acceptance"
    ]
    with (out/"PAPER_BENCHMARK_SUMMARY.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        writer.writeheader()
        for row in report["rows"]:
            t={key:(json.dumps(row[key]) if isinstance(row[key],list) else row[key]) for key in columns}
            writer.writerow(t)
    best=next(r for r in report["rows"] if r["scalar_id"]==15673)
    def v(x):
        return f"{x:.3f}" if isinstance(x,(int,float)) else str(x)
    lines=[
        "# Zee charged cascade: source-locked paper input and claim boundaries",
        "",
        "**All outputs are conditional at the explicitly stated order. Not globally allowed.**",
        "",
        f"- Actual MG5 LO 5FS 13 TeV scalar rates: **{report['n_actual_13TeV_scalar_production_rates']}/16**.",
        f"- Actual MG5 LO 5FS 14 TeV scalar rates: **{report['n_actual_14TeV_scalar_production_rates']}/16** (15591, 2264, 15673 only).",
        f"- Misiak 2026 leading-NP Gaussian screen: one-sided {report['n_B_one_sided_source_LO_NP_screen']}/16; two-sided {report['n_B_two_sided_source_LO_NP_screen']}/16; uncalibrated stress {report['n_B_one_sided_adversarial_stress_screen']}/16.",
        f"- Charged two-body BR basis: **{report['BR_input_family_scope']}**.",
        f"- 15673 actual LO 14 TeV H2 production: **{best['sigma14_actual_LO_5FS_fb']:.5f} fb**.",
        f"- 15673 raw tbZ cascade rate at 14 TeV: **{best['sigma14_H2_H1Z_tb_product_range_fb'][0]:.5f}–{best['sigma14_H2_H1Z_tb_product_range_fb'][1]:.5f} fb**.",
        f"- At 3000 fb^-1, before decays of Z/t and selections: **{best['events14_3000fb_minus1_before_Z_top_decays_and_selection'][0]:.0f}–{best['events14_3000fb_minus1_before_Z_top_decays_and_selection'][1]:.0f} raw events**.",
        "",
        "## Reviewer-critical restrictions",
        "",
        "1. These 16 are *preselected* certified scalar witnesses; the four historical or four reconstructed neutrino flavors per scalar are not unbiased model-space acceptance fractions.",
        "2. Do not claim 14 TeV rates for the other 13 spectra; no generic 13→14 interpolation was validated.",
        "3. 'Before decays and selections' is literal; do not present the above as an ATLAS event count or CLs reach.",
        "4. A two-sided or one-sided Gaussian B-screen is not the 2026 authors' full FC likelihood; stress survival is not a theory error bar.",
        "5. Total h125/H/A widths and model-appropriate HiggsTools exclusions remain unknown. Partial LFV dipoles do not substitute complete µ→3e/µ-e conversion.",
        "6. The novelty cannot be H2→H1Z (2021) or flavor-texture zeros (2023); show a substantive flavor-collider correlation beyond those results.",
        "7. All quoted cross-section uncertainties are **MC integration only**, not PDF/scale/theory. Avoid precision-comparison language.",
        "",
        "**Recommendation:** treat 15673 as *conditional benchmark*, not globally allowed. To submit a solid paper, finish a genuinely representative scan plus applied full leading Higgs/other LFV constraints or transparently narrow the title/claims.",
        ""
    ]
    (out/"PAPER_SCOPE_AND_REVIEWER_NOTES.md").write_text("\n".join(lines))
    return out


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output-dir",required=True,type=Path)
    a.add_argument("--fresh-json",type=Path)
    args=a.parse_args()
    result=build(read(args.fresh_json) if args.fresh_json else None)
    outputs(result,args.output_dir)
    print("PAPER_SOURCE_LOCKED_SCOPE_PASS",
          "13TeV",result["n_actual_13TeV_scalar_production_rates"],
          "14TeV",result["n_actual_14TeV_scalar_production_rates"],
          "B_ONE_SIDED",result["n_B_one_sided_source_LO_NP_screen"],
          "B_STRESS",result["n_B_one_sided_adversarial_stress_screen"],
          "FRESH",result["fresh_64_source_cards_consumed_in_this_replay"],
          "GLOBAL_ACCEPTANCE UNKNOWN",flush=True)
    for row in result["rows"]:
        if row["scalar_id"] in (15591,15673,2264,11016,14074):
            print("PAPER_RATE",row["scalar_id"],
                  "LO_13",row["sigma13_actual_LO_5FS_fb"],
                  "LO_14",row["sigma14_actual_LO_5FS_fb"],
                  "TBZ14",row["sigma14_H2_H1Z_tb_product_range_fb"],
                  "ONE_SIDED",row["B_one_sided_Gaussian_LO_NP_screen"],
                  "STRESS",row["B_one_sided_nonprobabilistic_stress_survival"],
                  flush=True)


if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Source-matched one-loop 64-family mu3e and mu-e(Au) *conditional* constraints.

Takes *actual* SARAH/SPheno FlavorKit results and a locally attested
rebuild of the original model with the two-line proton/neutron sign repair.
No dipole-dominance or partial mu3e substitution is permitted.

This classification is explicitly LO in the source's one-loop convention,
historical 2001 conversion nuclear inputs, no LEFT/QCD or higher-loop
materiality certification.  Never promote it to FULL_LFV_PASS.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from .spheno_64_source_gate import EXPECTED_SOURCES,PRIOR_COMPILED_EXE_SHA

PATCHED_OBSERVABLE_SHA="fd6e4ba58206e0f5d1be8f3993a469a018d0cd3a77160001000b73858f427293"
LIMITS_90CL={"mu_to_e_gamma":1.5e-13,"mu_to_3e":1.0e-12,
             "mu_to_e_conversion_Au197":7.0e-13}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def evaluate(native:dict,build:dict,thresholds=LIMITS_90CL):
    if native.get("number_original_cases")!=64 or len(native.get("cards",[]))!=64:
        raise ValueError("Incomplete original 64 Zee flavor source")
    if native.get("SPheno_historical_scalar_pn_conversion_swap_unrepaired") is not False or native.get("source_nuclear_patch_compiler_attestation_matched") is not True:
        raise ValueError("Native 64 source does not itself attest a rebuilt corrected nuclear observable")
    if any(card.get("historical_conversion_scalar_proton_neutron_swap_UNCORRECTED") is not False
           for card in native.get("cards",[])):
        raise ValueError("At least one native case was evaluated with the uncorrected conversion source")

    if native.get("global_acceptance") is not None or native.get("full_LFV")!="UNKNOWN":
        raise ValueError("Source full model acceptance not preserved")
    if native.get("native_binary_sha256")!=build.get("binary_sha256"):
        raise ValueError("SPheno source run and patched executable hashes disagree")
    if build.get("patched_observable_sha256")!=PATCHED_OBSERVABLE_SHA:
        raise ValueError("Patched nuclear source does not match exact independently audited two-line repair")
    if build.get("original_observable_sha256")!=EXPECTED_SOURCES["FlavorKit_Observables_ZeeTypeII.f90"]:
        raise ValueError("Original pre-repair nuclear source not certified")
    if build.get("force_complete_rebuild") is not True or build.get("build_exit_code")!=0:
        raise ValueError("No successful isolated forced rebuild from corrected source")
    if build.get("original_five_sha256")!=EXPECTED_SOURCES:
        raise ValueError("Original model source identity has changed")
    if build.get("binary_sha256")==PRIOR_COMPILED_EXE_SHA:
        raise ValueError("Old unpatched SPheno binary cannot be accepted")
    cases=[]
    for row in native["cards"]:
        k=(row["scalar_id"],row["ordering"],row["seed"])
        if row.get("global_acceptance") is not None or row.get("physical_mu3e") is not None:
            raise ValueError("Per-card full LFV accidentally promoted")
        y=row.get("native_source_yukawa_matching",{})
        if y.get("source_Yukawa_basis_validated") is not True:
            raise ValueError("Source native output complex F/Yee2/D not reproduced")
        if len(row.get("spectrum_mass_matching",{}))!=5:
            raise ValueError("Generated model spectrum does not match original scalar source")
        if row.get("native_executable_sha256")!=build["binary_sha256"]:
            raise ValueError("Per-card native binary drift")
        if row.get("source_verified_5_original_hashes")!=EXPECTED_SOURCES:
            raise ValueError("Full model-generated Fortran sources not verified")
        rates=row.get("native_one_loop_FlavorKitLFV",{})
        if not set(LIMITS_90CL).issubset(rates):
            raise ValueError("Incomplete mu-e source observable inventory")
        cmp={}
        for name,limit in LIMITS_90CL.items():
            value=rates[name]
            if not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
                raise ValueError("Invalid signed/interfering native observable "+name)
            cmp[name]={"prediction_1loop":value,"experimental_upper_90CL":limit,
                       "rate_over_limit":value/limit,
                       "source_1loop_below_experimental_limit":value<limit}
        al=rates.get("mu_to_e_conversion_Al27")
        if not isinstance(al,(int,float)) or not math.isfinite(al) or al<0:
            raise ValueError("Missing comparison-scale Al conversion nuclear prediction")
        au=float(rates["mu_to_e_conversion_Au197"])
        cases.append({
            "scalar_id":k[0],"ordering":k[1],"seed":k[2],
            "source_scalar_sha256":row["source_scalar_sha256"],
            "native_mu3e_1loop":rates["mu_to_3e"],
            "corrected_source_Au_conversion_historical_nuclear_model":au,
            "corrected_source_Al_conversion_historical_nuclear_model":float(al),
            "observed_90CL_screens":cmp,
            "source_1loop_all_three_below_limits":all(v["source_1loop_below_experimental_limit"] for v in cmp.values()),
            "Au_conversion_below_bound_even_if_nuclear_rate_x10":au*10<LIMITS_90CL["mu_to_e_conversion_Au197"],
            "physical_mu_e_conversion_in_modern_nuclear_EFT":None,
            "full_LFV": "UNKNOWN",
            "global_acceptance":None,
        })
    if len(cases)!=64 or len({(x["scalar_id"],x["ordering"],x["seed"]) for x in cases})!=64:
        raise ValueError("Repeated or missing 64 source Yukawa solutions")
    return {
        "schema":"zee-original-16x4-actual-1loop-SPheno-coherent-mue-corrected-source-90CL-screen-v1",
        "number_source_cases":64,
        "corrected_nuclear_observable_sha256":PATCHED_OBSERVABLE_SHA,
        "input_executable_sha256":build["binary_sha256"],
        "n_mu3e_one_loop_below_bound":sum(x["observed_90CL_screens"]["mu_to_3e"]["source_1loop_below_experimental_limit"] for x in cases),
        "n_Au_one_loop_historical_nuclear_below_bound":sum(x["observed_90CL_screens"]["mu_to_e_conversion_Au197"]["source_1loop_below_experimental_limit"] for x in cases),
        "n_all_three_named_one_loop_below_bound":sum(x["source_1loop_all_three_below_limits"] for x in cases),
        "n_Au_below_limit_with_x10_explicit_nuclear_stress":sum(x["Au_conversion_below_bound_even_if_nuclear_rate_x10"] for x in cases),
        "max_mu3e_1loop":max(x["native_mu3e_1loop"] for x in cases),
        "max_Au_conversion_historical_nuclear":max(x["corrected_source_Au_conversion_historical_nuclear_model"] for x in cases),
        "model_scope":"Original 16 certified spectra times four engineered neutrino-compatible Yukawa families",
        "not_calculated":"Two-loop Zee-specific EW gauge contributions, finite-q2 non-dipole, LEFT/QCD evolution, modern nucleon/nuclear inputs and conversion EFT uncertainties",
        "scoped_source_1loop_screen_only":True,
        "modern_physical_conversion":None,
        "full_LFV":"UNKNOWN",
        "global_acceptance":None,
        "cases":cases,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--native",type=Path,required=True)
    ap.add_argument("--build-receipt",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists():raise FileExistsError("Do not overwrite source LFV physics evidence")
    report=evaluate(json.loads(a.native.read_text()),json.loads(a.build_receipt.read_text()))
    a.output.write_text(json.dumps(report,allow_nan=False,indent=2,sort_keys=True)+"\n")
    print("ZEE_ALL64_NATIVE_MU3E_CONVERSION_1LOOP_DONE",
          report["n_all_three_named_one_loop_below_bound"],
          "OF",report["number_source_cases"],
          "FULL_LFV_UNKNOWN",flush=True)

if __name__=="__main__":
    main()

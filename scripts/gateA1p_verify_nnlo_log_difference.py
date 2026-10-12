#!/usr/bin/env python3
"""Gate A1P: test an exact analytic explanation for C3/C4 NNLO mismatch.

The comparison uses the already reported *unweighted* NNLO Wilson
matching coefficients of independently compiled HEPfit and SuperIso.

Claim being tested:
 HEPfit C_i^(2)     = cot(beta)^2 [n_i(x)+d_i(x) log(muW^2/mt^2)]
 SuperIso C_i^(2)  = cot(beta)^2 [n_i(x)-d_i(x) log(muW^2/mH^2)]
 for i=3,4; x=mt(muW)^2/mH^2.

This is a READ-ONLY source+number diagnosis, NOT a patch of matching.
The source-identification audit checks the actual A1M-patched SuperIso
v5.0 source and the pinned HEPfit source before attributing the mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB,git_blob_sha

MASSES=(300.0,700.0,1000.0,2000.0)
ORDERS=(3,4,5,6)
PRIMARY=(3,4)
RELATIVE_TOLERANCE=2e-9
ABSOLUTE_TOLERANCE=1e-11

def d3(x):
    """HEPfit cd32ct, algebraically rewritten using (1-x) powers."""
    l=math.log(x)
    return ((-30*x*x+20*x)/(27*(1-x)**4)*l
            +(-35*x**3+145*x*x-80*x)/(-81*(1-x)**3))

def d4(x):
    """HEPfit cd42ct, preserving the source's exact rational signs."""
    l=math.log(x)
    return ((-375*x**3-95*x*x+182*x)/(-54*(1-x)**5)*l
            +(133*x**4-108*x**3+4023*x*x-2320*x)/(324*(1-x)**4))

def predicted_shift(order,mass,mt,mu,tanbeta):
    x=(mt/mass)**2
    if not (0<x<1):
        raise ValueError("Require charged masses > running top for this audit")
    coeff={3:d3,4:d4}[order](x)
    log_superiso=math.log((mu/mass)**2)
    log_hepfit=math.log((mu/mt)**2)
    return (-(coeff/tanbeta**2)*(log_superiso+log_hepfit),
            coeff,log_superiso,log_hepfit)

def verify_sources(superiso_source,superiso_provenance,
                   hepfit_source,hepfit_provenance):
    sman=json.loads(superiso_provenance.read_text())
    hman=json.loads(hepfit_provenance.read_text())
    superiso=superiso_source.read_bytes()
    hepfit=hepfit_source.read_bytes()
    if hashlib.sha256(superiso).hexdigest()!=sman.get("patched_wilson_sha256"):
        raise ValueError("SuperIso A1M source does not match provenanced SHA")
    if git_blob_sha(hepfit)!=HEPFIT_BLOB or hman.get("upstream_git_blob")!=HEPFIT_BLOB:
        raise ValueError("HEPfit source does not match pinned Git blob")
    si=superiso.decode()
    hf=hepfit.decode()
    # Require original formula provenance, not merely a convention claim
    # imported from an unrelated SuperIso release.
    require={
        # SuperIso versions may express the SAME algebraic function as
        # -lu*lu*(...) or lu*lu*(-...), or using pow(lu,2.).
        # The coefficient's sign is tested *numerically against the
        # compiled, pinned A1M library* by verify_helper_output below,
        # not by fragile source-format regexes.
        "SuperIso_C3_delta_definition":r"double\s+Delta3H\s*\([^)]*\)\s*\{\s*return\s+[^;]*;",
        "SuperIso_C4_delta_definition":r"double\s+Delta4H\s*\([^)]*\)\s*\{\s*return\s+[^;]*;",
        "SuperIso_C3_log_mH":r"C3H_2\s*=\s*G3H\s*\(\s*yt\s*,\s*lu\s*\)\s*\+\s*Delta3H\s*\(\s*yt\s*,\s*lu\s*\)\s*\*\s*log\s*\(\s*pow\s*\(\s*mu_W\s*/\s*param->mass_H\s*,\s*2\.\s*\)\s*\)",
        "SuperIso_C4_log_mH":r"C4H_2\s*=\s*G4H\s*\(\s*yt\s*,\s*lu\s*\)\s*\+\s*Delta4H\s*\(\s*yt\s*,\s*lu\s*\)\s*\*\s*log\s*\(\s*pow\s*\(\s*mu_W\s*/\s*param->mass_H\s*,\s*2\.\s*\)\s*\)",
        "HEPfit_cd32ct":r"double\s+cd32ct\s*=",
        "HEPfit_cd42ct":r"double\s+cd42ct\s*=",
        "HEPfit_lstmu":r"double\s+lstmu\s*=\s*2\.\s*\*\s*log\s*\(\s*mu\s*/\s*mt\s*\)",
        "HEPfit_C3_log_mt":r"CWbsgArrayNNLO\[2\]\s*=\s*\(\s*n32ct\s*\+\s*cd32ct\s*\*\s*lstmu\s*\)\s*/\s*tan2",
        "HEPfit_C4_log_mt":r"CWbsgArrayNNLO\[3\]\s*=\s*\(\s*n42ct\s*\+\s*cd42ct\s*\*\s*lstmu\s*\)\s*/\s*tan2",
    }
    found={}
    for name,pattern in require.items():
        body=si if name.startswith("SuperIso") else hf
        found[name]=bool(re.search(pattern,body,re.S))
    if not all(found.values()):
        absent=[k for k,v in found.items() if not v]
        raise ValueError("Exact A1M/HEPfit source matching contract not "
                         f"confirmed, missing: {absent}")
    return {
        "status":"ACTUAL_SUPERISO5_A1M_AND_HEPFIT_LOG_STRUCTURE_CONFIRMED",
        "superiso_A1M_sha256":hashlib.sha256(superiso).hexdigest(),
        "HEPfit_blob":git_blob_sha(hepfit),
        "all_source_log_and_helper_definition_contracts_found":True,
        "source_text_does_not_prove_analytic_sign":True,
        "sign_requires_compiled_helper_probes":True,
        "source_checks":found,
    }

HELPER_ROW=re.compile(
    r"^HELPER mass=([-+0-9.eE]+) op=([34]) value=([-+0-9.eE]+)$")
HELPER_INPUT=re.compile(
    r"^INPUT mt_muW=([-+0-9.eE]+) tanbeta=([-+0-9.eE]+)$")

def verify_helper_output(helper_output, mass_input, result_json):
    """Check the physical sign using the ACTUAL compiled A1M helper.

    A string regex on 'return -lu*lu' cannot establish a function's
    algebraic sign; different source versions use different but
    equivalent factorizations. The independently compiled Delta3H,
    Delta4H values must satisfy the HEPfit coefficient identities.
    """
    data=json.loads(result_json.read_text())
    mi=json.loads(mass_input.read_text())
    mt=float(mi["mt_muW_GeV"])
    tanbeta=float(data["tanbeta"])
    lines=helper_output.read_text().splitlines()
    if "STATUS GATE_A1P_ACTUAL_SUPERISO_HELPER_VALUES_NOT_BR" not in lines:
        raise ValueError("Missing actual SuperIso helper executable marker")
    inp=[HELPER_INPUT.fullmatch(x) for x in lines]
    inp=[x for x in inp if x is not None]
    if len(inp)!=1 or not math.isclose(float(inp[0][1]),mt,rel_tol=0,abs_tol=1e-10) or not math.isclose(float(inp[0][2]),tanbeta,rel_tol=0,abs_tol=1e-12):
        raise ValueError("Helper probe mass/tanbeta not identical to A1P inputs")
    actual={}
    for line in lines:
        m=HELPER_ROW.fullmatch(line)
        if m:
            key=(float(m[1]),int(m[2]))
            if key in actual:
                raise ValueError(f"Duplicate helper probe: {key}")
            actual[key]=float(m[3])
    expected_keys={(mass,op) for mass in MASSES for op in PRIMARY}
    if set(actual)!=expected_keys:
        raise ValueError(f"Helper probe incomplete/unexpected rows: {set(actual)^expected_keys}")
    rows=[]
    for mass in MASSES:
        x=(mt/mass)**2
        for op,formula in ((3,d3),(4,d4)):
            independent=-formula(x)/(tanbeta**2)
            observed=actual[mass,op]
            if not math.isfinite(observed):
                raise ValueError(f"Nonfinite SuperIso helper result at m={mass}, C{op}")
            residual=observed-independent
            tolerance=2e-11+2e-9*abs(independent)
            if abs(residual)>tolerance:
                raise ValueError(
                    f"Actual SuperIso Delta{op}H sign/formula differs from "
                    f"-HEPfit cd{op}(x)/tanbeta^2 at mH={mass}: "
                    f"observed={observed:.17g}, expected={independent:.17g}, "
                    f"residual={residual:.17g}")
            rows.append({"mH_GeV":mass,"operator":f"C{op}",
                         "actual_compiled_SuperIso_Delta":observed,
                         "independent_negative_HEPfit_cd":independent,
                         "absolute_difference":abs(residual)})
    return {
        "status":"PINNED_COMPILED_SUPERISO_HELPER_SIGN_NUMERICALLY_CONFIRMED",
        "number_of_points":len(rows),
        "max_absolute_helper_residual":max(r["absolute_difference"] for r in rows),
        "rows":rows,
    }

def evaluate(existing_result,mass_input,source_checks,helper_verification):
    data=json.loads(existing_result.read_text())
    mi=json.loads(mass_input.read_text())
    if data.get("compared_count")!=44:
        raise ValueError("Need exactly 44 HEPfit-vs-SuperIso controls")
    if mi.get("status")!="GATE_A1P_RUNNING_TOP_FROM_SUPERISO_FUNCTION_NOT_LO_INVERSION":
        raise ValueError("Running top input was not directly evaluated in SuperIso")
    mt=mi["mt_muW_GeV"]
    tanbeta=data["tanbeta"]
    mu=data["muW_GeV"]
    if any(not math.isfinite(z) or z<=0 for z in (mt,tanbeta,mu)):
        raise ValueError("Invalid mass/scale/coupling")
    entries={(float(r["mass_GeV"]),r["order"],r["operator"]):r
             for r in data["compared_coefficients"]}
    if len(entries)!=44:
        raise ValueError("Duplicate comparison entries")
    output=[]
    maximum_residual=0.
    for mass in MASSES:
        row={"charged_mass_GeV":mass,"x_mt2_over_mH2":(mt/mass)**2,
             "coefficients":{}}
        for op in PRIMARY:
            observed=entries[mass,2,f"C{op}"]["superiso_minus_hepfit"]
            predicted,d,log_si,log_hf=predicted_shift(
                op,mass,mt,mu,tanbeta)
            residual=observed-predicted
            tol=ABSOLUTE_TOLERANCE+RELATIVE_TOLERANCE*abs(observed)
            if abs(residual)>tol:
                raise ValueError(f"Log explanation fails mH={mass} C{op}, "
                                 f"observed={observed:.17g} "
                                 f"predicted={predicted:.17g} "
                                 f"residual={residual:.17g}")
            maximum_residual=max(maximum_residual,abs(residual))
            row["coefficients"][f"C{op}"]={
                "observed_SuperIso_minus_HEPfit":observed,
                "predicted_from_differing_matching_logs":predicted,
                "residual":residual,
                "HEPfit_cd_coefficient":d,
                "log_muW2_over_mH2":log_si,
                "log_muW2_over_mt2":log_hf,
            }
        output.append(row)

    return {
        "status":"GATE_A1P_C3_C4_NNLO_LOG_DISCREPANCY_EXACTLY_REPRODUCED",
        "scope":"C3/C4 mismatch attribution only, not a corrected Wilson vector",
        "source_contract":source_checks,
        "actual_compiled_SuperIso_helper_sign_check":helper_verification,
        "mt_running_GeV":mt,"matching_scale_GeV":mu,"tanbeta":tanbeta,
        "prediction":"deltaCi=-(cd_i(x)/tanbeta^2) * "
                     "[ln(muW^2/mH^2)+ln(muW^2/mt(muW)^2)]",
        "results":output,
        "maximum_absolute_analytic_residual":maximum_residual,
        "NNLO_C3_C4_difference_inherited_by_C5_C6":True,
        "still_unresolved":["Correct logarithmic scale/sign based on analytic theory",
                            "C7^(2) and C8^(2) differences after accounting for "
                            "four-quark recombination and series approximations",
                            "Complete Type-II NNLO BR, uncertainty and Zee rates"],
        "SuperIso_source_modified":False,
        "HEPfit_source_modified":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("existing-result","mass-provenance","superiso-source",
                "a1m-provenance","hepfit-source","hepfit-provenance",
                "superiso-helper-output","output"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    source_checks=verify_sources(
        a.superiso_source,a.a1m_provenance,
        a.hepfit_source,a.hepfit_provenance)
    helper=verify_helper_output(
        a.superiso_helper_output,a.mass_provenance,a.existing_result)
    result=evaluate(a.existing_result,a.mass_provenance,source_checks,helper)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS:",result["status"])
    print("MAX ABSOLUTE C3/C4 LOG RESIDUAL:",
          result["maximum_absolute_analytic_residual"])
    for item in result["results"]:
        print(f"mH={item['charged_mass_GeV']:.0f}",
              "dC3=",item["coefficients"]["C3"]["residual"],
              "dC4=",item["coefficients"]["C4"]["residual"])
    print("STRICT: ROOT CAUSE ANALYTICALLY LOCALIZED, NO PHYSICS FIX OR EXCLUSION")
    print("Wrote",a.output)

if __name__=="__main__":
    main()

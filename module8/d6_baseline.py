"""D6 baseline arithmetic audit; does NOT calculate production uncertainties.

Reads committed, versioned D5 evidence, reproduces the exact three
charge-inclusive 13.6 TeV LO Z-only / gb references and D4 tree two-body
chain factors. Any full-model or scale/PDF results must come from NEW
independently validated MG5 runs, not from this helper.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

STATUS="D6_D5_BASELINE_ARITHMETIC_ONLY_NOT_NEW_PRODUCTION"
D5_SCHEMA="d5-real-two-process-1.0.0"
SPECTRA=("mH1_m50p0","source","mH1_p50p0")
PROCESSES=(("P1","H1H2_mixed_DY_Z_only","two_H1_product"),
           ("P2","tbH2_5FS","single_H1_product"))


def number(v, name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return float(v)


def audit(d5):
    if not isinstance(d5,dict) or d5.get("schema_version")!=D5_SCHEMA:
        raise ValueError("Expected versioned D5 REAL MG5 evidence")
    gates=set(d5.get("statuses",[]))
    if not {"D5_UFO_VERTEX_PASS","D5_EXECUTED_PARTON_LO_RATE_PASS",
            "D5_CHAIN_LO_ARITHMETIC_PASS"}<=gates:
        raise ValueError("D5 physical generator validation missing")
    if d5.get("global_zee_acceptance","invalid") is not None:
        raise ValueError("Input incorrectly declares model accepted")
    settings=d5["settings"]
    if settings["sqrt_s_TeV"]!=13.6 or settings["lhaid"]!=263000:
        raise ValueError("This audit is explicitly 13.6 TeV PDF263000")
    spectra=d5.get("spectra")
    if not isinstance(spectra,list) or len(spectra)!=3 or set(r["spectrum"] for r in spectra)!=set(SPECTRA):
        raise ValueError("Expected three distinct D5 spectra")
    chains=d5.get("tree_BR_composition")
    if not isinstance(chains,list) or len(chains)!=12:
        raise ValueError("Expected 12 D4 families with actual D5 rates")
    base={}
    for item in chains:
        if item["family"]=="baseline":
            spec=item["spectrum"]
            if spec in base:raise ValueError("Duplicate baseline family")
            base[spec]=item
    if set(base)!=set(SPECTRA):
        raise ValueError("Baseline family missing")
    out=[]
    for s in spectra:
        name=s["spectrum"]; row={"spectrum":name,
            "charged_masses_GeV":[s["physical"]["mH1"],s["physical"]["mH2"]],
            "reference_only":True,"processes":{}}
        chain=base[name]
        b2=number(chain["BR2_H1Z"],"BR2")
        b1=number(chain["BR1_tb"],"BR1")
        if b1>1 or b2>1:raise ValueError("BR larger than one")
        if not math.isclose(number(chain["single_H1_product"],"single product"),b2*b1,rel_tol=2e-13):
            raise ValueError("Invalid one-H1 product")
        if not math.isclose(number(chain["two_H1_product"],"two-H1 product"),b2*b1*b1,rel_tol=2e-13):
            raise ValueError("Invalid two-H1 product")
        for key,label,fac in PROCESSES:
            p=s[key]
            if p["spectrum"]!=name or p["process"]!=key:
                raise ValueError("Mixed spectrum/process")
            sig=number(p["sigma_LO_pb"],"cross section")
            err=number(p["integration_error_pb"],"integration error")
            if err>sig:raise ValueError("Unphysical integration error")
            product=number(chain[fac],"BR product")
            total=sig*product
            observed=chain["rates"][label]["conditional_sigma_times_tree_BR_pb"]
            if not math.isclose(observed,total,rel_tol=2e-12,abs_tol=1e-16):
                raise ValueError("D5 x BR composition mismatch")
            row["processes"][key]={"definition":label,
                 "sigma_charge_inclusive_LO_fb":1000*sig,
                 "integration_error_fb":1000*err,
                 "tree_chain_BR_product":product,
                 "conditional_sigma_x_tree_BR_fb":1000*total,
                 "full_model_vs_Z_only":"NOT_EVALUATED" if key=="P1" else "NOT_APPLICABLE",
                 "scale_uncertainty":"NOT_EVALUATED",
                 "PDF_uncertainty":"NOT_EVALUATED"}
        if row["processes"]["P1"]["conditional_sigma_x_tree_BR_fb"]<=0:
            raise ValueError("Expected nonzero Z-only control")
        row["P2_to_P1_chain_rate_ratio"]=(
            row["processes"]["P2"]["conditional_sigma_x_tree_BR_fb"]/
            row["processes"]["P1"]["conditional_sigma_x_tree_BR_fb"])
        out.append(row)
    return {"schema_version":"1.0.0","status":STATUS,"baseline_source":D5_SCHEMA,
      "sqrt_s_TeV":13.6,"PDF_LHAID":263000,
      "reference_spectra":out,
      "full_model_mixed_pair":"NOT_EVALUATED",
      "scale_PDF_variation":"NOT_EVALUATED",
      "physical_LHC_prediction":False,
      "global_zee_acceptance":None,
      "limitations":[
        "Exactly the validated D5 P1 Z-only and P2 5FS LO reference outputs; no new MG5 execution.",
        "Quoted errors are numerical integration only, not theory/PDF uncertainties.",
        "The mixed-pair P1 is Z-only; full-model diagrams and interference remain uncalculated.",
        "No physical Zee global viability, LHC limit, acceptance, detector or background claim.",
        "D4 BRs are on-shell tree two-body and their uncertainties are not assessed."]}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d5-evidence",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    if a.d5_evidence.resolve()==a.output.resolve():
        raise ValueError("Source and destination paths must differ")
    raw=a.d5_evidence.read_bytes()
    def pairs(seq):
        obj={}
        for k,v in seq:
            if k in obj:raise ValueError("Duplicate key "+k)
            obj[k]=v
        return obj
    src=json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda x:(_ for _ in ()).throw(ValueError("Invalid JSON constant: "+x)))
    result=audit(src)
    result["source_evidence_bytes_sha256"]=hashlib.sha256(raw).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=a.output.with_name(a.output.name+".tmp")
    tmp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    tmp.replace(a.output)
    print(STATUS)

if __name__=="__main__":main()

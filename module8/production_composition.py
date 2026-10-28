"""D5: compose *conditional* sigma times D4 tree-two-body branching fractions.

It does NOT generate events or cross sections. A real native UFO/MG5/PDF
audit must separately validate the cross section provenance before rates
can be used as physical parton-level LO predictions.
The 4FS and 5FS tbH2 estimates are alternative schemes, NEVER summed.
"""
import json
import math

STATUS = "D5_RATE_COMPOSITION_ARITHMETIC_ONLY"
PROCESSES = frozenset(("tbH2_4FS","tbH2_5FS","H1H2_mixed_DY"))
FAMILIES = ("baseline","index0","index2","mixed13")


def finite(x,name,nonnegative=False):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):
        raise ValueError(f"{name}: finite real required")
    if nonnegative and x<0:
        raise ValueError(f"{name}: negative value")
    return float(x)


def compose(d4, xsecs):
    """Pure arithmetic test surface; xsecs must be verified externally."""
    if (not isinstance(d4,dict) or
        "D4_COMPLETE_TWO_BODY_BR_PASS" not in d4.get("statuses",[]) or
        d4.get("global_zee_acceptance","bad") is not None):
        raise ValueError("Requires unmodified D4 conditional two-body ledger")
    if not isinstance(xsecs,dict) or set(xsecs)!={"schema_version","sqrt_s_TeV",
                                                "rate_cards","generator_validation"}:
        raise ValueError("Unexpected cross-section input schema")
    if xsecs["schema_version"]!="1.0.0":
        raise ValueError("Unknown rate-card schema")
    energy=finite(xsecs["sqrt_s_TeV"],"sqrt_s_TeV")
    if energy != 13.6:
        raise ValueError("D5 requires exactly 13.6 TeV")
    if xsecs["generator_validation"] not in ("UNVERIFIED", "EXECUTED_EXTERNAL_UNCERTIFIED"):
        raise ValueError("This arithmetic layer cannot certify generator provenance")
    rows=xsecs["rate_cards"]
    if not isinstance(rows,list) or len(rows)!=9:
        raise ValueError("Require all three production processes and all three D2 spectra")
    expected={(s,p) for s in ("mH1_m50p0","source","mH1_p50p0") for p in PROCESSES}
    got={}
    for row in rows:
        if not isinstance(row,dict) or set(row)!={"spectrum","process","sigma_LO_pb",
            "integration_error_pb","charge_scope","pdf_label","scale_label","source_run_id"}:
            raise ValueError("Missing/extra production card fields")
        tag=(row["spectrum"],row["process"])
        if tag not in expected or tag in got:
            raise ValueError("Unknown or duplicated production card")
        if row["charge_scope"]!="H2plus_and_H2minus_inclusive":
            raise ValueError("Provide explicit both charges once, no hidden factor of two")
        for k in ("pdf_label","scale_label","source_run_id"):
            if not isinstance(row[k],str) or not row[k].strip() or len(row[k])>256:
                raise ValueError("Missing generator input label "+k)
        sigma=finite(row["sigma_LO_pb"],"sigma_LO_pb",True)
        error=finite(row["integration_error_pb"],"integration_error_pb",True)
        if error>sigma:
            raise ValueError("Integration error exceeds LO central estimate")
        got[tag]=(sigma,error,row)
    if set(got)!=expected:
        raise ValueError("Incomplete per-spectrum 4FS/5FS/DY card")
    families=d4["conditional_lepton_families"]
    if not isinstance(families,list) or len(families)!=12:
        raise ValueError("Expected twelve D4 families")
    outputs=[]
    seen_families=set()
    for entry in families:
        spec=entry["spectrum_name"];fam=entry["family_name"]
        if spec not in ("mH1_m50p0","source","mH1_p50p0") or fam not in FAMILIES:
            raise ValueError("Unexpected D4 spectrum/family")
        if (spec,fam) in seen_families:
            raise ValueError("Duplicate D4 spectrum/family")
        seen_families.add((spec,fam))
        mothers=entry["mothers"]
        h2=mothers["H2"];h1=mothers["H1"]
        if (h2["status"]!="D4_COMPLETE_TWO_BODY_BR_PASS" or
            h1["status"]!="D4_COMPLETE_TWO_BODY_BR_PASS" or
            h2["missing_widths"] or h1["missing_widths"]):
            raise ValueError("No complete tree two-body ledger")
        b2=finite(h2["branching_fraction"],"BR(H2->H1Z)")
        b1=finite(h1["branching_fractions"]["t anti-b"],"BR(H1->tb)")
        if not (0<=b1<=1 and 0<=b2<=1):
            raise ValueError("Nonphysical BR")
        rates={}
        for p in sorted(PROCESSES):
            sigma,err,card=got[(spec,p)]
            cascade_factor=b2*b1 if p.startswith("tbH2_") else b2*b1*b1
            rates[p]={
               "sigma_LO_pb":sigma,
               "sigma_error_pb":err,
               "tree_chain_B_product":cascade_factor,
               "conditional_sigma_times_tree_BR_pb":sigma*cascade_factor,
               "conditional_integration_error_pb":err*cascade_factor,
               "additional_spectator_bottom_in_4FS":p=="tbH2_4FS",
               "source_run_id":card["source_run_id"],
               "accepted_LHC_prediction":False
            }
        outputs.append({
            "benchmark_id":entry["benchmark_id"],"spectrum":spec,"family":fam,
            "BR2_to_H1Z_tree":b2,"BR1_to_tb_tree":b1,
            "single_H1_chain_product":b2*b1,
            "mixed_pair_two_H1_chain_product":b2*b1*b1,
            "rates":rates,
            "global_zee_acceptance":None
        })
    if len({x["benchmark_id"] for x in outputs})!=12:
        raise ValueError("Duplicate D4 family IDs")
    return {
        "schema_version":"1.0.0","status":STATUS,
        "sqrt_s_TeV":energy,"source_BRs":"D4_TREE_ON_SHELL_TWO_BODY",
        "external_generator_validation":xsecs["generator_validation"],
        "processes_not_to_sum":["tbH2_4FS","tbH2_5FS"],
        "entries":outputs,
        "physical_rate_validation":False,
        "fiducial_acceptance":None,
        "experimental_exclusion":None,
        "global_zee_acceptance":None,
        "limitations":[
          "Arithmetic only until actual PDF/LHA/UFO/MG5 provenance is independently audited.",
          "4FS and 5FS are alternative LO approximations to overlapping tbH physics: NEVER add.",
          "Mixed pair DY produces TWO H1 scalars, hence squares BR(H1->tb).",
          "Production cross section for both charges is included exactly once.",
          "No Z/t/W branching, parton shower, finite width, interference, detector or background analysis.",
          "D4 BRs are LO on-shell two-body, not corrected physical decay probabilities.",
          "All Zee global viability/precision-flavor/LFV gates remain incomplete."
        ]
    }


def main():
    import argparse
    import hashlib
    import pathlib
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--d4-evidence",type=pathlib.Path,required=True)
    p.add_argument("--rate-card",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,required=True)
    a=p.parse_args()
    def strict(raw):
        def pairs(seq):
            out={}
            for key,val in seq:
                if key in out:raise ValueError("Duplicate key "+key)
                out[key]=val
            return out
        return json.loads(raw,object_pairs_hook=pairs,
            parse_constant=lambda x:(_ for _ in ()).throw(ValueError("Nonfinite JSON "+x)))
    d4_raw=a.d4_evidence.read_bytes();x_raw=a.rate_card.read_bytes()
    result=compose(strict(d4_raw),strict(x_raw))
    result["d4_bytes_sha256"]=hashlib.sha256(d4_raw).hexdigest()
    result["xsec_card_bytes_sha256"]=hashlib.sha256(x_raw).hexdigest()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=a.output.with_name(a.output.name+".tmp")
    tmp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    tmp.replace(a.output)
    print(STATUS)

if __name__=="__main__":
    main()

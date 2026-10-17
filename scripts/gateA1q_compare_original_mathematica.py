#!/usr/bin/env python3
"""Gate A1Q: evaluate original KIT c2HDM.m with Wolfram and compare A1P.

Unmodified authenticated Mathematica source with exact rational inputs:
Au=AuC=cot(beta), Ad=AdC=-tan(beta), r=mt(mu0)^2/mH^2.
HEPfit NNLO C8 effective is put into author basis by adding +40*C5.
This is a coefficient comparison, NOT full BR or physical exclusion.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

from gateA1q_inspect_original_mathematica import attest_source
from gateA1p_audit_effective_operator_basis import Y,Z,HEPFIT_CODE_Z

MASSES=(300,700,1000,2000)
OPS={0:(7,8),1:(7,8),2:(3,4,5,6,7,8),3:(7,8)}
RECORD=re.compile(
    r"^AUTHOR mass=(\d+) order=(\d+) op=(\d+) value=(\S+)$")

def decimal_rational(number):
    f=Fraction(Decimal(str(number)))
    return str(f.numerator),str(f.denominator)

def make_inputs(data):
    if data.get("compared_count")!=44 or len(data.get("compared_coefficients",[]))!=44:
        raise ValueError("Require all 44 A1P matching coefficients")
    mt=float(data["running_mt_muW_GeV"])
    mu=float(data["muW_GeV"])
    tan=float(data["tanbeta"])
    if not (math.isfinite(mt) and 100<mt<250 and
            math.isfinite(mu) and mu>0 and
            math.isfinite(tan) and tan>0):
        raise ValueError("Nonfinite/unphysical matching inputs")
    result={"status":"A1Q_ORIGINAL_SOURCE_NUMERIC_INPUTS_NOT_BR",
            "masses_GeV":list(MASSES),
            "Yukawa_convention":{
                "Au":"1/tanbeta","AuC":"1/tanbeta",
                "Ad":"-tanbeta","AdC":"-tanbeta"},
            "mt_GeV":mt,"mu_GeV":mu,"tanbeta":tan}
    for name,value in (("mt",mt),("mu",mu),("tan",tan)):
        num,den=decimal_rational(value)
        result[name+"_numerator"]=num
        result[name+"_denominator"]=den
    return result

def parse_wolfram_number(s):
    # InputForm may contain arbitrary-precision markers and exponents.
    cleaned=re.sub(r"\x60[0-9.]*","",s).replace("*^","e")
    try:
        val=float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Unparsable Wolfram real {s!r}") from exc
    if not math.isfinite(val):
        raise ValueError(f"Nonfinite Wolfram output {s!r}")
    return val

def read_authors_values(path):
    lines=Path(path).read_text().splitlines()
    if not lines or lines[0]!="STATUS A1Q_ORIGINAL_AUTHOR_NUMERICAL_VALUES_NO_BR":
        raise ValueError("Missing original-author Wolfram output marker")
    values={}
    for line in lines[1:]:
        mat=RECORD.fullmatch(line)
        if not mat:
            raise ValueError(f"Unexpected Mathematica output record {line[:150]!r}")
        mass,order,op=int(mat[1]),int(mat[2]),int(mat[3])
        key=(mass,order,op)
        if key in values:
            raise ValueError(f"Duplicate coefficient {key}")
        values[key]=parse_wolfram_number(mat[4])
    expected={(m,order,op) for m in MASSES for order,ops in OPS.items()
              for op in ops}
    if set(values)!=expected:
        raise ValueError(f"Original source output coverage differs "
                         f"missing={sorted(expected-set(values))} "
                         f"extra={sorted(set(values)-expected)}")
    return values

def compare(authors,old_data,inputs):
    old={(int(row["mass_GeV"]),int(row["order"]),int(row["operator"][1:])):row
         for row in old_data["compared_coefficients"]}
    if len(old)!=44 or len(authors)!=48:
        raise ValueError("Missing/duplicated A1P or original author results")
    if tuple(sorted({m for m,order,op in old}))!=MASSES:
        raise ValueError("A1P mass grid differs")
    out=[]
    for mass in MASSES:
        for original_order,ops in OPS.items():
            for op in ops:
                author=authors[mass,original_order,op]
                matching_order=min(original_order,2)
                if original_order==3:
                    basis="original_raw_dipole"
                elif op>=7:
                    basis="original_standard_effective_dipole"
                else:
                    basis="four_quark"
                def c(src,i):
                    return float(old[mass,matching_order,i][src])
                a="superiso_isolated_delta"
                b="independent_HEPfit_delta"
                if op<=6:
                    si,hepf=c(a,op),c(b,op)
                elif basis=="original_raw_dipole":
                    hepf_code_weights=Y if op==7 else HEPFIT_CODE_Z
                    si=c(a,op)
                    hepf=c(b,op)-sum(w*c(b,i)
                        for i,w in hepf_code_weights.items())
                else:
                    weights=Y if op==7 else Z
                    si=c(a,op)+sum(w*c(a,i) for i,w in weights.items()
                        if (mass,matching_order,i) in old)
                    hepf=c(b,op)
                    if matching_order==2 and op==8:
                        hepf+=40.0*c(b,5)
                out.append({
                    "mass_GeV":mass,"author_order":original_order,
                    "operator":f"C{op}","basis":basis,
                    "original_author":author,
                    "SuperIso_in_author_basis":si,
                    "HEPfit_in_author_basis":hepf,
                    "SuperIso_minus_author":si-author,
                    "HEPfit_minus_author":hepf-author,
                    "SuperIso_relative_deviation":abs(si-author)/
                        max(abs(si),abs(author),1e-30),
                    "HEPfit_relative_deviation":abs(hepf-author)/
                        max(abs(hepf),abs(author),1e-30),
                })
    return {
        "status":"GATE_A1Q_ORIGINAL_MATHEMATICA_NUMERICALLY_COMPARED_NOT_BR_VALIDATED",
        "original_author_source_sha256":
            "cb2d1328bc2542a6324e73efe6f89c43381efdc93db5e3b0ca8348db980645d8",
        "original_values_count":len(authors),
        "comparison_rows_count":len(out),"comparison_rows":out,
        "numeric_inputs":inputs,
        "original_C8_basis_correction_HEPfit_NNLO": "+40*C5",
        "full_NNLO_matching_validated":False,
        "BtoXs_gamma_BR_validated":False,
        "Zee_benchmark_allowed":None,"Zee_benchmark_excluded":None,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--authors-source",type=Path,required=True)
    ap.add_argument("--kit-provenance",type=Path,required=True)
    ap.add_argument("--existing-result",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--wolframscript",default="wolframscript")
    ap.add_argument("--authors-values",type=Path)
    ap.add_argument("--prepare-only",action="store_true")
    arg=ap.parse_args()
    _content,sha,_prov=attest_source(arg.authors_source,arg.kit_provenance)
    old=json.loads(arg.existing_result.read_text())
    inp=make_inputs(old)
    arg.output_dir.mkdir(parents=True,exist_ok=True)
    input_file=arg.output_dir/"original_mathematica_inputs.json"
    input_file.write_text(json.dumps(inp,indent=2)+"\n")
    wl=Path(__file__).with_name("gateA1q_eval_authors.wls")
    vals=arg.authors_values or arg.output_dir/"original_mathematica_values.txt"
    if arg.prepare_only:
        print("STATUS A1Q_ORIGINAL_MATHEMATICA_INPUTS_PREPARED_NO_EVALUATION")
        print("ORIGINAL_KIT_SHA256",sha)
        print("WOLFRAM_COMMAND",f"wolframscript -file {wl} "
              f"{arg.authors_source} {input_file} {vals}")
        return
    if not arg.authors_values:
        binary=shutil.which(arg.wolframscript)
        if not binary:
            raise SystemExit("A1Q_WOLFRAMSCRIPT_UNAVAILABLE: use --prepare-only "
                             "and run the .wls script on a Mathematica-equipped "
                             "machine, then supply --authors-values on AF")
        proc=subprocess.run(
            [binary,"-file",str(wl.resolve()),
             str(arg.authors_source.resolve()),str(input_file.resolve()),
             str(vals.resolve())],
            capture_output=True,text=True,timeout=300,check=False)
        if proc.returncode or not vals.is_file():
            raise ValueError("Original Mathematica evaluation failed: "
                 f"exit={proc.returncode} stdout={proc.stdout[-1300:]} "
                 f"stderr={proc.stderr[-1300:]}")
        print(proc.stdout[-1600:])
    authors=read_authors_values(vals)
    report=compare(authors,old,inp)
    dst=arg.output_dir/"original_vs_A1P_NNLO_numeric.json"
    dst.write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",report["status"])
    for row in report["comparison_rows"]:
        if row["author_order"]>=2:
            print(f"mH={row['mass_GeV']} {row['operator']}",
                  f"original_order={row['author_order']} {row['basis']}",
                  f"author={row['original_author']:.11g}",
                  f"SI-author={row['SuperIso_minus_author']:.10g}",
                  f"HF-author={row['HEPfit_minus_author']:.10g}")
    print("FULL_NNLO_VALIDATED",report["full_NNLO_matching_validated"])
    print("BR_VALIDATED",report["BtoXs_gamma_BR_validated"])
    print("Wrote",dst)

if __name__=="__main__": main()

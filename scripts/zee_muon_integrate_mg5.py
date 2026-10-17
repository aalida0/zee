#!/usr/bin/env python3
"""Integrate muon Zee mixed charged-scalar pairs with matched MG5 inputs.

Runs both charge conjugates at sqrt(s)=1.5 and 3 TeV, separately for
Z-restricted and full tree processes. The Yang/Wu SLHA card must be the
B4 scalar-matched *diagnostic* (f=0): NOT neutrino-compatible; its
DECAY widths are stale. Final heavy/light particles are stable here.

Read cross section from <MGGenerationInfo> in per-run LHE banner;
match analytic Z-only sigma using UFO's alpha,G_F,MZ input scheme.
No physical discovery/exclusion or signal decay sensitivity.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from gate7_make_diagnostic_param_card import (
    parse_card_values,validate_card_values,replacements)
from zee_muon_make_scalar_card import selected_point,MAP_KEYS
from zee_muon_asymmetric_pair_pilot import sigma_both_charges_fb

STATUS="ZEE_PAPER2_MG5_CROSS_SECTION_DIAGNOSTIC_NOT_ALLOWED"
NEEDED=("lpp1","lpp2","ebeam1","ebeam2","nevents","iseed")
CSV_FIELDS=("energy_GeV","mode","MG5_sigma_fb",
    "analytic_Z_sigma_fb","ratio_to_analytic",
    "relative_Z_difference","run","banner","status")
GENINFO=re.compile(r"<MGGenerationInfo>(.*?)</MGGenerationInfo>",re.I|re.S)
XSEC=re.compile(r"Integrated\s+weight\s*\(pb\)\s*:\s*"
    r"([+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+\-]?\d+)?)",re.I)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def patch_run_card(content,updates):
    seen=set();lines=[]
    for src in content.splitlines(keepends=True):
        bare=src.rstrip("\r\n");ending=src[len(bare):]
        m=re.match(r"^(\s*)([^=#]*?)(\s*=\s*)([A-Za-z_]\w*)(\s*(?:!.*)?)$",bare)
        if not m or m.group(4) not in updates:
            lines.append(src);continue
        key=m.group(4)
        if key in seen:raise ValueError("Duplicate run-card entry "+key)
        seen.add(key)
        lines.append(m.group(1)+str(updates[key])+m.group(3)+key+m.group(5)+ending)
    missing=set(NEEDED)-seen
    if missing:raise ValueError("Missing run-card entries "+repr(sorted(missing)))
    return "".join(lines)


def ew_from_slha(card):
    """Yang/Wu Parameters.fr alpha,Gf,MZ -> internal MW,sW2 tree scheme."""
    block=None;entries={}
    for line in Path(card).read_text().splitlines():
        m=re.match(r"^\s*block\s+(\w+)\b",line,re.I)
        if m:
            block=m.group(1).upper();continue
        if re.match(r"^\s*(decay|qnumbers)\b",line,re.I):
            block=None;continue
        if block not in ("SMINPUTS","MASS"):continue
        bits=line.split("#",1)[0].split()
        if len(bits)<2:continue
        try:
            i=int(bits[0]);v=float(bits[1].replace("D","E"))
        except ValueError:continue
        if (block,i) in entries:raise ValueError("Duplicate EW input")
        entries[block,i]=v
    a=1./entries["SMINPUTS",1]
    gf=entries["SMINPUTS",2]
    mz=entries["MASS",23]
    discriminant=mz**4/4-math.pi/math.sqrt(2)*a/gf*mz*mz
    if not (a>0 and gf>0 and mz>0 and discriminant>0):
        raise ValueError("Bad EW inputs")
    mw=math.sqrt(mz*mz/2+math.sqrt(discriminant))
    sw2=1-(mw/mz)**2
    if not (.1<sw2<.4):raise ValueError("Invalid weak mixing")
    return {"alpha":a,"GF":gf,"MZ":mz,"MW_internal":mw,"sw2":sw2}


def banner_pb(banner_path):
    """Fail closed if the LHE integrated cross section cannot be found."""
    content=Path(banner_path).read_text(errors="replace")
    section=GENINFO.findall(content)
    if len(section)!=1:raise ValueError("Ambiguous MGGenerationInfo")
    values=XSEC.findall(section[0])
    if len(values)!=1:raise ValueError("Missing integrated weight (pb)")
    v=float(values[0].replace("D","E").replace("d","e"))
    if not(math.isfinite(v) and v>=0):raise ValueError("Nonfinite MG5 sigma")
    return v


def generated_processes(directory,mode):
    directory=Path(directory)
    card=directory/"Cards"/"proc_card_mg5.dat"
    if not card.is_file():raise ValueError("Missing MG5 process card "+str(card))
    content=" ".join(card.read_text().split())
    for final in ("H+ h-","H- h+"):
        wanted="mu+ mu- > "+("z > " if mode=="Z_only" else "")+final
        if wanted not in content:
            raise ValueError("Process card missing "+wanted)
    if mode=="full_tree" and "mu+ mu- > z > H+" in content:
        raise ValueError("Full-tree process is Z restricted")
    if not (directory/"bin"/"generate_events").is_file():
        raise ValueError("Missing MG5 bin/generate_events")


def energy_list(spec):
    """Validate requested centre-of-mass energies with specific errors."""
    if not spec.strip():
        raise ValueError("Empty energy list")
    try:
        energies=[float(a.strip()) for a in spec.split(",")]
    except ValueError as exc:
        raise ValueError("Invalid energy: expected comma-separated GeV values") from exc
    if len(energies)!=len(set(energies)):
        raise ValueError("Repeated energies")
    if any(not math.isfinite(E) or E<=100 for E in energies):
        raise ValueError("Invalid energy")
    return energies


def write_json(p,obj):
    Path(p).write_text(json.dumps(obj,indent=2)+"\n")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b4-csv",type=Path,required=True)
    ap.add_argument("--candidate-id",required=True)
    ap.add_argument("--param-card",type=Path,required=True)
    ap.add_argument("--z-only-dir",type=Path,required=True)
    ap.add_argument("--full-tree-dir",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--energies-GeV",default="1500,3000")
    ap.add_argument("--events",type=int,default=3000)
    ap.add_argument("--tolerance",type=float,default=.05)
    ap.add_argument("--execute",action="store_true")
    a=ap.parse_args()
    if not(100<=a.events<=20000 and 0<a.tolerance<.5):
        ap.error("Invalid event count/tolerance")
    energies=energy_list(a.energies_GeV)
    point=selected_point(a.b4_csv,a.candidate_id)
    card=a.param_card.resolve()
    opts={k:point[k] for k in MAP_KEYS}
    expected=replacements(beta=point["beta"],mH1=point["mH1"],
                          mH2=point["mH2"],**opts)
    validate_card_values(card.read_text(),expected)
    parsed=parse_card_values(card.read_text())
    if any(parsed["ZEEYUKAWAF",k]!=0 for k in (1,2,3)):
        raise ValueError("Diagnostic card must have f=0")
    ew=ew_from_slha(card)
    directories={"Z_only":a.z_only_dir.resolve(),
                 "full_tree":a.full_tree_dir.resolve()}
    for mode,d in directories.items():generated_processes(d,mode)
    refs={E:sigma_both_charges_fb(
        E,point["mH1"],point["mH2"],point["gamma"],
        alpha=ew["alpha"],sw2=ew["sw2"]) for E in energies}
    report={
        "status":"PLAN_NOT_EXECUTED",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "candidate_id":a.candidate_id,"point":point,
        "param_card_sha256":sha(card),"ufo_EW_inputs":ew,
        "energies_GeV":energies,"events_per_run":a.events,
        "analytic_Z_both_charges_fb":{str(E):v for E,v in refs.items()},
        "model_has_physical_neutrino_yukawas":False,
        "decay_rates_calculated":False,
        "experimentally_allowed":None,"results":[]}
    print("STATUS",STATUS)
    for E in energies:
        print("ANALYTIC_MATCHED_EW",E,"GEV SIGMA_BOTH_CHARGES_FB",
              format(refs[E],".8g"))
    if not a.execute:
        print("DRY_RUN True; append --execute for MG5 stable-pair integrations")
        return
    out=a.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("Choose a NEW empty output directory")
    out.mkdir(parents=True)
    write_json(out/"manifest.json",report)
    try:
        for mode,d in directories.items():
            pcard=d/"Cards"/"param_card.dat"
            rcard=d/"Cards"/"run_card.dat"
            if not pcard.is_file() or not rcard.is_file():
                raise ValueError("Missing MG5 generated cards in "+str(d))
            for original in (pcard,rcard):
                backup=original.with_name(original.name+".before_zee_p2")
                if not backup.exists():shutil.copy2(original,backup)
            shutil.copyfile(card,pcard)
            for n,E in enumerate(energies):
                name="P2"+("Z" if mode=="Z_only" else "F")+str(int(E))
                if (d/"Events"/name).exists():
                    raise ValueError("Refusing to replace existing MG5 run "+name)
                updates={
                    "lpp1":0,"lpp2":0,"ebeam1":E/2,"ebeam2":E/2,
                    "nevents":a.events,"iseed":1100+n*100+(
                        0 if mode=="Z_only" else 1),
                    "polbeam1":0,"polbeam2":0}
                rcard.write_text(patch_run_card(rcard.read_text(),updates))
                command=[str(d/"bin"/"generate_events"),name,
                         "-f","--laststep=parton"]
                log=out/(name+".log")
                print("START",name,"LOG",log,flush=True)
                with log.open("w") as handle:
                    process=subprocess.run(command,cwd=d,stdout=handle,
                                           stderr=subprocess.STDOUT,check=False)
                if process.returncode:
                    raise RuntimeError(name+" integration failed:\n"+
                        "\n".join(log.read_text(errors="replace").splitlines()[-30:]))
                banners=list((d/"Events"/name).glob("*banner*.txt"))
                if len(banners)!=1:
                    raise ValueError(name+" expected 1 MG5 LHE banner")
                sigma=1000*banner_pb(banners[0])
                diff=abs(sigma/refs[E]-1) if mode=="Z_only" and refs[E] else None
                status=("Z_CLOSURE_PASS" if diff<=a.tolerance else
                        "Z_CLOSURE_FAIL_STOP") if diff is not None else (
                        "FULL_TREE_UNFITTED_YUKAWA_DIAGNOSTIC")
                record={"energy_GeV":E,"mode":mode,
                    "MG5_sigma_fb":sigma,"analytic_Z_sigma_fb":refs[E],
                    "ratio_to_analytic":sigma/refs[E] if refs[E]>0 else None,
                    "relative_Z_difference":diff,"run":name,
                    "banner":str(banners[0]),"status":status}
                report["results"].append(record)
                write_json(out/"manifest.json",report)
                print("RESULT",name,"sigma_fb",format(sigma,".8g"),
                      "analytic_Z_fb",format(refs[E],".8g"),
                      "status",status,flush=True)
        with (out/"cross_sections.csv").open("w",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=CSV_FIELDS)
            writer.writeheader();writer.writerows(report["results"])
        good=all(x["status"]=="Z_CLOSURE_PASS" for x in report["results"]
                 if x["mode"]=="Z_only")
        report["status"]=("Z_ONLY_CLOSURE_PASS_DIAGNOSTIC"
                          if good else "Z_ONLY_CLOSURE_FAIL_STOP")
        write_json(out/"manifest.json",report)
        print("FINAL",report["status"])
        print("OUTPUT",out/"cross_sections.csv")
        if not good:raise SystemExit(3)
    except BaseException as exc:
        if report["status"]=="PLAN_NOT_EXECUTED":
            report["status"]="FAILED_OR_INCOMPLETE_NOT_ALLOWED"
        report["error"]=str(exc)
        write_json(out/"manifest.json",report)
        raise


if __name__=="__main__":
    main()

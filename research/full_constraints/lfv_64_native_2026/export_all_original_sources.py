#!/usr/bin/env python3
"""Export the original FIVE hash-pinned ZeeTypeII LFV Fortran sources locally.

The generated sources belong to the original model setup. Do not upload
them to GitHub or attempt to substitute a different Zee model.

Checks five original SHA256 values from their archived source contracts,
constructs a deterministic zip and never writes source files to the repo.
If the original source is unavailable, the exporter FAILS rather than
regenerating a similar-but-inequivalent model.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import zipfile
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import EXPECTED_SOURCES,ROOT

MANIFEST=ROOT/"research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json"
MAX_FILE=60_000_000

def digest(buf):return hashlib.sha256(buf).hexdigest()

def sources_from_original_installation(manifest=MANIFEST):
    data=json.loads(Path(manifest).read_text())
    indexed={x["id"]:Path(x["path_hint"]).expanduser() for x in data["artifacts"]}
    base=indexed["generated"]
    # SARAH puts FlavorKit generated amplitudes and model observables in
    # the model's 'Observables' folder; LowEnergy is a sibling to that folder.
    parent=base.parent
    if parent.name.lower()!="observables":
        raise ValueError("Unexpected original ZeeTypeII SPheno model output location")
    candidates={
       "FlavorKit_LFV_ZeeTypeII.f90":[base],
       "Couplings_ZeeTypeII.f90":[indexed["couplings"]],
       "LoopFunctions.f90":[indexed["loops"]],
       "FlavorKit_Observables_ZeeTypeII.f90":[parent/"FlavorKit_Observables_ZeeTypeII.f90",
                                                parent.parent/"FlavorKit_Observables_ZeeTypeII.f90"],
       "LowEnergy_ZeeTypeII.f90":[parent.parent/"LowEnergy_ZeeTypeII.f90",
                                   parent/"LowEnergy_ZeeTypeII.f90"],
    }
    found={}
    for name,options in candidates.items():
        matches=[]
        for path in options:
            if not path.is_file():continue
            if path.stat().st_size>MAX_FILE:raise ValueError("Unreasonable generated source size "+str(path))
            if digest(path.read_bytes())==EXPECTED_SOURCES[name]:
                matches.append(path)
        if len(matches)!=1:
            raise FileNotFoundError("Missing unique SHA256-pinned original source "+name+"; searched "+str(options))
        found[name]=matches[0]
    return found

def export(output:Path,paths:dict[str,Path]):
    if output.exists():raise FileExistsError("Never overwrite private model source archive")
    if set(paths)!=set(EXPECTED_SOURCES):
        raise ValueError("Need all five model-specific Fortran sources")
    payload={}
    for name,path in paths.items():
        raw=Path(path).read_bytes()
        if digest(raw)!=EXPECTED_SOURCES[name]:raise ValueError("Original source SHA changed "+name)
        payload[name]=raw
    source={"model":"ZeeTypeII","original_SARAH":"4.15.4",
            "source_filenames_sha256":EXPECTED_SOURCES,
            "original_source_local_locations":{k:str(v) for k,v in paths.items()},
            "complete_one_loop_64_runs_completed":False,
            "physical_mu3e":None,"physical_mu_e_conversion":None}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"x") as archive:
        for name,raw in sorted(payload.items()):
            item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(item,raw)
        info=zipfile.ZipInfo("SOURCE_SHA256_AND_STATUS.json",date_time=(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,json.dumps(source,sort_keys=True,indent=2)+"\\n")
    with zipfile.ZipFile(output) as archive:
        for name,expected in EXPECTED_SOURCES.items():
            if digest(archive.read(name))!=expected:
                raise IOError("Archive generated with modified source "+name)
    return {"archive":str(output),"source_count":len(payload),
            "source_sha256":{x:digest(buf) for x,buf in payload.items()},
            "native_LFV_executed":False}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,default=Path.home()/"zee_TypeII_original_five_LFV_sources.zip")
    args=ap.parse_args()
    result=export(args.output,sources_from_original_installation())
    print("FIVE_ORIGINAL_ZEE_SOURCE_SHA256_VERIFIED",result["source_count"])
    print("PRIVATE_SOURCE_ARCHIVE",result["archive"])
    print("FULL_NEW_64_LFV_NOT_YET_EXECUTED")
if __name__=="__main__":main()

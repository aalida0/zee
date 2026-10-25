#!/usr/bin/env python3
"""F16 strict transferable AF -> LOCAL F13 scalar/complex f/Y source check."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
STATUS="F16_THREE_EXACT_ZEE_SARAH_SCALAR_FLAVOR_VERTEX_FIXTURES_NOT_MADWIDTH_BR"
FILES=("F16_three_exact_F13_Zee_SARAH_charged_vertices.m",
       "F16_three_exact_F13_Zee_input_reconstruction.json")
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def verify(folder,model):
    folder=Path(folder).expanduser().resolve()
    model=Path(model).expanduser().resolve()
    summ=json.loads((folder/"summary.json").read_text())
    manifest=json.loads((folder/"manifest.json").read_text())
    if summ.get("status")!=STATUS or manifest.get("status")!=STATUS:
        raise ValueError("F16 status/source not recognized")
    if manifest.get("summary_SHA256")!=sha(folder/"summary.json"):
        raise ValueError("F16 summary SHA corrupted")
    for actual,expected,label in [
      (sha(folder/FILES[0]),summ.get("numeric_fixture_SHA256"),"Wolfram fixture"),
      (sha(folder/FILES[1]),summ.get("source_reconstruction_SHA256"),"complex source JSON"),
      (sha(model),summ.get("SARAH_ZeeTypeII_source_SHA256"),"SARAH model source"),
      (manifest.get("fixture_SHA256"),sha(folder/FILES[0]),"manifest fixture"),
    ]:
        if actual!=expected:raise ValueError("F16 "+label+" mismatched or stale")
    source=json.loads((folder/FILES[1]).read_text())
    if (len(source)!=3 or len(set(source))!=3 or
        set(source)!=set(summ.get("exact_F13_candidates",[]))):
        raise ValueError("F16 exactly three original F13 cases required")
    if (summ.get("all_three_local_SARAH_numeric_vertex_checks_passed") is not False
        or summ.get("actual_generated_complex_Zee_UFO_exists") is not False
        or manifest.get("all_three_local_SARAH_numeric_vertex_checks_passed") is not False):
        raise ValueError("F16 input bundle cannot already claim SARAH validation")
    for name,point in source.items():
        if (point.get("full_model_madwidth_physical_totals") is not None or
            point.get("complete_UFO_and_Ward_amplitudes_validated") is not False or
            not point.get("complex_Y_and_f_reconstructed_from_exact_F13")):
            raise ValueError("F16 source case incorrectly claims complete physics "+name)
    print("F16_TRANSFER_SHA256_PASS","THREE_REAL_F13",len(source),
          "SOURCE_HASH",sha(folder/FILES[0]))
    print("F16_PENDING_LOCAL_SARAH_VERTEX_AND_UFO_NOT_ALLOWED")
    return summ

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--model",type=Path,default=Path(
        "models/SARAH/ZeeTypeII/ZeeTypeII.m"))
    args=p.parse_args()
    verify(args.directory,args.model)
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Strict F17 *generated* JSON integrity check, not a physical UFO card check.

Checks source exporter complete three F13 IDs and all 7 numeric real/imag
matrix arrays. If a failed Mathematica Export left a truncated artifact,
the local runner archives ONLY that generated F17 file and regenerates it.
No F16 original source or existing validated UFO is ever modified.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
IDS={"F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003"}
SHAPES={"FSARAH":(3,3),"YeSARAH":(3,3),"Ye2SARAH":(3,3),
        "YChen":(3,3),"MixCharged":(3,3),
        "MixCPeven":(2,2),"MixCPodd":(2,2)}
STATUS="F17_F16_SOURCE_EXACT_THREE_COMPLEX_MATRICES_NOT_UFO_PARAM_CARD"

def verify_json(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data,dict) or data.get("status")!=STATUS:
        raise ValueError("Not original F17 source complex export")
    if (set(data.get("candidate_ids",[]))!=IDS or
        len(data["candidate_ids"])!=3 or
        data.get("full_Zee_param_card_validated") is not False):
        raise ValueError("F17 cohort or physics-card claim inconsistent")
    rows=data.get("matrices")
    if not isinstance(rows,list) or len(rows)!=3 or {
        r.get("candidate_id") for r in rows if isinstance(r,dict)}!=IDS:
        raise ValueError("F17 original three physical case set missing")
    for row in rows:
        mats=row.get("matrices_re_im")
        if not isinstance(mats,dict) or set(mats)!=set(SHAPES):
            raise ValueError("Missing extra or wrong complex matrix keys")
        if (row.get("full_Zee_param_card_validated") is not False or
            row.get("ufo_fermion_couplings_checked") is not False):
            raise ValueError("F17 source cannot claim a validated card")
        for key,(n,m) in SHAPES.items():
            matrix=mats[key]
            if (not isinstance(matrix,list) or len(matrix)!=n or
                any(not isinstance(a,list) or len(a)!=m for a in matrix)):
                raise ValueError(f"Nonrectangular matrix {key}")
            for line in matrix:
                for entry in line:
                    if (not isinstance(entry,list) or len(entry)!=2 or
                        any(isinstance(x,bool) or not isinstance(x,(int,float))
                            or not math.isfinite(x) for x in entry)):
                        raise ValueError(f"Symbolic/nonfinite complex entry {key}")
        for name in ("mH1_GeV","mH2_GeV","mA_GeV",
                     "mHeavyNeutral_GeV","vev_GeV",
                     "alpha_rad","beta_rad","gamma_rad"):
            x=row.get(name)
            if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):
                raise ValueError(f"Nonfinite physical scalar {name}")
        lep=row.get("lepton_masses_GeV")
        if (not isinstance(lep,list) or len(lep)!=3 or
            any(isinstance(x,bool) or not isinstance(x,(float,int)) or
                not math.isfinite(x) or x<0 for x in lep)):
            raise ValueError("Lepton masses not original numerical triplet")
    return data

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("input",type=Path)
    args=p.parse_args()
    source=verify_json(args.input)
    print("F17_EXACT_THREE_SOURCE_COMPLEX_JSON_STRUCTURE_PASS",
          len(source["matrices"]), "MATRIX_GROUPS", len(SHAPES))
if __name__=="__main__":main()

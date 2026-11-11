#!/usr/bin/env python3
"""Source-locked SusHi 1.7.0 actual LO ggF/bbH for 16 original Zee H/A spectra.

Identical physics card to the already source-validated D7/F13 SusHi bridge;
only the particular original scalar is changed. Real Type-II quark Yukawas
are checked against native vertices; the charged-singlet Yukawa sector
does NOT enter LO neutral production. No NLO precision is claimed.
"""
from __future__ import annotations
import argparse,hashlib,json,math,subprocess
from pathlib import Path
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.higgs.sushi_bridge import PDF,card as original_card,couplings,blocks
from module14.scan import digest

def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def card_16(name, p, scalar_sha256, state, scale=(1.,1.), member=0, factors=(1.,1.,1.)):
    couplings(p,state)
    if len(scale)!=2 or any(not math.isfinite(x) or x<=0 for x in scale):
        raise ValueError('Positive finite scale multipliers required')
    if not isinstance(member,int) or isinstance(member,bool) or not 0<=member<=50:
        raise ValueError('PDF member outside pinned set')
    if len(factors)!=3 or any(not math.isfinite(x) for x in factors):
        raise ValueError('Finite charm/top/bottom factors required')
    # The central scales are M/2 for ggF and (M,M/4) for 5FS bbH.
    rr,ff=scale
    return f'''# Source certified Zee {name}; scalar SHA256 {scalar_sha256}
Block SUSHI
 1 2
 2 {12 if state=='H' else 21}
 3 0
 4 13000.0
 5 0
 6 0
 7 0
 19 1
 20 0
Block 2HDM
 2
Block SMINPUTS
 1 137.035999084
 2 {1/(math.sqrt(2)*p['v']**2):.16e}
 3 0.135
 4 91.1876
 5 4.183
 6 172.4
 8 1.273
Block MINPAR
 3 {math.tan(p['beta']):.16e}
Block ALPHA
 {p['alpha']+math.pi/2:.16e}
Block MASS
 25 {p['mh1']:.16e}
 35 {p['mh2']:.16e}
 36 {p['ma']:.16e}
Block DISTRIB
 1 0
 2 0
 3 0
 4 0
Block SCALES
 1 {rr*.5:.16e}
 2 {ff*.5:.16e}
 11 {rr:.16e}
 12 {ff*.25:.16e}
 3 0
Block RENORMBOT
 1 0
 4 4.78
Block PDFSPEC
 1 {PDF}.LHgrid
 2 {PDF}.LHgrid
 3 {PDF}.LHgrid
 4 {PDF}.LHgrid
 10 {member}
Block VEGAS
 1 10000
 2 5
 3 0
 4 10000
 5 5
 14 20000
 15 3
 6 0
 7 10000
 8 5
 17 20000
 18 3
 9 0
Block FACTORS
 1 {factors[0]:.16e}
 2 {factors[1]:.16e}
 3 {factors[2]:.16e}
'''



def run(executable:Path,out_dir:Path):
    if out_dir.exists():raise FileExistsError("Refuse overwrite of native SusHi physical receipts")
    if not executable.is_file():raise FileNotFoundError("SusHi 1.7.0 executable not available")
    points=source_points()
    if len(points)!=16 or len({p["id"] for p in points})!=16:
        raise ValueError("Original certified scalar sample not 16 unique source cards")
    out_dir.mkdir()
    results=[]
    for point in points:
        id=point["id"]; physical=point["input_card"]["physical"]
        if digest(point["input_card"])!=point["scalar_sha256"]:
            raise ValueError("Original scalar hash changed")
        for state in ("H","A"):
            basename=f"zee_{id}_{state}_LO_13TeV"
            inp=out_dir/(basename+".in");out=out_dir/(basename+".out");log=out_dir/(basename+".log")
            inp.write_text(card_16(id,physical,point["scalar_sha256"],state))
            with log.open("w") as stream:
                subprocess.run([str(executable),str(inp),str(out)],stdout=stream,stderr=subprocess.STDOUT,
                               check=True,timeout=240)
            data=blocks(out)
            expected=couplings(physical,state)
            for code,key in ((101,"top"),(201,"bottom")):
                if not math.isclose(data["hggsusy"][code],expected[key],rel_tol=2e-8,abs_tol=1e-11):
                    raise ValueError(f"Public SusHi/native Zee {id} {state} Yukawa mismatch")
            rates={tag:{"sigma_pb":float(data[block][1]),
                        "integration_error_pb":float(data[block][101])}
                   for tag,block in (("ggF","sushiggh"),("bbH","sushibbh"))}
            if any(not(math.isfinite(z["sigma_pb"]) and z["sigma_pb"]>=0
                           and math.isfinite(z["integration_error_pb"]) and z["integration_error_pb"]>=0)
                   for z in rates.values()):
                raise ValueError("Unphysical public production rate")
            row={"scalar_id":id,"original_scalar_sha256":point["scalar_sha256"],
                 "state":state,"mass_GeV":float(physical["mh2" if state=="H" else "ma"]),
                 "energy_TeV":13,"QCD_order":"LO","parton_scheme":"5FS",
                 "PDF":PDF,"PDF_member":0,"SusHi_version":"1.7.0",
                 "native_couplings":expected,"rates":rates,
                 "input_sha256":hash_file(inp),"output_sha256":hash_file(out),"log_sha256":hash_file(log),
                 "physical_Higgs_bounds_acceptance":None,"global_acceptance":None}
            results.append(row)
            print("ZEE_SUSHI_NATIVE_16",id,state,"M",row["mass_GeV"],"ggF",rates["ggF"]["sigma_pb"],
                  "bbH",rates["bbH"]["sigma_pb"],"LO_ONLY",flush=True)
    if len(results)!=32:raise ValueError("Not all 16x2 neutral production cards executed")
    report={
        "schema":"zee-16-source-scalar-H_A-13TeV-SusHi-1.7.0-LO-v1",
        "scalars":16,"executed_neutral_states":32,"energy_TeV":13,
        "original_SusHi_LO_reference_scope":"CTB coherent ggF and bbar annihilation with fixed MMHT2014lo68cl",
        "PDF":PDF,"QCD_order":"LO_5FS",
        "NLO_QCD_theory_sigma":None,
        "heavy_H_A_HiggsBounds_exclusion":None,"global_acceptance":None,
        "cases":results,
    }
    (out_dir/"zee-SusHi-16-HA-real-production.json").write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("ZEE_SUSHI_SOURCE_16x2_COMPLETED",len(results),"NO_HEAVY_HIGGS_EXCLUSION",flush=True)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sushi",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    x=p.parse_args()
    run(x.sushi,x.output_dir)
if __name__=="__main__":
    main()

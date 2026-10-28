"""D7 deterministic 32-point NO *development* scan inputs for HTCondor.

No physics gates run here. This is NOT an accepted-parameter distribution:
two strata, a broad mass/angle arm and a quasi-degenerate neutral/heavy arm.
The latter is a hypothesis for efficient scalar-EWPO screening, not a prior.
All generated records are strict nested Module3/Module2/SHA-bound Module1
inputs, derived from the same pinned NO target and inverse-family seed.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import random

from module2.interface import canonical_hash
from module3.interface import validate as validate3
from module9.d7_inputs import seed_input, validate_point, VARIED

STATUS="D7_DEVELOPMENT_SCAN_INPUTS_ONLY"
SEED=20261028
TOTAL=32
SHARDS=4
POINTS_PER_SHARD=TOTAL//SHARDS
ANCESTOR="a39afed7cd0ee7f4358dabdbde32729818f1f909"

def _latin(rng,count,dims):
    out={}
    for key in dims:
        order=list(range(count))
        rng.shuffle(order)
        out[key]=[(i+rng.random())/count for i in order]
    return [{key:out[key][j] for key in dims} for j in range(count)]

def design():
    """32 reproducible finite points, including heavy charged states up to ~2.1 TeV."""
    rng=random.Random(SEED)
    points=[]
    for arm in ("broad","neutral_near_heavy"):
        dims=("light","gap","neutral_h","neutral_a","beta","gamma","alpha","m12")
        for i,u in enumerate(_latin(rng,TOTAL//2,dims)):
            light=250+950*u["light"]
            gap=105+795*u["gap"] if arm=="broad" else 105+495*u["gap"]
            heavy=light+gap
            beta=0.55+0.95*u["beta"]
            gamma=0.2+1.2*u["gamma"]
            if arm=="broad":
                mh2=300+1600*u["neutral_h"]
                ma=300+1600*u["neutral_a"]
                alpha=1.10+.40*u["alpha"]
                m12=20000+280000*u["m12"]
            else:
                mh2=heavy-75+150*u["neutral_h"]
                ma=heavy-75+150*u["neutral_a"]
                alpha=beta-0.08+0.16*u["alpha"]
                m12=57700*(heavy/700.)**2*(0.65+0.7*u["m12"])
            values={"mH1":light,"mH2":heavy,"mh2":max(126.,mh2),
                    "ma":max(1.,ma),"beta":beta,"gamma":gamma,
                    "alpha":alpha,"m12sq":m12}
            if not (0<values["mH1"]<values["mH2"] and
                    values["mH2"]>values["mH1"]+91.1876):
                raise ValueError("Invalid open-cascade construction")
            if any(not math.isfinite(v) for v in values.values()):
                raise ValueError("Invalid design float")
            points.append((f"d7_NO_{arm}_{i:02d}",arm,values))
    if len(points)!=TOTAL or len({x[0] for x in points})!=TOTAL:
        raise ValueError("Not exactly 32 unique design points")
    return points

def make_point(source,identity,physical):
    validate_point(source)
    if not isinstance(physical, dict) or not set(physical) <= set(VARIED):
        raise ValueError("Unsupported D7 scalar variation")
    point=copy.deepcopy(source)
    point["benchmark_id"]=identity
    point["module2_input"]["benchmark_id"]=identity
    wrapper=point["module2_input"]["scalar"]
    wrapper["record"]["benchmark_id"]=identity
    wrapper["record"]["physical"].update(physical)
    wrapper["sha256"]=canonical_hash(wrapper["record"])
    resolved=validate_point(point)
    for key in physical:
        if resolved[key]!=physical[key]:
            raise ValueError("Generator scalar/mass mix mismatch")
    return point

def prepare(seed_json,folder):
    """Create all shards and manifest; refuses to overwrite any prior scan run."""
    src=seed_input(seed_json)
    validate3(src,"input.schema.json")
    folder=Path(folder)
    if folder.exists() and any(folder.iterdir()):
        raise ValueError("Refuse nonempty output directory; never overwrite scan runs")
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"shards").mkdir()
    inventory=[]
    choices=design()
    for n in range(SHARDS):
        records=[]
        for identity,arm,parameters in choices[n*POINTS_PER_SHARD:(n+1)*POINTS_PER_SHARD]:
            inp=make_point(src,identity,parameters)
            records.append({"point_id":identity,"arm":arm,
                 "input_sha256":canonical_hash(inp),"input":inp})
            inventory.append({"point_id":identity,"arm":arm,
                "input_sha256":canonical_hash(inp),
                "scalar_sha256":inp["module2_input"]["scalar"]["sha256"],
                "physical":inp["module2_input"]["scalar"]["record"]["physical"],
                "ordering":"NO","global_zee_acceptance":None})
        path=folder/"shards"/f"part_{n:03d}.jsonl"
        path.write_text("".join(json.dumps(row,allow_nan=False,sort_keys=True)+"\n"
                                 for row in records),encoding="utf-8")
    paths=sorted((folder/"shards").glob("*.jsonl"))
    manifest={"schema_version":"d7-pilot-1.0.0","status":STATUS,
      "ancestor_commit":ANCESTOR,"deterministic_seed":SEED,"total_points":TOTAL,
      "point_count_per_shard":POINTS_PER_SHARD,"shard_count":SHARDS,
      "source_bytes_sha256":hashlib.sha256(seed_json).hexdigest(),
      "source_ordering":"NO","nufit_likelihood":"NOT_EVALUATED",
      "design":"16 broad + 16 neutral-near-heavy developmental LHS; not a physical posterior",
      "shards":[{"name":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                 "points":POINTS_PER_SHARD} for p in paths],
      "points":inventory,"global_zee_acceptance":None,"constraints_complete":False}
    (folder/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True,allow_nan=False)+"\n")
    (folder/"shards.txt").write_text("\n".join(p.name for p in paths)+"\n")
    return manifest

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    args=ap.parse_args()
    m=prepare(args.seed.read_bytes(),args.output_dir)
    print(STATUS,m["total_points"],"points",m["shard_count"],"shards")

if __name__=="__main__":main()

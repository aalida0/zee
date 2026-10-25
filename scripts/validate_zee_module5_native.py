"""Fail-closed structural checker for *raw* native SARAH Module5 vertices.

It validates evidence completeness only, NEVER Wilson matching or 2026
Hamiltonian equivalence. A raw extraction cannot establish Delta C7/C8.
"""
import json
import sys
from pathlib import Path

STATUS = "RAW_VERTICES_EXTRACTED_NOT_MATCHED"

def expected_keys():
    plus={f"plus_{{{k}, {a}, {b}}}" for k in range(1,4) for a in range(1,4) for b in range(1,4)}
    minus={f"minus_{{{k}, {b}, {a}}}" for k in range(1,4) for b in range(1,4) for a in range(1,4)}
    return plus|minus|{"photon_top","photon_bottom","gluon_top","gluon_bottom"}

def check(record):
    if not isinstance(record,dict) or record.get("status") != STATUS:
        raise ValueError("No successful raw SARAH extraction")
    raw=record.get("raw_vertices")
    if not isinstance(raw,dict) or set(raw)!=expected_keys() or record.get("query_count")!=58:
        raise ValueError("Incomplete or unrecognized raw vertex keys")
    if record.get("raw_vertex_keys")!=list(raw):
        raise ValueError("Query inventory does not match actual raw entries")
    if not record.get("sarah_version") or not record.get("math_version"):
        raise ValueError("Software version metadata missing")
    for name,v in raw.items():
        if (not isinstance(v,str) or not v.strip() or v=="{}" or
            "$Aborted" in v or "SARAH`Vertex" in v or "Vertex[" in v or
            "Missing[" in v):
            raise ValueError(f"Unevaluated/unavailable vertex: {name}")
    return {"status":STATUS,"count":58,
            "operator_matching":"NOT_EVALUATED",
            "physical_B_to_Xs_gamma":"NOT_EVALUATED"}

def main():
    if len(sys.argv)!=2:raise SystemExit("Usage: python scripts/validate_zee_module5_native.py FILE.json")
    def pairs_unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError("Duplicate JSON key: "+k)
            d[k]=v
        return d
    r=json.loads(Path(sys.argv[1]).read_text(),object_pairs_hook=pairs_unique)
    print(json.dumps(check(r),sort_keys=True))

if __name__=="__main__":main()

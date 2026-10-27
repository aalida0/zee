"""Tree-level H2^+ -> H1^+ Z *partial width* in the restricted Zee model.

Source: Florentino/Romao/Silva, EPJC 81 (2021) 1148,
https://doi.org/10.1140/epjc/s10052-021-09956-2
Eq. (72), (73), Appendix B.1 Eqs. (B.2), (B.3b,c).

The two charged mass eigenstates mix a weak doublet and a charged
singlet. Normalized off-diagonal gauge vertex:
g_HpjHmkZ[2,1] = -sin(2*gamma)/2
in the paper's conventions. The decay is kinematically open iff
mH2 > mH1 + mZ. This module does not compute competing widths,
branching fractions, production cross sections, or experimental limits.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = "Florentino-Romao-Silva EPJC81(2021)1148 Eq72, Eq73, AppB.1"
STATUS = "TREE_CASCADE_PARTIAL_WIDTH_ONLY"
REQUIRED = frozenset(("mH1_GeV", "mH2_GeV", "mZ_GeV", "mW_GeV", "v_GeV", "gamma_rad"))


def finite(x, name):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError(f"{name} must be finite real")
    return float(x)


def cascade_width(values):
    if not isinstance(values, dict) or set(values) != REQUIRED:
        raise ValueError("Expected exactly the six explicit scalar/EW inputs")
    p = {k: finite(v,k) for k,v in values.items()}
    light, heavy, z, w, vev, gamma = (p[k] for k in
        ("mH1_GeV", "mH2_GeV", "mZ_GeV", "mW_GeV", "v_GeV", "gamma_rad"))
    if min(light,heavy,z,w,vev) <= 0 or not light < heavy or not w < z:
        raise ValueError("Require ordered charged masses, positive scales and mW<mZ")
    if abs(gamma) > math.pi/2:
        raise ValueError("Outside frozen physical gamma convention")
    cw = w/z
    g = 2*w/vev
    offdiagonal = 0.0 if gamma == 0.0 or abs(gamma) == math.pi/2 else -0.5*math.sin(2*gamma)
    gauge_coupling = g/(2*cw)*offdiagonal
    threshold = light+z
    if heavy <= threshold:
        lam_half = 0.0
        width = 0.0
        open_channel = False
    else:
        # Stable positive factorization of sqrt[lambda(M^2,m^2,mZ^2)].
        factors=(heavy-light-z,heavy+light+z,
                 heavy-light+z,heavy+light-z)
        if min(factors) <= 0:
            raise ValueError("Internal phase-space factor error")
        lam_half = math.sqrt(math.prod(factors))
        # Eq. (72) with g_HpjHmkZ[2,1]=-sin(2gamma)/2:
        # g^2/(64*pi*heavy^3*w^2) * offdiag^2 * lambda_half^3.
        width=(g*g/(64*math.pi*heavy**3*w*w)
               *offdiagonal**2*lam_half**3)
        open_channel = True
    if not math.isfinite(width) or width < 0:
        raise ValueError("Nonfinite or negative cascade partial width")
    return {
        "schema_version":"1.0.0","status":STATUS,"source":SOURCE,
        "input":p,
        "normalized_offdiagonal_Z_coupling":offdiagonal,
        "absolute_gauge_vertex_coefficient":abs(gauge_coupling),
        "is_kinematically_open":open_channel,
        "kinematic_threshold_GeV":threshold,
        "kallen_sqrt_GeV2":lam_half,
        "partial_width_GeV":width,
        "branching_fraction":None,
        "total_width_GeV":None,
        "production_cross_section_pb":None,
        "physical_collider_acceptance":None,
        "global_zee_acceptance":None,
        "limitations":[
            "Tree-level on-shell two-body Z channel only; no finite-Z-width or off-shell Z treatment.",
            "Not a branching ratio until all relevant competing modes and full total width are computed.",
            "No pp production rate, PDFs, higher-order corrections, fiducial efficiencies, or detector results.",
            "The off-diagonal Z charged scalar coupling and this formula are already known in the 2021 literature."
        ]
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    if args.input.resolve()==args.output.resolve():
        raise ValueError("Input and output paths must differ")
    raw=args.input.read_bytes()
    def unique_pairs(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError("Duplicate JSON key: "+k)
            d[k]=v
        return d
    obj=json.loads(raw,object_pairs_hook=unique_pairs,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Nonfinite JSON "+x)))
    out=cascade_width(obj)
    out["input_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_name(args.output.name+".tmp")
    tmp.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    tmp.replace(args.output)
    print(STATUS)

if __name__=="__main__":main()

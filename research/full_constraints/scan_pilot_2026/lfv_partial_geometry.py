#!/usr/bin/env python3
"""Local differential rank of the *included* Zee mu-e gamma dipole around
the fully serialized new 2264 neutrino-family benchmark.

The linearized 4x8 real Jacobian is a diagnostic of the 4-real-observable
partial amplitude, NOT a proof of a 4-dimensional physically allowed region.
Omitted LFV structures and other flavor observables are not constraints here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import numpy as np

from research.full_constraints.scan_pilot_2026 import fresh_8d_lfv_pilot as physics

SOURCE = Path(__file__).with_name("2264_fresh_8d_reference.json")
H = 0.001
R = 0.03


def run(output: Path):
    if output.exists():
        raise FileExistsError("Refuse to overwrite rank receipt")
    ref = json.loads(SOURCE.read_text())
    source = ref["optimized_input"]
    ck = source["homogeneous_coefficients"]
    x = np.array(ck["real"] + ck["imag"]) / physics.COEFFICIENT_UNIT
    if np.max(abs(x)) + R >= physics.TRUST_BOX:
        raise ArithmeticError("Original optimized card too close to trust boundary")
    center = physics.evaluate(source, x)
    if not math.isclose(center["partial_BR"],
                        ref["retained_reference"]["mu_to_e_gamma_BR"],
                        rel_tol=1e-9, abs_tol=1e-30):
        raise ArithmeticError("Frozen partial LFV baseline changed")
    amplitude_limit = (
        float(np.linalg.norm(center["amp_components"])) *
        math.sqrt(physics.MEGII_BOUND / center["partial_BR"])
    )
    columns = []
    for j in range(8):
        d = np.zeros(8)
        d[j] = H
        pp = physics.evaluate(source, x+d)["amp_components"]
        mm = physics.evaluate(source, x-d)["amp_components"]
        columns.append((pp-mm)/(2*H*amplitude_limit))
    jac = np.stack(columns, axis=1)
    U, singular, Vt = np.linalg.svd(jac, full_matrices=True)
    tolerance = np.finfo(float).eps * max(jac.shape) * singular[0]
    rank = int((singular>tolerance).sum())
    tested = []
    for name, basis in (("sensitivity", Vt[:4]), ("linearized_nullspace", Vt[4:])):
        for k, d in enumerate(basis):
            plus = physics.evaluate(source, x+R*d)
            minus = physics.evaluate(source, x-R*d)
            tested.append({
                "basis": name, "direction": k,
                "linearized_normalized_response": float(np.linalg.norm(jac@d)),
                "partial_BR_plus": plus["partial_BR"],
                "partial_BR_minus": minus["partial_BR"],
                "both_below_MEGII": bool(
                    max(plus["partial_BR"],minus["partial_BR"]) < physics.MEGII_BOUND
                ),
            })
    if rank < 4:
        raise ArithmeticError("Fewer than four independent retained-dipole directions")
    if not all(z["both_below_MEGII"] for z in tested if z["basis"]=="linearized_nullspace"):
        raise ArithmeticError("One of the declared small null directions exceeds retained limit")
    out = {
        "schema": "zee-2264-8d-4real-partial-dipole-local-jacobian-v1",
        "status": "LOCAL_RETAINED_DIPOLE_DIFFERENTIAL_GEOMETRY_VALIDATED",
        "optimized_input_sha256": ref["optimized_input_sha256"],
        "source_reference_sha256": physics.digest(ref),
        "step_in_dimensionless_coefficient_coordinates": H,
        "step_in_original_homogeneous_coefficients": H * physics.COEFFICIENT_UNIT,
        "test_radius": R, "test_absolute_coefficient_radius": R*physics.COEFFICIENT_UNIT,
        "normalized_jacobian": jac.tolist(),
        "singular_values": singular.tolist(),
        "rank_of_four_by_eight_real_partial_dipole_jacobian": rank,
        "linearized_null_dimension": 8-rank,
        "relative_singular_value_ratio": float(singular[-1]/singular[0]),
        "orthonormal_singular_direction_tests": tested,
        "neutrino_target_frozen": True,
        "scalar_frozen": True,
        "physical_LFV": "UNKNOWN",
        "global_acceptance": None,
        "warning": (
            "Linearized null direction is NOT an LFV constraint-free physical "
            "manifold: missing two-loop terms, mu3e and mu-e conversion remain "
            "outside the optimized 4 real dipole components."
        ),
    }
    output.write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False)+"\n")
    print("PARTIAL_DIPOLE_JACOBIAN_SINGULAR",*[f"{v:.8g}" for v in singular],flush=True)
    print("PARTIAL_DIPOLE_RANK",rank,"NULL",8-rank,
          "CONDITION",float(singular[0]/singular[-1]),flush=True)
    for z in tested:
        print("LOCAL_SVD_DIRECTION",z["basis"],z["direction"],
              "BR+",z["partial_BR_plus"],"BR-",z["partial_BR_minus"],
              "BOTH_SUB",z["both_below_MEGII"],flush=True)
    print("PHYSICAL_LFV UNKNOWN",flush=True)
    return out


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    run(args.output)

if __name__=="__main__":
    main()

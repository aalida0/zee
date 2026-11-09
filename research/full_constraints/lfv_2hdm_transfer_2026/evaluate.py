#!/usr/bin/env python3
"""Neutral 2HDM -> Zee Type-II scalar semileptonic tree transfer.

Compute mu->e scalar-quark four-fermion Wilsons, and a separately labeled,
illustrative nucleon scalar projection. NOT a full mu-e conversion prediction.

Run from repository root:
  python3 -m research.full_constraints.lfv_2hdm_transfer_2026.evaluate
  python3 -m unittest discover -s research/full_constraints/lfv_2hdm_transfer_2026 -p 'test_*.py'

Native action:
  L_Y = -phi * bar(f) [C_f PL + C_f^* PR] f
  L_eff (tree) = + S_L^q (bar e PL mu)(bar q q)
                 + S_R^q (bar e PR mu)(bar q q)
  [S_X^q] = GeV^-2; coefficient of m_mu*m_q in Hou-style Eq.12
            is S_X^q/(m_mu*m_q).
The mu-e-conversion EFT coefficients are NOT independently matched to
the existing FlexibleSUSY nuclear response action by this calculation.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from module2.interface import decode
from module3.core import vertices
from module4.couplings import quarks

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "validation/module12/d12_benchmarks.json"
SOURCE_SHA256 = "f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8"
OLD_LEDGER = ROOT / "research/full_constraints/lfv_lo_closure_2026/WILSON_LEDGER.json"
EXPECTED = (
    "d7_NO_neutral_near_heavy_07/NO/texture_0.0001",
    "d7_NO_neutral_near_heavy_07/IO/texture_0.0001",
    "F13_heavy_0001330/NO/texture_0.001",
    "F13_heavy_0001330/IO/texture_0.001",
)

# Nominal illustrative scalar fractions, cited from Hou-Kumar 2020, PRD 102,
# 115017, Eqs 10-12. NOT a nuclear uncertainty estimate or physical limit.
FRACTIONS = {
    "proton": {"u": 0.024, "d": 0.033, "s": 0.043, "mass": 0.9382720813},
    "neutron": {"u": 0.033, "d": 0.024, "s": 0.043, "mass": 0.9395654133},
}
# These mass choices cancel in C_q/m_q at tree level, and are NOT a
# matched running mass scheme for loop Wilsons.
QUARK_MASSES_GEV = {
    "up": 0.0022, "down": 0.0047, "strange": 0.093,
    "charm": 1.27, "bottom": 4.18, "top": 160.0,
}
LIGHT = {"u": "up", "d": "down", "s": "strange"}
HEAVY = ("charm", "bottom", "top")


def pair(value):
    v = complex(value)
    assert math.isfinite(v.real) and math.isfinite(v.imag)
    return [float(v.real), float(v.imag)]


def read_cards():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("frozen D12 SHA-256 mismatch")
    groups = json.loads(raw)["groups"]
    ids = tuple(g["witnesses"]["low_joint"]["id"] for g in groups)
    if ids != EXPECTED:
        raise RuntimeError(f"unexpected texture cards: {ids}")
    return [g["witnesses"]["low_joint"] for g in groups]


def analytic_doublet_factors(p):
    """Independent Higgs-basis analytic tree formula, GeV^-2.

    q_h^u = (m_u/v)(cos δ-cot β sin δ);
    q_H^u = (m_u/v)(sin δ+cot β cos δ);
    q_h^d = (m_d/v)(cos δ+tan β sin δ);
    q_H^d = (m_d/v)(sin δ-tan β cos δ).
    The off-diagonal lepton neutral vertices are -sin δ D/sqrt2 and
    +cos δ D/sqrt2 for h,H, respectively.
    """
    delta = p["beta"] - p["alpha"]
    s, c, t = math.sin(delta), math.cos(delta), math.tan(p["beta"])
    ah, aH = p["mh1"] ** -2, p["mh2"] ** -2
    common = s * c * (aH - ah)
    u = common + (s*s*ah + c*c*aH)/t
    d = common - t * (s*s*ah + c*c*aH)
    return {"up_type": u, "down_type": d}


def scalar_quark_wilsons(w):
    """Exact h/H/A neutral tree transfer in frozen Yukawa convention.

    Returns coefficient of (bar e P_X mu)(bar q q). The CP-odd A has
    zero scalar q density in the real Type-II quark sector; separate
    pseudoscalar operators are not presented as coherent scalar conversion.
    """
    p = w["module2_input"]["scalar"]["record"]["physical"]
    ml = w["module2_input"]["lepton_masses_GeV"]
    D = decode(w["yukawas"]["D"])
    leptons = vertices(D, p, ml)
    # External chirality on INCOMING muon; D RH rows, LH columns.
    phases = {"L": D[0, 1], "R": D[1, 0].conjugate()}
    independent = analytic_doublet_factors(p)
    type_for = {
        "up": "up_type", "charm": "up_type", "top": "up_type",
        "down": "down_type", "strange": "down_type", "bottom": "down_type",
    }
    per_chirality = {"L": {}, "R": {}}
    signed_by_scalar = {"L": {}, "R": {}}
    max_residual = 0.
    for species, mass in QUARK_MASSES_GEV.items():
        couplings = quarks(mass, species, p)
        for chirality in ("L", "R"):
            terms = {}
            for scalar, (Cl, ms) in leptons.items():
                lep = Cl[0, 1] if chirality == "L" else Cl[1, 0].conjugate()
                # Scalar q density is (bar q PL q + bar q PR q);
                # q Yukawa CP-odd pieces instead multiply bar q gamma5 q.
                terms[scalar] = lep * complex(couplings[scalar]).real / ms**2
            full = sum(terms.values())
            exact_analytic = (
                phases[chirality] / (math.sqrt(2) * p["v"]) *
                independent[type_for[species]] * mass
            )
            scale = max(abs(full), abs(exact_analytic), 1.e-40)
            residual = abs(full-exact_analytic)/scale
            max_residual = max(max_residual, residual)
            if residual > 1.e-11:
                raise ArithmeticError(f"2HDM analytic mismatch {species}/{chirality}: {residual}")
            if abs(terms["A"]) > 1.e-40:
                raise ArithmeticError("CP-odd A generated forbidden scalar density")
            per_chirality[chirality][species] = full / mass
            signed_by_scalar[chirality][species] = {s: pair(v) for s, v in terms.items()}
    return per_chirality, signed_by_scalar, max_residual


def project_to_nucleon(reduced, fractions=FRACTIONS):
    """Leading heavy-quark 2/27 trace-anomaly scalar projection.

    All inputs S^q/m_q are GeV^-3, nucleon coefficients GeV^-2.
    No vector, photon monopole, dipole, Z penguin, pseudoscalar nuclear
    matrix element, 1-loop matching or theory-uncertainty band is claimed.
    """
    out = {"L": {}, "R": {}}
    for ch in out:
        for nuc, data in fractions.items():
            fg = 1-data["u"]-data["d"]-data["s"]
            if not (0. < fg < 1.):
                raise ValueError("invalid hadronic scalar fractions")
            light = sum(data[k]*reduced[ch][sp] for k,sp in LIGHT.items())
            heavy = (2./27.)*fg*sum(reduced[ch][sp] for sp in HEAVY)
            out[ch][nuc] = data["mass"] * (light+heavy)
    return out


def evaluate_card(w):
    p = w["module2_input"]["scalar"]["record"]["physical"]
    reduced, components, residual = scalar_quark_wilsons(w)
    nucleons = project_to_nucleon(reduced)
    return {
        "id": w["id"], "scalar_sha256": w["scalar_sha256"],
        "yukawa_sha256": w["yukawa_sha256"],
        "precision": "complex native scalar-quark matching (2HDM tree h,H,A), CP-conserving Type-II quarks",
        "scalar_quark_C_over_mq_GeV_minus3": {
            ch: {q: pair(v) for q,v in vals.items()} for ch, vals in reduced.items()
        },
        "source_summed_scalar_quark_by_state_GeV_minus2": components,
        "nominal_scalar_nucleon_C_GeV_minus2": {
            ch: {n: pair(v) for n,v in vals.items()} for ch, vals in nucleons.items()
        },
        "typeII_analytic_factors_GeV_minus2": analytic_doublet_factors(p),
        "analytic_vs_frozen_vertex_max_relative_residual": residual,
        "charged_singlet_F_dependence": "ABSENT_EXACTLY_AT_TREE_NEUTRAL",
        "charged_mixing_gamma_dependence": "ABSENT_EXACTLY_AT_TREE_NEUTRAL",
        "physical_muAl_conversion": None,
        "physical_lfv": "UNKNOWN",
    }


def run(*, write=True):
    cards = read_cards()
    results = [evaluate_card(w) for w in cards]
    out = {
        "status": "SOURCE_FORMULA_MATCHED_TREE_SUBSET",
        "scope": "2HDM neutral scalar h/H/A exchange to Type-II quarks, four exact Zee low-texture witnesses",
        "operator": "L_eff = sum_q [S_L^q*(bar e PL mu)+S_R^q*(bar e PR mu)]*(bar q q) + h.c.",
        "operator_units": "S_X^q [GeV^-2]; stored S_X^q/m_q [GeV^-3]",
        "source": [
            "Hou/Kumar PRD102 (2020) 115017 Eq(12) neutral-scalar contact structure",
            "Hou and Kumar EPJC 81 (2021) 1132 Eqs(12-13) conversion scalar normalization",
            "frozen module3/core.py neutral Yukawa and module4/couplings.py Type-II quarks",
        ],
        "nucleon_fractions": FRACTIONS,
        "nucleon_fraction_status": "ILLUSTRATIVE_FIXED_INPUT_NO_UNCERTAINTY",
        "cards": results,
        "missing_uv_operators": [
            "off-shell photon monopole K1",
            "low-q^2 Z penguin",
            "semileptonic vector and box",
            "leading QED/QCD matching and complete RG",
            "pseudoscalar nucleon and spin-dependent response",
            "common signed dipole nuclear convention and all interference",
            "quantified hadronic/nuclear uncertainties",
        ],
        "physical_muAl_conversion": None,
        "physical_lfv": "UNKNOWN",
        "global_acceptance": None,
    }
    if write:
        (HERE/"RESULT.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    return out


if __name__ == "__main__":
    result = run()
    print("Validated source-algebraic 2HDM Type-II scalar semileptonic tree matching on",len(result["cards"]),"cards")
    print("physical_muAl_conversion=null; physical_lfv=UNKNOWN")

#!/usr/bin/env python3
"""F-only charged-photon mu-e conversion vector coefficient (restricted source).

Crivellin et al., Phys Rev D103 (2021) 073002, appendix Eqs A1--A3.
Native charged A1 from lfv_2hdm_photon_2026/CHARGED_RESULT.json.
This is NOT a full LFV rate, and must not be added to other Wilsons yet.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "research/full_constraints/lfv_2hdm_photon_2026/CHARGED_RESULT.json"
ALPHA = 1 / 137.035999084
MUON_GEV = 0.1056583755
AL_OVERLAPS = (0.0161, 0.0173)  # KKO equal-proton/neutron-density benchmark
AL_CAPTURE_GEV = 4.6e-19  # Crivellin et al. Eq (A7)
EXPECTED_IDS = (
    "d7_NO_neutral_near_heavy_07/NO/texture_0.0001",
    "d7_NO_neutral_near_heavy_07/IO/texture_0.0001",
    "F13_heavy_0001330/NO/texture_0.001",
    "F13_heavy_0001330/IO/texture_0.001",
)


def pair(z):
    z = complex(z)
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise ValueError("Nonfinite complex coefficient")
    return [z.real, z.imag]


def z(pair_value):
    if not isinstance(pair_value, (list, tuple)) or len(pair_value) != 2:
        raise ValueError("Expected [real, imag]")
    return complex(pair_value[0], pair_value[1])


def evaluate_card(c, *, alpha=ALPHA):
    """Source Eq (A2) extended to *separate diagonal photon loops* of H1/H2.

    F external left-current only. All D, neutral, Z, box and dipole terms
    omitted, never interpreted as zero physical Wilsons.
    """
    if not (0 < alpha < 1):
        raise ValueError("Unphysical alpha")
    lam = z(c["lam_FdagF"])
    weight = 0.0
    for state_name in ("H1", "H2"):
        state = c["by_state"][state_name]
        mass = state["mass_GeV"]
        singlet = state["singlet_fraction"]
        if not (math.isfinite(mass) and mass > 0 and math.isfinite(singlet)):
            raise ValueError("Unphysical charged scalar input")
        weight += singlet * singlet / mass**2
    if not math.isclose(
        sum(c["by_state"][st]["singlet_fraction"]**2 for st in ("H1", "H2")),
        1.0, rel_tol=2e-12, abs_tol=2e-12
    ):
        raise ValueError("Charged singlet mixing fractions do not sum to unity")

    e2 = 4 * math.pi * alpha
    cu = e2 * (2 / 3) * lam * weight / (288 * math.pi**2)
    cd = e2 * (-1 / 3) * lam * weight / (288 * math.pi**2)
    # Source Eq (A1): same Cu, Cd for quark PL and PR (vector photon).
    gp = 2 * (2 * cu + cd)
    gn = 2 * (cu + 2 * cd)
    a1 = z(c["A1L_F"])
    a2 = z(c["A2R_F"])
    if abs(a1 + lam * weight / (288 * math.pi**2)) > 2e-11 * max(abs(a1), 1e-90):
        raise ValueError("Hundi/native A1 versus Crivellin charged topology mismatch")
    if abs(gp + 2 * e2 * a1) > 2e-11 * max(abs(gp), 1e-90):
        raise ValueError("Proton vector versus native charged A1 mismatch")
    if abs(gn) > 1e-12 * max(abs(gp), 1e-90):
        raise ValueError("Photon should not generate a neutron charge")

    # Eq (9) c_R in the source's action, compared to native e*m_mu/2*A2.
    source_cr = math.sqrt(e2) * MUON_GEV * lam * weight / (384 * math.pi**2)
    native_cr = math.sqrt(e2) * MUON_GEV / 2 * a2
    if abs(source_cr + native_cr) > 2e-11 * max(abs(source_cr), 1e-90):
        raise ValueError("Published/native on-shell dipole magnitude test failed")
    vp, vn = AL_OVERLAPS
    amp = gp * vp + gn * vn
    rate = 4 * MUON_GEV**5 * abs(amp)**2 / AL_CAPTURE_GEV
    return dict(
        id=c["id"],
        F_weight_GeV_minus2=weight,
        Cu_LL=pair(cu), Cu_LR=pair(cu), Cd_LL=pair(cd), Cd_LR=pair(cd),
        gp_F_photon_source=pair(gp), gn_F_photon_source=pair(gn),
        source_Eq9_dipole_cR=pair(source_cr), native_e_mmu_over_2_A2R_F=pair(native_cr),
        Al27_F_photon_vector_ONLY_diagnostic=rate,
        physical_Al27_conversion_rate=None, physical_lfv="UNKNOWN",
        source_dipole_sign_versus_native="OPPOSITE; NO RELATIVE INTERFERENCE CLAIM",
    )


def evaluate(source=INPUT):
    data = json.loads(Path(source).read_text())
    if data.get("status") != "CHARGED_MASSLESS_NEUTRINO_PHOTON_SOURCE_TRANSFER":
        raise ValueError("Unexpected upstream charged source status")
    if data.get("full_common_K1") is not None or data.get("physical_lfv") != "UNKNOWN":
        raise ValueError("Do not reinterpret a complete Wilson as an F-only subset")
    cards = data["cards"]
    if tuple(c["id"] for c in cards) != EXPECTED_IDS:
        raise ValueError("Not the source-hashed four D7/F13 low_joint cards")
    return dict(
        status="CHARGED_F_SOURCE_MATCHED_PHOTON_VECTOR_PARTIAL_ONLY",
        source="Crivellin et al. PRD103 (2021) 073002, Appendix A1--A3",
        assumptions="F-only photon vector, separate physical H1/H2 loops, massless nu",
        Al27_overlap_source="KKO equal-density table; Vp=.0161 Vn=.0173",
        Al27_capture_source="Crivellin Eq A7, 4.6e-19 GeV",
        physical_lfv="UNKNOWN", global_acceptance=None,
        physical_Al27_conversion_rate=None,
        cards=[evaluate_card(c) for c in cards],
    )


if __name__ == "__main__":
    out = evaluate()
    for c in out["cards"]:
        print(c["id"], "F-photon vector-only Al27 diagnostic:",
              "%.8e" % c["Al27_F_photon_vector_ONLY_diagnostic"])
    print("PHYSICAL_LFV=UNKNOWN: complete operator basis/sign interference absent")

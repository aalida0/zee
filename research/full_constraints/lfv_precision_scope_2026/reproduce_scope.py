#!/usr/bin/env python3
"""Read-only reproducibility check of four-card F-only one-loop LFV scales.

No new loop amplitude is calculated. This is direct arithmetic from frozen
Module3's LO charged-singlet formula and the source-hashed D12 witnesses.
Run: python3 research/full_constraints/lfv_precision_scope_2026/reproduce_scope.py
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
D12 = ROOT / "validation/module12/d12_benchmarks.json"
EXPECTED_D12_SHA = "f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8"
AUDIT = ROOT / "research/full_constraints/lfv/TEXTURE_COUPLING_AUDIT.json"
OUTPUT = HERE / "SCOPE_DIAGNOSTICS.json"


def close(a: float, b: float, *, relative: float = 3e-12) -> None:
    assert math.isfinite(a) and math.isfinite(b), (a, b)
    assert abs(a - b) <= relative * max(abs(a), abs(b), 1e-40), (a, b)


def complex_matrix(value):
    return [[complex(re, im) for re, im in zip(r, i, strict=True)]
            for r, i in zip(value["real"], value["imag"], strict=True)]


def main():
    raw = D12.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_D12_SHA, "Original D12 SHA mismatch"
    source = json.loads(raw)
    audit = json.loads(AUDIT.read_text())
    saved = json.loads(OUTPUT.read_text())
    cards = audit["cards"]
    assert len(cards) == len(source["groups"]) == len(saved["cards"]) == 4
    limit = saved["mu_e_gamma_norm_limit_90CL_GeV_minus2"]
    close(limit, 1.3677858240837514e-12)
    checked = 0
    for group, record, published in zip(source["groups"], cards, saved["cards"], strict=True):
        low = group["witnesses"]["low_joint"]
        assert low["id"] == record["id"] == published["id"]
        assert low["yukawa_sha256"] == record["yukawa_sha256"] == published["yukawa_sha256"]
        F = complex_matrix(low["yukawas"]["F"])
        assert len(F) == len(F[0]) == 3
        FF_em = sum(F[k][0].conjugate() * F[k][1] for k in range(3))
        close(abs(FF_em), record["FdagF_em"]["abs"])
        close(abs(FF_em), published["FdagF_e_mu_abs"])
        p = low["module2_input"]["scalar"]["record"]["physical"]
        assert (p["mH1"], p["mH2"]) == tuple(published["charged_masses_GeV"])
        close(p["gamma"], published["gamma_rad"])
        w = math.sin(p["gamma"])**2/p["mH1"]**2 + math.cos(p["gamma"])**2/p["mH2"]**2
        close(w, published["singlet_propagator_weight_GeV_minus2"])
        assert w > 0
        # Frozen module3/core.py::dipole_ledger H1_F and H2_F,
        # with electron/muon daughter-mass suppression of C_L.
        CR = abs(FF_em) * w / (192 * math.pi**2)
        m_e, m_mu = low["module2_input"]["lepton_masses_GeV"][:2]
        CL = CR * m_e/m_mu
        close(CR, published["CR_F_only_abs_GeV_minus2"])
        close(math.hypot(CL, CR), CR, relative=1.5e-5)
        close(limit/CR, published["critical_enhancement_factor_to_mu_gamma_limit_using_F_only"])
        close(CR/record["retained_norm"], published["F_only_abs_over_saved_retained_total_norm"])
        assert record["retained_norm"] < limit and published["physical_exclusion"] is None
        assert published["status"] == "DIAGNOSTIC_NOT_A_BOUND"
        checked += 1
    assert saved["physical_lfv"] == "UNKNOWN" and saved["global_acceptance"] is None
    print(f"PASS {checked} frozen source-hashed F-only one-loop scope diagnostics")
    print("No two-loop coefficient, model remainder bound, or physical exclusion calculated.")


if __name__ == "__main__":
    main()

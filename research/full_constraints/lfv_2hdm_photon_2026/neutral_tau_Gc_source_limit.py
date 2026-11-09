#!/usr/bin/env python3
"""Two-source consistency check for Zee neutral-tau off-shell photon monopole.

Chowdhury & Nasri, JHEP 12(2015)040, Eqs.(3.11), (B.4):
G_c(x) for a charged internal fermion and neutral scalar.
Herrero-Garcia et al., JHEP04(2017)130, Eq.(3.25):
restricted neutral internal-tau leading small-x term.

This module ONLY compares the universal small-x kernel and computes
a finite-x tau-kernel *candidate correction* under zero-external-momentum
assumptions. It does not produce a complete common Zee K1 or physical rate.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "RESULT.json"
MTAU_GEV = 1.77686
ALPHA_EM = 1 / 137.035999084


def pair(z: complex):
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise ValueError("nonfinite complex coefficient")
    return [float(z.real), float(z.imag)]


def z(value):
    if len(value) != 2:
        raise ValueError("expected [real, imag]")
    return complex(float(value[0]), float(value[1]))


def gc_kernel(x):
    """2015 Eq.(B.4); use mpmath only near x=1 if eventually needed.

    This fixed-card task has x < 3e-4, where direct double precision
    is numerically well-conditioned. Reject cancellation region explicitly.
    """
    if not (math.isfinite(x) and 0 < x < .05):
        raise ValueError("This implementation only covers tau/heavy-scalar x<0.05")
    return (
        16 - 45*x + 36*x*x - 7*x**3 + 6*(2-3*x)*math.log(x)
    )/(6*(1-x)**4)


def gc_asymptotic(x):
    if not (math.isfinite(x) and x > 0):
        raise ValueError("x must be positive finite")
    return (16 + 12*math.log(x))/6


def herrero_gamma_kernel_prefactor(m_tau, m_scalar, alpha=ALPHA_EM):
    """2017 Eq(3.25): coefficient of ordered neutral Yukawa product."""
    x = (m_tau/m_scalar)**2
    return -alpha/(18*math.pi*m_scalar**2)*(4+3*math.log(x))


def common_asymptotic_identity(m_tau, m_scalar, alpha=ALPHA_EM):
    """Algebraic source-kernel identity; not a signed native-operator bridge.

    -e²/(48π²mphi²) Gc_asym(x) equals the scalar prefactor of 2017
    gLV/gRV. The original 2015 A_ND^c has a different charged-fermion
    electric charge and distinct amplitude convention; do not identify
    full K1 without a source matching.
    """
    x = (m_tau/m_scalar)**2
    e2 = 4*math.pi*alpha
    lhs = -e2*gc_asymptotic(x)/(48*math.pi**2*m_scalar**2)
    rhs = herrero_gamma_kernel_prefactor(m_tau, m_scalar, alpha)
    return lhs, rhs


def recalculate_card(card, m_tau=MTAU_GEV):
    left = right = 0j
    left_2017 = right_2017 = 0j
    details = {}
    for name in ("h", "H", "A"):
        scalar = card["by_scalar"][name]
        mass = float(scalar["mass_GeV"])
        x = (m_tau/mass)**2
        gc = gc_kernel(x)
        g0 = gc_asymptotic(x)
        factor = gc/g0
        lhs, rhs = common_asymptotic_identity(m_tau, mass)
        assert math.isclose(lhs, rhs, rel_tol=5e-15, abs_tol=0)
        lv0 = z(scalar["gLV_GeV_minus2"])
        rv0 = z(scalar["gRV_GeV_minus2"])
        lv1 = lv0*factor
        rv1 = rv0*factor
        left += lv1
        right += rv1
        left_2017 += lv0
        right_2017 += rv0
        details[name] = dict(
            mass_GeV=mass, x_tau=x,
            Gc_source_2015=gc, Gc_small_x_analytic=g0,
            ratio_full_kernel_to_small_x=factor,
            per_scalar_relative_correction=factor-1,
            source2017_gLV=pair(lv0), source2017_gRV=pair(rv0),
            finite_x_kernel_candidate_gLV=pair(lv1),
            finite_x_kernel_candidate_gRV=pair(rv1),
            prefactor_asymptotic_source_residual=abs(lhs-rhs)/max(abs(rhs),1e-100),
        )
    ref_l=z(card["gLV_source_tau_neutral_GeV_minus2"])
    ref_r=z(card["gRV_source_tau_neutral_GeV_minus2"])
    for value, source_ref in ((left_2017,ref_l),(right_2017,ref_r)):
        if abs(value-source_ref)>2e-12*max(abs(source_ref),1e-100):
            raise ArithmeticError("2017 source by-scalar sum does not reproduce original")
    return dict(
        id=card["id"], scalars=details,
        gLV_2017_tau_only_source=pair(left_2017),
        gRV_2017_tau_only_source=pair(right_2017),
        gLV_tau_only_finite_x_kernel_candidate=pair(left),
        gRV_tau_only_finite_x_kernel_candidate=pair(right),
        relative_tau_L_kernel_shift=abs(left-left_2017)/max(abs(left_2017),1e-100),
        relative_tau_R_kernel_shift=abs(right-right_2017)/max(abs(right_2017),1e-100),
        physical_mu3e_BR=None, physical_muAl_conversion=None,
        full_common_K1=None, physical_lfv="UNKNOWN",
    )


def evaluate(source=SOURCE):
    data=json.loads(Path(source).read_text())
    if data.get("status") != "RESTRICTED_2HDM_TAU_NEUTRAL_OFFSHELL_PHOTON":
        raise ValueError("Unexpected upstream restricted tau source")
    if data.get("physical_lfv") != "UNKNOWN":
        raise ValueError("Unexpected upstream physics closure")
    cards=data["cards"]
    if len(cards)!=4:
        raise ValueError("Four frozen source-hashed witness cards required")
    rows=[recalculate_card(c) for c in cards]
    return dict(
        status="INDEPENDENT_2015_2017_TAU_KERNEL_MATCH__FINITE_X_CANDIDATE_ONLY",
        source_2015="Chowdhury-Nasri JHEP12(2015)040 Eqs 3.11 B.4; charged internal fermion + neutral scalar",
        source_2017="Herrero-Garcia et al JHEP04(2017)130 Eq 3.25; neutral tau only",
        scope="common asymptotic loop-function structure, not complete gauge-invariant neutral K1 or full physical rate",
        limitations=[
            "2015 source charged-fermion representation, electric charge and exact source-action basis require explicit transfer to the Zee charged lepton",
            "different Yukawa/chirality contractions and scalar CP signs not independently derived beyond original 2017 restricted source",
            "electron and muon loops cannot be obtained by inserting m_e or m_mu in the small-q² limit without checking external invariant hierarchy",
            "wavefunction terms, off-shell Ward identity, matching to native K1, Z and boxes remain open",
            "finite-x candidate correction is not a bound on missing photon amplitude"
        ],
        cards=rows,physical_lfv="UNKNOWN",global_acceptance=None,
        full_common_K1=None,mu3e_BR=None,muAl_conversion=None
    )


if __name__=="__main__":
    out=evaluate()
    for row in out["cards"]:
        print(row["id"],
              "tau-only candidate finite-x change (L,R) =",
              "%.8e"%row["relative_tau_L_kernel_shift"],
              "%.8e"%row["relative_tau_R_kernel_shift"])
    print("FULL_K1=UNKNOWN; PHY_LFV=UNKNOWN")

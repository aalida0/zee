"""Synthetic harness tests only; actual HyperIso NLO execution is Gate C2's job."""
import copy
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module5.hyperiso_patch_contract import make_contract
from module5.bsgamma_lo import compute
from module5.bsgamma_matching_accuracy import evaluate, STATUS, EXPECTED_UPSTREAM

M_T=163.96892236746697
BETA=math.atan(5.3)
PHYS={"mH1_GeV":550.,"mH2_GeV":900.,"beta_rad":BETA,
      "gamma_rad":1.09,"mt_MSbar_GeV":M_T,"matching_scale_GeV":160.}

def mock_witness(phys=PHYS):
    """STRUCTURAL fake, never to be published as actual upstream evidence."""
    states=[]
    for m in (phys["mH1_GeV"],phys["mH2_GeV"]):
        o=compute(m,m,phys["beta_rad"],0.,phys["mt_MSbar_GeV"],160.)
        states.append({"mH_GeV":m,"C7_LO":o["delta_C7_LO_at_matching_scale"],
                       "C8_LO":o["delta_C8_LO_at_matching_scale"],
                       "C4_NLO_raw":0.12,"C7_NLO_raw":-0.25,"C8_NLO_raw":-0.40,
                       "C1_to_C6_LO_zero":True})
    return {"schema_version":"1.0.0","upstream_commit":EXPECTED_UPSTREAM,
            "source_status":"EXECUTED_HYPERISO_UNMODIFIED",
            "normalization":"C_0_PLUS_ALPHA_S_OVER_4PI_TIMES_C_1",
            "binary_sha256":"a"*64,"source_LHA_sha256":"b"*64,"runtime_log_sha256":"c"*64,
            "qmatch_GeV":160.,"mt_MSbar_at_qmatch_GeV":phys["mt_MSbar_GeV"],
            "tan_beta":math.tan(phys["beta_rad"]),"alpha_s_at_qmatch":0.108,
            "unweighted_native_states":states}

class MatchingAccuracyMathTests(unittest.TestCase):
    def test_weighted_NLO_and_alpha_s_factor(self):
        r=evaluate(make_contract(PHYS),mock_witness())
        self.assertEqual(r["status"],STATUS)
        a=0.108/(4*math.pi)
        n=r["matching_coefficients"]["NLO_shift_times_alpha_s_over_4pi"]
        self.assertAlmostEqual(n["DeltaC4"],0.12*a,places=15)
        self.assertAlmostEqual(n["DeltaC7"],-0.25*a,places=15)
        self.assertAlmostEqual(n["DeltaC8"],-0.40*a,places=15)
        self.assertIsNone(r["physical_BR"])
        self.assertIsNone(r["global_zee_acceptance"])
        self.assertEqual(r["nonlinear_BSM_curvature"],"NOT_EVALUATED")

    def test_signed_LO_frozen_sum(self):
        r=evaluate(make_contract(PHYS),mock_witness())
        c=make_contract(PHYS)
        for key in ("C7","C8"):
            self.assertAlmostEqual(r["matching_coefficients"]["LO"]["Delta"+key],
                                   c["coefficients"][key]["real"],places=14)
        self.assertNotEqual(r["2026_Eq4_matching_dipole_sensitivity_in_units_1e_minus4"]["NLO_matching_dipole_only_increment"],0)

    def test_state_exchange_is_invariant_for_mass_dependent_NLO(self):
        witness=mock_witness()
        witness["unweighted_native_states"][0]["C7_NLO_raw"]=-0.27
        witness["unweighted_native_states"][1]["C7_NLO_raw"]=-0.49
        before=evaluate(make_contract(PHYS),witness)
        swapped={**PHYS,"mH1_GeV":900.,"mH2_GeV":550.,"gamma_rad":math.pi/2-1.09}
        flipped=copy.deepcopy(witness)
        flipped["unweighted_native_states"].reverse()
        after=evaluate(make_contract(swapped),flipped)
        for k in ("C7_LO","C8_LO","C7_NLO_raw","C8_NLO_raw"):
            self.assertAlmostEqual(before["matching_coefficients"]["LO" if k.endswith("LO") else "NLO_raw_unmultiplied"]["Delta"+k.split("_")[0]],
                after["matching_coefficients"]["LO" if k.endswith("LO") else "NLO_raw_unmultiplied"]["Delta"+k.split("_")[0]],places=13)

    def test_fail_closed_provenance_scale_scheme_and_coefficients(self):
        original=mock_witness();contract=make_contract(PHYS)
        changes=(
            lambda d:d.__setitem__("source_status","NOT_RUN"),
            lambda d:d.__setitem__("upstream_commit","bad"),
            lambda d:d.__setitem__("normalization","ALPHA_S_ALREADY_MULTIPLIED"),
            lambda d:d.__setitem__("binary_sha256",""),
            lambda d:d.__setitem__("qmatch_GeV",81),
            lambda d:d.__setitem__("mt_MSbar_at_qmatch_GeV",163.),
            lambda d:d.__setitem__("tan_beta",1.),
            lambda d:d.__setitem__("alpha_s_at_qmatch",float("nan")),
            lambda d:d["unweighted_native_states"][0].__setitem__("C7_LO",0.),
            lambda d:d["unweighted_native_states"][0].__setitem__("C1_to_C6_LO_zero",False),
            lambda d:d["unweighted_native_states"][0].__setitem__("C4_NLO_raw",float("inf")),
            lambda d:d["unweighted_native_states"].pop()
        )
        for change in changes:
            w=copy.deepcopy(original);change(w)
            with self.subTest(change=str(change)),self.assertRaises(ValueError):
                evaluate(contract,w)

    def test_invalid_contract(self):
        contract=make_contract(PHYS)
        for change in (lambda c:c["coefficients"]["C7"].__setitem__("real",0.),
                       lambda c:c["input"].__setitem__("gamma_rad",0.),
                       lambda c:c.__setitem__("status","ZEE_ALLOWED")):
            v=copy.deepcopy(contract);change(v)
            with self.assertRaises(ValueError):evaluate(v,mock_witness())

if __name__=="__main__":unittest.main()

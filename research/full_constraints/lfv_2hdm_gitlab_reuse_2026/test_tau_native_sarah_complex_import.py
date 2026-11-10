import json
import math
import unittest

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_native_sarah_complex_import import (
    validate, REQUIRED_ORIGIN, CHANNELS, M_TAU, H_BAR, TAU_LIFETIME,
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_radiative_threebody_diagnostic import GATE


def synthetic_fixture():
    gate=json.loads(GATE.read_text())
    norm=gate["alphaEM_for_native"]*M_TAU**5/(4*(H_BAR/TAU_LIFETIME))
    rows=[]
    for x in gate["cards"]:
        channels={}
        for channel in CHANNELS:
            br=x["native_one_loop_BR_"+channel]
            amp=math.sqrt(br/norm)
            channels[channel]={"K2L":[amp,0.0],"K2R":[0.0,0.0],
                               "native_source_BR":br}
        rows.append({"card":x["card"],"channels":channels})
    return {"source_origin":REQUIRED_ORIGIN,
            "fortran_sha256":gate["native_original_Fortran_sha256"],
            "compiler_command":gate["source_compile"],
            "lepton_order":["e","mu","tau"],
            "native_K2_convention":"K2L=-OA2L/(2*e*m_parent);K2R=-OA2R/(2*e*m_parent)",
            "cards":rows}


class NativeInputContractTests(unittest.TestCase):
    def test_synthetic_norm_only_input_never_source_certified(self):
        x=validate(synthetic_fixture())
        self.assertEqual(len(x["cards"]),4)
        self.assertFalse(x["input_phases_independently_verified"])
        self.assertFalse(x["original_fortran_executed_in_this_validation"])
        self.assertEqual(x["physical_lfv"],"UNKNOWN")
        self.assertIsNone(x["global_acceptance"])

    def test_undetectable_phase_replacement_not_false_certified(self):
        a=synthetic_fixture()
        a["cards"][0]["channels"]["tauegamma"]["K2L"]=[0.,a["cards"][0]["channels"]["tauegamma"]["K2L"][0]]
        x=validate(a)
        self.assertFalse(x["cards"]["D7_NO"]["tauegamma"]["can_phase_be_verified_from_rate_alone"])

    def test_fail_source_mismatch_and_missing_channel(self):
        for badcase in ("hash","compiler","origin","channel","massnorm","sourceBR"):
            p=synthetic_fixture()
            v=p["cards"][0]["channels"]["tauegamma"]
            if badcase=="hash":p["fortran_sha256"]["generated"]="f"*64
            if badcase=="compiler":p["compiler_command"]="unverified"
            if badcase=="origin":p["source_origin"]="invented"
            if badcase=="channel":del p["cards"][0]["channels"]["taumugamma"]
            if badcase=="massnorm":v["K2L"][0]*=1.1
            if badcase=="sourceBR":v["native_source_BR"]*=1.1
            with self.assertRaises(ValueError):validate(p)

    def test_reject_nonfinite_and_wrong_orders(self):
        for badcase in ("nan","missing_card","wrong_order","wrong_k2"):
            p=synthetic_fixture()
            if badcase=="nan":p["cards"][0]["channels"]["tauegamma"]["K2L"][0]=float("nan")
            if badcase=="missing_card":p["cards"].pop()
            if badcase=="wrong_order":p["lepton_order"]=["mu","e","tau"]
            if badcase=="wrong_k2":p["native_K2_convention"]="unverified"
            with self.assertRaises(ValueError):validate(p)


if __name__=="__main__":
    unittest.main()

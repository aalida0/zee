"""Tests for coherent candidate provenance and non-exclusion semantics.

Mocks isolate orchestration; a **real** end-to-end run is required by AGENTS.
"""
import copy
import json
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module6.coherent_pilot import pilot,STATUS,SOURCE_TOP_MS_160,LHA_SOURCE_SHA256

def source():
    return json.loads((ROOT/"module3/example.json").read_text())

def fake_scalar(record):
    return {"benchmark_id":record["benchmark_id"],
            "status":"SCALAR_PIPELINE_UNKNOWN",
            "global_zee_acceptance":None,
            "gates":{"bfb":{"assessment":"PASS","status":"PASS"},
                     "vacuum":{"assessment":"UNKNOWN","status":"UNKNOWN"}}}

def fake_lfv(record):
    channels=("mu_to_e_gamma","tau_to_e_gamma","tau_to_mu_gamma")
    return {"benchmark_id":record["benchmark_id"],
            "status":"SCOPED_LFV_COMPUTED","global_zee_acceptance":None,
            "COMPLETE_LFV":False,
            "gates":{"full_lfv":"NOT_EVALUATED"},
            "observables":{k:{"partial_BR":1e-12,"physical_status":"SCALAR_ONE_LOOP_APPROXIMATION",
                              "experimental_comparison":"NOT_EVALUATED"} for k in channels}}

def execute(inp=None):
    with patch("module6.coherent_pilot.scalar_evaluate",side_effect=fake_scalar),patch(
         "module6.coherent_pilot.lfv_evaluate",side_effect=fake_lfv):
        return pilot(inp if inp is not None else source(),SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)

class PilotTests(unittest.TestCase):
    def test_coherent_and_explicitly_incomplete(self):
        out=execute()
        self.assertEqual(out["status"],STATUS)
        self.assertEqual(out["ordering"],"NO")
        self.assertIsNone(out["global_zee_acceptance"])
        self.assertFalse(out["constraints_complete"])
        self.assertFalse(out["neutrino_lfv"]["COMPLETE_LFV"])
        self.assertEqual(out["bsgamma"]["flavor_classification"],"UNCLASSIFIED")
        self.assertEqual(out["bsgamma"]["nonlinear_reliability"],"UNKNOWN")
        self.assertEqual(out["neutrino_lfv"]["module4_Barr_Zee_and_W_completion"],"NOT_EVALUATED")
        self.assertEqual(out["scalar"]["global_vacuum_certification"],"NOT_ESTABLISHED")

    def test_derives_charge_masses_from_same_bound_scalar_record(self):
        inp=source()
        out=execute(inp)
        self.assertEqual(out["provenance"]["bound_scalar_sha256"],inp["module2_input"]["scalar"]["sha256"])
        self.assertEqual(out["benchmark_id"],inp["benchmark_id"])
        self.assertNotEqual(out["bsgamma"]["delta_C7"],0.)

    def test_tampered_scalar_sha_rejected(self):
        inp=source()
        inp["module2_input"]["scalar"]["record"]["physical"]["mH1"]=600.
        with self.assertRaises(ValueError): execute(inp)

    def test_reject_bad_top_mass_or_lha(self):
        with patch("module6.coherent_pilot.scalar_evaluate",side_effect=fake_scalar), patch(
            "module6.coherent_pilot.lfv_evaluate",side_effect=fake_lfv):
            for mass, sha in ((163.,LHA_SOURCE_SHA256),
                              (SOURCE_TOP_MS_160,"0"*64),
                              (True,LHA_SOURCE_SHA256)):
                with self.assertRaises(ValueError):pilot(source(),mass,sha)

    def test_reject_unexpected_full_lfv_claim(self):
        bad=fake_lfv(source());bad["COMPLETE_LFV"]=True
        with patch("module6.coherent_pilot.scalar_evaluate",side_effect=fake_scalar), patch(
            "module6.coherent_pilot.lfv_evaluate",return_value=bad):
            with self.assertRaises(ValueError):pilot(source(),SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)

if __name__=="__main__":unittest.main()

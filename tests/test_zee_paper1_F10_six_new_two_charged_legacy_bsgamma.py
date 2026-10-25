#!/usr/bin/env python3
"""F10 truth contract and same-kernel ratio tests; no mocked test is physics."""
from __future__ import annotations
import csv,json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"scripts"))
import zee_paper1_F10_six_new_two_charged_legacy_bsgamma as F
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import digest
class TestF10(unittest.TestCase):
    def test_truth_contract(self):
        self.assertIn("NOT_EXCLUSION",F.STATUS)
        self.assertEqual(len(F.MISSING),4)
        self.assertTrue(any("NNLO" in v for v in F.MISSING))
    def test_six_numerical_mocked_source_comparator(self):
        input=[]
        reference={}
        for i in range(6):
            name=f"B4_p{i}"
            input.append(dict(id=name,mH1=str(250+i*10),
                              mH2=str(700+i*5),gamma="1.1",tanbeta="5.6"))
            reference[name]=dict(
                nonleptonic_cascade_proxy_NOT_pb=".5",
                flavor_corrected_included_cascade_proxy_NOT_pb=".49",
                partial_LFV_max_ratio_NOT_CL=".0001")
        def source(_,m1,m2,g,t):
            self.assertEqual(t,5.6)
            return .000385 if m1!=m2 else .000370
        result=F.evaluate(input,reference,None,.000338,source_br=source)
        self.assertEqual(len(result),6)
        self.assertAlmostEqual(result[0]["cascade_width_retention"],.98)
        self.assertAlmostEqual(result[0][
            "Zee_to_TypeII670_legacy_NP_shift_ratio_NOT_CL"],
            (.000385-.000338)/(.000370-.000338))
        self.assertIsNone(result[0]["physical_full_Zee_allowed_or_excluded"])
        self.assertIsNone(result[0]["hadronic_signal_rate_pb"])
    def test_source_scan_rejects_wrong_status_and_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            (d/"summary.json").write_text(json.dumps({
                "status":"SIMULATED_SUCCESS",
                "modern_model_complete_constraints_passed":None,
                "candidate_file_SHA256":{}}))
            with self.assertRaises(ValueError):
                F.read_scan(d)
            (d/"summary.json").write_text(json.dumps({
                "status":"PAPER1_ACTUAL_SCALAR_NEUTRINO_PARTIAL_LFV_CASCADE_PILOT_NOT_ALLOWED",
                "modern_model_complete_constraints_passed":None,
                "candidate_file_SHA256":{}}))
            with self.assertRaises(FileNotFoundError):
                F.read_scan(d)
    def test_source_read_checks_exact_six_and_matched_point_files(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            scalar=[]
            ranked=[]
            for i in range(6):
                k=f"B4_{i:05d}"
                scalar.append(dict(id=k,mH1=300+i,mH2=700+i,
                                   gamma=1.089,tanbeta=5.6,
                                   candidate_status="SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"))
                ranked.append(dict(candidate_id=k,mH1_GeV=300+i,
                                   mH2_GeV=700+i,gamma=1.089,
                                   fully_allowed="",nonleptonic_cascade_proxy_NOT_pb=.5,
                                   flavor_corrected_included_cascade_proxy_NOT_pb=.495,
                                   partial_LFV_max_ratio_NOT_CL=.001))
                (d/f"point_{i+1:02d}_NOT_ALLOWED.json").write_text(
                    json.dumps({"scalar":{"id":k},
                       "full_Zee_allowed_or_excluded":None,
                       "flavor":{"model_allowed_or_excluded":None}}))
            for name,rows in ((F.SCALAR,scalar),(F.RANKED,ranked)):
                with (d/name).open("w",newline="") as ff:
                    w=csv.DictWriter(ff,fieldnames=list(rows[0]))
                    w.writeheader();w.writerows(rows)
            summary={"status":
                    "PAPER1_ACTUAL_SCALAR_NEUTRINO_PARTIAL_LFV_CASCADE_PILOT_NOT_ALLOWED",
                    "modern_model_complete_constraints_passed":None,
                    "candidate_file_SHA256":{name:digest(d/name) for name
                                             in (F.SCALAR,F.RANKED)}}
            (d/"summary.json").write_text(json.dumps(summary))
            (d/"manifest.json").write_text(json.dumps({
                "status":summary["status"],
                "summary_SHA256":digest(d/"summary.json")}))
            data,join,p=F.read_scan(d)
            self.assertEqual(len(data),6)
            self.assertEqual(len(join),6)
            self.assertIn("scan_summary_SHA256",p)
            (d/"point_03_NOT_ALLOWED.json").write_text(
                json.dumps({"scalar":{"id":"WRONG"},"flavor":{}}))
            with self.assertRaises(ValueError):
                F.read_scan(d)
if __name__=="__main__":unittest.main()

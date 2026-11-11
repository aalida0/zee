"""Strict source-accounting regression tests for stratified Zee scans.

All fixtures in this test module are deliberately synthetic. They are used
to check deterministic arm selection and the accounting of UNKNOWN, not to
manufacture a physics acceptance percentage.
"""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research.full_constraints.pheno_paper_2026 import scan_accounting as m


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


class TestZeeScalarScanAccounting(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.config={
            "sampling_mode":"correlated_heavy_v1",
            "seed":20261112,
            "count":12,
            "arms":[
                {"name":"sub_TeV","weight":3,"ranges":{"mH2":[500,1000]}},
                {"name":"production_window","weight":5,"ranges":{"mH2":[1000,1350]}},
                {"name":"broad_control","weight":2,"ranges":{"mH2":[500,2200]}}
            ]
        }
        self.config_path=self.root/"config.json"
        self.config_path.write_text(json.dumps(self.config))
        self.manifest_path=self.root/"manifest.jsonl"
        self.worker_path=self.root/"worker.jsonl"
        self.config_sha=canonical_hash(self.config)
        self.manifest=[]
        self.worker=[]
        schedule=["sub_TeV"]*3+["production_window"]*5+["broad_control"]*2
        labels=["PASS","FAIL","UNKNOWN","PASS","FAIL","PASS","UNKNOWN","ERROR","PASS","UNKNOWN"]
        for i in range(12):
            arm=schedule[i%len(schedule)]
            scalar={"benchmark_id":f"test_{i}"}
            rec={
                "id":i,
                "arm":arm,
                "config_sha256":self.config_sha,
                "scalar_sha256":canonical_hash(scalar),
                "scalar":scalar,
            }
            self.manifest.append(rec)
            result=labels[i%len(labels)]
            gates={
                name:{"assessment":"PASS"} for name in
                ("reconstruction","bfb","unitarity","ewpo","vacuum")
            }
            if result=="UNKNOWN":gates["vacuum"]["assessment"]="UNKNOWN"
            if result=="FAIL":gates["bfb"]["assessment"]="FAIL"
            if result=="ERROR":gates["reconstruction"]["assessment"]="ERROR"
            self.worker.append({
                "id":i,"config_sha256":self.config_sha,
                "scalar_sha256":rec["scalar_sha256"],
                "scalar_status":result,"gates":gates,
                "neutrino":[{"status":"PASS"}] if result=="PASS" else "NOT_EVALUATED",
                "global_acceptance":None,
            })
        self._write()

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self):
        self.manifest_path.write_text("".join(json.dumps(v)+"\n" for v in self.manifest))
        self.worker_path.write_text("".join(json.dumps(v)+"\n" for v in self.worker))

    def test_all_source_arms_counted_separately_and_no_global_allowed_fraction(self):
        out=m.audit(self.config_path,self.manifest_path,[self.worker_path],True)
        self.assertEqual(out["total_expected"],12)
        self.assertEqual(out["total_processed"],12)
        self.assertTrue(out["complete_worker_coverage"])
        self.assertEqual(out["per_arm"]["sub_TeV"]["n_proposed"],5)
        self.assertEqual(out["per_arm"]["production_window"]["n_proposed"],5)
        self.assertEqual(out["per_arm"]["broad_control"]["n_proposed"],2)
        self.assertEqual(out["per_arm"]["sub_TeV"]["scalar_gate_labels"]["FAIL"]["n"],1)
        self.assertTrue(out["arms_overlap_in_physical_space"])
        self.assertFalse(out["global_parameter_space_sampling_density_normalized"])
        self.assertFalse(out["full_B_LFV_Higgs_constraints_applied"])
        self.assertIsNone(out["global_statistical_allowed_fraction"])
        self.assertIsNone(out["model_globally_allowed"])

    def test_unknowns_not_rewritten_as_fail_or_pass(self):
        a=m.audit(self.config_path,self.manifest_path,[self.worker_path],True)
        self.assertEqual(a["per_arm"]["sub_TeV"]["scalar_gate_labels"]["UNKNOWN"]["n"],1)
        self.assertEqual(a["per_arm"]["production_window"]["scalar_gate_labels"]["UNKNOWN"]["n"],1)
        self.assertEqual(a["per_arm"]["broad_control"]["scalar_gate_labels"]["ERROR"]["n"],1)
        self.assertEqual(m.wilson(0,0),None)
        self.assertEqual(m.wilson(0,10)[0],0)
        self.assertEqual(m.wilson(10,10)[1],1)
        with self.assertRaises(ValueError):
            m.wilson(12,10)

    def test_partial_worker_set_requires_explicit_allowance(self):
        self.worker=self.worker[:5]
        self._write()
        with self.assertRaisesRegex(ValueError,"Partial workers"):
            m.audit(self.config_path,self.manifest_path,[self.worker_path],True)
        a=m.audit(self.config_path,self.manifest_path,[self.worker_path],False)
        self.assertFalse(a["complete_worker_coverage"])
        self.assertEqual(a["total_processed"],5)
        self.assertEqual(sum(x["n_unprocessed"] for x in a["per_arm"].values()),7)

    def test_duplicate_and_source_hash_mismatch_fail_closed(self):
        self.worker.append(copy.deepcopy(self.worker[0]))
        self._write()
        with self.assertRaisesRegex(ValueError,"duplicate worker"):
            m.audit(self.config_path,self.manifest_path,[self.worker_path],True)
        self.worker=self.worker[:-1]
        self.worker[0]["scalar_sha256"]="corrupted"
        self._write()
        with self.assertRaisesRegex(ValueError,"scalar source SHA"):
            m.audit(self.config_path,self.manifest_path,[self.worker_path],True)

    def test_arm_schedule_and_proposal_config_source_mismatch(self):
        self.manifest[0]["arm"]="production_window"
        self._write()
        with self.assertRaisesRegex(ValueError,"Arm schedule"):
            m.audit(self.config_path,self.manifest_path,[self.worker_path],True)
        self.manifest[0]["arm"]="sub_TeV"
        self.manifest[0]["config_sha256"]="corrupted"
        self._write()
        with self.assertRaisesRegex(ValueError,"config"):
            m.audit(self.config_path,self.manifest_path,[self.worker_path],True)


if __name__=="__main__":
    unittest.main()

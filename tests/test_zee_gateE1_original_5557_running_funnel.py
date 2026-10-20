"""E1 original-B4 5,557-point funnel integrity and ranking tests.

These synthetic fixtures are NOT 10-TeV source RGE or vacuum physics.
The real AF campaign must use a Q4v13-pinned generator and 5,557
archived scalar/EWPO-screened B4 records.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE1_original_5557_running_funnel as e


class E1IntegrityContract(unittest.TestCase):
    def fixture(self):
        row={"id":"B4_0006862",
             "candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"}
        row.update({k:1. for k in e.KEYS})
        row.update({
            "production_weighted_nonleptonic_cascade_upper_proxy":.65,
            "chi2_Gfitter":.15,
            "max_unitarity":11.0})
        return row

    def test_B4_source_parser_requires_real_fields_and_not_allowed_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"data.csv"
            row=self.fixture()
            with file.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader()
                w.writerow(row)
            rows=e.parse_rows(file)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["id"],"B4_0006862")
            row["candidate_status"]="PHYSICAL_ALLOWED"
            with file.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader();w.writerow(row)
            with self.assertRaisesRegex(ValueError,"mislabeled"):
                e.parse_rows(file)

    def test_duplicate_legacy_B4_ID_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"data.csv"
            row=self.fixture()
            with file.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(row))
                w.writeheader();w.writerow(row);w.writerow(row)
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                e.parse_rows(file)

    def test_nonfinite_scalar_parameters_and_proxy_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"data.csv"
            for k in ("mH2","production_weighted_nonleptonic_cascade_upper_proxy"):
                row=self.fixture()
                row[k]=math.nan
                with file.open("w",newline="") as f:
                    w=csv.DictWriter(f,fieldnames=list(row))
                    w.writeheader();w.writerow(row)
                with self.assertRaisesRegex(ValueError,"Nonfinite"):
                    e.parse_rows(file)

    def test_collier_rank_locks_diversity_and_requires_RGE_vacuum_fields(self):
        rows=[]
        for i in range(5):
            rows.append({
                "id":f"B4_{i:07d}",
                "mH1_GeV":300. if i<2 else 350.+30*i,
                "mH2_GeV":700. if i<2 else 750.+50*i,
                "gamma":1.02,
                "cascade_upper_proxy":.71-.01*i,
                "maximum_unity_ratio_to_8pi_along_run":.48+.02*i,
                "diagnostic_status":
                    "ORIGINAL_RGE_AND_NO_TREE_DEEPER_WITNESS_DIAGNOSTIC"})
        chosen=e.rank_pool(rows,4)
        self.assertEqual(chosen[0]["id"],"B4_0000000")
        self.assertNotIn("B4_0000001",[x["id"] for x in chosen])
        self.assertTrue(all("NOT_ALLOWED" in e.STATUS for _ in chosen))

    def test_unimplemented_observables_are_explicitly_unavailable(self):
        self.assertIn("HiggsTools"," ".join(e.EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED))
        self.assertIn("B_to_Xs_gamma"," ".join(e.EVIDENCE_CONSTRAINTS_NOT_IMPLEMENTED))
        self.assertTrue("NOT_ALLOWED" in e.STATUS)
        self.assertTrue("NOT_ALLOWED" in e.BLOCKED)


if __name__=="__main__":
    unittest.main()

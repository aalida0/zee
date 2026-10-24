#!/usr/bin/env python3
"""F21b one-pass production regression: relocated exact F20 manifest source.

No tiny model studies. Protect 24-job CERN production from the
F20scalar.csv Condor transfer rename that killed all F21 first jobs.
"""
import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import numpy as np
from zee_paper1_F21_stratified_wide_mass_mix_scan import (
    f20_source,candidate,region,M2_EDGES,T_EDGES,G_EDGES)

SOURCE_NAME="F20_ALL_shards_scalar_LO_flavor_NOT_EXCLUSION.csv"
def synthetic(root):
    csv_bytes=b"candidate_id,mH1,mH2\nA,350,850\nB,700,1200\n"
    staged=root/"F20scalar.csv"
    staged.write_bytes(csv_bytes)
    src_sha=hashlib.sha256(csv_bytes).hexdigest()
    manifest=root/"F20summary.json"
    manifest.write_text(json.dumps({
        "status":"F20_FOUR_SHARDS_MERGED_EXPLORATORY_SCAN_NOT_FULL_ZEE_ALLOWED",
        "four_complete_shards":True,
        "calibrated_model_exclusions_or_accepted_points":None,
        "output_files_SHA256":{SOURCE_NAME:src_sha},
        "screened_scalar_parameter_records_not_unique_allowed_volume":2,
    }))
    return staged,manifest

class TestF21bProductionSourceSafety(unittest.TestCase):
    def test_real_condor_staged_filename_is_authentic_by_content(self):
        with tempfile.TemporaryDirectory() as d:
            staged,manifest=synthetic(Path(d))
            rows,_=f20_source(staged,manifest)
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[0]["candidate_id"],"A")
    def test_manifest_sha_tampering_fails(self):
        with tempfile.TemporaryDirectory() as d:
            staged,manifest=synthetic(Path(d))
            staged.write_bytes(staged.read_bytes()+b"X")
            with self.assertRaisesRegex(ValueError,"content SHA"):
                f20_source(staged,manifest)
    def test_exact_original_manifest_key_is_required(self):
        with tempfile.TemporaryDirectory() as d:
            staged,manifest=synthetic(Path(d))
            obj=json.loads(manifest.read_text())
            obj["output_files_SHA256"]={"F20scalar.csv":list(
                obj["output_files_SHA256"].values())[0]}
            manifest.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"content SHA"):
                f20_source(staged,manifest)
    def test_wide_strata_cover_all_five_mass_bins(self):
        rng=np.random.default_rng(20261024)
        visited=set()
        for k in range(100):
            point=candidate(rng,k)
            self.assertIsNotNone(point)
            self.assertTrue(200<=point["mH1"]<=1200)
            self.assertTrue(450<=point["mH2"]<=2500)
            self.assertGreater(point["mH2"]-point["mH1"],91.1876)
            tb=math.tan(point["beta"])
            self.assertTrue(.7<=tb<=35.)
            self.assertTrue(.08<=point["gamma"]<=1.49)
            self.assertTrue(all(math.isfinite(x) for x in point.values()))
            visited.add(region(point)[:3])
        self.assertEqual(len(visited),100)
        self.assertEqual({v[0] for v in visited},set(range(5)))

if __name__=="__main__":unittest.main()

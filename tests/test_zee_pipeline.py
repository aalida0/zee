"""Regression tests for the thin Zee pipeline driver, without external tools."""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from zee_pipeline import (
    STATUS,settings,validate_points,run_stage,digest,
)


def sample_point():
    return {
        "id":"B4_0001","mH1":"300","mH2":"700",
        "mh2":"580.7","ma":"633.7","alpha":"1.398",
        "beta":"1.394","gamma":"1.089","m12sq":"57700",
        "tanbeta":str(math.tan(1.394)),
        "candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED",
    }


def create_csv(path,rows):
    with path.open("w",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def create_settings(path,**flags):
    body={
        "schema_version":1,
        "neutrino_partial_LFV":{"trials_per_candidate":3,"top":2},
        "legacy_superiso":{"enabled":False},
        "higgstools":{"enabled":False},
        "full_LFV":{"enabled":False},
        "modern_b_to_s_gamma":{"enabled":False},
    }
    body.update(flags)
    path.write_text(json.dumps(body))
    return body


class TestZeePipeline(unittest.TestCase):
    def test_accepts_existing_screened_spectrum_only_as_input(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"points.csv"
            create_csv(path,[sample_point()])
            rows=validate_points(path)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["id"],"B4_0001")

    def test_duplicate_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"points.csv"
            create_csv(path,[sample_point(),sample_point()])
            with self.assertRaisesRegex(ValueError,"duplicate"):
                validate_points(path)

    def test_inconsistent_beta_and_tanbeta_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"points.csv"
            bad=sample_point();bad["tanbeta"]="2"
            create_csv(path,[bad])
            with self.assertRaisesRegex(ValueError,"Inconsistent"):
                validate_points(path)

    def test_bad_candidate_status_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"points.csv"
            bad=sample_point();bad["candidate_status"]="ALLOWED"
            create_csv(path,[bad])
            with self.assertRaisesRegex(ValueError,"unclassified"):
                validate_points(path)

    def test_legacy_superiso_requires_pinned_provenance(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"settings.json"
            create_settings(path,legacy_superiso={"enabled":True})
            with self.assertRaisesRegex(ValueError,"a1m_provenance"):
                settings(path)

    def test_full_higgstools_cannot_be_claimed_without_adapter(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"settings.json"
            create_settings(path,higgstools={"enabled":True})
            with self.assertRaisesRegex(ValueError,"COMPLETE Zee"):
                settings(path)

    def test_full_lfv_cannot_be_claimed(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"settings.json"
            create_settings(path,full_LFV={"enabled":True})
            with self.assertRaisesRegex(ValueError,"partial"):
                settings(path)

    def test_modern_bsgamma_cannot_be_claimed(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"settings.json"
            create_settings(path,modern_b_to_s_gamma={"enabled":True})
            with self.assertRaisesRegex(ValueError,"not validated"):
                settings(path)

    def test_external_stage_records_exact_artifact_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            output=root/"artifact.json"
            manifest={"stages":{}}
            cmd=[sys.executable,"-c",
                 f"from pathlib import Path;Path({str(output)!r}).write_text('ok')"]
            run_stage("fake_adapter",cmd,output,root,manifest)
            self.assertEqual(manifest["stages"]["fake_adapter"]["status"],
                             "DIAGNOSTIC_COMPLETE_NOT_EXCLUSION")
            self.assertEqual(manifest["stages"]["fake_adapter"]["output_sha256"],
                             digest(output))
            saved=json.loads((root/"manifest.json").read_text())
            self.assertEqual(saved["stages"]["fake_adapter"]["output_sha256"],
                             digest(output))

    def test_nonzero_backend_exit_does_not_fabricate_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest={"stages":{}}
            with self.assertRaisesRegex(RuntimeError,"exit 7"):
                run_stage("fake_fail",[sys.executable,"-c",
                                      "raise SystemExit(7)"],
                          root/"never.json",root,manifest)
            self.assertEqual(manifest["stages"]["fake_fail"]["status"],
                             "ERROR")

    def test_extended_partial_lfv_gate_is_not_full_lfv(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"settings.json"
            body=create_settings(path)
            body["extended_partial_LFV"]={"enabled":True}
            path.write_text(json.dumps(body))
            self.assertTrue(settings(path)["extended_partial_LFV"]["enabled"])
            # Explicit full LFV flag must still be rejected.
            body["full_LFV"]={"enabled":True}
            path.write_text(json.dumps(body))
            with self.assertRaisesRegex(ValueError,"partial"):
                settings(path)

    def test_extended_partial_lfv_requires_boolean_switch(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"settings.json"
            body=create_settings(path)
            body["extended_partial_LFV"]={"enabled":"yes"}
            path.write_text(json.dumps(body))
            with self.assertRaisesRegex(ValueError,"must be boolean"):
                settings(path)

    def test_status_blocks_allowed_claim(self):
        self.assertIn("NOT_ALLOWED",STATUS)
        self.assertIn("PARTIAL",STATUS)


if __name__=="__main__":
    unittest.main()

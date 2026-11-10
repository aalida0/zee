import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.full_constraints.scan_pilot_2026.vacuum_followup import (
    strict_inputs,evaluate_one,IDS,EXPECTED_MANIFEST_SHA,EXPECTED_COMMIT,
)

class VacuumFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.inputs=strict_inputs()
    def test_all_five_original_scalar_hashes_and_provenance(self):
        self.assertEqual(tuple(x["id"] for x in self.inputs),IDS)
        self.assertEqual(len({x["scalar_sha256"] for x in self.inputs}),5)
        self.assertTrue(EXPECTED_MANIFEST_SHA and EXPECTED_COMMIT)
    def test_d10_pass_control_and_bounded_search_scope(self):
        row=next(x for x in self.inputs if x["id"]==112)
        with patch("research.full_constraints.scan_pilot_2026.vacuum_followup.constrained_search") as f:
            f.return_value={"runs":[],"lowest_credible_minimum":None,"global_stability_proven":False}
            result=evaluate_one(row,16,0)
        self.assertTrue(result["exact_sufficient_certificate"]["certified"])
        self.assertEqual(result["new_vacuum_assessment"],"PASS")
        self.assertIsNone(result["globally_allowed"])
        self.assertFalse(result["finite_search_proves_global"])
    def test_unknown_candidate_does_not_become_allowed_after_empty_search(self):
        row=next(x for x in self.inputs if x["id"]==284)
        with patch("research.full_constraints.scan_pilot_2026.vacuum_followup.constrained_search") as f:
            f.return_value={"runs":[],"lowest_credible_minimum":None,"global_stability_proven":False}
            result=evaluate_one(row,16,16)
        self.assertEqual(result["new_vacuum_assessment"],"UNKNOWN")
        self.assertIsNone(result["globally_allowed"])
        self.assertEqual(f.call_count,2)
    def test_invalid_sources_rejected(self):
        import json
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"altered.json"
            obj=json.loads(Path(__file__).with_name("selected_five_vacuum_inputs_400.json").read_text())
            obj["cards"][2]["scalar"]["physical"]["gamma"]+=.0001
            p.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"SHA-256"):strict_inputs(p)
    def test_invalid_starts_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_one(self.inputs[0],10,0)

if __name__=="__main__":
    unittest.main()

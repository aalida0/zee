"""Test structural fail-closed evidence gating without pretending physics is proven."""
import copy
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from validate_zee_module5_native import expected_keys, check, STATUS

def example():
    keys=sorted(expected_keys())
    return {"status":STATUS,"query_count":58,"sarah_version":"4.15.4",
            "math_version":"synthetic-test-only",
            "raw_vertex_keys":keys,
            "raw_vertices":{k:"{nontrivial_symbolic_coefficient}" for k in keys}}

class NativeInventoryTests(unittest.TestCase):
    def test_complete_structure_never_certifies_matching(self):
        a=example();r=check(a)
        self.assertEqual(len(expected_keys()),58)
        self.assertEqual(r["operator_matching"],"NOT_EVALUATED")
        self.assertEqual(r["physical_B_to_Xs_gamma"],"NOT_EVALUATED")

    def test_missing_or_extra_state_rejected(self):
        a=example()
        for name in list(a["raw_vertices"]):
            altered=copy.deepcopy(a);altered["raw_vertices"].pop(name)
            with self.assertRaises(ValueError):check(altered)
        altered=copy.deepcopy(a);altered["raw_vertices"]["extra"]="value"
        with self.assertRaises(ValueError):check(altered)

    def test_placeholder_and_invalid_evidence_rejected(self):
        for bad in ("{}","$Aborted","SARAH`Vertex[{...}]","Vertex[{...}]","","Missing[foo]"):
            altered=example();altered["raw_vertices"]["photon_top"]=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):check(altered)
        for key,value in (("status","BLOCKED"),("query_count",57),("sarah_version","")):
            altered=example();altered[key]=value
            with self.assertRaises(ValueError):check(altered)

if __name__=="__main__":unittest.main()

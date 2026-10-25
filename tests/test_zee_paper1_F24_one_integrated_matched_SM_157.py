#!/usr/bin/env python3
"""One source-safe F24 matched-SM production contract: no synthetic exclusions."""
import importlib.util,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

p=Path(__file__).resolve().parents[1]/"scripts/zee_paper1_F24_157_matching_SM_same_LHA_HyperIso_2026_LO_audit.py"
spec=importlib.util.spec_from_file_location("zee_F24_native_matched_same_LHA",p)
import sys
sys.path.insert(0,str(p.parent))
f=importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)

class TestF24MatchedSMScientificIntegrity(unittest.TestCase):
    def test_genuine_native_cli_correct_model_exact_same_input(self):
        seen=[]
        def stub(argv,**kw):
            seen.append(argv)
            return subprocess.CompletedProcess(argv,0,"Header\nBR_B__Xs_gamma = 0.0003578\n","")
        with patch.object(f.subprocess,"run",side_effect=stub):
            br,out=f.native_sm_baseline(Path("/upstream/hyperiso-ui"),
                                         Path("/immutable/F23_exact_source.lha"))
        self.assertEqual(br,.0003578)
        self.assertEqual(len(seen),1)
        self.assertEqual(seen[0][0],"/upstream/hyperiso-ui")
        self.assertEqual(seen[0][seen[0].index("--model")+1],"SM")
        self.assertEqual(seen[0][seen[0].index("--lha")+1],"/immutable/F23_exact_source.lha")
        self.assertEqual(seen[0][seen[0].index("--spectrum")+1],"true")
        self.assertEqual(seen[0][seen[0].index("--order")+1],"NNLO")
    def test_fail_closed_duplicate_or_nonphysical_native_observable(self):
        with patch.object(f.subprocess,"run",return_value=subprocess.CompletedProcess(
           [],0,"BR_B__Xs_gamma = 0.00035\nBR_B__Xs_gamma = 0.00035\n","")):
            with self.assertRaisesRegex(ValueError,"ambiguous"):
                f.native_sm_baseline(Path("binary"),Path("source"))
        with patch.object(f.subprocess,"run",return_value=subprocess.CompletedProcess(
           [],0,"BR_B__Xs_gamma = nan\n","")):
            with self.assertRaisesRegex(ValueError,"ambiguous"):
                f.native_sm_baseline(Path("binary"),Path("source"))
        with patch.object(f.subprocess,"run",return_value=subprocess.CompletedProcess(
           [],12,"","critical model issue")):
            with self.assertRaisesRegex(RuntimeError,"native SM"):
                f.native_sm_baseline(Path("binary"),Path("source"))
    def test_scientific_baseline_reference_not_subtracted(self):
        # Independent R3 is a different LHA. The code must explicitly
        # subtract BR_SM with the original same-LHA THDM physics inputs.
        source=p.read_text()
        self.assertIn("delta=full-matched",source)
        self.assertNotIn('delta=full-number(f23report["R3_SM_BR"]',source)
        self.assertIn("same_LHA_same_NNLO_HyperIso_SM_BR",source)
        self.assertIn("historical_NP_delta_plus_2026_SM_not_a_valid_physical_prediction",source)
        self.assertIn('full_model_allowed_or_excluded":None',source)

if __name__=="__main__":unittest.main()

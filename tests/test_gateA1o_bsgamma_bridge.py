"""Gate A1O: source-only bridge injection and synthetic BR-closure gates."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1o_prepare_bsgamma_bridge import patch
from gateA1o_check_internal_matching_bridge import compare
from gateA1n_check_br_candidate import NAMES

def fixture_source():
    lines=[""]*748
    lines[0]='#include "include.h"'
    lines[681]='CW_calculator(2,C0w,C1w,C2w,mu_W,param);'
    lines[742]='CW_calculator(2,C0w,C1w,C2w,mu_W,&param);'
    return "\n".join(lines)+"\n"

def fixture_br(path,bridged,alter_zee=False,alter_control=False):
    lines=["STATUS GATE_A1N_BR_CANDIDATE_NOT_VALIDATED_FOR_EXCLUSION"]
    for scale in range(5):
        for name in sorted(NAMES):
            br=.0003382
            if name in ("TYPEII_300","ENDPOINT_H1"): br=.0004701
            elif name in ("TYPEII_700","ENDPOINT_H2"): br=.0003871
            elif name=="TYPEII_1000": br=.0003681
            elif name=="TYPEII_2000": br=.0003531
            elif name.startswith("ZEE_"):
                br=(.00040375 if bridged else
                    (.00040415 if name in ("ZEE_300_700","ZEE_REPEAT_MASS_300")
                     else .000403416))
                if alter_zee and name=="ZEE_SAME_WC_ALT_MASS_700":
                    br+=1e-6
            if scale and name!="SM": br+=scale*1e-7
            if alter_control and name=="TYPEII_700" and bridged: br+=1e-6
            lines.append(f"RESULT {name} {br:.17g} "
                         f"muW=160.7384 mub=2.39 cpmax=0.00333156 scale={scale}")
            lines.append(f"CPDETAIL {name} C7p_re=0.00333156 C7p_im=0 "
                         f"C8p_re=0.001 C8p_im=0 scale={scale}")
    lines.append("STATUS_END GATE_A1N_BR_CANDIDATE_NO_EXCLUSION")
    path.write_text("\n".join(lines)+"\n")

class TestGateA1O(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=pathlib.Path(self.tmp.name)
        self.orig=self.path/"original.log"
        self.bridged=self.path/"bridged.log"
        self.sm=self.path/"sm.log"
        self.sm.write_text("BR(b->s gamma) 3.382e-04\n")
        fixture_br(self.orig,False)
        fixture_br(self.bridged,True)

    def test_patch_one_internal_matching_only(self):
        source=fixture_source()
        patched,lineno=patch(source)
        self.assertEqual(lineno,682)
        self.assertIn('gateA1o_set_internal_C0w78',patched)
        self.assertIn('C0w[7]=gateA1o_c0w7;',patched)
        self.assertIn('C0w[8]=gateA1o_c0w8;',patched)
        self.assertIn('CW_calculator(2,C0w,C1w,C2w,mu_W,&param);',patched)
        self.assertEqual(patched.count('if(gateA1o_c0w_override_active)'),1)

    def test_reject_already_modified_source(self):
        patched,_=patch(fixture_source())
        with self.assertRaises(ValueError):
            patch(patched)

    def test_reject_wrong_internal_call_signature(self):
        with self.assertRaises(ValueError):
            patch(fixture_source().replace(
                "CW_calculator(2,C0w,C1w,C2w,mu_W,param);",
                "CW_calculator(1,C0w,C1w,C2w,mu_W,param);"))

    def test_single_state_and_zee_closure(self):
        result=compare(self.orig,self.bridged,self.sm)
        self.assertIn("CANDIDATE_ONLY",result["status"])
        self.assertEqual(result["max_SM_TypeII_absolute_rate_change"],0)
        self.assertEqual(result["max_zee_BR_arbitrary_mass_spread_after"],0)
        self.assertIsNone(result["Zee_benchmark_excluded"])

    def test_reject_shifted_single_typeII(self):
        fixture_br(self.bridged,True,alter_control=True)
        with self.assertRaisesRegex(ValueError,"single-state"):
            compare(self.orig,self.bridged,self.sm)

    def test_reject_zee_arbitrary_mass_dependence(self):
        fixture_br(self.bridged,True,alter_zee=True)
        with self.assertRaisesRegex(ValueError,"still depends"):
            compare(self.orig,self.bridged,self.sm)

    def test_reject_sm_reference_mismatch(self):
        self.sm.write_text("BR(b->s gamma) 2e-4\n")
        with self.assertRaises(ValueError):
            compare(self.orig,self.bridged,self.sm)

if __name__=="__main__":
    unittest.main()

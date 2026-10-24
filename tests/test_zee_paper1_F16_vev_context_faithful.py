#!/usr/bin/env python3
"""Static regression protecting real F16 SARAH VEV-context substitution path.

A real Mathematica selftest runs locally; these CI checks prevent accidental
omission of its invocation and unbalanced Wolfram input.
"""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from zee_paper1_F16_wolfram_syntax_lint import check

class TestVevContextSource(unittest.TestCase):
    def test_physical_vev_contexts_all_explicit_and_not_defaulted(self):
        resolver=(ROOT/"scripts"/"zee_paper1_F16_SARAH_context_vevs.m").read_text()
        check(resolver)
        for context in ("Global","SARAH","Susyno`LieGroups"):
            for vev in ("v1","v2"):
                self.assertIn("HoldPattern["+context+"`"+vev+"]",resolver)
        self.assertIn("vev Cos[beta]",resolver)
        self.assertIn("vev Sin[beta]",resolver)
    def test_real_audit_uses_physical_f13_vev_beta_not_model_defaults(self):
        audit=(ROOT/"scripts"/"zee_paper1_F16_SARAH_three_heavy_vertex_audit.m").read_text()
        check(audit)
        self.assertIn("zeeF16ResolveVEVs[z,o[\"V\"],o[\"Beta\"]]",audit)
        self.assertIn('Get[FileNameJoin[{root,"scripts",',audit)
        self.assertIn("F16_NONNUMERIC_MASS",audit)
    def test_wolfram_selftest_and_local_fail_closed(self):
        selftest=(ROOT/"scripts"/"zee_paper1_F16_SARAH_context_vevs_selftest.m").read_text()
        check(selftest)
        self.assertIn("F16_VEV_CONTEXT_SELFTEST_PASS",selftest)
        self.assertIn("UnknownF16Context",selftest)
        shell=(ROOT/"scripts"/"zee_paper1_F16_local_SARAH_three_heavy_one_shot.sh").read_text()
        self.assertIn("F16_SARAH_context_vevs_selftest.m",shell)
        self.assertIn("F16_FAIL_CLOSED_PHYSICAL_VEV_CONTEXT_REGRESSION",shell)

if __name__=="__main__":unittest.main()

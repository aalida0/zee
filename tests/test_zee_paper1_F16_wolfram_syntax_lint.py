#!/usr/bin/env python3
"""Check F16 Mathematica source delimiter lint catches the original syntax bug."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from zee_paper1_F16_wolfram_syntax_lint import check

class TestWolframBalance(unittest.TestCase):
    def test_actual_f16_vertex_script_is_complete(self):
        check((ROOT/"scripts"/"zee_paper1_F16_SARAH_three_heavy_vertex_audit.m").read_text())
        check((ROOT/"scripts"/"zee_paper1_F16_SARAH_MakeUFO_after_vertex_gate.m").read_text())
    def test_detect_exact_original_unclosed_Module(self):
        original='Do[Module[{x},If[True,AppendTo[x,"foo"]],{i,3}];'
        with self.assertRaisesRegex(ValueError,"unclosed"):
            check(original)
        check('Do[Module[{x},If[True,AppendTo[x,"foo"]]],{i,3}];')
    def test_nested_comments_and_strings_are_ignored(self):
        check('(* nested (* [ { *) comment *) Print["fake \\[ brace"];')
    def test_bad_unterminated_string_comment_rejected(self):
        for bad in ('Print["unterminated]', '(* unterminated', 'a={1,2]]'):
            with self.assertRaises(ValueError):
                check(bad)

if __name__=="__main__":unittest.main()

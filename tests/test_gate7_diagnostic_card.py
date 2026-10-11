"""Gate7 diagnostic LHA card writer tests: physical scalar map, unphysical leptons."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate7_make_diagnostic_param_card import replacements, render_card, parse_card_values, validate_card_values


class LhaTests(unittest.TestCase):
    def test_scalar_indices_and_lepton_defaults(self):
        x=replacements()
        self.assertAlmostEqual(x["ZEEINPUTS",4],math.pi/2-1.089,places=12)
        self.assertEqual(x["MASS",227],700.)
        self.assertEqual(x["MASS",228],300.)
        for i in (1,2,3):
            self.assertEqual(x["ZEEYUKAWAF",i],0.)
        for i in range(1,10):
            self.assertEqual(x["ZEEYUKAWAY",i],0.
                             if i not in (1,5,9) else x["ZEEYUKAWAY",i])
        self.assertAlmostEqual(x["ZEEYUKAWAY",9],
                               -math.tan(1.394)*math.sqrt(2)*1.777/246.21965)

    def test_mock_lha_updates_every_value_and_keeps_decays(self):
        vals=replacements()
        blocks={}
        for (name,key) in vals:
            blocks.setdefault(name,[]).append(key)
        content=""
        for name in sorted(blocks):
            content += "Block "+name+"\n"
            for key in sorted(blocks[name]):
                content += f"   {key}  1.000000e+00  # test index {key}\n"
        content += "DECAY 227 0.0107 # stale width\n"
        content += "DECAY 228 0.0107 # stale width\n"
        new=render_card(content,vals)
        self.assertIn("DECAY 227 0.0107 # stale width",new)
        self.assertIn("DECAY 228 0.0107 # stale width",new)
        self.assertIn("0.000000000000e+00",new)
        self.assertIn("7.000000000000e+02",new)
        # Refuse template that silently dropped one required entry
        with self.assertRaises(ValueError):
            render_card(content.replace("Block MASS","Block BOGUS"),vals)

    def test_preserve_newlines_and_independent_slha_readback(self):
        values = replacements()
        blocks = {}
        for block, code in values:
            blocks.setdefault(block, []).append(code)
        lines = ["# reproduce original Gate7 silent lost-newline bug\n"]
        for name in sorted(blocks):
            lines.append("BLOCK " + name + "\n")
            for code in sorted(blocks[name]):
                lines.append(f"   {code}  1.000000e+00  # comment for entry {code}\n")
        template = "".join(lines)
        updated = render_card(template, values)
        self.assertEqual(updated.count("\n"), template.count("\n"))
        self.assertTrue(validate_card_values(updated,values))
        parsed=parse_card_values(updated)
        self.assertAlmostEqual(parsed["MASS",225],580.7)
        self.assertAlmostEqual(parsed["MASS",227],700.)
        self.assertAlmostEqual(parsed["MASS",228],300.)
        self.assertIn("comment for entry 225\n",updated)

    def test_detect_corrupt_card_with_joined_lines(self):
        vals={("MASS",225):580.7,("MASS",227):700.}
        broken="BLOCK MASS\n   225 5.807e+02 # hHeavy   227 7.000e+02 # Hcharged\n"
        with self.assertRaisesRegex(ValueError,"missing"):
            validate_card_values(broken,vals)

    def test_duplicate_block_entry_rejected(self):
        data=replacements()
        data={("ZEELAMS",1):data["ZEELAMS",1]}
        s="Block ZEELAMS\n  1 1.0\n 1 2.0\n"
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            render_card(s,data)


if __name__=="__main__":
    unittest.main()

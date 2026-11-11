"""Source equivalence tests for all-16 native SusHi card generalized from D7/F13."""
import math
import unittest
from research.full_constraints.higgs.sushi_bridge import card as source_card,benchmark
from research.full_constraints.pheno_paper_2026.sushi_16 import card_16

class SusHi16SourceEquivalenceTests(unittest.TestCase):
    def test_original_D7_F13_physics_cards_reproduce_bytewise_beyond_header(self):
        for name in ("D7","F13"):
            record,_=benchmark(name)
            p=record["input"]["physical"]
            for state in ("H","A"):
                ref=source_card(name,state)
                gen=card_16(name,p,record["input_sha256"],state)
                self.assertEqual(ref.split("\n",1)[1],gen.split("\n",1)[1])
                self.assertIn("Block MASS",gen)
                self.assertIn("Block SUSHI",gen)

    def test_reject_wrong_cp_pdf_or_physical_coupling(self):
        record,_=benchmark("F13");p=record["input"]["physical"]
        with self.assertRaises(ValueError):
            card_16("F13",p,record["input_sha256"],"h")
        bad=dict(p);bad["alpha"]=float("nan")
        with self.assertRaises((ValueError,ArithmeticError)):
            card_16("F13",bad,record["input_sha256"],"H")
        with self.assertRaises(ValueError):
            card_16("F13",p,record["input_sha256"],"H",member=60)

if __name__=="__main__":
    unittest.main()

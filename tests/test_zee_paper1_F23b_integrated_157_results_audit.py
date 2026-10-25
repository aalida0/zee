#!/usr/bin/env python3
"""F23b consolidated source and physics numerical-record audit regressions."""
import importlib.util,math,tempfile,unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"scripts/zee_paper1_F23b_one_pass_157_real_outputs_audit.py"
s=importlib.util.spec_from_file_location("f23b_integrated",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

R6="""== Wilson summary ==
order=NNLO, qmatch=81, q=81
Group: BCoefficients
  C7  matching=(0.000800431,0)  running=(0.000795987,0)
  C8  matching=(0.000870192,0)  running=(0.000868799,0)
  C9  matching=(-0.000277916,0)  running=(-0.000277916,0)
  C10  matching=(-0.00488018,0)  running=(-0.00488018,0)
"""

class TestF23bRealNumericalSourceAudit(unittest.TestCase):
    def test_upstream_R6_C7_C8_C9_C10_exact_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);tag=root/"tag.txt";real=root/"real.txt"
            tag.write_text(R6)
            real.write_text("$ hyperiso-ui wilson summary ...\n"+R6)
            d=m.tagged_r6_log(real,tag)
            self.assertEqual(set(d),{"C7","C8","C9","C10"})
            real.write_text(real.read_text().replace("0.000800431","0.002800431"))
            with self.assertRaisesRegex(ValueError,"R6 native"):
                m.tagged_r6_log(real,tag)

    def test_source_THDM_scalar_mass_and_direct_TypeII_Yukawa_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"physical.lha"
            p.write_text("""BLOCK MASS
 37 1575.59
BLOCK MINPAR
 3 7.947
BLOCK YU
 2 2 0.1258336480
BLOCK YD
 2 2 -7.947
BLOCK YE
 2 2 -7.947
""")
            d=m.physical_lha(p)
            self.assertEqual(d["MASS",(37,)],1575.59)
            self.assertAlmostEqual(d["MINPAR",(3,)],7.947)
            self.assertAlmostEqual(d["YD",(2,2)],-7.947)
            p.write_text(p.read_text()+" 2 2 -3.0\n")
            with self.assertRaisesRegex(ValueError,"duplicate LHA"):
                m.physical_lha(p)

    def test_mass_rank_and_conditional_correlation(self):
        x=[4,1,3,2,5];y=[40,10,30,20,50]
        self.assertEqual(m.math_rank(x),[4.,1.,3.,2.,5.])
        self.assertAlmostEqual(m.correlation(x,y),1.0)
        self.assertAlmostEqual(m.correlation(m.math_rank(x),m.math_rank(y)),1.0)
        self.assertIsNone(m.correlation([1,2],[3,4]))
        self.assertTrue(math.isfinite(m.number("0.000354","physical BR")))
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            m.number("nan","corrupt BR")

if __name__=="__main__":unittest.main()

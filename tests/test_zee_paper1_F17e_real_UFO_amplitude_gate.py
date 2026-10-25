#!/usr/bin/env python3
"""F17e synthetic spin-trace, AST coupling and SLHA integrity tests.

These do not constitute independent numerical validation of the user's
locally exported SARAH UFO and F13 original three benchmarks.
"""
from pathlib import Path
import math,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_paper1_F17e_real_UFO_amplitude_gate import (
    UFOCalculator,read_f17d_card,lorentz_chirality,tb_width_from_ufo_scalar,
    scalar_vector_width,one_scalar_amplitude,parse_3body_vertices,vertex_set)
from zee_paper1_F17d_source_matched_prevalidation_cards import (
    slots_from_real_ufo,check_slots)
from test_zee_paper1_F17_real_UFO_interface import dummy_ufo
from zee_paper1_F15_charged_width_CKM_mass_scheme_audit import GF


class TestF17e(unittest.TestCase):
    def test_typeII_tb_spin_trace_signed_chiral(self):
        # Test the analytic F15 Vtb=1 LO charged Higgs H1 tb benchmark.
        m=573.25;mt=172.;mb=4.7;v=246.22
        t=5.31;gamma=1.089
        cg=math.cos(gamma)
        left=math.sqrt(2)*mt/t/v*cg
        right=math.sqrt(2)*mb*t/v*cg
        data={"vertex":"V_tb","pdgs":[-6,5,37],"couplings":[
            dict(name="GC_left",colour=0,lorentz="FFS1",structure="ProjM(2,1)",
                 value_re=0.,value_im=-left),
            dict(name="GC_right",colour=0,lorentz="FFS2",structure="ProjP(2,1)",
                 value_re=0.,value_im=-right)]}
        masses={("MASS",(6,)):mt,("MASS",(5,)):mb,("MASS",(37,)):m}
        calculated,_=tb_width_from_ufo_scalar(data,masses)
        ru=(mt/m)**2; rd=(mb/m)**2
        target=(3*GF*m/(4*math.sqrt(2)*math.pi)*cg*cg*
                math.sqrt((1-ru-rd)**2-4*ru*rd)*
                ((mt*mt/t**2+mb*mb*t*t)*(1-ru-rd)-4*mt*mt*mb*mb/m**2))
        self.assertAlmostEqual(calculated/target,1.,delta=5e-5)
        data["couplings"][1]["value_im"]*=-1
        broken,_=tb_width_from_ufo_scalar(data,masses)
        self.assertNotAlmostEqual(calculated,broken,delta=1e-6)

    def test_unknown_or_duplicate_projectors_rejected(self):
        with self.assertRaises(ValueError):
            lorentz_chirality("Gamma(3,2,1)")
        base={"pdgs":[-6,5,37],"couplings":[
            dict(colour=0,structure="ProjM(2,1)",value_re=1.,value_im=0.),
            dict(colour=0,structure="ProjM(2,1)",value_re=1.,value_im=0.)]}
        with self.assertRaises(ValueError):
            tb_width_from_ufo_scalar(base,{("MASS",(6,)):172.,
                                          ("MASS",(5,)):4.7,
                                          ("MASS",(37,)):570.})

    def test_real_ufo_safe_complex_functions(self):
        params={"foo":{"name":"foo","nature":"external","value":0.,"type":"real"}}
        calc=UFOCalculator(params,{"foo":2.})
        self.assertEqual(calc.eval("complexconjugate(complex(1,2))*foo"),2-4j)
        self.assertEqual(calc.eval("re(complex(1,2))+im(complex(1,2))"),3.)
        with self.assertRaises(ValueError):
            calc.eval("__import__('os').system('echo unsafe')")

    def test_scalar_width_and_vertex_closure_fail(self):
        g=.15;m=880.;child=550.;mz=91.1876
        self.assertGreater(scalar_vector_width(m,child,mz,g),0.)
        with self.assertRaises(ValueError):
            one_scalar_amplitude([{"couplings":[{"absolute":2.0}]}],1., "bad")

    def test_synthetic_actual_ufo_vertex_signature_extractor(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            dummy_ufo(p)
            matches=vertex_set(parse_3body_vertices(p),[5,6,37])
            self.assertEqual(len(matches),1)
            self.assertEqual(matches[0]["vertex"],"V_1")

    def test_duplicate_or_missing_slha_slot_fails_closed(self):
        slots={("MASS",(37,)):"MHm2",("CHARGEMIX",(2,3)):"ZP23"}
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"card.slha"
            dest.write_text("BLOCK MASS\n 37 500\nBLOCK CHARGEMIX\n 2 3 .25\n")
            self.assertEqual(read_f17d_card(dest,slots),{
                ("MASS",(37,)):500.,("CHARGEMIX",(2,3)):.25})
            dest.write_text(dest.read_text()+" 2 3 .25\n")
            with self.assertRaises(ValueError):read_f17d_card(dest,slots)
            dest.write_text("BLOCK MASS\n 37 500\n")
            with self.assertRaises(ValueError):read_f17d_card(dest,slots)

if __name__=="__main__": unittest.main()

#!/usr/bin/env python3
"""F17 regression using a synthetic *structure-only* SARAH-style UFO.
Real physical F13 complex matrices and the user's exported UFO are
checked separately at runtime; no fake physical card is endorsed.
"""
from pathlib import Path
import sys,unittest,tempfile,math
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from zee_paper1_F17_inspect_real_SARAH_UFO import (
    SCALAR_POT,SCALAR_PDGS,inspect_ufo,consistency,cmat,scalar_fragments)
def dummy_ufo(directory):
 p=Path(directory)
 for n in ('object_library.py','couplings.py','lorentz.py','__init__.py'):
  (p/n).write_text('# SOURCE-STRUCTURE MOCK ONLY\n')
 sources=['from object_library import Parameter']
 for i,((block,code),source) in enumerate(SCALAR_POT.items()):
  sources.append(f'p_{i}=Parameter(name={source!r},nature="external",type="real",value=0.,lhablock={block!r},lhacode={list(code)!r})')
 sources.append('Y12=Parameter(name="Y12",nature="external",type="real",value=0.,lhablock="YEE2",lhacode=[1,2])')
 sources.append('MassDummy=Parameter(name="x",nature="internal",type="real",value="p_0 + p_1")')
 (p/'parameters.py').write_text('\n'.join(sources)+'\n')
 particles=['from object_library import Particle']
 specs={'z':23,'ph':22,'w':24,'h':25,'H':35,'A':36,'c1':37,'c2':9000037,
        't':6,'b':5,'e':11,'ve':12}
 for key,pdg in specs.items():
  particles.append(f'{key}=Particle(name={key!r},antiname={key!r},pdg_code={pdg},spin=1)')
 (p/'particles.py').write_text('\n'.join(particles)+'\n')
 combos=[('z','c1','c2'),('t','b','c1'),('t','b','c2'),
  ('h','c1','c2'),('H','c1','c2'),('w','h','c1'),
  ('w','h','c2'),('e','ve','c1'),('e','ve','c2')]
 vertices=['from object_library import Vertex','import particles as P']
 for i,combo in enumerate(combos):
  vertices.append('V_%d=Vertex(name="V_%d",particles=[%s],color=[],lorentz=[],couplings={})'%(
    i,i,','.join('P.'+x for x in combo)))
 (p/'vertices.py').write_text('\n'.join(vertices)+'\n')

class TestF17UFO(unittest.TestCase):
 def test_14_scalar_ext_and_critical_decay_vertices(self):
  with tempfile.TemporaryDirectory() as d:
   dummy_ufo(d);a=inspect_ufo(d)
   self.assertEqual(a['n_vertices'],9)
   self.assertEqual(a['n_parameters'],16)
   self.assertTrue(all(a['scalar_species_found'].values()))
   self.assertTrue(a['offdiag_Z_present'])
   self.assertTrue(a['tb_both_charged_present'])
   self.assertTrue(a['offdiag_photon_absent'])
   self.assertTrue(a['all_14_scalar_lagrangian_slots_externally_present_and_real'])
   self.assertFalse(a['full_5state_Zee_slha_card_validated'])
 def test_source_scalar_fragments_are_not_full_cards(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);ufo=root/'ufo';ufo.mkdir();dummy_ufo(ufo)
   a=inspect_ufo(ufo);out=root/'out';out.mkdir()
   data={'sarah_2VEV_lagrangian_rules':{value:float(i+1) for i,value in enumerate(SCALAR_POT.values())}}
   p={key:dict(data) for key in ('F13_heavy_0001330','F13_heavy_0000981','F13_heavy_0001003')}
   summary=scalar_fragments(a,p,out)
   self.assertEqual(len(summary['files']),3)
   self.assertIn('NOT_COMPLETE_MODEL_CARD',summary['status'])
   for item in summary['files']:
    content=(out/item['path']).read_text()
    self.assertIn('BLOCK ZEEPOT',content)
    self.assertIn('BLOCK ZEEQUARTIC',content)
    self.assertNotIn('BLOCK MASS',content)
 def test_fail_missing_scalar_slot_or_vertex(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);dummy_ufo(root)
   f=root/'parameters.py';f.write_text(f.read_text().replace('p_13=Parameter','p_13=NOT_PARAMETER'))
   a=inspect_ufo(root)
   self.assertFalse(a['all_14_scalar_lagrangian_slots_externally_present_and_real'])
   f=root/'vertices.py';f.write_text(f.read_text().replace('P.z,P.c1,P.c2','P.ph,P.c1,P.c2'))
   b=inspect_ufo(root)
   self.assertFalse(b['offdiag_Z_present'])
   self.assertFalse(b['offdiag_photon_absent'])
 def test_exact_complex_matrix_shapes_and_source_identity_rejected(self):
  good={'matrices_re_im':{'FZEE':[[[0.,0.]]*3]*3}}
  with self.assertRaises(ValueError):cmat(good,'FZEE',(2,2))
  with self.assertRaises(ValueError):consistency({}, {'status':'bad','candidate_ids':[]})
if __name__=='__main__':unittest.main()

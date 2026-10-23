#!/usr/bin/env python3
"""F17b actual-UFO diagnostic tests; synthetic UFO is structural only."""
from pathlib import Path
import sys,tempfile,json,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from test_zee_paper1_F17_real_UFO_interface import dummy_ufo
from zee_paper1_F17_inspect_real_SARAH_UFO import inspect_ufo
from zee_paper1_F17b_real_UFO_blocker_triage import (
    triage,photon_couplings,candidates,STATUS)

class TestF17b(unittest.TestCase):
 def test_missing_scalar_and_symbolic_photon_not_physical_claim(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);ufo=d/'ufo';ufo.mkdir();dummy_ufo(ufo)
   parameters=ufo/'parameters.py'
   parameters.write_text(parameters.read_text().replace('p_13=Parameter','p_13=NOT_PARAMETER'))
   vertices=ufo/'vertices.py'
   vertices.write_text(vertices.read_text()+
     '\nV_P=Vertex(name="V_P",particles=[P.ph,P.c1,P.c2],color=[],lorentz=[],couplings={(0,0):C.GC_5})\n')
   couplings=ufo/'couplings.py'
   couplings.write_text('from object_library import Coupling\nGC_5=Coupling(name="GC_5",value="ZP11*ZP21+ZP12*ZP22+ZP13*ZP23",order={})\n')
   a=inspect_ufo(ufo)
   self.assertFalse(a['offdiag_photon_absent'])
   self.assertFalse(a['all_14_scalar_lagrangian_slots_externally_present_and_real'])
   rep=d/'summary.json'
   rep.write_text(json.dumps({'actual_SARAH_export_UFO_interface':a}))
   result=triage(rep)
   self.assertEqual(result['status'],STATUS)
   self.assertEqual(result['source_scalar_external_real_slots_matched'],13)
   self.assertIn('K12',result['unmapped_or_nonreal_source_scalar_slots'])
   self.assertTrue(result['photon_H1_H2_symbolic_vertex_present'])
   self.assertFalse(result['original_F17_UFO_photon_amplitude_at_exact_rotation_computed'])
   self.assertEqual(len(result['photon_symbolic_vertex_coupling_sources']),1)
   self.assertEqual(result['photon_symbolic_vertex_coupling_sources'][0]['couplings'][0]
                    ['original_coupling_expressions'][0]['symbol'],'GC_5')
 def test_diagnostic_never_changes_original_source(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);ufo=d/'ufo';ufo.mkdir();dummy_ufo(ufo)
   original=(ufo/'parameters.py').read_bytes()
   rep=d/'summary.json'
   rep.write_text(json.dumps({'actual_SARAH_export_UFO_interface':inspect_ufo(ufo)}))
   result=triage(rep)
   self.assertEqual((ufo/'parameters.py').read_bytes(),original)
   self.assertFalse(result['physical_Zee_UFO_parameter_card_ready'])
   self.assertFalse(result['photon_H1_H2_symbolic_vertex_present'])
if __name__=='__main__':unittest.main()

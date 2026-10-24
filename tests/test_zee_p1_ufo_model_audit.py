"""Static UFO compatibility audits: complete species, vertices, split complex E3 inputs."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_p1_ufo_model_audit as U

def model(root,complex_flavor=True,omit_vertex=None):
 root=Path(root);root.mkdir(exist_ok=True)
 parameters=[]
 for family,items in U.FLAVOR_BLOCKS.items():
  if not complex_flavor:continue
  for k,name in enumerate(items,1):
   pref="R" if family.endswith("R") else "I"
   label=pref+name
   parameters.append(f"{label} = Parameter(name='{label}',nature='external',"
     f"type='real',lhablock='{family}',lhacode=[{k}])")
 if not complex_flavor:
  parameters.append("fem = Parameter(name='fem',nature='external',"
     "type='real',lhablock='ZEEYUKAWAF',lhacode=[1])")
  parameters.append("ylzee = Parameter(name='ylzee',nature='external',"
     "type='real',lhablock='ZEEYUKAWAY',lhacode=[1])")
 (root/"parameters.py").write_text("\n".join(parameters)+"\n")
 pse=[("Z",23),("W__plus__",24),("t",6),("b",5),
      ("h",25),("H",225),("A",226),("HHp",227),("hHp",228)]
 particle=[]
 for symbol,pdg in pse:
  particle.append(f"{symbol} = Particle(name='{symbol}',antiname='{symbol}bar',pdg_code={pdg})")
  particle.append(f"{symbol}bar = {symbol}.anti()")
 (root/"particles.py").write_text("\n".join(particle)+"\n")
 v=[("offdiag",("Z","HHp","hHpbar")),
    ("tbheavy",("t","bbar","HHp")),
    ("tblight",("t","bbar","hHp")),
    ("Hlight1",("H","hHp","hHpbar")),
    ("Hheavy2",("H","HHp","HHpbar"))]
 for phys in ("h","H","A"):
  v.extend([("Wlight"+phys,("W__plus__",phys,"hHpbar")),
            ("Wheavy"+phys,("W__plus__",phys,"HHpbar"))])
 v=[(x,y) for x,y in v if x!=omit_vertex]
 (root/"vertices.py").write_text("\n".join(
  f"{name} = Vertex(particles=[{','.join('P.'+x for x in content)}])"
  for name,content in v)+"\n")
 for f in ("couplings.py","lorentz.py"):
  (root/f).write_text("# synthetic UFO structure for isolated contract testing\n")
 return root

class ZeeUFOAudit(unittest.TestCase):
 def test_12_flavor_24_components_and_all_spectrum_vertex_conditions(self):
  with tempfile.TemporaryDirectory() as d:
   z=U.audit(model(Path(d)/"ufo"))
   self.assertEqual(z["number_of_vertices"],11)
   self.assertTrue(z["static_necessary_conditions_pass"])
   self.assertTrue(z["split_complex_12_flavor_inputs"][
        "all_24_real_and_imaginary_entries_present"])
   self.assertFalse(z["full_scalar_potential_basis_matched_to_E2_E3"])
   self.assertFalse(z["valid_Zee_MadWidth_309_input_ready"])
   self.assertIsNone(z["complete_global_Zee_allowed_excluded"])

 def test_original_real_only_Zee_model_rejected_for_E3(self):
  with tempfile.TemporaryDirectory() as d:
   z=U.audit(model(Path(d)/"ufo",complex_flavor=False))
   self.assertTrue(z["split_complex_12_flavor_inputs"][
        "unpatched_real_only_flavor_inputs_detected"])
   self.assertFalse(z["static_necessary_conditions_pass"])
   self.assertFalse(z["valid_Zee_MadWidth_309_input_ready"])

 def test_no_heavy_charged_tb_cannot_claim_model(self):
  with tempfile.TemporaryDirectory() as d:
   z=U.audit(model(Path(d)/"ufo",omit_vertex="tbheavy"))
   self.assertFalse(z["necessary_vertices_present"]["tb_H2_three_point"])
   self.assertFalse(z["static_necessary_conditions_pass"])

 def test_missing_offdiag_Z_cascade_fails(self):
  with tempfile.TemporaryDirectory() as d:
   z=U.audit(model(Path(d)/"ufo",omit_vertex="offdiag"))
   self.assertFalse(z["necessary_vertices_present"]["Z_H1_H2_three_point"])
   self.assertFalse(z["static_necessary_conditions_pass"])

 def test_missing_real_imag_component_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=model(Path(d)/"ufo")
   path=root/"parameters.py"
   path.write_text(path.read_text().replace("Ifem = Parameter","BAD = Parameter"))
   z=U.audit(root)
   self.assertFalse(z["split_complex_12_flavor_inputs"][
        "all_24_real_and_imaginary_entries_present"])
   self.assertFalse(z["static_necessary_conditions_pass"])

 def test_no_UFO_file_refused(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,"complete extracted UFO"):
    U.audit(d)

if __name__=="__main__":unittest.main()

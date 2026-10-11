"""Gate 7 UFO static vertex-inventory regressions."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate7_validate_typeii_ufo import inspect_vertex_file, validate_folder

BASE="""V_1 = Vertex(name = 'V_1',
 particles = [ P.Z, P.h__minus__, P.H__plus__ ],
 color = ['1'], lorentz = [L.VSS1], couplings={(0,0):C.GC_1})
V_2 = Vertex(name = 'V_2',
 particles = [ P.Z, P.h__plus__, P.H__minus__ ],
 color = ['1'], lorentz = [L.VSS1], couplings={(0,0):C.GC_2})
"""
Q="""V_3 = Vertex(name = 'V_3',
 particles = [ P.t__tilde__, P.b, P.H__plus__ ],
 color = ['Identity(1,2)'], lorentz = [L.FFS1], couplings={(0,0):C.GC_3})
V_4 = Vertex(name = 'V_4',
 particles = [ P.b__tilde__, P.t, P.H__minus__ ],
 color = ['Identity(1,2)'], lorentz = [L.FFS1], couplings={(0,0):C.GC_4})
V_5 = Vertex(name = 'V_5',
 particles = [ P.t__tilde__, P.b, P.h__plus__ ],
 color = ['Identity(1,2)'], lorentz = [L.FFS1], couplings={(0,0):C.GC_5})
V_6 = Vertex(name = 'V_6',
 particles = [ P.b__tilde__, P.t, P.h__minus__ ],
 color = ['Identity(1,2)'], lorentz = [L.FFS1], couplings={(0,0):C.GC_6})
"""


class Gate7UfoTests(unittest.TestCase):
    def test_existing_zee_has_Z_but_no_top_bottom_yukawas(self):
        x=inspect_vertex_file(BASE)
        self.assertFalse(x["PASS_static_vertex_inventory"])
        self.assertTrue(x["Z_offdiagonal_both_charges_present"])
        self.assertFalse(x["tb_heavy_both_charges_present"])

    def test_new_zee_typeii_all_vertices_pass(self):
        x=inspect_vertex_file(BASE+Q)
        self.assertEqual(x["n_vertices"],6)
        self.assertTrue(x["PASS_static_vertex_inventory"])
        self.assertEqual(len(x["tb_light_charged_vertices"]),2)
        self.assertEqual(len(x["tb_heavy_charged_vertices"]),2)

    def test_off_diagonal_photon_is_forbidden(self):
        gam="""V_7 = Vertex(name='V_7',
particles=[P.a,P.h__minus__,P.H__plus__],couplings={(0,0):C.GC_7})
"""
        x=inspect_vertex_file(BASE+Q+gam)
        self.assertFalse(x["PASS_static_vertex_inventory"])
        self.assertFalse(x["no_photon_offdiagonal_3point"])

    def test_no_vertices_fails_closed(self):
        with self.assertRaises(ValueError):
            inspect_vertex_file("# empty\n")

    def test_particle_names_and_pdg_required(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/"vertices.py").write_text(BASE+Q)
            (p/"particles.py").write_text(
                "H__plus__ = Particle(pdg_code = 227, name='H+')\n"
                "h__plus__ = Particle(pdg_code = 228, name='h+')\n")
            self.assertTrue(validate_folder(p)["PASS_static_vertex_inventory"])
            (p/"particles.py").write_text("H__plus__ = Particle(pdg_code = 227)\n")
            with self.assertRaises(ValueError):
                validate_folder(p)


if __name__=="__main__":
    unittest.main()

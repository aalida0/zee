#!/usr/bin/env python3
"""F17c unit tests: synthetic AST fixtures only, never a physical UFO PASS."""
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from zee_paper1_F17c_real_UFO_scalar_photon import (
    NumericUFO, scalar_dependencies, photon_numeric, source_ew, EPS_PHOTON,
)


def parameter(name, nature="internal", value="0", **extra):
    return {"name": name, "nature": nature, "value": value, "type": "real", **extra}


def make_case():
    beta, gamma = 1.394, 1.089
    b, g = beta, gamma
    zp = [[math.cos(b), math.sin(b), 0],
          [-math.sin(b)*math.cos(g), math.cos(b)*math.cos(g), math.sin(g)],
          [math.sin(b)*math.sin(g), -math.cos(b)*math.sin(g), math.cos(g)]]
    return {"candidate_id": "F13_heavy_0001330", "vev_GeV": 246.22,
            "beta_rad": beta, "gamma_rad": gamma,
            "matrices_re_im": {"MixCharged": [
                [[z, 0.0] for z in line] for line in zp]}}


def setup():
    row = make_case()
    ew = source_ew(row)
    pars = {name: parameter(name, "external", val) for name, val in
            (( "g1", 0), ("g2", 0), ("TW", 0))}
    for i in range(1, 4):
        for j in range(1, 4):
            pars["ZP%d%d" % (i, j)] = parameter("ZP%d%d" % (i, j), "external", 0)
    expr = ("-1./2.*complex(0,1)*(2*g1*ZP23*ZP33*cmath.cos(TW)"
            "+ZP21*ZP31*(g1*cmath.cos(TW)+g2*cmath.sin(TW))"
            "+ZP22*ZP32*(g1*cmath.cos(TW)+g2*cmath.sin(TW)))")
    # Synthetic diagonal photon vertices use charge-normalized expressions.
    couplings = {"GC_176": expr, "GC_178": expr,
                 "GC_D1": "complex(0,1)*g2*cmath.sin(TW)",
                 "GC_D2": "-complex(0,1)*g2*cmath.sin(TW)"}
    verts = {
        "offdiagonal": [{"vertex": "V_176", "couplings": [{"slot": "(0,0)", "coupling": "GC_176"}]},
                        {"vertex": "V_178", "couplings": [{"slot": "(0,0)", "coupling": "GC_178"}]}],
        "diagonal_H1": [{"vertex": "V_D1", "couplings": [{"slot": "(0,0)", "coupling": "GC_D1"}]}],
        "diagonal_H2": [{"vertex": "V_D2", "couplings": [{"slot": "(0,0)", "coupling": "GC_D2"}]}],
    }
    return row, pars, couplings, verts


class TestF17c(unittest.TestCase):
    def test_sarah_lam_outputname_aliases(self):
        from zee_paper1_F17c_real_UFO_scalar_photon import scalar_dependencies
        params = {
            **{'Lam'+str(i): {'name':'Lam'+str(i), 'nature':'external',
                'value':0.1} for i in range(1,6)},
            'LamC': {'name':'LamC','nature':'external','value':0.2},
        }
        deps = scalar_dependencies(params, {}, {})
        for name in ['Lambda1','Lambda2','Lambda3','Lambda4','Lambda5','LambdaC']:
            self.assertEqual(deps[name]['classification'],'UFO_EXTERNAL')
            self.assertTrue(deps[name]['mapping_to_source_coefficients_proven'])

    def test_f16_photon_formula_uses_actual_ufo_expression(self):
        row, pars, couplings, verts = setup()
        result = photon_numeric(pars, couplings, verts, row)
        self.assertTrue(result["PASS"])
        self.assertLess(result["max_offdiagonal_absolute_coupling"], EPS_PHOTON)
        self.assertIn("g1*ZP23", result["evaluated_original_UFO_photon_couplings"]
                      ["offdiagonal"][0]["source_UFO_expression"])

    def test_source_rotation_corrupted_fails(self):
        row, pars, couplings, verts = setup()
        row["matrices_re_im"]["MixCharged"][2][2][0] += 0.02
        self.assertFalse(photon_numeric(pars, couplings, verts, row)["PASS"])

    def test_photon_gauge_relation_fail_closed(self):
        row, pars, couplings, verts = setup()
        pars["g1"] = parameter("g1", "internal", "2*g2")
        with self.assertRaises(ValueError):
            photon_numeric(pars, couplings, verts, row)

    def test_unsafe_arithmetic_rejected(self):
        parser = NumericUFO({"a": parameter("a", "internal", "__import__('os').system('false')")}, {})
        with self.assertRaises(ValueError):
            parser.param("a")

    def test_missing_scalar_not_falsely_inferred_from_mass(self):
        row, pars, couplings, verts = setup()
        pars["MAh2"] = parameter("MAh2", "external", 500., lhablock="MASS", lhacode=[36])
        deps = scalar_dependencies(pars, {}, couplings)
        for k in ("M112", "M222", "M12Sq", "MCS2"):
            self.assertEqual(deps[k]["classification"], "NOT_A_UFO_PARAMETER")
            self.assertFalse(deps[k]["mapping_to_source_coefficients_proven"])
        pars["M112"] = parameter("M112", "internal", "MAh2*MAh2")
        deps = scalar_dependencies(pars, {}, couplings)
        self.assertEqual(deps["M112"]["internal_matches"][0]["external_ancestors"], ["MAh2"])


if __name__ == "__main__":
    unittest.main()

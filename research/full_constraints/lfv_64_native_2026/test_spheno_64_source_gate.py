"""Fail-closed contracts for full complex 64-family native FlavorKit input writer.

Does NOT claim a physics result: only the user's original hash-pinned
SARAH/FlavorKit source can execute the missing one-loop Wilsons.
"""
import math
import tempfile
import unittest
from pathlib import Path
import numpy as np
from module2.interface import encode
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import (
    split_slha,block_values,set_model_blocks,parse_observables,
    tree_scheme_mass_gate,check_source_bundle,MINPAR,
)

TEMPLATE="""Block MODSEL
  1 0
Block MINPAR
  1 1.0000000e-1
  10 2.0
Block FZEE
  1 2 1.0e-6
Block YEE2
  1 1 1.0e-4
Block SMINPUTS
  4 9.11876000e+1
  6 1.72760000e+2
Block SPHENOINPUT
  55 0
"""
MASS="""Block MASS
 25 1.250000e2
 35 1.100000e3
 36 1.010000e3
 37 8.000000e2
 900037 1.300000e3
Block FlavorKitLFV # lepton flavor violating observables
 701 1.5e-19 # BR(mu->e gamma)
 800 2.5e-20 # CR(mu-e,Al)
 804 3.5e-20 # CR(mu-e,Au)
 901 4.5e-21 # BR(mu->3e)
"""

class NativeInputContracts(unittest.TestCase):
    def test_exact_scalar_and_full_complex_Ye2_F(self):
        p=source_points()[0]["input_card"]
        f=np.zeros((3,3),complex);f[0,1]=1e-4+3e-4j;f[1,0]=-f[0,1]
        y=np.eye(3,dtype=complex)*1e-3;y[2,0]=.0004+.007j
        out=set_model_blocks(TEMPLATE,p,{"F":encode(f),"Ye2":encode(y)})
        blocks=split_slha(out)
        self.assertEqual(block_values(blocks["MINPAR"])[(10,)],math.tan(p["physical"]["beta"]))
        self.assertEqual(len([i for i in MINPAR if (i,) in block_values(blocks["MINPAR"])]),13)
        self.assertAlmostEqual(block_values(blocks["IMFZEE"])[(1,2)],.0003)
        self.assertAlmostEqual(block_values(blocks["IMYEE2"])[(3,1)],.007)
        self.assertAlmostEqual(block_values(blocks["FZEE"])[(2,1)],-.0001)
        self.assertAlmostEqual(block_values(blocks["YEE2"])[(1,1)],.001)
        self.assertAlmostEqual(block_values(blocks["SMINPUTS"])[(6,)],172.76)
        self.assertEqual(block_values(blocks["SPHENOINPUT"])[(55,)],0)

    def test_missing_original_model_block_refused(self):
        p=source_points()[0]["input_card"]
        f=np.zeros((3,3),complex)
        with self.assertRaises(ValueError):
            set_model_blocks(TEMPLATE.replace("Block YEE2","Block NOT_OUR_MODEL"),
                            p,{"F":encode(f),"Ye2":encode(f)})

    def test_parse_actual_flavorkit_sarah_output_indices(self):
        y=parse_observables(MASS)
        self.assertEqual(y["mu_to_3e"],4.5e-21)
        self.assertEqual(y["mu_to_e_conversion_Al27"],2.5e-20)
        self.assertEqual(y["mu_to_e_conversion_Au197"],3.5e-20)
        self.assertEqual(y["mu_to_e_gamma"],1.5e-19)
        for token in ("901 4.5e-21","804 3.5e-20","800 2.5e-20"):
            with self.assertRaises(ValueError):
                parse_observables(MASS.replace(token,""))
        with self.assertRaises(ValueError):
            parse_observables(MASS.replace("901 4.5e-21","901 -4.5e-21"))

    def test_native_spectrum_gate_is_not_silently_lost(self):
        p=dict(mh1=125.,mh2=1100.,ma=1010.,mH1=800.,mH2=1300.)
        self.assertEqual(len(tree_scheme_mass_gate(MASS,p)),5)
        with self.assertRaises(ValueError):
            tree_scheme_mass_gate(MASS.replace("35 1.100000e3","35 1.210000e3"),p)

    def test_pinned_generated_model_source_required(self):
        with self.assertRaises(ValueError):
            check_source_bundle({})
        with tempfile.TemporaryDirectory() as d:
            wrong={k:Path(d)/k for k in
                    ("FlavorKit_LFV_ZeeTypeII.f90",
                     "Couplings_ZeeTypeII.f90",
                     "LoopFunctions.f90",
                     "FlavorKit_Observables_ZeeTypeII.f90",
                     "LowEnergy_ZeeTypeII.f90")}
            for p in wrong.values():p.write_text("malicious or untrusted source")
            with self.assertRaises(ValueError):
                check_source_bundle(wrong)

    def test_duplicate_or_malformed_source_blocks_refused(self):
        with self.assertRaises(ValueError):
            split_slha("Block MASS\n 1 2\nBlock MASS\n 1 3")
        with self.assertRaises(ValueError):
            block_values(["Block FZEE"," 1 1 0.1"," 1 1 0.2"])

if __name__=="__main__":
    unittest.main()

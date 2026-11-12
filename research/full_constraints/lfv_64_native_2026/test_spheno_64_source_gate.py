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
    tree_scheme_mass_gate,check_source_bundle,native_yukawa_gate,MINPAR,
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
  57 1 # calculate FlavorKit low energy observables
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

    def test_original_SARAH_IN_blocks_repeated_and_complex_physics_preserved(self):
        p=source_points()[0]["input_card"]
        f=np.zeros((3,3),dtype=complex)
        f[0,1]=3e-4+4e-4j
        f[1,0]=-f[0,1]
        y=np.eye(3,dtype=complex)*.011
        y[2,0]=.007-.003j
        native=TEMPLATE.replace("Block FZEE","Block FZEEIN").replace(
            "Block YEE2","Block YEE2IN")
        native+="\nBlock FZEEIN\n 1 2 4.1\nBlock YEE2IN\n 1 1 9.8\n"
        # Repeated historical IN blocks must be normalized, never accepted
        # as two conflicting physical Yukawa sources.
        with self.assertRaises(ValueError):
            split_slha(native)
        generated=set_model_blocks(native,p,{"F":encode(f),"Ye2":encode(y)})
        headers=[s.upper().strip() for s in generated.splitlines()
                 if s.lstrip().upper().startswith("BLOCK ")]
        self.assertEqual(headers.count("BLOCK FZEEIN"),1)
        self.assertEqual(headers.count("BLOCK YEE2IN"),1)
        self.assertIn("BLOCK IMFZEEIN",headers)
        self.assertIn("BLOCK IMYEE2IN",headers)
        self.assertNotIn("BLOCK FZEE",headers)
        self.assertNotIn("BLOCK YEE2",headers)
        sec=split_slha(generated)
        self.assertAlmostEqual(block_values(sec["FZEEIN"])[(1,2)],3e-4)
        self.assertAlmostEqual(block_values(sec["IMFZEEIN"])[(1,2)],4e-4)
        self.assertAlmostEqual(block_values(sec["FZEEIN"])[(2,1)],-3e-4)
        self.assertAlmostEqual(block_values(sec["YEE2IN"])[(3,1)],.007)
        self.assertAlmostEqual(block_values(sec["IMYEE2IN"])[(3,1)],-.003)
        self.assertEqual(block_values(sec["SMINPUTS"]),block_values(split_slha(TEMPLATE)["SMINPUTS"]))
        self.assertEqual(block_values(sec["SPHENOINPUT"]),block_values(split_slha(TEMPLATE)["SPHENOINPUT"]))

    def test_ambiguity_rejects_both_input_and_output_model_stems(self):
        p=source_points()[0]["input_card"]
        z=np.zeros((3,3),dtype=complex)
        both=TEMPLATE+"\nBlock FZEEIN\n 1 2 .3\n"
        with self.assertRaises(ValueError):
            set_model_blocks(both,p,{"F":encode(z),"Ye2":encode(z)})
        repeated_other=TEMPLATE+"\nBlock MINPAR\n 1 .1\n"
        with self.assertRaises(ValueError):
            set_model_blocks(repeated_other,p,{"F":encode(z),"Ye2":encode(z)})

    def test_native_tree_template_repeated_SPhenoInput_controls_merge_losslessly(self):
        p=source_points()[0]["input_card"]
        f=np.zeros((3,3),complex)
        f[0,1]=3e-5+4e-5j
        f[1,0]=-f[0,1]
        y=np.eye(3,dtype=complex)*.021
        # Authentic native input may repeat both FZEEIN and SPhenoInput
        # sections. Additional switches must survive, not be dropped.
        native=(TEMPLATE.replace("Block FZEE","Block FZEEIN")
                        .replace("Block YEE2","Block YEE2IN"))
        native += "\nBlock SPHENOINPUT\n  57 1  # identical duplicate\n  76 0.\n"
        native += "Block SPHENOINPUT\n  12 1.\n  76 0.\n"
        native += "Block FZEEIN\n  1 2 999.\n"
        with self.assertRaisesRegex(ValueError,"Duplicate SLHA input block SPHENOINPUT"):
            split_slha(native)
        canonical=set_model_blocks(native,p,{"F":encode(f),"Ye2":encode(y)})
        parsed=split_slha(canonical)
        head=[line.upper() for line in canonical.splitlines() if line.upper().startswith("BLOCK ")]
        self.assertEqual(head.count("BLOCK SPHENOINPUT"),1)
        self.assertEqual(head.count("BLOCK FZEEIN"),1)
        self.assertEqual(head.count("BLOCK YEE2IN"),1)
        ctrl=block_values(parsed["SPHENOINPUT"])
        self.assertEqual(ctrl,{(55,):0.0,(57,):1.0,(76,):0.0,(12,):1.0})
        self.assertAlmostEqual(block_values(parsed["IMFZEEIN"])[(1,2)],4e-5)
        self.assertAlmostEqual(block_values(parsed["FZEEIN"])[(1,2)],3e-5)
        self.assertAlmostEqual(block_values(parsed["YEE2IN"])[(1,1)],.021)
        self.assertEqual(block_values(parsed["SMINPUTS"]),
                         block_values(split_slha(TEMPLATE)["SMINPUTS"]))

    def test_repeated_SPhenoInput_conflicting_flags_denied(self):
        p=source_points()[0]["input_card"]
        z=np.zeros((3,3),complex)
        for conflicting in (
            "Block SPHENOINPUT\n 57 0.\n",
            "Block SPHENOINPUT\n 55 1.\n",
        ):
            with self.assertRaisesRegex(ValueError,"Conflicting repeated SLHA control SPHENOINPUT"):
                set_model_blocks(TEMPLATE+"\n"+conflicting,p,{"F":encode(z),"Ye2":encode(z)})
        self.assertEqual(block_values(split_slha(TEMPLATE)["SPHENOINPUT"])[(57,)],1.)

    def test_missing_original_model_block_refused(self):
        p=source_points()[0]["input_card"]
        f=np.zeros((3,3),complex)
        with self.assertRaises(ValueError):
            set_model_blocks(TEMPLATE.replace("Block YEE2","Block NOT_OUR_MODEL"),
                            p,{"F":encode(f),"Ye2":encode(f)})

    def test_spheno_low_energy_flag_57_mandatory(self):
        p=source_points()[0]["input_card"]
        z=np.zeros((3,3),dtype=complex)
        for modified in (TEMPLATE.replace("  57 1 # calculate FlavorKit low energy observables","  57 0"),
                         TEMPLATE.replace("  57 1 # calculate FlavorKit low energy observables","")):
            with self.assertRaises(ValueError):
                set_model_blocks(modified,p,{"F":encode(z),"Ye2":encode(z)})

    def test_slha_decay_termination_does_not_pollute_mass_block(self):
        sample="Block MASS\n 25 125.\nDECAY 25 4.0e-3\n 1.0 2 5 -5\n"
        data=block_values(split_slha(sample)["MASS"])
        self.assertEqual(data,{(25,):125.})

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

    def test_genuine_native_complex_Yukawa_output_reconstructs_exact_physical_D(self):
        from module2.interface import encode
        p=source_points()[0]["input_card"]["physical"]
        beta=float(p["beta"])
        f=np.zeros((3,3),complex)
        f[0,1]=1.e-4+2.e-4j;f[1,0]=-f[0,1]
        d=np.diag([.01+.02j,.004+.005j,.001+.002j]).astype(complex)
        ye2=np.diag([.022-.01j,.023+.004j,.012-.002j]).astype(complex)
        ye=(math.cos(beta)*ye2-d)/math.sin(beta)
        def asblock(name,arr,imag=False):
            return ("Block "+name+"\n"+
                "".join(f" {i+1} {j+1} {z:.17e}\n"
                    for i,row in enumerate(arr) for j,z in enumerate(
                    row.imag if imag else row.real)))
        def build(YE=ye):
            return (f"Block MINPAR\n 10 {math.tan(beta):.17e}\n"+
                asblock("YE",YE)+asblock("IMYE",YE,True)+
                asblock("YEE2",ye2)+asblock("IMYEE2",ye2,True)+
                asblock("FZEE",f)+asblock("IMFZEE",f,True))
        source={"F":encode(f),"D":encode(d),"Ye2":encode(ye2)}
        valid=native_yukawa_gate(build(),p,source)
        self.assertTrue(valid["source_Yukawa_basis_validated"])
        self.assertLess(valid["native_e_mu_offdiag_max_abs"],1.e-12)
        bad=ye.copy();bad[0,1]=.005
        with self.assertRaises(ValueError):
            native_yukawa_gate(build(bad),p,source)
        with self.assertRaises(ValueError):
            native_yukawa_gate(build().replace("Block IMFZEE","Block NOTIMFZEE"),p,source)

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

"""Paper 2 MG5 stable mixed-pair runner input and banner regression tests."""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_muon_integrate_mg5 import (
    STATUS,patch_run_card,ew_from_slha,banner_pb,
    energy_list,generated_processes
)
from zee_muon_asymmetric_pair_pilot import sigma_both_charges_fb

RUN_CARD = """3000 = nevents ! number of events
0 = iseed ! seed
1 = lpp1 ! left beam
1 = lpp2 ! right beam
6500 = ebeam1 ! beam energy
6500 = ebeam2 ! beam energy
0 = polbeam1 ! left polarisation
0 = polbeam2 ! right polarisation
"""
SLHA="""Block SMINPUTS
  1  127.9 # inverse alpha
  2  1.16637e-5 # G_F
  3  0.1184
Block MASS
  23 91.1876 # Z mass
  24 80.379
"""
BANNER="""<LesHouchesEvents>
<header>
<MGGenerationInfo>
# Number of Events : 3000
# Integrated weight (pb) : .27853E-03
</MGGenerationInfo>
</header>
</LesHouchesEvents>
"""

class TestZeeMuonMG5Integration(unittest.TestCase):
    def test_status_fails_closed(self):
        self.assertIn("DIAGNOSTIC",STATUS)
        self.assertIn("NOT_ALLOWED",STATUS)

    def test_run_card_patch_preserves_eol_and_comments(self):
        updated=patch_run_card(RUN_CARD,{
            "lpp1":0,"lpp2":0,
            "ebeam1":750.,"ebeam2":750.,
            "nevents":3000,"iseed":1234,
            "polbeam1":0,"polbeam2":0})
        self.assertEqual(len(updated.splitlines()),len(RUN_CARD.splitlines()))
        self.assertIn("0 = lpp1 ! left beam",updated)
        self.assertIn("750.0 = ebeam2 ! beam energy",updated)
        self.assertIn("1234 = iseed ! seed",updated)

    def test_missing_beam_parameter_rejected(self):
        with self.assertRaisesRegex(ValueError,"Missing"):
            patch_run_card("3000 = nevents\n",{"nevents":1000})

    def test_duplicate_beam_parameter_rejected(self):
        duplicate=RUN_CARD+"0 = lpp1 ! duplicate\n"
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            patch_run_card(duplicate,{
                "nevents":2000,"iseed":42,
                "lpp1":0,"lpp2":0,
                "ebeam1":750,"ebeam2":750})

    def test_yang_wu_internal_GF_alpha_scheme(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"card.dat"
            path.write_text(SLHA)
            ew=ew_from_slha(path)
            self.assertAlmostEqual(ew["alpha"],1/127.9,places=14)
            self.assertAlmostEqual(ew["GF"],1.16637e-5,places=14)
            # Yang/Wu's declared tree-level (alpha,G_F,MZ) scheme
            # yields MW=79.82436, NOT the separate MASS[24]=80.379.
            # Test exact scheme closure rather than an arbitrary 80-82 band.
            self.assertAlmostEqual(
                ew["MW_internal"],79.82435974619784,delta=1e-8)
            self.assertAlmostEqual(
                ew["sw2"],0.23369913342182436,delta=1e-11)
            lhs=ew["MW_internal"]**2*(1-ew["MW_internal"]**2/
                                           ew["MZ"]**2)
            rhs=math.pi*ew["alpha"]/(math.sqrt(2.)*ew["GF"])
            self.assertAlmostEqual(lhs,rhs,delta=1e-8)
            self.assertGreater(sigma_both_charges_fb(
                1500.,207.26,686.47,1.18453,
                alpha=ew["alpha"],sw2=ew["sw2"]),0)

    def test_integrated_weight_from_mg5_banner(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"run_banner.txt"
            path.write_text(BANNER)
            self.assertAlmostEqual(1000*banner_pb(path),.27853,places=8)

    def test_invalid_ambiguous_banner_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"run_banner.txt"
            path.write_text(BANNER+BANNER)
            with self.assertRaisesRegex(ValueError,"Ambiguous"):
                banner_pb(path)

    def test_unequal_mass_energy_scan_syntax(self):
        self.assertEqual(energy_list("1500,3000"),[1500.,3000.])
        with self.assertRaisesRegex(ValueError,"Repeated energies"):
            energy_list("1500,1500")
        with self.assertRaisesRegex(ValueError,"Empty energy"):
            energy_list("")
        with self.assertRaisesRegex(ValueError,"Invalid energy"):
            energy_list("1500,garbage")
        with self.assertRaisesRegex(ValueError,"Invalid energy"):
            energy_list("1500,nan")

    def test_process_generation_card_modes_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root)
            for mode,lines in (
                ("Z_only",["generate mu+ mu- > z > H+ h- QCD=0",
                           "add process mu+ mu- > z > H- h+ QCD=0"]),
                ("full_tree",["generate mu+ mu- > H+ h- QCD=0",
                              "add process mu+ mu- > H- h+ QCD=0"])):
                p=root/mode
                (p/"Cards").mkdir(parents=True)
                (p/"bin").mkdir()
                (p/"bin"/"generate_events").write_text("stub")
                (p/"Cards"/"proc_card_mg5.dat").write_text(
                    "\n".join(lines)+"\n")
                generated_processes(p,mode)
            with self.assertRaisesRegex(ValueError,"missing"):
                generated_processes(root/"full_tree","Z_only")


if __name__=="__main__":
    unittest.main()

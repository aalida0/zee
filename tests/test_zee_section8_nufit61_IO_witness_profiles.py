"""NuFIT 6.1 Zee IO 2D-profile parser regression using SYNTHETIC xz grids.

Synthetic data never count as experimental data or an allowed benchmark.
Only hash-verified official NuFIT files are valid for the physics gate.
"""
import lzma
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_nufit61_IO_witness_profiles import (
    Grid,read_tables,profile_ratio,analyze,verify,witness,STATUS,
    THRESHOLD_3SIGMA_2DOF
)

class TestZeeNufit61IO(unittest.TestCase):
    def test_bilinear_grid_and_no_extrapolation(self):
        g=Grid([(0,0,0),(1,0,1),(0,2,2),(1,2,3)],"SYNTHETIC")
        self.assertAlmostEqual(g.interpolate(.5,1.),1.5,places=12)
        with self.assertRaisesRegex(ValueError,"Outside official table support"):
            g.interpolate(1.1,1.)
        with self.assertRaisesRegex(ValueError,"Nonrectangular"):
            Grid([(0,0,0),(1,0,1),(0,2,2)],"INCOMPLETE")

    @staticmethod
    def synthetic_xz(filename,scale=1.):
        with lzma.open(filename,"wt",encoding="utf-8") as h:
            for section,xs,ys in (
                ("T13/T12",[.020,.024],[.29,.33]),
                ("T23/DCP",[.4,.6],[-180.,-90.]),
                ("DMS/DMA",[-5.,-4.],[-3.,-2.])):
                h.write("# "+section+" projection: SYNTHETIC test only\n")
                for x in xs:
                    for y in ys:
                        h.write(f"{x} {y} {scale*(6+.2*x+.01*y)}\n")

    def test_official_table_provenance_rejects_fake(self):
        with tempfile.TemporaryDirectory() as work:
            file=Path(work)/"synthetic.txt.xz"
            self.synthetic_xz(file)
            with self.assertRaisesRegex(ValueError,"SHA256/size mismatch"):
                verify(file,"TBoff-IO")

    def test_profile_parsing_scoring_not_summed(self):
        with tempfile.TemporaryDirectory() as work:
            file=Path(work)/"synthetic.txt.xz"
            self.synthetic_xz(file)
            c={"sin2theta12":.318,"sin2theta13":.021,
               "sin2theta23":.436,"deltaCP_deg_signed":-142.8,
               "dm21_sq_eV2":9.25e-5,"dm32_sq_eV2":-.002534,
               "solar_over_abs_atm":9.25e-5/.002534,
               "sum_mnu_eV":.1062}
            r=analyze(file,"TBoff-IO",c,check_hash=False)
            self.assertIsNone(r["full_NuFIT_joint_likelihood"])
            self.assertIsNone(r["physical_Zee_allowed"])
            v=r["individual_marginal_2D_profiles_DO_NOT_SUM"]
            self.assertEqual(len(v),4)
            self.assertFalse(r["at_least_one_profile_incompatible_3sigma"])
            grids=read_tables(file)
            prof=profile_ratio(grids["DMS/DMA"],c["solar_over_abs_atm"],1001)
            self.assertLess(prof["dm32_eV2"],0)
            self.assertGreater(prof["dm21_eV2"],0)
            self.assertIn("NOT_JOINT_LIKELIHOOD_OR_ALLOWED",STATUS)

    def test_synthetic_excluded_single_profile(self):
        with tempfile.TemporaryDirectory() as work:
            file=Path(work)/"synthetic2.txt.xz"
            self.synthetic_xz(file,scale=3.)
            c={"sin2theta12":.318,"sin2theta13":.021,
               "sin2theta23":.436,"deltaCP_deg_signed":-142.8,
               "dm21_sq_eV2":9.25e-5,"dm32_sq_eV2":-.002534,
               "solar_over_abs_atm":9.25e-5/.002534,
               "sum_mnu_eV":.1062}
            r=analyze(file,"TBoff-IO",c,check_hash=False)
            self.assertTrue(r["at_least_one_profile_incompatible_3sigma"])
            self.assertLess(THRESHOLD_3SIGMA_2DOF,13.)

    def test_physical_witness_uses_IO_sign_and_delta_wrap(self):
        r=witness()
        self.assertAlmostEqual(r["dm21_sq_eV2"],9.249e-5,delta=1e-8)
        self.assertAlmostEqual(r["dm32_sq_eV2"],-.002534,delta=1e-6)
        self.assertAlmostEqual(r["solar_over_abs_atm"],.0365,places=6)
        self.assertAlmostEqual(r["deltaCP_deg_signed"],-142.79380270145,places=7)

if __name__=="__main__":unittest.main()

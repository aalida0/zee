import math
import os
import tempfile
import unittest
import json
from pathlib import Path

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_qed_dipole_ll_diagnostic import (
    MW, MTAU, ALPHA_ZERO, diagonal_qed_factor, compute
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_native_monopole_source import (
    EXPECTED
)


class QEDDipoleLeadingLogTests(unittest.TestCase):
    def test_operator_diagonal_leading_log(self):
        factor=1-16*ALPHA_ZERO/(4*math.pi)*math.log(MW/MTAU)
        self.assertAlmostEqual(diagonal_qed_factor(),factor)
        self.assertAlmostEqual(factor,0.9645825297250689,places=12)
        self.assertEqual(diagonal_qed_factor(MTAU,MTAU),1)
        self.assertLess(diagonal_qed_factor(2*MW),factor)
        for x in ((MTAU/2,MTAU),(-1,MTAU),(MW,-1),(MW,MTAU,float('nan'))):
            with self.assertRaises(ValueError):
                diagonal_qed_factor(*x)

    def test_shows_only_homogeneous_QED_and_not_full_electroweak(self):
        f=diagonal_qed_factor()
        self.assertGreater(f,0.9)
        self.assertLess(f,1)
        # When treated as an amplitude factor, rate scales with f**2.
        self.assertAlmostEqual(f*f,0.9304194566508134,places=12)

    def test_original_source_card_compatibility_and_BZ_provenance(self):
        source=os.environ.get('ZEE_BZ_SIGNED_OUTPUT')
        if not source:self.skipTest("run from source-locked GitLab CI")
        r=compute(Path(source))
        self.assertEqual(tuple(r['cards']),EXPECTED)
        self.assertTrue(r['operator_mixing_omitted'])
        self.assertTrue(r['EW_matching_omitted'])
        self.assertFalse(r['all_Zee_2loop'])
        self.assertEqual(r['physical_lfv'],'UNKNOWN')
        self.assertIsNone(r['global_acceptance'])
        for w in r['cards'].values():
            for ch,row in w.items():
                self.assertTrue(math.isfinite(row['fractional_shift_in_restricted_partial_rate']))
                self.assertIsNone(row['physical_radiative_BR'])
                self.assertTrue(row['missing_mixed_Zee_electroweak_2loop'])

    def test_bad_signed_bz_source_rejected(self):
        source=os.environ.get('ZEE_BZ_SIGNED_OUTPUT')
        if not source:self.skipTest("run from source-locked GitLab CI")
        x=json.loads(Path(source).read_text())
        x['gitlab_thdm_sha256']='wrong'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'false_source.json';p.write_text(json.dumps(x))
            with self.assertRaises(ValueError):compute(p)


if __name__=='__main__':
    unittest.main()

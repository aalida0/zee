"""Independent chiral phase-space, coherent production and missing-input checks."""
import copy
import math
import unittest
import tarfile
import numpy as np
from module2.interface import decode
from module3.core import vertices
from module7.d4_inputs import SM
from module7.d4_tree_kernels import scalar_fermions
from research.full_constraints.higgs.sushi_bridge import benchmark
from research.full_constraints.higgs.h125_signal_strength import calculate, signal_strength, RECEIPTS


class PhysicalLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=calculate()

    def test_native_chiral_widths_both_charges(self):
        for row in self.evidence['cases']:
            r,w=benchmark(row['name']);p=r['input']['physical'];ml=SM['lepton_masses']
            C=vertices(decode(w['yukawas']['D']),p,ml)['h'][0]
            count=0
            for i,a in enumerate(('e','mu','tau')):
                for j,b in enumerate(('e','mu','tau')):
                    if j<i:continue
                    independent=scalar_fermions(125.,ml[i],ml[j],C[i,j],C[j,i].conjugate(),1)
                    if i!=j:independent+=scalar_fermions(125.,ml[j],ml[i],C[j,i],C[i,j].conjugate(),1)
                    self.assertAlmostEqual(row['width']['partial_widths_GeV'][a+b]/independent,1.,places=13)
                    count+=1
            self.assertEqual(count,6)

    def test_incomplete_never_becomes_a_signal(self):
        for row in self.evidence['cases']:
            with self.assertRaisesRegex(ValueError,'MISSING_PREDICTION'):
                signal_strength(row['width'],1.,1.,.004)
            zeroed=copy.deepcopy(row['width']);zeroed['missing']=[]
            zeroed['total_width_GeV']=zeroed['known_channel_sum_GeV']
            with self.assertRaises(ValueError):signal_strength(zeroed,1.,1.,.004)
            self.assertTrue(all(x is None for x in row['signal_strengths'].values()))

    def test_sm_normalization_and_width_independent_ratio(self):
        width=dict(status='COMPLETE',missing=[],total_width_GeV=.004,partial_widths_GeV={'a':.003,'b':.001})
        self.assertEqual(signal_strength(width,1.,1.,.004),1.)
        for row in self.evidence['cases']:
            n=row['signal_strength_numerators'];ratio=row['width_independent_signal_strength_ratios']['ggF_gammagamma_over_VBF_WW']
            for total in (.004,.0048):
                self.assertAlmostEqual((n['ggF_gammagamma']/total)/(n['VBF_WW']/total),ratio,places=14)
        with self.assertRaisesRegex(ValueError,'MISSING_PREDICTION'):signal_strength(width,None,1.,.004)

    def test_mass_scheme_and_coherent_ggF(self):
        self.assertAlmostEqual(self.evidence['converted_mc3_GeV'],.99282721003944163,places=12)
        for row in self.evidence['cases']:
            self.assertLess(row['charm_scheme_correction_GeV'],0)
            self.assertAlmostEqual(row['production_ratios']['ggF']/row['ggF_coherent_t_b_c_ratio'],1.,places=7)
            self.assertGreater(abs(row['production_ratios']['ggF']-row['ggF_incoherent_ratio']),1e-4)
            self.assertIsNone(row['production_ratios']['ZH_inclusive'])

    def test_all_on_shell_scalar_channels_closed(self):
        for row in self.evidence['cases']:
            p=row['physical']
            for mass in row['scalar_thresholds_GeV'].values():self.assertGreater(mass,125.)
            self.assertIsNone(row['neutrinos']['leading_loop_width_GeV'])
            self.assertEqual(row['neutrinos']['tree_width_GeV'],0.)
            self.assertAlmostEqual(math.fsum(row['width']['partial_widths_GeV'].values()),row['width']['known_channel_sum_GeV'],places=15)

    def test_raw_receipts_preserved(self):
        with tarfile.open(RECEIPTS/'RAW_OUTPUTS.tar.gz') as archive:
            self.assertEqual(len(archive.getnames()),9)
            for member in archive.getmembers():
                raw=archive.extractfile(member).read().decode()
                normalized='\n'.join(line.rstrip() for line in raw.splitlines())+'\n'
                self.assertEqual((RECEIPTS/member.name).read_text(),normalized)

    def test_experimental_absolute_rate_convention(self):
        category=self.evidence['experimental_category']
        self.assertNotEqual(category['pinned_observed_sigma_BR_pb'][1],category['paper_observed_mu'])
        self.assertEqual(category['pinned_observed_sigma_BR_pb'][1],category['paper_sigma_BR_pb'])
        self.assertAlmostEqual(category['native_SM_reference_sigma_BR_pb'],2.20257783862,places=11)
        self.assertEqual(category['HiggsSignals_calls'],0)


if __name__=='__main__':unittest.main()

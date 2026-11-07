import json, math, unittest
from pathlib import Path
p=Path(__file__).with_name('NOVELTY_WITNESS_MATRIX.json')
x=json.loads(p.read_text())
class Regression(unittest.TestCase):
 def test_known_d7_counterfactual(self):
  rows={r['label']:r for r in x['D12_witnesses'] if r['scalar'].startswith('d7_') and r['ordering']=='NO'}
  a,b=(rows[k]['observables'] for k in ('central','high_F'))
  self.assertAlmostEqual(b['H1']['lnu']-a['H1']['lnu'],0.311673394418999,places=13)
  self.assertAlmostEqual(b['cascade']['lnu'],0.014160446375204989,places=14)
  self.assertAlmostEqual(b['H2']['H1Z']*b['H1']['tb'],0.031164050118795823,places=14)
 def test_f13_and_nulls(self):
  a=next(r for r in x['D12_witnesses'] if r['scalar'].startswith('F13') and r['ordering']=='NO' and r['label']=='high_F')
  self.assertAlmostEqual(a['observables']['cascade']['lnu_over_tb'],1.1770589372233156,places=13)
  self.assertIsNone(a['production_pb']); self.assertIsNone(a['global_acceptance'])
  self.assertTrue(all(r['observables']['H2_tb'] is None for r in x['D14_rows']['13']))
 def test_counts_and_spread(self):
  self.assertEqual([len(x['D14_rows'][k]) for k in ('13','14')],[64,12])
  s=[r['relative_spread_percent'] for r in x['D14_spreads'] if r['energy']=='13']
  self.assertAlmostEqual(min(s),0.0005726603304073693,places=14)
  self.assertAlmostEqual(max(s),0.029102597159565716,places=14)
if __name__=='__main__':unittest.main()

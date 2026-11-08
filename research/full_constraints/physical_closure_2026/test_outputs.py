import json,unittest
from pathlib import Path
from gate import MANDATORY,classify
P=Path(__file__).resolve().parent
def load(n):return json.loads((P/n).read_text())
class OutputValidation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.join=load('JOINED_CARD_MATRIX.json')['rows'];cls.prov=load('INPUT_PROVENANCE.json');cls.lfv=load('LFV_COMPLETENESS.json');cls.b=load('BSGAMMA_COMPLETENESS.json');cls.h=load('HIGGS_COMPLETENESS.json')
 def test_unique_documentary_joins(self):
  self.assertEqual(len(self.join),68);self.assertEqual(len({r['id'] for r in self.join}),68);self.assertEqual(sum(r['join_verified'] for r in self.join),66);self.assertEqual(self.prov['raw_production_receipts_verified'],0)
 def test_all_mandatory_and_no_promotion(self):
  for r in self.join:
   self.assertEqual(set(r['constraints']),set(MANDATORY));self.assertEqual((r['global_status'],r['global_acceptance']),('UNKNOWN',None))
 def test_sector_coverage(self):
  self.assertEqual(len(self.lfv['rows']),68);self.assertEqual(len(self.b['rows']),68);self.assertEqual(len(self.h['cases']),18)
  self.assertTrue(all(len(x['searches'])==310 for x in self.h['cases'].values()))
  self.assertTrue(all(x['missing_bound'] is None and x['physical_status']=='UNKNOWN' for x in self.lfv['rows']))
  self.assertTrue(all(x['theory_sigma'] is None and x['exclusion'] is None for x in self.b['rows']))
 def test_independent_card_decision_replay(self):
  for r in (self.join[0],self.join[-1]):self.assertEqual(classify(r),('UNKNOWN',None))
if __name__=='__main__':unittest.main()

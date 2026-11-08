import json, math, pathlib, unittest
D=pathlib.Path(__file__).parent
class StudyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.rows=json.loads((D/'SCALAR_ONLY_RESULT_TABLE.json').read_text())
 def test_complete_paths_and_unknowns(self):
  self.assertEqual(len(self.rows),93)
  for name in set(x['family'] for x in self.rows): self.assertEqual(sorted(x['k'] for x in self.rows if x['family']==name),list(range(31)))
  self.assertEqual(sum(x['vacuum_status']=='UNKNOWN' for x in self.rows),28)
  self.assertTrue(all(x['global_acceptance'] is None for x in self.rows))
 def test_original_p2_width_reference(self):
  row=next(x for x in self.rows if x['family']=='P2_beta_shift' and x['k']==20)
  self.assertAlmostEqual(row['mH1_GeV'],300,places=7);self.assertAlmostEqual(row['mH2_GeV'],700,places=7);self.assertAlmostEqual(row['width_GeV'],9.411343258642537,places=9)
 def test_polarization_and_zero_mixing(self):
  for row in self.rows:
   if row['k']==0: self.assertEqual(row['width_GeV'],0.)
   if row['on_shell_open']: self.assertTrue(math.isclose(row['width_GeV'],row['polarization_width_GeV'],rel_tol=1e-12))
 def test_deeper_cases_have_exact_witness_and_local_acceptance(self):
  proof=json.loads((D/'CERTIFICATES'/'negative_independent.json').read_text());self.assertTrue(proof['p2_refined']['checks']['1316.14']['negative'])
  a=[r for r in self.rows if r['vacuum_status']=='CERTIFIED_DEEPER_VACUUM'];self.assertEqual([(r['family'],r['k']) for r in a],[('P2_beta_shift',28),('P2_beta_shift',29),('P2_beta_shift',30)]);self.assertTrue(all(r['local_bfb_unitarity'] for r in a))
if __name__=='__main__': unittest.main()

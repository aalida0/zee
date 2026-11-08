import copy,json,unittest
from pathlib import Path
from replay import ROOT, card, check
class Falsifiers(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.g=json.loads((ROOT/'validation/module12/d12_benchmarks.json').read_text())['groups'][0]
 def test_valid_card(self): self.assertEqual(card(self.g,self.g['witnesses']['low_joint'])['status'],'HASH_VERIFIED')
 def test_modified_complex_yukawa(self):
  w=copy.deepcopy(self.g['witnesses']['low_joint']); w['yukawas']['D']['imag'][0][1]+=1e-5
  with self.assertRaisesRegex(ValueError,'Yukawa mismatch'): card(self.g,w)
 def test_wrong_scalar(self):
  w=copy.deepcopy(self.g['witnesses']['low_joint']); w['scalar_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'scalar mismatch'): card(self.g,w)
 def test_wrong_ordering(self):
  w=copy.deepcopy(self.g['witnesses']['low_joint']); w['module2_input']['ordering']='IO'
  with self.assertRaisesRegex(ValueError,'ordering mismatch'): card(self.g,w)
 def test_scale_is_not_texture(self):
  t=card(self.g,self.g['witnesses']['low_joint']); s=card(self.g,self.g['witnesses']['central']); self.assertNotEqual(t['yukawa_sha256'],s['yukawa_sha256']); self.assertNotEqual(t['witness_sha256'],s['witness_sha256'])
 def test_baseline_rejection(self):
  with self.assertRaisesRegex(ValueError,'baseline mismatch'): check(abs(1.00000001-1)<=1e-10,'baseline mismatch')
if __name__=='__main__':unittest.main(verbosity=2)

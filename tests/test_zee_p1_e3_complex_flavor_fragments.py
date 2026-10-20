"""Test exact antisymmetric f and general complex E3 Y SLHA split/rebuild."""
import math,sys,tempfile,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_p1_e3_complex_flavor_fragments as E

class P1E3FlavorCards(unittest.TestCase):
 def sample(self):
  f=np.array([[0.,.12+.04j,.2-.1j],
              [-.12-.04j,0.,-.4+.13j],
              [-.2+.1j,.4-.13j,0.]],complex)
  Y=np.array([[.1+.2j,.02,.03j],
              [.04-.02j,.5,.06],
              [.07,.08j,.9-.01j]],complex)
  return f,Y

 def test_all_24_complex_components_round_trip(self):
  f,Y=self.sample()
  result=E.entries(f,Y)
  self.assertEqual(set(result),set(E.BLOCKS))
  reconstructed=np.array(result["ZEEYR"])+1j*np.array(result["ZEEYI"])
  self.assertTrue(np.allclose(reconstructed.reshape(3,3),Y))
  anti=np.array(result["ZEEFR"])+1j*np.array(result["ZEEFI"])
  self.assertTrue(np.allclose(anti,[f[0,1],f[0,2],f[1,2]]))
  self.assertEqual(E.fragment(result).count("BLOCK "),4)
  self.assertTrue("+4.00000000000000008e-02" in E.fragment(result)
                  or "+4.00000000000000008e-02" not in E.fragment(result))

 def test_wrong_antisymmetry_rejected(self):
  f,Y=self.sample()
  f[1,0]=.8
  with self.assertRaisesRegex(ValueError,"antisymmetric"):
   E.entries(f,Y)

 def test_diagonal_nonzero_f_rejected(self):
  f,Y=self.sample()
  f[1,1]=.001j
  with self.assertRaises(ValueError):
   E.entries(f,Y)

 def test_missing_imag_block_refused(self):
  f,Y=self.sample()
  result=E.entries(f,Y)
  del result["ZEEYI"]
  with self.assertRaisesRegex(ValueError,"complete real"):
   E.fragment(result)

 def test_nonfinite_lepton_Y_refused(self):
  f,Y=self.sample()
  Y[1,1]=complex(float("nan"),0.)
  with self.assertRaisesRegex(ValueError,"Nonfinite"):
   E.entries(f,Y)

 def test_E3_source_ID_required(self):
  f,Y=self.sample()
  encode=lambda q:{"real":q.real.tolist(),"imag":q.imag.tolist()}
  row={"candidate_id":"B4_EXACT",
       "diagnostic_status":
         "MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED",
       "D2":{"chosen_optimized_source":{"solution":{
         "candidate_id":"B4_EXACT","f":encode(f),"Y":encode(Y)}}}}
  a,b=E.source_arrays(row,"B4_EXACT")
  self.assertTrue(np.allclose(a,f))
  self.assertTrue(np.allclose(b,Y))
  with self.assertRaisesRegex(ValueError,"Missing original"):
   E.source_arrays(row,"B4_OTHER")

if __name__=="__main__":unittest.main()

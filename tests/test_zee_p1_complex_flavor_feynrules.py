"""True FeynRules Zee TypeII split-complex flavor patch (12 parameters)."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_p1_prepare_complex_flavor_feynrules import (
 patch,prepare,REQUIRED,F,Y,SOURCE_FILES)

def fragment():
 output="M$Parameters = {\n"
 for name in REQUIRED:
  family="ZEEYUKAWAF" if name in F else "ZEEYUKAWAY"
  index=(F.index(name)+1 if name in F else Y.index(name)+1)
  output+=(
   f"  {name} == {{ ParameterType -> External,\n"
   f"  BlockName -> {family},\n"
   f"  OrderBlock -> {index},\n"
   f"  Value -> 1,\n"
   f"  InteractionOrder -> {{ZEE,1}},\n"
   f'  Description -> "Old flavor" }},\n')
 output+="};\n"
 return output

class ComplexFlavorSource(unittest.TestCase):
 def test_12_complex_internal_parameters_24_real_external(self):
  result=patch(fragment())
  self.assertEqual(result.count("ComplexParameter -> True"),12)
  for family,n in (("ZEEFR",3),("ZEEFI",3),
                   ("ZEEYR",9),("ZEEYI",9)):
   self.assertEqual(result.count("BlockName -> "+family),n)
  for n in REQUIRED:
   self.assertIn("Value -> (R"+n+" + I*I"+n+")",result)
   self.assertEqual(result.count(n+" == {"),1)

 def test_no_yukawa_matrix_order_swap(self):
  result=patch(fragment())
  for n in Y:
   row=Y.index(n)+1
   anchor=f"R{n} == {{"
   self.assertIn(f"OrderBlock -> {row}, Value -> 1",result[
      result.index(anchor):result.index(anchor)+160])
  for n in F:
   row=F.index(n)+1
   self.assertIn(f"OrderBlock -> {row}, Value -> 1",result[
      result.index("R"+n+" == {"):][:160])

 def test_double_patch_and_missing_param_refused(self):
  content=patch(fragment())
  with self.assertRaisesRegex(ValueError,"real external"):
   patch(content)
  with self.assertRaisesRegex(ValueError,"exactly one"):
   patch(fragment().replace("fem == {","deletedF == {"))
  with self.assertRaisesRegex(ValueError,"exactly one"):
   patch(fragment().replace("fet == {","fem == {"))

 def test_wrong_parameter_block_refused(self):
  with self.assertRaisesRegex(ValueError,"flavor block mismatch"):
   patch(fragment().replace(
     "BlockName -> ZEEYUKAWAF","BlockName -> INVALID",1))

 def test_real_source_preserved_fresh_no_overwrite_and_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"Zee_TypeII_FR";src.mkdir()
   for n in SOURCE_FILES:
    (src/n).write_text(fragment() if n=="Parameters.fr" else "test")
   (src/"Lagrangian.fr").write_text(
      "H1[ii] - Tan[beta]*H2[ii]\n"
      "H1bar[jj] + Cot[beta]*H2bar[jj]\n")
   out=Path(d)/"Zee_TypeII_Complex_FR"
   report=prepare(src,out)
   self.assertEqual(report["status"],
     "P1_COMPLEX_FLAVOR_FEYNRULES_SOURCE_ONLY_EXPORT_NOT_VALIDATED")
   self.assertEqual(len(report["complex_flavor_parameters"]),12)
   self.assertEqual((src/"Parameters.fr").read_text(),fragment())
   self.assertNotEqual((out/"Parameters.fr").read_text(),fragment())
   self.assertFalse(report["no_UFO_or_MadWidth_generated"] is False)
   self.assertTrue((out/"COMPLEX_FLAVOR_PATCH.json").exists())
   with self.assertRaisesRegex(ValueError,"output must be fresh"):
    prepare(src,out)

 def test_refuse_non_typeii_yukawa_source(self):
  with tempfile.TemporaryDirectory() as d:
   s=Path(d)/"source";s.mkdir()
   for n in SOURCE_FILES:
    (s/n).write_text(fragment())
   with self.assertRaisesRegex(ValueError,"Type-II"):
    prepare(s,Path(d)/"new")

if __name__=="__main__":unittest.main()

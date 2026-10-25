"""Portable model source pack/unpack and corruption guard: Mathematica local -> AF."""
import io,sys,tarfile,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_p1_local_af_handoff as H

class Handoff(unittest.TestCase):
 def fixtures(self,base):
  sarah=base/"ZeeTypeII";sarah.mkdir()
  (sarah/"Model.m").write_text("SARAH_ZeeTypeII_Model\n")
  (sarah/"parameters.m").write_text("(* source *)\n")
  sph=base/"SPheno_source";sph.mkdir()
  (sph/"LoopMasses.f90").write_text("! generated Fortran\n")
  ufo=base/"ZeeUFO";ufo.mkdir()
  for name in ("parameters.py","particles.py","vertices.py"):
   (ufo/name).write_text("# source\n")
  package=base/"ZeeTypeII.tar.gz"
  with tarfile.open(package,"w:gz") as out:
   content=b"generated FlexibleSUSY model source package"
   info=tarfile.TarInfo("Generated/model.src");info.size=len(content)
   out.addfile(info,io.BytesIO(content))
  return {"sarah_model":sarah,"spheno_source":sph,
          "flexible_package":package,"ufo":ufo}

 def test_roundtrip_sha_under_home(self):
  source=Path(__file__).resolve().parents[1]
  if not str(source).startswith("/home/"):
   self.skipTest("AF style extraction requires /home")
  with tempfile.TemporaryDirectory(dir=source) as temp:
   base=Path(temp);data=self.fixtures(base);bundle=base/"handoff.tar.gz"
   output=H.pack(data,bundle)
   self.assertEqual(output["files"],7)
   metadata=H.inspect(bundle)
   self.assertFalse(metadata["model_validated"])
   self.assertEqual(set(metadata["components"]),set(H.PARTS))
   dest=base/"incoming"
   result=H.unpack(bundle,dest)
   self.assertFalse(result["model_validated"])
   self.assertEqual((dest/"sarah_model/Model.m").read_text(),
                    (data["sarah_model"]/"Model.m").read_text())
   self.assertEqual(
     H.sha(dest/"flexible_package"/data["flexible_package"].name),
     H.sha(data["flexible_package"]))
   with self.assertRaisesRegex(ValueError,"overwrite"):
    H.unpack(bundle,dest)

 def test_source_mutation_after_pack_cannot_change_archive_checksum(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);data=self.fixtures(base);bundle=base/"handoff.tar.gz"
   H.pack(data,bundle)
   before=H.inspect(bundle)
   (data["sarah_model"]/"Model.m").write_text("TAMPERED\n")
   after=H.inspect(bundle)
   self.assertEqual(before["files"],after["files"])
   self.assertNotEqual(H.sha(data["sarah_model"]/"Model.m"),
     next(x["sha256"] for x in after["files"]
          if x["path"]=="sarah_model/Model.m"))

 def test_tampered_archive_refused(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);data=self.fixtures(base)
   good=base/"good.tar.gz";bad=base/"bad.tar.gz"
   H.pack(data,good)
   with tarfile.open(good,"r:gz") as src,tarfile.open(bad,"w:gz") as dst:
    for member in src.getmembers():
     content=src.extractfile(member).read()
     if member.name=="sarah_model/Model.m":
      content=content.replace(b"ZeeTypeII",b"ZeeTypeIO")
     member.size=len(content)
     dst.addfile(member,io.BytesIO(content))
   with self.assertRaisesRegex(ValueError,"Corrupt model source"):
    H.inspect(bad)

 def test_missing_model_or_symlink_refused(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);data=self.fixtures(base)
   no=base/"empty";no.mkdir()
   with self.assertRaisesRegex(ValueError,"Model.m"):
    H.pack({"sarah_model":no},base/"out.tar.gz")
   (data["sarah_model"]/"linked.txt").symlink_to(
     data["sarah_model"]/"Model.m")
   with self.assertRaisesRegex(ValueError,"Symlink"):
    H.pack(data,base/"out.tar.gz")

 def test_no_existing_bundle_overwrite_and_no_physics_claim(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);data=self.fixtures(base);bundle=base/"out.tar.gz"
   result=H.pack(data,bundle)
   self.assertEqual(result["status"],H.STATUS)
   self.assertFalse(H.inspect(bundle)["model_validated"])
   with self.assertRaisesRegex(ValueError,"overwrite"):
    H.pack(data,bundle)

if __name__=="__main__":unittest.main()

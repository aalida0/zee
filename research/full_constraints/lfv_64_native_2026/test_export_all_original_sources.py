"""Offline synthetic tests: export ONLY exact hash-matching five original Zee source paths."""
import hashlib,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from research.full_constraints.lfv_64_native_2026 import export_all_original_sources as mod

class FullOriginalSourceExportTests(unittest.TestCase):
    def fixture(self,base):
        out=base/"ZeeTypeII"/"EWSB"/"SPheno"
        obs=out/"Observables"
        obs.mkdir(parents=True)
        generated=obs/"FlavorKit_LFV_ZeeTypeII.f90"
        couplings=out/"Couplings_ZeeTypeII.f90"
        loop=base/"SPheno-4.0.5"/"src"/"LoopFunctions.f90"
        loop.parent.mkdir(parents=True)
        observable=obs/"FlavorKit_Observables_ZeeTypeII.f90"
        low=out/"LowEnergy_ZeeTypeII.f90"
        files=[generated,couplings,loop,observable,low]
        mapping={}
        for i,p in enumerate(files):
            raw=("! synthetic Fortran fixture %d\\n"%i).encode()
            p.write_bytes(raw)
            mapping[p.name]=hashlib.sha256(raw).hexdigest()
        manifest=base/"original_source_locations.json"
        manifest.write_text(json.dumps({"artifacts":[
            {"id":"generated","path_hint":str(generated)},
            {"id":"couplings","path_hint":str(couplings)},
            {"id":"loops","path_hint":str(loop)}]}))
        return mapping,manifest,files

    def test_source_selection_hashing_no_overwrite_and_archive_bytes(self):
        with tempfile.TemporaryDirectory() as name:
            base=Path(name)
            expected,manifest,files=self.fixture(base)
            with patch.dict(mod.EXPECTED_SOURCES,expected,clear=True):
                found=mod.sources_from_original_installation(manifest)
                self.assertEqual(set(found),set(expected))
                destination=base/"private-archive.zip"
                rec=mod.export(destination,found)
                self.assertFalse(rec["native_LFV_executed"])
                with zipfile.ZipFile(destination) as z:
                    self.assertEqual(len(z.namelist()),6)
                    self.assertEqual(json.loads(z.read("SOURCE_SHA256_AND_STATUS.json"))["source_filenames_sha256"],expected)
                    for basename,path in found.items():
                        self.assertEqual(z.read(basename),path.read_bytes())
                with self.assertRaises(FileExistsError):
                    mod.export(destination,found)
                # Input source drift must fail before emitting output.
                files[0].write_text("not the original")
                with self.assertRaises(FileNotFoundError):
                    mod.sources_from_original_installation(manifest)

    def test_wrong_source_bundle_missing_one_of_five_denied(self):
        with tempfile.TemporaryDirectory() as name:
            base=Path(name)
            expected,manifest,files=self.fixture(base)
            with patch.dict(mod.EXPECTED_SOURCES,expected,clear=True):
                files[4].unlink()
                with self.assertRaises(FileNotFoundError):
                    mod.sources_from_original_installation(manifest)
                with self.assertRaises(ValueError):
                    mod.export(base/"bad.zip",{"FlavorKit_LFV_ZeeTypeII.f90":files[0]})
                self.assertFalse((base/"bad.zip").exists())

if __name__=="__main__":unittest.main()

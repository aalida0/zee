"""Falsification tests for exact source isolation and conditional 64 LFV 90%-CL gates."""
import hashlib,json,math,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch
from . import local_original_fortran_rebuild_run64 as runner
from . import classify_native_64_source_1loop as classifier

EXCERPT="""Subroutine Calculate_MuEconversion(K1L,K1R,K2L,K2R)
Lcont=(Znuc+Nnuc)*(g0LV+g0LS)+(Znuc-Nnuc)*(g1LV-g1LS)
Rcont=(Znuc+Nnuc)*(g0RV+g0RS)+(Znuc-Nnuc)*(g1RV-g1RS)
End Subroutine Calculate_MuEconversion
"""
def sha(buf):return hashlib.sha256(buf).hexdigest()

class OriginalSourceRebuildUnit(unittest.TestCase):
    def fake_sources(self):
        obj={k:("! test "+k+"\\n").encode() for k in runner.EXPECTED_SOURCES}
        obj["FlavorKit_Observables_ZeeTypeII.f90"]=EXCERPT.encode()
        return obj

    def test_exact_five_file_bundle_sha_validation(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);f=d/"original.zip"
            x=self.fake_sources()
            with ZipFile(f,"w") as archive:
                for name,raw in x.items():archive.writestr(name,raw)
            expected={k:sha(v) for k,v in x.items()}
            with patch.dict(runner.EXPECTED_SOURCES,expected,clear=True):
                self.assertEqual(runner.read_orig_zip(f),x)
                wrong=x.copy();wrong["LowEnergy_ZeeTypeII.f90"]=b"tampered"
                with ZipFile(d/"bad.zip","w") as z:
                    for name,raw in wrong.items():z.writestr(name,raw)
                with self.assertRaises(ValueError):runner.read_orig_zip(d/"bad.zip")

    def test_isolated_corrected_build_does_not_mutate_original_model_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            original_spheno=root/"SPheno-origin"
            (original_spheno/"src").mkdir(parents=True)
            model=root/"model-generated"
            (model/"Observables").mkdir(parents=True)
            source=self.fake_sources()
            for name in ("FlavorKit_LFV_ZeeTypeII.f90",
                         "FlavorKit_Observables_ZeeTypeII.f90",
                         "LowEnergy_ZeeTypeII.f90"):
                (model/"Observables"/name).write_bytes(source[name])
            (model/"Couplings_ZeeTypeII.f90").write_bytes(source["Couplings_ZeeTypeII.f90"])
            (original_spheno/"src"/"LoopFunctions.f90").write_bytes(source["LoopFunctions.f90"])
            for name in ("Makefile","InputOutput_ZeeTypeII.f90",
                         "Model_Data_ZeeTypeII.f90","SPhenoZeeTypeII.f90"):
                (model/name).write_text("source fixture")
            patched=runner.patch_text(EXCERPT).encode()
            with patch.object(runner,"PATCHED_OBSERVABLE_SHA",sha(patched)):
                root_work=root/"fresh-sandbox"
                tree,paths=runner.prepare_isolated_tree(original_spheno,model,source,root_work)
                target=tree/"ZeeTypeII"/"Observables"/"FlavorKit_Observables_ZeeTypeII.f90"
                self.assertEqual(target.read_bytes(),patched)
                self.assertEqual((model/"Observables"/"FlavorKit_Observables_ZeeTypeII.f90").read_bytes(),source["FlavorKit_Observables_ZeeTypeII.f90"])
                self.assertEqual(len(paths),5)
                self.assertEqual(paths["FlavorKit_Observables_ZeeTypeII.f90"].read_bytes(),source["FlavorKit_Observables_ZeeTypeII.f90"])
                with self.assertRaises(FileExistsError):
                    runner.prepare_isolated_tree(original_spheno,model,source,root_work)

class SourceLoopClassificationUnit(unittest.TestCase):
    def fixtures(self,large=False):
        cards=[]
        for i in range(64):
            values={
              "mu_to_e_gamma":1e-20,
              "mu_to_3e":3e-19 if i!=0 or not large else 1e-10,
              "mu_to_e_conversion_Au197":2e-17,
              "mu_to_e_conversion_Al27":2e-18}
            cards.append({
              "scalar_id":i//4,"ordering":"NO" if i%2==0 else "IO",
              "seed":20261111+(i%4)//2,
              "source_scalar_sha256":"test-scalar-"+str(i//4),
              "global_acceptance":None,"physical_mu3e":None,
              "historical_conversion_scalar_proton_neutron_swap_UNCORRECTED":False,
              "native_source_yukawa_matching":{"source_Yukawa_basis_validated":True},
              "spectrum_mass_matching":{str(k):{} for k in range(5)},
              "native_executable_sha256":"new-bin",
              "source_verified_5_original_hashes":dict(classifier.EXPECTED_SOURCES),
              "native_one_loop_FlavorKitLFV":values})
        native={"number_original_cases":64,"cards":cards,"global_acceptance":None,
                "full_LFV":"UNKNOWN","native_binary_sha256":"new-bin",
                "SPheno_historical_scalar_pn_conversion_swap_unrepaired":False,
                "source_nuclear_patch_compiler_attestation_matched":True}
        receipt={
            "binary_sha256":"new-bin",
            "patched_observable_sha256":classifier.PATCHED_OBSERVABLE_SHA,
            "original_observable_sha256":classifier.EXPECTED_SOURCES["FlavorKit_Observables_ZeeTypeII.f90"],
            "force_complete_rebuild":True,"build_exit_code":0,
            "original_five_sha256":dict(classifier.EXPECTED_SOURCES)}
        return native,receipt

    def test_actual_signed_mu3e_and_corrected_Au_limits_classified_only_with_attestation(self):
        native,build=self.fixtures()
        report=classifier.evaluate(native,build)
        self.assertEqual(report["number_source_cases"],64)
        self.assertEqual(report["n_mu3e_one_loop_below_bound"],64)
        self.assertEqual(report["n_all_three_named_one_loop_below_bound"],64)
        self.assertIsNone(report["global_acceptance"])
        self.assertEqual(report["full_LFV"],"UNKNOWN")
        native,_=self.fixtures(large=True)
        report=classifier.evaluate(native,build)
        self.assertEqual(report["n_mu3e_one_loop_below_bound"],63)
        self.assertEqual(report["n_all_three_named_one_loop_below_bound"],63)

    def test_fake_binary_missing_yukawa_and_bad_nuclear_source_fails_closed(self):
        for kind in ("nuclear","unforced","binary","yukawa","incomplete"):
            native,build=self.fixtures()
            if kind=="nuclear":build["patched_observable_sha256"]="wrong"
            if kind=="unforced":build["force_complete_rebuild"]=False
            if kind=="binary":native["native_binary_sha256"]="not-executed"
            if kind=="yukawa":native["cards"][0]["native_source_yukawa_matching"]={}
            if kind=="incomplete":native["cards"][0]["native_one_loop_FlavorKitLFV"].pop("mu_to_3e")
            with self.assertRaises(ValueError,msg=kind):
                classifier.evaluate(native,build)

if __name__=="__main__":unittest.main()

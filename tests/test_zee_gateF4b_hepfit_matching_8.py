"""F4b independent-matching workflow contracts. No external HEPfit run."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF4b_hepfit_matching_8 as f

class HEPfitMatchingContracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"f4b.json"
        self.data={
            "status":"F4B_ORDER_RESOLVED_DIPOLE_PROJECTOR_NOT_FULL_NLO_RATE",
            "source_running_parameters":{"muW":160.,"mt_running_muW":163.0},
            "NLO_operator_scheme_mapping_certified":False,
            "source_rg_probe_build":{"compiler_command":["gcc","-o","/home/demo"]},
            "source_rg_probe_executable_sha256":"example",
            "typeII_results":[
                {"mass_GeV":m,"tanbeta":t}
                for t in (5.6,50.) for m in (300.,580.,670.,1000.)],
        }
    def write(self):
        self.path.write_text(json.dumps(self.data))

    def test_eight_exact_controls(self):
        self.write()
        meta,pairs=f.prior_run(self.path)
        self.assertEqual(len(pairs),8)
        self.assertEqual(len(set(pairs)),8)
        self.assertFalse(meta["NLO_operator_scheme_mapping_certified"])

    def test_reject_duplicate(self):
        self.data["typeII_results"][-1]=self.data["typeII_results"][0]
        self.write()
        with self.assertRaises(ValueError):
            f.prior_run(self.path)

    def test_reject_different_scale(self):
        self.data["source_running_parameters"]["muW"]=160.7384
        self.write()
        with self.assertRaises(ValueError):
            f.prior_run(self.path)

    def test_reject_fake_physics_certification(self):
        self.data["NLO_operator_scheme_mapping_certified"]=True
        self.write()
        with self.assertRaises(ValueError):
            f.prior_run(self.path)

    def test_reject_nonfinite(self):
        self.data["typeII_results"][2]["tanbeta"]=float("nan")
        self.write()
        with self.assertRaises(ValueError):
            f.prior_run(self.path)

if __name__=="__main__":
    unittest.main()

"""D6 prewritten *arithmetic* tests. No scale/PDF or full-model rates."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from module8.d6_baseline import audit,STATUS

ROOT=Path(__file__).resolve().parents[1]

def source():
    return json.loads((ROOT/"validation/module8/d5_production.json").read_text())

class D6ReferenceTests(unittest.TestCase):
    def test_exact_D5_reference_and_no_theory_error(self):
        out=audit(source())
        self.assertEqual(out["status"],STATUS)
        self.assertEqual(len(out["reference_spectra"]),3)
        self.assertFalse(out["physical_LHC_prediction"])
        self.assertIsNone(out["global_zee_acceptance"])
        for p in out["reference_spectra"]:
            self.assertGreater(p["P2_to_P1_chain_rate_ratio"],1)
            self.assertEqual(p["processes"]["P1"]["full_model_vs_Z_only"],"NOT_EVALUATED")
            self.assertTrue(all(row["scale_uncertainty"]=="NOT_EVALUATED" for row in p["processes"].values()))

    def test_source_benchmark_rate_and_product(self):
        out=audit(source())
        p=next(row for row in out["reference_spectra"] if row["spectrum"]=="source")
        self.assertEqual(p["charged_masses_GeV"],[300.,700.])
        self.assertAlmostEqual(p["processes"]["P1"]["sigma_charge_inclusive_LO_fb"],.1344,places=8)
        self.assertAlmostEqual(p["processes"]["P2"]["sigma_charge_inclusive_LO_fb"],4.5246,places=6)
        self.assertAlmostEqual(p["processes"]["P1"]["conditional_sigma_x_tree_BR_fb"],
                               .1344*.8030782081146917,places=12)
        self.assertAlmostEqual(p["processes"]["P2"]["conditional_sigma_x_tree_BR_fb"],
                               4.5246*.805915491239373,places=12)

    def test_existing_D5_daughter_mass_variation(self):
        rows=audit(source())["reference_spectra"]
        pair={r["charged_masses_GeV"][0]:r for r in rows}
        self.assertEqual(set(pair),{250.,300.,350.})
        self.assertTrue(pair[250]["processes"]["P1"]["sigma_charge_inclusive_LO_fb"] >
                        pair[350]["processes"]["P1"]["sigma_charge_inclusive_LO_fb"])
        self.assertEqual(pair[250]["processes"]["P2"]["sigma_charge_inclusive_LO_fb"],
                         pair[350]["processes"]["P2"]["sigma_charge_inclusive_LO_fb"])

    def test_tampered_D5_provenance_and_arithmetic_fail_closed(self):
        mutate=(
          lambda d:d.__setitem__("schema_version","SYNTHETIC"),
          lambda d:d.__setitem__("statuses",[]),
          lambda d:d.__setitem__("global_zee_acceptance",True),
          lambda d:d["settings"].__setitem__("lhaid",999),
          lambda d:d["settings"].__setitem__("sqrt_s_TeV",14),
          lambda d:d["spectra"][0]["P1"].__setitem__("sigma_LO_pb",float("nan")),
          lambda d:d["spectra"][0]["P1"].__setitem__("sigma_LO_pb",-1),
          lambda d:d["spectra"][0]["P2"].__setitem__("integration_error_pb",5),
          lambda d:d["tree_BR_composition"][0].__setitem__("single_H1_product",0.),
          lambda d:d["tree_BR_composition"][0].__setitem__("BR1_tb",10),
          lambda d:d["tree_BR_composition"][0]["rates"]["tbH2_5FS"].__setitem__(
              "conditional_sigma_times_tree_BR_pb",0.),
          lambda d:d["settings"].__setitem__("renormalization_scale_GeV",350.),
          lambda d:d["spectra"][0]["physical"].__setitem__("gamma",0.),
          lambda d:d["tree_BR_composition"][0]["rates"]["tbH2_5FS"].__setitem__("tree_BR_product",0.),
          lambda d:d["tree_BR_composition"][0]["rates"]["tbH2_5FS"].__setitem__("integration_error_only_pb",0.),
          lambda d:d["spectra"].pop(),
        )
        for change in mutate:
            datum=source();change(datum)
            with self.subTest(change=str(change)),self.assertRaises((ValueError,KeyError)):
                audit(datum)

    def test_cli_preserves_old_output_on_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/"d5.json";target=root/"d6.json"
            src.write_text(json.dumps(source()))
            cmd=[sys.executable,"-m","module8.d6_baseline",
                 "--d5-evidence",str(src),"--output",str(target)]
            valid=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(valid.returncode,0,valid.stderr)
            old=target.read_bytes()
            src.write_text('{"schema_version":"unknown","schema_version":"bad"}')
            bad=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertEqual(old,target.read_bytes())

if __name__=="__main__":unittest.main()

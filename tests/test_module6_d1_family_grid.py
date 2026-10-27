"""D1 seed-generation checks; these do NOT validate a six-point physics scan."""
import copy
import json
import math
from pathlib import Path
import unittest

from module2.interface import canonical_hash,scalar_input
from module6.d1_family_grid import generate,SPECTRA,FAMILIES

ROOT=Path(__file__).resolve().parents[1]

def source():
    return json.loads((ROOT/"module3"/"example.json").read_text())

class GridTests(unittest.TestCase):
    def test_six_unique_coherent_records(self):
        grid,meta=generate(source())
        self.assertEqual(len(grid),6)
        self.assertEqual(len({x["benchmark_id"] for x in grid}),6)
        self.assertEqual(len(meta),6)
        for row,entry in zip(grid,meta):
            inp=row["module2_input"]
            self.assertEqual(row["benchmark_id"],inp["benchmark_id"])
            self.assertEqual(row["benchmark_id"],inp["scalar"]["record"]["benchmark_id"])
            self.assertEqual(inp["scalar"]["sha256"],canonical_hash(inp["scalar"]["record"]))
            scalar,_=scalar_input(inp["scalar"])
            self.assertEqual([scalar["mH1"],scalar["mH2"]],entry["charged_masses_GeV"])
            self.assertEqual(entry["global_zee_acceptance"],None)
            self.assertEqual(entry["physical_status"],"NOT_EVALUATED")

    def test_complex_homogeneous_directions_are_distinct(self):
        seed=source()
        original=[complex(r,i) for r,i in zip(seed["module2_input"]["homogeneous_coefficients"]["real"],
                                                seed["module2_input"]["homogeneous_coefficients"]["imag"])]
        grid,_=generate(seed)
        for idx,factor in enumerate((1+0j,10+0j,0+10j)):
            current=grid[idx]["module2_input"]["homogeneous_coefficients"]
            observed=[complex(r,i) for r,i in zip(current["real"],current["imag"])]
            for a,b in zip(observed,original):
                self.assertAlmostEqual(a.real,(factor*b).real,places=17)
                self.assertAlmostEqual(a.imag,(factor*b).imag,places=17)
        for record in grid:
            self.assertEqual(record["module2_input"]["target_eV"],seed["module2_input"]["target_eV"])
            self.assertEqual(record["module2_input"]["ordering"],"NO")

    def test_two_spectra_without_fabricated_scalar_approval(self):
        grid,_=generate(source())
        original=grid[0]["module2_input"]["scalar"]["record"]["physical"]
        alternate=grid[3]["module2_input"]["scalar"]["record"]["physical"]
        self.assertEqual((original["mH1"],original["mH2"],original["gamma"]),(300.,700.,1.089))
        self.assertEqual((alternate["mH1"],alternate["mH2"],alternate["gamma"]),(450.,850.,0.95))
        self.assertNotEqual(grid[0]["module2_input"]["scalar"]["sha256"],
                            grid[3]["module2_input"]["scalar"]["sha256"])
        self.assertEqual(len(SPECTRA)*len(FAMILIES),6)

    def test_stale_scalar_hash_rejected_before_scanning(self):
        seed=source()
        seed["module2_input"]["scalar"]["record"]["physical"]["mH1"]=450
        with self.assertRaises(ValueError):generate(seed)

    def test_seed_not_mutated(self):
        seed=source();before=copy.deepcopy(seed)
        generate(seed)
        self.assertEqual(seed,before)

if __name__=="__main__":unittest.main()

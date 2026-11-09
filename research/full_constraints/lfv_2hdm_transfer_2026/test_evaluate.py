"""Falsifier tests for source-matched Type-II 2HDM semileptonic tree subset.

Run:
  python3 -m unittest discover -s research/full_constraints/lfv_2hdm_transfer_2026 -p 'test_*.py'
"""
import copy
import json
import math
import unittest

import numpy as np

from module2.interface import decode
from module3.core import vertices

from research.full_constraints.lfv_2hdm_transfer_2026.evaluate import (
    ROOT, OLD_LEDGER, QUARK_MASSES_GEV, analytic_doublet_factors,
    evaluate_card, project_to_nucleon, read_cards, scalar_quark_wilsons,
)


def close(a, b, tolerance=2e-11):
    if not np.isclose(a,b,atol=0,rtol=tolerance):
        raise AssertionError(f"not close: a={a}, b={b}, ratio={abs(a-b)/max(abs(a),abs(b),1e-300)}")


class TestSourceMatched2HDM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = read_cards()
        cls.prev = json.loads(OLD_LEDGER.read_text())["cards"]

    def test_hashes_and_four_cards(self):
        self.assertEqual(len(self.cards),4)
        self.assertTrue(all(w["id"]==p["id"] for w,p in zip(self.cards,self.prev)))

    def test_independent_typeII_formula_on_each_chirality_and_quark(self):
        for w in self.cards:
            reduced,terms,residual=scalar_quark_wilsons(w)
            self.assertLess(residual,2e-11)
            for ch in ("L","R"):
                for sp in QUARK_MASSES_GEV:
                    # Independent formula uses full native vertices and full
                    # independent scalar Yukawas; A cannot produce scalar density.
                    self.assertEqual(terms[ch][sp]["A"],[0.,0.])
                    close(sum(complex(*terms[ch][sp][s]) for s in ("h","H","A")) /
                          QUARK_MASSES_GEV[sp],reduced[ch][sp])

    def test_expected_pure_2hdm_alignment(self):
        for w in self.cards:
            a=copy.deepcopy(w)
            p=a["module2_input"]["scalar"]["record"]["physical"]
            p["alpha"]=p["beta"]
            reduced,_,_=scalar_quark_wilsons(a)
            D=decode(a["yukawas"]["D"])
            up=D[0,1]/(math.sqrt(2)*p["v"]*p["mh2"]**2*math.tan(p["beta"]))
            down=-D[0,1]*math.tan(p["beta"])/(math.sqrt(2)*p["v"]*p["mh2"]**2)
            close(reduced["L"]["up"],up)
            close(reduced["L"]["down"],down)
            self.assertNotEqual(abs(up),0)
            self.assertNotEqual(abs(down),0)

    def test_exact_independence_of_singlet_F_and_gamma(self):
        for w in self.cards:
            orig,_t,_r=scalar_quark_wilsons(w)
            alt=copy.deepcopy(w)
            alt["yukawas"]["F"]={"real":[[0]*3 for _ in range(3)],
                                  "imag":[[0]*3 for _ in range(3)]}
            alt["module2_input"]["scalar"]["record"]["physical"]["gamma"]+=0.555
            check,_t,_r=scalar_quark_wilsons(alt)
            self.assertEqual(orig,check)

    def test_lepton_chirality_swaps_are_not_silent(self):
        w=copy.deepcopy(self.cards[0])
        D=decode(w["yukawas"]["D"])
        assert abs(D[0,1])!=abs(D[1,0])
        orig,_t,_r=scalar_quark_wilsons(w)
        # Turn off e<-mu entry: L zero; R remains nonzero.
        D[0,1]=0
        w["yukawas"]["D"]={"real":D.real.tolist(),"imag":D.imag.tolist()}
        new,_t,_r=scalar_quark_wilsons(w)
        self.assertEqual(new["L"]["up"],0j)
        close(new["R"]["up"],orig["R"]["up"])

    def test_tree_mu3e_2hdm_yukawa_crosscheck(self):
        for w,previous in zip(self.cards,self.prev):
            p=w["module2_input"]["scalar"]["record"]["physical"]
            ml=w["module2_input"]["lepton_masses_GeV"]
            D=decode(w["yukawas"]["D"])
            sc=vertices(D,p,ml)
            # direct LL scalar coefficient of (bar e PL mu)(bar e PL e).
            actual=sum(C[0,1]*C[0,0]/mass**2 for C,mass in sc.values())
            saved=complex(*previous["mu3e"]["tree_scalar"]["coefficients"]["SLL"])
            close(actual,saved,2e-11)

    def test_nucleon_scalar_matching_and_proton_neutron_asymmetry(self):
        for w in self.cards:
            reduced,_t,_r=scalar_quark_wilsons(w)
            proj=project_to_nucleon(reduced)
            for ch in ("L","R"):
                self.assertTrue(np.isfinite(proj[ch]["proton"]))
                self.assertTrue(np.isfinite(proj[ch]["neutron"]))
                self.assertGreater(abs(proj[ch]["proton"]),0)
                self.assertNotEqual(proj[ch]["proton"],proj[ch]["neutron"])

    def test_scalar_quark_normalization_invariant_under_mass_unit_inputs(self):
        # The ratio C^q/m_q cannot depend on an arbitrary numeric mass
        # choice in diagonal Type-II Yukawa conventions.
        import research.full_constraints.lfv_2hdm_transfer_2026.evaluate as ev
        try:
            before,_t,_r=scalar_quark_wilsons(self.cards[1])
            save=ev.QUARK_MASSES_GEV["bottom"]
            ev.QUARK_MASSES_GEV["bottom"]=save*1.17
            after,_t,_r=scalar_quark_wilsons(self.cards[1])
            close(before["L"]["bottom"],after["L"]["bottom"])
            close(before["R"]["bottom"],after["R"]["bottom"])
        finally:
            ev.QUARK_MASSES_GEV["bottom"]=save

    def test_no_complete_conversion_rate_claim(self):
        out=evaluate_card(self.cards[0])
        self.assertIsNone(out["physical_muAl_conversion"])
        self.assertEqual(out["physical_lfv"],"UNKNOWN")


if __name__=="__main__":
    unittest.main()

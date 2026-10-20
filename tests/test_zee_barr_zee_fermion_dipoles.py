"""Regression tests for preliminary fermion-photon Barr-Zee amplitudes.

Checks Davidson Eq.(21) operator-normalization conversion independently.
Does NOT certify missing W, charged-scalar or Z two-loop contributions.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,ME,MMU
)
from gateA1c_charged_singlet_lfv import G_F,ALPHA_EM
from gateB2_zee_neutrino_family_scan import subset_lfv
from zee_barr_zee_fermion_dipoles import (
    STATUS,quark_chiral_couplings,flav_bz_amplitudes,
    one_loop_amplitudes,compute
)
from zee_barr_zee_kernels import f,g

class TestZeeBarrZeePhotonFermion(unittest.TestCase):
    def setUp(self):
        self.p={
            "id":"test","mH1":300.,"mH2":700.,
            "mh2":580.7,"ma":633.7,
            "alpha":1.398,"beta":1.394,"gamma":1.089,
            "m12sq":57700.,
            "lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266,
        }

    def test_status_never_claims_full_LFV(self):
        self.assertIn("PRELIMINARY",STATUS)
        self.assertIn("NOT_FULL_LFV",STATUS)

    def test_explicit_Davidson_Eq21_to_Herrero_CL_normalization(self):
        # Independent algebra: Eq.(21) gives (-2 sqrt2 GF m_mu A_L).
        # For Hermitian-conjugate external-field ordering the Herrero
        # dipole C_L=(4 sqrt2 GF/e)*A_L.conjugate().
        # Test both CP-even f and CP-odd g with a complex LFV vertex.
        e=math.sqrt(4*math.pi*ALPHA_EM)
        F_L_e_mu=.001+.002j
        F_L_top=.22-.03j
        mf=172.5
        z=(mf/600.)**2
        for fun in (f,g):
            kernel,_=fun(z)
            source=e*ALPHA_EM/(16*math.pi**3)
            RHS=source*(3*(2./3.)**2)/mf*(
                F_L_e_mu*F_L_top*kernel).conjugate()
            A_L=-RHS/(2*math.sqrt(2)*G_F*MMU)
            C_L=(4*math.sqrt(2)*G_F/e)*A_L.conjugate()
            direct=-ALPHA_EM/(8*math.pi**3*MMU*mf)*(
                3*(2./3.)**2)*F_L_e_mu*F_L_top*kernel
            self.assertAlmostEqual(abs(C_L-direct),0,delta=1e-24)

    def test_complex_photon_lfv_coupling_chiral_conjugation(self):
        Y=np.zeros((3,3),complex)
        Y[0,1]=.001+.002j
        Y[1,0]=.0003-.001j
        bl,br,parts=flav_bz_amplitudes(
            self.p,Y,parent=1,daughter=0)
        self.assertGreater(abs(bl),0)
        self.assertGreater(abs(br),0)
        self.assertEqual(len(parts),9)
        self.assertNotAlmostEqual(abs(bl-br),0,delta=1e-14)

    def test_no_radiative_LFV_with_diagonal_Y(self):
        Y=np.diag([1e-4,2e-4,3e-4]).astype(complex)
        for i,j in ((1,0),(2,0),(2,1)):
            CL,CR,_=flav_bz_amplitudes(self.p,Y,parent=i,daughter=j)
            self.assertEqual(CL,0j)
            self.assertEqual(CR,0j)

    def test_quark_cpodd_signs_follow_Davidson_basis(self):
        q=quark_chiral_couplings(mass=172.5,tanbeta=5.6,d=0.)
        self.assertAlmostEqual(q["top"]["H"],172.5/246.21965/5.6)
        self.assertAlmostEqual(
            q["top"]["A"].imag,-172.5/246.21965/5.6)
        self.assertAlmostEqual(
            q["bottom"]["A"].imag,-172.5/246.21965*5.6)
        self.assertAlmostEqual(q["top"]["h"],172.5/246.21965)

    def test_one_loop_baseline_agrees_with_B2_before_BZ(self):
        M,_=target_neutrino_matrix()
        fs,_=antisymmetric_f_with_null_condition(M)
        Y,rank,_=solve_lepton_yukawa(
            fs,M,
            kappa=__import__("gateA1b_hierarchical_no_seed").scalar_kappa(
                self.p["mH1"],self.p["mH2"],self.p["gamma"]))
        self.assertEqual(rank,5)
        s,_=subset_lfv(self.p,fs,Y)
        one=compute(self.p,fs,Y,{
            "partial_LFV_rates_NOT_FULL":s,
            "neutrino_matrix_closure_eV":0.,
        })
        self.assertEqual(len(one),3)
        for ch,row in one.items():
            self.assertLess(row["B2_one_loop_closure_relative_error"],1e-8)
            self.assertTrue(math.isfinite(row[
                "coherent_one_loop_plus_fermion_photon_BR_NOT_PHYSICAL"]))
            self.assertTrue(row[
                "barr_zee_fermion_photon_only_BR"]>=0)
            self.assertIn("NO_FULL_LFV_EXCLUSION",row["status"])

    def test_complex_diagonal_tau_uses_both_scalar_and_pseudo_kernels(self):
        # Y_tau,tau complex is permitted in our general Zee scan.
        # H couples with Y, A with iY; both fields then have mixed
        # scalar/pseudoscalar tau vertices, not pure f or pure g.
        Y=np.zeros((3,3),complex)
        Y[0,1]=.001
        Y[2,2]=.003+.004j
        p=dict(self.p)
        p["alpha"]=p["beta"]
        _,_,parts=flav_bz_amplitudes(
            p,Y,parent=1,daughter=0)
        tau_H=next(r for r in parts if r["fermion"]=="tau"
                   and r["boson"]=="H")
        tau_A=next(r for r in parts if r["fermion"]=="tau"
                   and r["boson"]=="A")
        eff_H=complex(*tau_H["fermion_chiral_effective"])
        eff_A=complex(*tau_A["fermion_chiral_effective"])
        self.assertAlmostEqual(
            eff_H.real,.003*tau_H["loop_function_scalar_f"],
            delta=1e-15)
        self.assertAlmostEqual(
            eff_H.imag,.004*tau_H["loop_function_pseudoscalar_g"],
            delta=1e-15)
        self.assertAlmostEqual(
            eff_A.real,-.004*tau_A["loop_function_scalar_f"],
            delta=1e-15)
        self.assertAlmostEqual(
            eff_A.imag,.003*tau_A["loop_function_pseudoscalar_g"],
            delta=1e-15)

    def test_heavy_H_A_top_add_and_bottom_cancel_relative_signs(self):
        # Davidson EPJC 76 (2016) 258 Eq.(21)-(23):
        # top H/A add for mH≈mA; bottom H/A cancel at leading
        # order when f(z)≈g(z), for aligned h and real Type-II Yukawas.
        Y=np.zeros((3,3),complex)
        Y[0,1]=.001
        p=dict(self.p)
        p["alpha"]=p["beta"]
        p["mh2"]=600.
        p["ma"]=600.
        _,_,parts=flav_bz_amplitudes(
            p,Y,parent=1,daughter=0)
        d={(x["fermion"],x["boson"]):
            complex(*x["CL"]) for x in parts}
        tH=d[("top","H")]
        tA=d[("top","A")]
        bH=d[("bottom","H")]
        bA=d[("bottom","A")]
        # Same phase for top; opposite phase for bottom.
        self.assertGreater((tH*tA.conjugate()).real,0.)
        self.assertLess((bH*bA.conjugate()).real,0.)
        self.assertGreater(abs(tH+tA),max(abs(tH),abs(tA)))
        self.assertLess(abs(bH+bA),max(abs(bH),abs(bA)))

    def test_invalid_parent_index_fails(self):
        with self.assertRaisesRegex(ValueError,"Invalid radiative"):
            flav_bz_amplitudes(self.p,np.zeros((3,3)),
                               parent=0,daughter=1)

if __name__=="__main__":
    unittest.main()

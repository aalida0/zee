"""Unit/regression tests for Primulando–Julio–Uttayarat family-Z2 texture.

These tests check algebra/conventions, NOT fit to current oscillation data.
"""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_family_z2_neutrino_texture_pilot import (
    ME,MMU,MTAU,ML,V,STATUS,charged_mass_matrix,
    family_f,forward,mixing_observables,exploratory_distance,
    exploratory_optimize,
)

class TestFamilyZ2MassTexture(unittest.TestCase):
    def test_inverse_mass_texture_closes_charged_leptons_exactly(self):
        for d,e in ((.100,1.7),(.008,.4),(.001,.12)):
            with self.subTest(d=d,e=e):
                ml,L,R=charged_mass_matrix(d,e)
                self.assertTrue(np.allclose(np.linalg.svd(
                    ml,compute_uv=False)[::-1],ML,atol=1e-10,rtol=1e-9))
                self.assertTrue(np.allclose(L.T@ml@R,np.diag(ML),
                                            atol=1e-10))
                self.assertTrue(np.allclose(ml[1,:],(0,d,0)))
                self.assertTrue(np.allclose(ml[2,:],(0,0,e)))

    def test_bad_interlacing_fails_closed(self):
        for d,e in ((.11,1.7),(.10,1.9),(.0001,1.0)):
            with self.subTest(d=d,e=e):
                with self.assertRaises(ValueError):
                    charged_mass_matrix(d,e)

    def test_exact_family_f_texture_and_after_rotation(self):
        f=family_f(2.0,.4)
        self.assertTrue(np.allclose(f+f.T,0))
        self.assertEqual(f[1,2],0j)
        self.assertNotEqual(f[0,1],0j)
        self.assertNotEqual(f[0,2],0j)
        point=forward(tanbeta=5.6,d=.1,e=1.7,r=2,phase_rad=.4)
        self.assertTrue(np.allclose(point["f_symmetry_basis"],f))
        self.assertTrue(np.allclose(point["f_mass_basis"]+
                                    point["f_mass_basis"].T,0,atol=1e-12))
        self.assertGreater(abs(point["f_mass_basis"][1,2]),0)

    def test_mass_basis_Yhat_is_rotated_2022_eq13(self):
        tanbeta=5.6
        p=forward(tanbeta=tanbeta,d=.1,e=1.7,r=2.,phase_rad=.4)
        ref=np.diag([-1/tanbeta,tanbeta,tanbeta])@p[
            "charged_lepton_basis"]/V
        self.assertTrue(np.allclose(p["Y_symmetry_basis"],ref))
        self.assertTrue(np.allclose(p["Y_mass_basis_2022"],
            p["left_rotation"].T@ref@p["right_rotation"]))

    def test_majorana_one_loop_exact_symmetry_and_PMM_mixing(self):
        p=forward(tanbeta=5.6,d=.1,e=1.7,r=2.,phase_rad=.4)
        A=p["f_mass_basis"]@np.diag(ML)@p["Y_mass_basis_2022"].T
        ref=p["kappa_2022"]*(A+A.T)
        self.assertTrue(np.allclose(p["mnu_for_f1_GeV"],ref,atol=1e-14))
        self.assertTrue(np.allclose(ref,ref.T,atol=1e-14))
        self.assertLess(p["charged_mass_closure_max_GeV"],1e-9)
        for ordering in ("NO","IO"):
            o=mixing_observables(p,ordering=ordering)
            for k in ("sin2theta12","sin2theta13","sin2theta23"):
                self.assertGreaterEqual(o[k],0)
                self.assertLessEqual(o[k],1)
            self.assertGreater(o["mass_ratio"],0)
            self.assertGreater(o["sum_masses_eV"],0)
            self.assertGreater(o["f_e_mu_to_match_atm_abs"],0)
            self.assertTrue(np.isfinite(exploratory_distance(o)))

    def test_scalar_mass_changes_only_overall_loop_scale(self):
        a=forward(tanbeta=5.6,d=.1,e=1.7,r=2.,phase_rad=.4,
                  mH1=300,mH2=700,gamma=1.089)
        b=forward(tanbeta=5.6,d=.1,e=1.7,r=2.,phase_rad=.4,
                  mH1=300,mH2=900,gamma=1.18)
        self.assertTrue(np.allclose(
            a["mnu_for_f1_GeV"]/a["kappa_2022"],
            b["mnu_for_f1_GeV"]/b["kappa_2022"],atol=1e-14))
        o=mixing_observables(a)
        x=mixing_observables(b)
        for k in ("sin2theta12","sin2theta13","sin2theta23",
                  "J_CP","mass_ratio","sum_masses_eV"):
            self.assertAlmostEqual(o[k],x[k],places=8)

    def test_opposite_mu_tau_diagonal_branch_is_exact_basis_relabeling(self):
        # The generic triangular charged-lepton mass matrix has an
        # interlacing branch d<m_mu<e and its "opposite" e<m_mu<d.
        # Family Z2 assigns the SAME charge to L_mu,L_tau and to all
        # right-handed charged leptons, so the swap is a gauge-flavor
        # basis relabeling, not a new physical oscillation branch.
        # Perform the complete transformation on M_l, f and Y,
        # including the swap of both left/right leptons.  Normalizing
        # f'_e_mu=1 changes M_nu by only a common complex factor.
        d,e=.025,.7
        tb=15.
        ml,L,R=charged_mass_matrix(d,e)
        f=family_f(.3,.4)
        z=f[0,2]
        Y=np.diag([-1/tb,tb,tb])@ml/V
        fh=L.T@f@L
        yh=L.T@Y@R
        mnu=fh@np.diag(ML)@yh.T + yh@np.diag(ML)@fh.T
        P=np.asarray([[1.,0.,0.],[0.,0.,1.],[0.,1.,0.]])
        mp=P@ml@P.T
        lp=P@L
        rp=P@R
        fp=P@f@P.T/z
        yp=P@Y@P.T
        self.assertTrue(np.allclose(lp.T@mp@rp,np.diag(ML),atol=1e-12))
        self.assertGreater(mp[1,1],MMU)
        self.assertLess(mp[2,2],MMU)
        self.assertAlmostEqual(abs(fp[0,1]-1),0.,places=12)
        fhp=lp.T@fp@lp
        yhp=lp.T@yp@rp
        mnup=fhp@np.diag(ML)@yhp.T + yhp@np.diag(ML)@fhp.T
        self.assertTrue(np.allclose(mnup,mnu/z,atol=1e-12))
        # All mixing angles, J_CP and mass-squared ratios depend on
        # eigenvectors of mnu^dagger*mnu, and therefore are invariant
        # under a common nonzero complex rescaling.
        ev=np.linalg.eigvalsh(mnu.conj().T@mnu)
        evp=np.linalg.eigvalsh(mnup.conj().T@mnup)
        self.assertTrue(np.allclose(evp,ev/abs(z)**2,rtol=1e-10,
                                     atol=1e-20))

    def test_optimizer_does_not_claim_real_fit(self):
        x=exploratory_optimize(tanbeta=5.6,maxiter=2,popsize=3,
                               seed=11)
        self.assertEqual(x["status"],STATUS)
        self.assertFalse(x["NuFIT_likelihood_used"])
        self.assertFalse(x["neutrino_full_fit_completed"])
        self.assertFalse(x["full_LFV_completed"])
        self.assertIsNone(x["full_neutrino_oscillation_NuFIT_compatibility"])
        self.assertIsNone(x["physical_Zee_allowed"])
        self.assertGreaterEqual(x["proxy_score_NOT_chisquare"],0)

if __name__=="__main__":
    unittest.main()

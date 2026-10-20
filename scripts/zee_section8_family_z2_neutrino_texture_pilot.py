#!/usr/bin/env python3
"""G8: Family-Z2 Zee leptonic texture, charged-lepton closure and neutrino pilot.

Based on Primulando, Julio, Uttayarat, EPJC 82 (2022) 253:
Eqs. (1)-(2),(8)-(10),(13)-(14),(17).

This constructs the *symmetry-basis* mass matrix
  M_l = [[a,b,c],[0,d,0],[0,0,e]]
and antisymmetric f with only f_e_mu, f_e_tau nonzero. It
diagonalizes M_l, rotates f and the non-VEV Higgs-basis Yukawa
Y, and computes the one-loop symmetric Majorana neutrino mass.

Unusual useful fact: choosing d between m_e and m_mu and e
between m_mu and m_tau fixes a,b,c ANALYTICALLY to reproduce
the three charged-lepton masses, leaving exactly 2 charged-lepton
mixing directions. There is no unrestricted B2 f/Y fit.

THIS IS NOT A FULL NEUTRINO FIT: optional differential evolution
minimizes a deliberately *illustrative*, uncorrelated distance to
the frozen reference oscillation inputs, not NuFIT likelihood.
No LFV, HiggsTools, flavor, global vacuum or modern model exclusion.
The loop-normalization convention here follows the 2022 paper; do
not pass Y to the Chen-convention B2/B3 code without independent
normalization/transpose/conjugation validation.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import numpy as np

ME, MMU, MTAU = (0.00051099895, 0.1056583755, 1.77686)
ML = np.asarray((ME, MMU, MTAU), float)
V = 246.21965
STATUS="FAMILY_Z2_LEPTON_MASS_AND_NEUTRINO_TEXTURE_PILOT_NOT_FIT_OR_ALLOWED"
# Illustrative target copied from existing A1B numerical benchmark; NOT
# a current experimental NuFIT likelihood, and no correlations are modeled.
TARGET={"sin2theta12":.307,"sin2theta13":.02195,
        "sin2theta23":.561,"dm21_eV2":7.49e-5,
        "abs_dmatm_eV2":2.534e-3,"delta_CP_deg":240.}
# Arbitrary exploratory score scales; MUST NOT be relabeled experimental errors.
PROXY_SCALES={"sin2theta12":.02,"sin2theta13":.003,
              "sin2theta23":.04,"mass_ratio":.003,
              "J_CP":.01}


def charged_mass_matrix(d:float,e:float):
    """Exact 5-entry triangular M_l with fixed physical singular values.

    Eigenvalues x_i=m_i² of M M^T interlace the two diagonal minors
    d² and e². Evaluating the characteristic polynomial at each
    minor yields b²,c²; determinant yields a. There is no
    SVD mass optimization and no assumption of diagonal M_l.
    """
    if not (math.isfinite(d) and math.isfinite(e) and
            ME<d<MMU<e<MTAU):
        raise ValueError("Require m_e<d<m_mu<e<m_tau")
    eig=ML**2
    p=lambda x:float(np.prod(eig-x))
    b2=-p(d*d)/(d*d*(e*e-d*d))
    c2=-p(e*e)/(e*e*(d*d-e*e))
    if b2<=0 or c2<=0:
        raise ValueError("Invalid interlaced charged-lepton spectrum")
    a=math.prod(ML)/(d*e)
    mat=np.asarray([[a,math.sqrt(b2),math.sqrt(c2)],
                    [0.,d,0.],[0.,0.,e]],float)
    left,values,righth=np.linalg.svd(mat)
    idx=np.argsort(values)
    left=left[:,idx];right=righth.T[:,idx];values=values[idx]
    if not np.allclose(values,ML,atol=1e-10,rtol=1e-8):
        raise ValueError("Charged-lepton mass closure failed")
    if not np.allclose(left.T@mat@right,np.diag(ML),
                       atol=1e-10,rtol=1e-8):
        raise ValueError("Charged-lepton biorthogonal rotation failed")
    return mat,left,right


def family_f(r:float,phase_rad:float):
    """2022 Eq. (8), set f_e_mu=1 before overall neutrino scaling."""
    if not (math.isfinite(r) and r>0 and math.isfinite(phase_rad)):
        raise ValueError("Invalid f ratio or phase")
    z=r*np.exp(1j*phase_rad)
    return np.array([[0,1,z],[-1,0,0],[-z,0,0]],complex)


def forward(*,tanbeta:float,d:float,e:float,
            r:float,phase_rad:float,
            mH1:float=300.,mH2:float=700.,gamma:float=1.089):
    """Construct family-basis Yukawas, rotate, compute nu texture.

    Output neutrino matrix is in GeV for f_e_mu=1; only SHAPE
    observables follow. Absolute scale fixed afterward from dm_atm.
    """
    if not(math.isfinite(tanbeta) and tanbeta>0 and
           0<mH1<mH2 and math.isfinite(gamma) and
           0<gamma<math.pi/2):
        raise ValueError("Invalid scalar/mixing/tanbeta inputs")
    ml,L,R=charged_mass_matrix(d,e)
    f0=family_f(r,phase_rad)
    y0=np.diag([-1./tanbeta,tanbeta,tanbeta])@ml/V
    fh=L.T@f0@L
    yh=L.T@y0@R
    if np.max(np.abs(f0+f0.T))>1e-13 or (
            np.max(np.abs(fh+fh.T))>1e-12):
        raise ValueError("Zee f antisymmetry violated")
    if not(np.max(np.abs(f0[1:,1:]))<1e-13 and
           np.max(np.abs(ml[np.tril_indices(3,-1)]))<1e-13):
        raise ValueError("Family Z2 Yukawa texture violation")
    kappa=math.sin(2*gamma)*math.log(mH1*mH1/(mH2*mH2))/(16*math.pi**2)
    A=fh@np.diag(ML)@yh.T
    mnu=kappa*(A+A.T)
    if not np.allclose(mnu,mnu.T,atol=1e-12):
        raise ValueError("Majorana symmetry violated")
    mass2,U=np.linalg.eigh(mnu.conj().T@mnu)
    mass2=np.clip(mass2,0.,None)
    if mass2[2]<=mass2[1] or mass2[1]<=mass2[0]:
        raise ValueError("Degenerate neutrino spectrum")
    return {"charged_lepton_basis":ml,"left_rotation":L,
            "right_rotation":R,"f_symmetry_basis":f0,
            "Y_symmetry_basis":y0,"f_mass_basis":fh,
            "Y_mass_basis_2022":yh,"mnu_for_f1_GeV":mnu,
            "mass2_for_f1_GeV2":mass2,"U_sorted_mass_columns":U,
            "kappa_2022":kappa,
            "charged_mass_closure_max_GeV":float(np.max(np.abs(
                np.linalg.svd(ml,compute_uv=False)[::-1]-ML)))}


def mixing_observables(result,ordering="NO"):
    """Mass-order eigenvectors: NO=(0,1,2), IO=(1,2,0)."""
    if ordering not in ("NO","IO"):
        raise ValueError("Expected NO or IO")
    vals=result["mass2_for_f1_GeV2"]
    inds=[0,1,2] if ordering=="NO" else [1,2,0]
    U=result["U_sorted_mass_columns"][:,inds]
    den=1-abs(U[0,2])**2
    if den<1e-12: raise ValueError("Singular PMNS mixing angle")
    s13=float(abs(U[0,2])**2)
    s12=float(abs(U[0,1])**2/den)
    s23=float(abs(U[1,2])**2/den)
    J=float(np.imag(U[1,2]*np.conj(U[0,2])*U[0,1]*np.conj(U[1,1])))
    physical=vals[inds]
    dm21=physical[1]-physical[0]
    if dm21<=0:raise ValueError("Invalid solar mass ordering")
    atm=(physical[2]-physical[0]) if ordering=="NO" else (
        physical[1]-physical[2])
    if atm<=0:raise ValueError("Invalid atmospheric mass ordering")
    norm=math.sqrt(TARGET["abs_dmatm_eV2"]/atm)/1e9
    physical_masses_eV=np.sqrt(physical)*norm*1e9
    return {"ordering":ordering,"sin2theta12":s12,
            "sin2theta13":s13,"sin2theta23":s23,"J_CP":J,
            "mass_ratio":float(dm21/atm),
            "f_e_mu_to_match_atm_abs":norm,
            "masses_eV":physical_masses_eV.tolist(),
            "sum_masses_eV":float(np.sum(physical_masses_eV)),
            "mass_matrix_2022_loop_convention_only":True}


def target_J():
    a,b,c=(TARGET[k] for k in ("sin2theta12","sin2theta13",
                              "sin2theta23"))
    return (math.sqrt(a*(1-a)*b*c*(1-c))*(1-b)*
            math.sin(math.radians(TARGET["delta_CP_deg"])))


def exploratory_distance(mix):
    """NON-statistical distance. No NuFIT intervals/correlations."""
    obs=("sin2theta12","sin2theta13","sin2theta23",
         "mass_ratio","J_CP")
    expected=[TARGET["sin2theta12"],TARGET["sin2theta13"],
              TARGET["sin2theta23"],
              TARGET["dm21_eV2"]/TARGET["abs_dmatm_eV2"],
              target_J()]
    return float(sum(((mix[key]-exp)/PROXY_SCALES[key])**2
                     for key,exp in zip(obs,expected)))


def candidate_from_unit(zz):
    """Four bounded optimization coordinates (2 mass textures + r + phase)."""
    x,y,log_r,phase=map(float,zz)
    sx=1/(1+math.exp(-x))
    sy=1/(1+math.exp(-y))
    return {"d":ME+(MMU-ME)*sx,
            "e":MMU+(MTAU-MMU)*sy,
            "r":10**log_r,"phase_rad":phase}


def exploratory_optimize(*,tanbeta,ordering="NO",mH1=300.,
                         mH2=700.,gamma=1.089,
                         maxiter=65,popsize=10,seed=20261018):
    """Small, deterministic, source-texture-only diagnostic; NOT a fit."""
    from scipy.optimize import differential_evolution
    if not (1<=maxiter<=2000 and 3<=popsize<=100):
        raise ValueError("Unsafe pilot population/iterations")
    def loss(x):
        try:
            p=candidate_from_unit(x)
            point=forward(tanbeta=tanbeta,mH1=mH1,mH2=mH2,
                          gamma=gamma,**p)
            obs=mixing_observables(point,ordering=ordering)
            return exploratory_distance(obs)
        except (ValueError,FloatingPointError,np.linalg.LinAlgError):
            return 1e12
    res=differential_evolution(
        loss,[(-6.,6.),(-6.,6.),(-2.,2.),(-math.pi,math.pi)],
        maxiter=maxiter,popsize=popsize,polish=True,
        seed=seed,updating="immediate",workers=1,
        tol=0.01)
    parameters=candidate_from_unit(res.x)
    result=forward(tanbeta=tanbeta,mH1=mH1,mH2=mH2,
                   gamma=gamma,**parameters)
    obs=mixing_observables(result,ordering=ordering)
    out={"status":STATUS,"neutrino_full_fit_completed":False,
         "full_LFV_completed":False,"NuFIT_likelihood_used":False,
         "optimizer_diagnostic_only":True,"parameters":parameters,
         "tanbeta":tanbeta,"ordering":ordering,
         "mH1_GeV":mH1,"mH2_GeV":mH2,"gamma":gamma,
         "oscillation_shape_proxy_target":TARGET,
         "proxy_scales_NOT_experimental_errors":PROXY_SCALES,
         "proxy_score_NOT_chisquare":exploratory_distance(obs),
         "observables":obs,
         "charged_mass_closure_max_GeV":result[
             "charged_mass_closure_max_GeV"],
         "gauge_flavor_basis_f_mu_tau_zero":True,
         "k12_equal_zero_required_by_exact_familyZ2_quartics":True,
         "full_neutrino_oscillation_NuFIT_compatibility":None,
         "physical_Zee_allowed":None}
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tanbeta",type=float,required=True)
    p.add_argument("--ordering",choices=("NO","IO"),default="NO")
    p.add_argument("--mH1",type=float,default=300.)
    p.add_argument("--mH2",type=float,default=700.)
    p.add_argument("--gamma",type=float,default=1.089)
    p.add_argument("--maxiter",type=int,default=65)
    p.add_argument("--popsize",type=int,default=10)
    p.add_argument("--seed",type=int,default=20261018)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=exploratory_optimize(
        tanbeta=a.tanbeta,ordering=a.ordering,
        mH1=a.mH1,mH2=a.mH2,gamma=a.gamma,
        maxiter=a.maxiter,popsize=a.popsize,seed=a.seed)
    if a.output.exists():raise FileExistsError("Use new output file")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",STATUS)
    print("CHARGED_MASS_CLOSURE_GEV",result["charged_mass_closure_max_GeV"])
    print("PROXY_SCORE_NOT_CHISQUARE",result["proxy_score_NOT_chisquare"])
    print("OSCILLATION_SHAPE",json.dumps(result["observables"],sort_keys=True))
    print("COMPLETE_NUFIT_LIKELIHOOD False")
    print("COMPLETE_LFV False")
    print("PHYSICAL_ALLOWED False")
    print("OUTPUT",a.output)


if __name__=="__main__":main()

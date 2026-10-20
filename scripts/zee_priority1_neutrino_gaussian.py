#!/usr/bin/env python3
"""Genuine Zee Majorana-matrix Takagi diagonalization and neutrino fit pilot.

This computes physical neutrino masses, three PMNS angles, the Dirac
CP phase and two measured mass splittings in NO and IO. Experimental
chi-square inputs must be user-supplied from a pinned oscillation-data
release; this is a multivariate Gaussian approximation, NOT a full
non-Gaussian NuFIT likelihood or an experimental exclusion.

The Zee f/Y source algebra already exists in gateB2/gateA1b; call the
existing neutrino reconstruction there, then evaluate its 3x3 complex
symmetric mass matrix here. All units in eV.
"""
from __future__ import annotations
import json,math
import numpy as np

FIELDS=("s12_sq","s13_sq","s23_sq","dm21_sq_eV2","dm3l_sq_eV2")
def complex_matrix(payload):
    if isinstance(payload,dict):
        arr=np.asarray(payload.get("real"),dtype=float)+1j*np.asarray(
            payload.get("imag"),dtype=float)
    else:
        arr=np.asarray(payload,dtype=complex)
    if arr.shape!=(3,3) or not np.isfinite(arr).all():
        raise ValueError("Need finite 3x3 complex neutrino mass matrix in eV")
    if np.max(abs(arr-arr.T))>1e-10:
        raise ValueError("Majorana mass matrix must be symmetric, not Hermitian")
    return arr

def takagi(matrix,ordering):
    """Diagonalize M = U* diag(m) U^dagger, for nondegenerate spectrum."""
    if ordering not in ("NO","IO"):raise ValueError("Invalid ordering")
    M=complex_matrix(matrix)
    w,U=np.linalg.eigh(M.conj().T@M)
    if np.any(w < -1e-16):raise ValueError("Negative Mdagger M eigenvalue")
    if ordering=="IO":
        U=U[:,[1,2,0]]
    # Each column is rephased to make diagonal U^T M U real positive.
    D=np.diag(U.T@M@U)
    # A vanishing lightest neutrino mass is physical; its unobservable
    # column phase can be chosen arbitrarily. Validate the full matrix,
    # not a spurious strictly-positive lightest-mass requirement.
    U=U*np.exp(-.5j*np.angle(D))[None,:]
    d=U.T@M@U
    masses=np.abs(np.diag(d))
    scale=max(float(np.max(masses)),1e-9)
    if (np.max(abs(d-np.diag(masses)))/scale>1e-7 or
        np.max(abs(U.conj()@np.diag(masses)@U.conj().T-M))/scale>1e-7):
        raise ValueError("Takagi mass reconstruction/phase closure failed")
    if ordering=="NO" and not (masses[0]<=masses[1]<=masses[2]):
        raise ValueError("NO mass ordering mismatch")
    if ordering=="IO" and not(masses[2]<=masses[0]<=masses[1]):
        raise ValueError("IO mass ordering mismatch")
    return masses,U

def parameters(matrix,ordering):
    masses,U=takagi(matrix,ordering)
    se2=float(abs(U[0,2])**2);ce2=1-se2
    if not 1e-10<ce2 and 1e-10<se2<1-1e-10:
        raise ValueError("PMNS parameters singular at zero/maximum theta13")
    s12=float(abs(U[0,1])**2/ce2)
    s23=float(abs(U[1,2])**2/ce2)
    if not all(1e-10<v<1-1e-10 for v in (s12,s23)):
        raise ValueError("PMNS angles singular")
    c12=math.sqrt(1-s12); ss12=math.sqrt(s12)
    c23=math.sqrt(1-s23); ss23=math.sqrt(s23)
    s13=math.sqrt(se2);c13=math.sqrt(ce2)
    J=float(np.imag(U[0,0]*U[1,1]*U[0,1].conj()*U[1,0].conj()))
    norm=c12*ss12*c23*ss23*ce2*s13
    sind=J/norm
    cosd=(float(abs(U[1,0])**2)-s12*c23**2-
          (1-s12)*s23*s13**2)/(2*ss12*c12*c23*ss23*s13)
    delta=float(math.atan2(sind,cosd)%(2*math.pi))
    ret={
        "ordering":ordering,"masses_eV":masses.tolist(),
        "s12_sq":s12,"s13_sq":se2,"s23_sq":s23,
        "dm21_sq_eV2":float(masses[1]**2-masses[0]**2),
        "dm3l_sq_eV2":float(masses[2]**2-(
                      masses[0]**2 if ordering=="NO" else masses[1]**2)),
        "delta_CP_rad":delta,
        "absolute_Jarlskog":abs(J),
        "takagi_matrix_reconstruction_passed":True,
    }
    return ret

def gaussian_fit(p,fit):
    """Correlated Gaussian proxy only, no fake full oscillation likelihood."""
    if fit.get("ordering")!=p["ordering"] or not fit.get("data_release"):
        raise ValueError("Missing/mismatched neutrino data release/ordering")
    fields=list(fit.get("fields",FIELDS))
    if fields!=list(FIELDS):
        raise ValueError("Use same five experimental oscillation coordinates")
    x=np.asarray([p[k] for k in fields])
    mu=np.asarray(fit.get("central"),dtype=float)
    cov=np.asarray(fit.get("covariance"),dtype=float)
    if (mu.shape!=(5,) or cov.shape!=(5,5) or
        not np.isfinite(mu).all() or not np.isfinite(cov).all() or
        not np.allclose(cov,cov.T,rtol=1e-10,atol=1e-22)):
        raise ValueError("Invalid reference covariance")
    if np.min(np.linalg.eigvalsh(cov))<=0:
        raise ValueError("Reference covariance not positive definite")
    delta=x-mu
    chi2=float(delta@np.linalg.solve(cov,delta))
    if not math.isfinite(chi2) or chi2<0:
        raise ValueError("Nonfinite neutrino chi2")
    return {
       "status":"NEUTRINO_CORRELATED_GAUSSIAN_PROXY_NOT_FULL_GLOBAL_LIKELIHOOD",
       "ordering":p["ordering"],
       "chi2_Gaussian_NOT_NuFIT_likelihood":chi2,
       "data_release":fit["data_release"],
       "experimental_CL_exclusion":None,
    }

def evaluate(matrix,references):
    """Evaluate both possible labels; preserve actual measured splittings."""
    if set(references)!={"NO","IO"}:
        raise ValueError("Both NO and IO experimental input releases required")
    out={}
    for ordering in ("NO","IO"):
        try:
            p=parameters(matrix,ordering)
            out[ordering]={"observables":p,"proxy":gaussian_fit(p,references[ordering])}
        except ValueError as err:
            out[ordering]={"status":"TAKAGI_OR_OSCILLATION_FIT_BLOCKED",
                           "error":str(err),"experimentally_excluded":None}
    return {
        "status":"BOTH_ORDERINGS_MASS_MATRIX_ANALYSIS_GAUSSIAN_ONLY",
        "orderings":out,
        "full_global_oscillation_likelihood_computed":False,
        "allowed_or_excluded":None,
    }

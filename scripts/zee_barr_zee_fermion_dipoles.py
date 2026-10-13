#!/usr/bin/env python3
"""Preliminary Zee fermion-PHOTON Barr-Zee dipoles; NOT complete LFV.

Implements the finite top, bottom and tau fermion + photon subset in
Davidson, EPJC 76 (2016) 258, Eq.(21)-(23), in the same Barr-Zee f(z),
g(z) convention as zee_barr_zee_kernels.py.

The relation to the Herrero-Garcia (2017) Eq.(3.12) dipoles used by
our existing coherent scalar ONE LOOP backend is algebraically:
  C_{L,R} = (4 sqrt(2) GF/e) conjugate(A_{L,R}^{Davidson}),
  assuming the conjugate external-field ordering. For one f gamma loop,
  C_X = -alpha/(8 pi^3 m_parent m_f) * Nc Q_f^2
        * F_X(e,parent) * F_X(f,f) * [f(z) for h,H; g(z) for A].
The Davidson conjugation is explicit and tested both ways.

CAUTION: the general-Zee lepton Yukawa scalar basis of A1D uses
C_A=iY; the corresponding Type-II-like quark pseudoscalar coupling
here has the common field rephasing required by Davidson Eq.(15).
The Type-II-like quark Yukawas remain a phenomenological ansatz,
not a demonstrated fully symmetry-protected Zee texture.

Not present: W-photon, charged-scalar-photon, Z-mediated two-loop,
full 3lepton loops, mu-e conversion or independent full-BSM benchmark
validation. Outputs are a coherent PARTIAL-AMPLITUDE DIAGNOSTIC, not
an excluded/allowed LFV prediction. Do not infer physical pass from
these small rates.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np

from gateA1b_hierarchical_no_seed import ME,MMU,MTAU
from gateA1c_charged_singlet_lfv import (
    CHANNELS,ALPHA_EM,G_F,dipole_coefficient_f_only
)
from gateA1d_neutral_tree_lfv import scalar_couplings
from gateA1e_neutral_one_loop_dipoles import (
    total_neutral_dipoles, partial_radiative_br
)
from gateA1f_charged_doublet_y_dipoles import charged_doublet_y_dipole
from gateB3_general_zee_charged_lepton_widths import (
    read_b1,complex_matrix,ensure_neutrino_closure
)
from gateA1b_hierarchical_no_seed import target_neutrino_matrix
from zee_barr_zee_kernels import f as scalar_f,g as pseudoscalar_g

STATUS="ZEE_BARR_ZEE_FERMION_PHOTON_AMPLITUDES_PRELIMINARY_NOT_FULL_LFV_ALLOWED"
VEV=246.21965
# Mass convention is explicitly nominal and not matched to running Yukawa.
FERMIONS={"top":(172.5,3,2./3.),
          "bottom":(4.18,3,-1./3.),
          "tau":(MTAU,1,-1.)}
LEPTON_MASSES=(ME,MMU,MTAU)
CSV_FIELDS=(
    "candidate_id","b2_solution_rank","channel",
    "one_loop_only_BR","barr_zee_fermion_photon_only_BR",
    "coherent_one_loop_plus_fermion_photon_BR_NOT_PHYSICAL",
    "coherent_partial_over_limit_NOT_EXCLUSION",
    "bz_abs_CL_GeV_minus2","bz_abs_CR_GeV_minus2",
    "bz_vs_one_loop_amplitude_norm",
    "B2_one_loop_closure_relative_error",
    "status",
)


def quark_chiral_couplings(*,mass,tanbeta,d):
    """CP-even/odd left-chiral neutral quark vertices in A1D basis.

    h=cos(d) Higgs_vev - sin(d) Higgs_extra,
    H=sin(d) Higgs_vev + cos(d) Higgs_extra,
    C^L_A(top)=-i cot(beta) m_t/v,
    C^L_A(bottom)=+i (-tan(beta)) m_b/v.
    Signs compensate the A field phase in A1D C_A=iY relative to
    Davidson Eq.(15) for the charged leptons.
    """
    if not (math.isfinite(mass) and mass>0 and
            math.isfinite(tanbeta) and tanbeta>0 and
            math.isfinite(d)):
        raise ValueError("Invalid quark couplings")
    c,s=math.cos(d),math.sin(d)
    k=mass/VEV
    tu=1./tanbeta
    td=-tanbeta
    return {
        "top":{"h":k*(c-s*tu),"H":k*(s+c*tu),
               "A":-1j*k*tu},
        "bottom":{"h":k*(c-s*td),"H":k*(s+c*td),
                  "A":1j*k*td},
    }


def flav_bz_amplitudes(p,Y,*,parent,daughter):
    """Finite fermion-photon two-loop subset; dimension [GeV^-2].

    Returns CL,CR and separate complex contributions for transparency.
    """
    if parent not in (1,2) or daughter not in (0,1) or parent<=daughter:
        raise ValueError("Invalid radiative LFV channel")
    Y=np.asarray(Y,complex)
    if Y.shape!=(3,3) or not np.all(np.isfinite(Y)):
        raise ValueError("Invalid Y Yukawa matrix")
    masses={"h":125.,"H":float(p["mh2"]),"A":float(p["ma"])}
    C_mats={
        k:C for k,(C,_) in zip(("h","H","A"),scalar_couplings(
            Y,mh=125,mH=p["mh2"],mA=p["ma"],
            alpha=p["alpha"],beta=p["beta"]))}
    tb=math.tan(p["beta"])
    d=p["beta"]-p["alpha"]
    cp={}
    for fermion,(mf,_,_) in FERMIONS.items():
        if fermion=="tau":
            cp[fermion]={k:C_mats[k][2,2] for k in masses}
        else:
            cp[fermion]={k:quark_chiral_couplings(
                mass=mf,tanbeta=tb,d=d)[fermion][k] for k in masses}
    mi=LEPTON_MASSES[parent]
    CL=0j;CR=0j
    rows=[]
    for fermion,(mf,nc,q) in FERMIONS.items():
        for boson,mphi in masses.items():
            z=(mf/mphi)**2
            kernel=(pseudoscalar_g(z)[0] if boson=="A"
                    else scalar_f(z)[0])
            c=C_mats[boson]
            left=c[daughter,parent]
            right=np.conj(c[parent,daughter])
            f_left=cp[fermion][boson]
            f_right=np.conj(f_left)
            # Eq.(21) after complex conjugation and C/A conversion.
            factor=-ALPHA_EM/(8.*math.pi**3*mi*mf)*nc*q*q*kernel
            aL=factor*left*f_left
            aR=factor*right*f_right
            CL+=aL; CR+=aR
            rows.append({
                "fermion":fermion,"boson":boson,"z":z,
                "loop_function":kernel,
                "CL":[aL.real,aL.imag],"CR":[aR.real,aR.imag]})
    if not all(math.isfinite(v) for v in (
            CL.real,CL.imag,CR.real,CR.imag)):
        raise ArithmeticError("Nonfinite Barr-Zee photon amplitudes")
    return CL,CR,rows


def one_loop_amplitudes(p,f,Y,*,parent,daughter):
    nl,nr,_=total_neutral_dipoles(
        Y,parent=parent,daughter=daughter,
        mH=p["mh2"],mA=p["ma"],
        alpha=p["alpha"],beta=p["beta"])
    yl,yr=charged_doublet_y_dipole(
        Y,parent=parent,daughter=daughter,
        m1=p["mH1"],m2=p["mH2"],gamma=p["gamma"])
    sr=dipole_coefficient_f_only(
        f,parent=parent,daughter=daughter,
        m1=p["mH1"],m2=p["mH2"],gamma=p["gamma"])
    return nl+yl,nr+yr+sr


def as_pair(z):
    return [float(z.real),float(z.imag)]


def compute(p,f,Y,sol):
    target,_=target_neutrino_matrix()
    closure=ensure_neutrino_closure(p,f,Y,target)
    if closure>=1e-9:
        raise ValueError("Neutrino matrix mismatch")
    out={}
    for channel,info in CHANNELS.items():
        parent,daughter=info["parent"],info["daughter"]
        ol,orr=one_loop_amplitudes(
            p,f,Y,parent=parent,daughter=daughter)
        bl,br,parts=flav_bz_amplitudes(
            p,Y,parent=parent,daughter=daughter)
        one=partial_radiative_br(ol,orr,norm_br=info["norm_br"])
        b2=float(sol["partial_LFV_rates_NOT_FULL"][channel])
        if not math.isclose(one,b2,rel_tol=1e-8,abs_tol=1e-29):
            raise ValueError("One-loop LFV baseline does not close B2 for "+
                             channel)
        bz=partial_radiative_br(bl,br,norm_br=info["norm_br"])
        subtotal=partial_radiative_br(
            ol+bl,orr+br,norm_br=info["norm_br"])
        ratio=subtotal/info["limit"]
        denom=math.hypot(abs(ol),abs(orr))
        out[channel]={
            "one_loop_only_BR":one,
            "barr_zee_fermion_photon_only_BR":bz,
            "coherent_one_loop_plus_fermion_photon_BR_NOT_PHYSICAL":subtotal,
            "coherent_partial_over_limit_NOT_EXCLUSION":ratio,
            "one_loop_CL":as_pair(ol),"one_loop_CR":as_pair(orr),
            "barr_zee_CL":as_pair(bl),"barr_zee_CR":as_pair(br),
            "barr_zee_vs_one_loop_amplitude_norm":
                (math.hypot(abs(bl),abs(br))/denom if denom else None),
            "barr_zee_terms":parts,
            "B2_one_loop_closure_relative_error":
                abs(one-b2)/max(one,b2) if max(one,b2)>0 else 0.,
            "status":"ONELOOP_PLUS_FERMION_PHOTON_SUBSET_NO_FULL_LFV_EXCLUSION",
        }
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=Path,required=True)
    ap.add_argument("--b2-json",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    points=read_b1(a.points)
    data=json.loads(a.b2_json.read_text())
    if set(data)!=set(points):raise ValueError("B2 and scalar ID sets mismatch")
    flat=[];details={}
    for ident,p in points.items():
        solutions=data[ident]
        if not isinstance(solutions,list) or not solutions:
            raise ValueError("Missing Yukawa family")
        details[ident]=[]
        for rank,sol in enumerate(solutions,1):
            if str(sol["candidate_id"])!=ident:
                raise ValueError("Wrong candidate ID in B2 solution")
            for key in ("mH1","mH2","gamma"):
                if not math.isclose(float(sol[key]),p[key],
                                    rel_tol=1e-11,abs_tol=1e-10):
                    raise ValueError("Mismatched scalar spectrum "+key)
            f=complex_matrix(sol["f"],"f")
            Y=complex_matrix(sol["Y"],"Y")
            res=compute(p,f,Y,sol)
            details[ident].append({
                "rank":rank,"channels":res,
                "status":"PRELIMINARY_PHOTON_FERMION_SUBSET_NOT_ALLOWED"})
            for channel,row in res.items():
                flat.append({
                    "candidate_id":ident,"b2_solution_rank":rank,
                    "channel":channel,
                    **{k:row[k] for k in CSV_FIELDS
                       if k in row and k not in (
                           "bz_abs_CL_GeV_minus2",
                           "bz_abs_CR_GeV_minus2")},
                    "bz_abs_CL_GeV_minus2":math.hypot(*row["barr_zee_CL"]),
                    "bz_abs_CR_GeV_minus2":math.hypot(*row["barr_zee_CR"]),
                })
    a.output_dir.mkdir(parents=True,exist_ok=True)
    out=a.output_dir/"photon_fermion_BZ_dipoles_ONLY_NOT_ALLOWED.csv"
    with out.open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=CSV_FIELDS,extrasaction="ignore")
        w.writeheader();w.writerows(flat)
    full=a.output_dir/"details_preliminary_NO_FULL_LFV.json"
    full.write_text(json.dumps(details,indent=2)+"\n")
    summary={
        "status":STATUS,
        "scalar_points":len(points),
        "neutrino_Yukawa_solutions":sum(len(x) for x in data.values()),
        "three_radiative_channels_per_solution":3,
        "calculated_amplitude_subset":"fermion-photon Barr-Zee top,bottom,tau",
        "fermion_masses_nominal_GeV":{
            k:v[0] for k,v in FERMIONS.items()},
        "A1D_Yukawa_basis_matches_quark_TypeII_ansatz_not_UV_validated":True,
        "independent_full_2HDM_fermion_amplitude_benchmark_validated":False,
        "W_and_charged_scalar_two_loop_implemented":False,
        "Z_exchange_two_loop_implemented":False,
        "physical_mu_to_e_gamma_rate_implemented":False,
        "LFV_allowed_or_excluded":None,
        "output_csv":str(out),
    }
    (a.output_dir/"summary.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print("STATUS",STATUS)
    print("SCALAR_CANDIDATES",len(points))
    print("NEUTRINO_YUKAWA_SOLUTIONS",
          summary["neutrino_Yukawa_solutions"])
    print("RADIATIVE_SUBSET_ROWS",len(flat))
    print("B2_ONELOOP_CLOSURE_REQUIRED True")
    print("FULL_BARR_ZEE_COMPLETE False")
    print("PHYSICAL_LFV_EXCLUSION_CALCULATED False")
    print("OUTPUT",out)


if __name__=="__main__":
    main()

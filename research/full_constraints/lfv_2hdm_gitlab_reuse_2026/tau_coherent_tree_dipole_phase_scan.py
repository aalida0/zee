#!/usr/bin/env python3
"""Signed, phase-scanned tau->3l neutral-tree / constant-dipole interference.

The input complex K2 comes from the independent Module3 one-loop calculation
plus the exact corrected authors' neutral-fermion Barr-Zee source. It is
NOT the original generated SARAH complex K2 and is NOT a complete Zee LFV
prediction. A free relative global phase is scanned, not set to a known
physical value.

The photon is assumed to have a constant K2 at nonzero q²; off-shell K1,
K2 running, Z penguins, boxes, and Zee-specific gauge-completed 2loop are
NOT included.

For a=b (identical final negative leptons), the fully antisymmetrized
scalar amplitude T changes sign under exchange of two negative leptons.
Consequently (1/2) integral T (P_direct-P_cross)* equals
integral T P_direct* by exchange symmetry. This eliminates the
crossed-photon collinear problem from the interference integral.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from module2.interface import decode
from module3.core import vertices
from module3 import tree
from research.full_constraints.lfv_2hdm_transfer_2026.evaluate import read_cards
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_exact_dipole_phase_space import (
    ALPHA_PAIR, ALPHA_SOURCE, photon_tensors, photon_width,
    kernel_range, radiative_width_unit, spin_inner
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_neutral_tree import (
    CARD_IDS, GAMMA_TAU_GEV
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_signed_complex_wilson_bridge import (
    run as source_bridge, CORRECTED_AUTHOR_SHA256
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_native_sarah_complex_import import (
    run as import_original_norm_checked
)

CHANNELS = (
    ("tau_to_3e", "tauegamma", 0, 0),
    ("tau_to_3mu", "taumugamma", 1, 1),
    ("tau_to_e_minus_mu_minus_mu_plus", "tauegamma", 0, 1),
    ("tau_to_mu_minus_e_minus_e_plus", "taumugamma", 1, 0),
)


def pairs_to_complex(vals):
    if len(vals)!=2 or any(len(c)!=2 for c in vals):
        raise ValueError("CL/CR complex-pair format invalid")
    out=np.array([complex(x[0],x[1]) for x in vals],dtype=complex)
    if not np.all(np.isfinite(out)):
        raise ValueError("Nonfinite complex K2")
    return out


def q2(ps,first,second):
    v=ps[first]+ps[second]
    return float(v[0]*v[0]-np.dot(v[1:],v[1:]))


def neutral_tree_tensor(direct,cross,ms,ps):
    s23=q2(ps,2,3)
    s13=q2(ps,1,3)
    return (np.einsum("s,sabcd->abcd",1/(ms*ms-s23),direct)
            - np.einsum("s,sabcd->abcd",1/(ms*ms-s13),cross))


def interference_width(scalars,ml,a,b,cl,cr,ns=56,nz=20):
    """Return integral spin_sum(T_scalar, P_direct)*dPhi, GeV.

    For identical finals the physical full photon+tree interference
    integrates to this expression EXACTLY by final-electron exchange
    symmetry; see module docstring. For mixed finals P_direct is the
    only photon diagram, so expression also holds without symmetry.
    """
    if (type(ns) is not int or type(nz) is not int
            or not (12<=ns<=160) or not (8<=nz<=128)):
        raise ValueError("ns/nz invalid")
    M,ma,mb=map(float,(ml[2],ml[a],ml[b]))
    if not (M>ma+2*mb and ma>0 and mb>0):
        raise ValueError("closed or unphysical channel")
    direct,cross,ms=tree.tensors(scalars,2,a,b)
    lo,hi=(2*mb)**2,(M-ma)**2
    extent=math.log(hi/lo)
    sn,sw=np.polynomial.legendre.leggauss(ns)
    zn,zw=np.polynomial.legendre.leggauss(nz)
    result=0j
    for x,wx in zip(sn,sw):
        s=lo*math.exp(extent*(x+1)/2)
        jac=s*extent/2
        phase=math.sqrt(max(0.,tree.kallen(M*M,ma*ma,s)*tree.kallen(s,mb*mb,mb*mb)))
        phase/=512*math.pi**3*M**3*s
        for z,wz in zip(zn,zw):
            ps=tree.momenta(M,(ma,mb,mb),s,z)
            T=neutral_tree_tensor(direct,cross,ms,ps)
            P,_=photon_tensors(ps,M,cl,cr,identical=False,
                               alpha_pair=ALPHA_PAIR,alpha_source=ALPHA_SOURCE)
            result+=wx*wz*jac*phase*spin_inner(T,P,ps,M,(ma,mb,mb))
    if not (math.isfinite(result.real) and math.isfinite(result.imag)):
        raise ArithmeticError("nonfinite scalar-dipole interference")
    return complex(result)


def positive_hermitian_photon_width(M,ma,mb,cl,cr,ns,nz):
    """Reconstruct complex-K2 photon response from four stable unit probes.

    Numerically stable at tiny Wilsons: the hermitian 2x2 positive quadratic
    form is independently evaluated on (1,0),(0,1),(1,1),(1,i).
    This avoids direct spin-sum precision loss near collinear e+e- threshold
    for certain complex phases at O(10^-12) Wilson magnitudes.
    """
    k=kernel_range(M,ma,mb,ns,nz)
    ref=radiative_width_unit(M,ma)
    ll=k["pure_CL_conversion"]*ref
    rr=k["pure_CR_conversion"]*ref
    both=k["equal_real_CL_CR_conversion"]*2*ref
    ipair=k["relative_imaginary_CL_CR_conversion"]*2*ref
    off=complex((both-ll-rr)/2,(ipair-ll-rr)/2)
    result=ll*abs(cl)**2+rr*abs(cr)**2 +2*(cl*cr.conjugate()*off).real
    if result < -1e-11*(ll*abs(cl)**2+rr*abs(cr)**2):
        raise ArithmeticError("dipole response Hermiticity/positivity failure")
    return max(0.,float(result))


def compute(source_dir: Path, source_revision:str,ns=56,nz=20,tree_order=24,
            native_original_json:Path|None=None):
    source=source_bridge(Path(source_dir),source_revision)
    # Optional ORIGINAL native JSON must come from an independently audited
    # Fortran execution: the import validator checks rates and source hashes,
    # but DOES NOT authenticate the individual complex phases.
    native=(import_original_norm_checked(Path(native_original_json))
            if native_original_json is not None else None)
    if (source["physical_lfv"]!="UNKNOWN"
            or source["gitlab_thdm_sha256"]!=CORRECTED_AUTHOR_SHA256):
        raise ValueError("Unreviewed complex Barr-Zee bridge")
    wits=read_cards()
    if len(wits)!=4 or tuple(source["cards"])!=CARD_IDS:
        raise ValueError("Frozen source changed")
    if tree_order<8 or tree_order>48:
        raise ValueError("tree quadrature order outside tested range")
    results={}
    for short,w in zip(CARD_IDS,wits):
        p=w["module2_input"]["scalar"]["record"]["physical"]
        ml=w["module2_input"]["lepton_masses_GeV"]
        D=decode(w["yukawas"]["D"])
        vs=vertices(D,p,ml)
        data={}
        for ch,rad,a,b in CHANNELS:
            ledger=source["cards"][short]["channels"][rad]
            if ledger["source_exact_complex_native_K2_confirmed"]:
                raise RuntimeError("Unexpected claim of exact original SARAH K2")
            if native is None:
                cl,cr=pairs_to_complex(ledger["partial_signed_plus_CL_CR_GeV_minus2"])
                coefficient_input="module3_analytic_1L_plus_corrected_neutral_BZ"
            else:
                entry=native["cards"][short][rad]
                native_lr=pairs_to_complex([
                    entry["module3_CL_from_native"],
                    entry["module3_CR_from_native"],
                ])
                bz_lr=pairs_to_complex(
                    ledger["author_neutral_BZ_in_module3_CL_CR_GeV_minus2"])
                cl,cr=native_lr+bz_lr
                coefficient_input="claimed_original_native_K2_norm_checked_plus_corrected_neutral_BZ"
            tree_w=tree.width(vs,2,a,b,ml,order=tree_order,contact=False)
            dip_w=positive_hermitian_photon_width(
                float(ml[2]),float(ml[a]),float(ml[b]),cl,cr,ns,nz)
            I=interference_width(vs,ml,a,b,cl,cr,ns,nz)
            norm=math.sqrt(tree_w*dip_w)
            # Cauchy is a stringent self-consistency check, not a bound
            # on the missing diagrams.
            if abs(I)>norm*(1+2e-3)+1e-40:
                raise ArithmeticError("Cauchy violation: wrong spinor/phase convention")
            center=(tree_w+dip_w)/GAMMA_TAU_GEV
            radius=2*abs(I)/GAMMA_TAU_GEV
            if radius>center*(1+2e-3):
                raise ArithmeticError("unphysical coherent phase modulation")
            rows={
                "tree_BR":tree_w/GAMMA_TAU_GEV,
                "dipole_constant_K2_BR":dip_w/GAMMA_TAU_GEV,
                "tree_dipole_integrated_complex_cross_GeV":[I.real,I.imag],
                "tree_dipole_coherent_center_BR":center,
                "max_absolute_interference_shift_BR":radius,
                "phase_freedom_lower_BR":max(0.,center-radius),
                "phase_freedom_upper_BR":center+radius,
                "chiral_K2_Module3_CL_CR_GeV_minus2":[[cl.real,cl.imag],[cr.real,cr.imag]],
                "original_native_complex_source_K2_recovered":False,
                "complex_coefficient_input":coefficient_input,
                "imported_native_source_K2_norm_checked":native is not None,
                "imported_native_K2_phases_independently_verified":False,
                "physical_total_BR":None,
                "missing_offshell_and_loop_terms":True,
                "relative_phase_not_source_matched":True,
            }
            data[ch]=rows
            print("SIGNED_INTERFERENCE_APPROX",short,ch,
                  "tree",f"{rows['tree_BR']:.9e}",
                  "dipole",f"{rows['dipole_constant_K2_BR']:.9e}",
                  "phase_envelope",f"[{rows['phase_freedom_lower_BR']:.9e},{rows['phase_freedom_upper_BR']:.9e}]",
                  "overlap",f"{abs(I)/max(norm,1e-300):.8g}",flush=True)
        results[short]={"frozen_input_id":w["id"],"channels":data}
    return {
        "status":"SIGNED_COMPLEX_AUTHOR_BZ_PLUS_MODULE3_APPROX_ZEE_ONELOOP_TREE_DIPOLE_INTERFERENCE_PHASE_UNMATCHED",
        "source":{"corrected_2HDM_thdm_sha256":CORRECTED_AUTHOR_SHA256,
                  "original_native_SARAH_complex_K2_file":None,
                  "module3_approx_not_exact_generated_source":native is None,
                  "native_source_JSON_imported_norm_checked":native is not None,
                  "native_source_JSON_phase_independently_replayed":False,
                  "source_running_MSbar_quark_masses":True},
        "interference_phase":"unmatched between published operator and scalar tree; global physical phase NOT asserted; scan over all global phases",
        "formula":"B(phi)=(Gamma_tree+Gamma_dipole+2Re(exp(-i phi)*I))/Gamma_tau, I=int T_tree P_direct* dPhi",
        "identical_exchange_identity":"1/2 int T*(Pdirect-Pcross)^* = int T*Pdirect^*",
        "missing":["original native complex SARAH K2 source", "Zee charged mixed gauge two-loop",
                   "off-shell K1(q2), K2(q2)", "Z penguins and boxes",
                   "full one-loop contact terms", "QED corrections"],
        "quadrature":{"ns":ns,"nz":nz,"tree_order":tree_order},
        "cards":results,
        "physical_lfv":"UNKNOWN",
        "global_acceptance":None,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--commit",default="b5035cd5")
    p.add_argument("--ns",type=int,default=56)
    p.add_argument("--nz",type=int,default=20)
    p.add_argument("--tree-order",type=int,default=24)
    p.add_argument("--output",type=Path)
    p.add_argument("--native-original-json",type=Path,help="Optional original compiled SARAH K2 JSON; SHA+BR checks do not certify complex phases")
    a=p.parse_args()
    x=compute(a.source,a.commit,a.ns,a.nz,a.tree_order,
              native_original_json=a.native_original_json)
    if a.output:
        if a.output.exists():
            raise FileExistsError("Refuse overwrite")
        a.output.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("FULL_ZEE_LFV UNKNOWN: signed phase reference and exact native complex K2 not yet validated")


if __name__=="__main__":
    main()

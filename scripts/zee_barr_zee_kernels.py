#!/usr/bin/env python3
"""Validated Barr--Zee fermionic photon-loop FUNCTIONS (not dipole amplitudes).

Following H.E. Haber, "Evaluating integrals arising from Barr-Zee
diagrams", March 2024, Eq.(1),(39),(40):
 g(z) = z/2 * integral_0^1 dx log[x(1-x)/z]/[x(1-x)-z]
 f(z) = z(2+log z)+(1-2z)*g(z).

Numerically evaluate g through its exactly equivalent
 log(1+t)/t integrand, t=(x(1-x)-z)/z, with a stable small-t
 expansion. This removes the apparent 0/0 at x(1-x)=z.

This is a physical loop-function calculation, but NOT a calculation of
C_L/R, mu->e gamma, a Barr-Zee branching ratio, any LFV exclusion, or
a global Zee experimental constraint. Fermion charges, gamma/Z exchange,
quark Yukawa conventions, CP-even/odd relative phases, W and charged
scalar diagrams, and interference must be validated separately.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from scipy.integrate import quad

STATUS="ZEE_BARR_ZEE_PHOTON_FERMION_KERNELS_MATH_ONLY_NOT_LFV_EXCLUSION"
FERMION_MASSES_GEV={
    "top_nominal":172.5,
    "bottom_nominal":4.18,
    "tau":1.77686,
}
OUTPUT_FIELDS=("candidate_id","fermion","fermion_mass_GeV","scalar",
               "scalar_mass_GeV","z","f_scalar","g_pseudoscalar",
               "numerical_quad_absolute_error","status")


def _log_over_t(t):
    if not math.isfinite(t) or t<=-1.:
        raise ValueError("Require -1<t<infinity")
    if abs(t)<1.e-5:
        # log(1+t)/t; alternating series to t^5 near removable t=0.
        return (1.-t/2.+t*t/3.-t**3/4.+t**4/5.-t**5/6.)
    return math.log1p(t)/t


def g(z):
    """The fermionic CP-odd photon Barr-Zee loop function for real z>0."""
    z=float(z)
    if not math.isfinite(z) or not 1e-12<z<1e8:
        raise ValueError("Require finite 1e-12 < z < 1e8")
    def fun(x):
        u=x*(1.-x)
        if u==0.:
            # quad never evaluates at endpoints; integrable log divergence.
            return float("inf")
        t=(u-z)/z
        return .5*_log_over_t(t)
    points=[]
    if z<.25:
        root=math.sqrt(1.-4.*z)
        points=[(1.-root)/2.,(1.+root)/2.]
    ans,err=quad(fun,0.,1.,points=points,
                 epsabs=5e-12,epsrel=5e-12,limit=400)
    if not math.isfinite(ans) or not math.isfinite(err) or ans<=0:
        raise ArithmeticError("Barr-Zee g(z) quadrature not finite/positive")
    if err>max(1e-9,abs(ans)*1e-7):
        raise ArithmeticError("Barr-Zee g(z) quadrature unreliable")
    return float(ans),float(err)


def f(z):
    """CP-even fermionic photon Barr-Zee function, analytic Haber identity."""
    zz=float(z)
    gg,err=g(zz)
    val=zz*(2.+math.log(zz))+(1.-2.*zz)*gg
    if not math.isfinite(val) or val<=0:
        raise ArithmeticError("Barr-Zee f(z) numerically invalid")
    return val,err


def kernels_for_masses(scalar_masses,fermion_masses=None):
    fermions=fermion_masses or FERMION_MASSES_GEV
    if any(not math.isfinite(float(m)) or float(m)<=0
           for m in list(scalar_masses.values())+list(fermions.values())):
        raise ValueError("All masses must be finite and positive")
    rows=[]
    for boson,mass in scalar_masses.items():
        for species,mf in fermions.items():
            z=(float(mf)/float(mass))**2
            gv,err=g(z)
            fv=z*(2.+math.log(z))+(1.-2.*z)*gv
            rows.append({
                "fermion":species,"fermion_mass_GeV":float(mf),
                "scalar":boson,"scalar_mass_GeV":float(mass),
                "z":z,"f_scalar":fv,"g_pseudoscalar":gv,
                "numerical_quad_absolute_error":err,
                "status":"LOOP_FUNCTION_ONLY_NO_DIPOLERATE_OR_EXCLUSION"})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--points",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    with a.points.open(newline="") as handle:
        reader=csv.DictReader(handle)
        required=("id","mh2","ma")
        if not reader.fieldnames or any(x not in reader.fieldnames
                                       for x in required):
            raise ValueError("Requires Zee scalar candidate CSV with id,mh2,ma")
        points=list(reader)
    if not points or len(set(r["id"] for r in points))!=len(points):
        raise ValueError("Empty or duplicate scalar points")
    result=[]
    for pnt in points:
        rows=kernels_for_masses({
            "h125":125.0,"Hheavy":float(pnt["mh2"]),
            "A":float(pnt["ma"])})
        for row in rows:
            row["candidate_id"]=pnt["id"]
            result.append(row)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    out=a.output_dir/"barr_zee_fermion_photon_kernels_NO_LFV_EXCLUSION.csv"
    with out.open("w",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(result)
    summary={
        "status":STATUS,
        "n_scalar_spectra":len(points),
        "n_kernel_entries":len(result),
        "fermion_masses_GeV":FERMION_MASSES_GEV,
        "higgs_masses_GeV":"h=125 GeV, heavy H and A from candidate CSV",
        "physical_Barr_Zee_dipole_implemented":False,
        "physical_LFV_exclusion_calculated":False,
        "note":"g/f are only dimensionless loop functions. The nominal "
               "fermion masses are not a matched running Yukawa scheme.",
        "reference":"H.E. Haber, Evaluating integrals arising from "
                    "Barr-Zee diagrams (2024), Eqs. 1,39,40.",
        "output_csv":str(out),
    }
    (a.output_dir/"summary.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print("STATUS",STATUS)
    print("SCALAR_CANDIDATES",len(points))
    print("KERNEL_ENTRIES",len(result))
    print("BARR_ZEE_AMPLITUDE_IMPLEMENTED False")
    print("LFV_EXCLUSION_CALCULATED False")
    print("OUTPUT",out)

if __name__=="__main__":
    main()

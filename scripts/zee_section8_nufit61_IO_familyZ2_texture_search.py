#!/usr/bin/env python3
"""NuFIT6.1 IO symmetry-restricted Zee neutrino TEXTURE feasibility screen.

Minimize the LARGEST of three SEPARATE, overlapping marginalized 2D
Delta-chi2 projections (T13/T12,T23/DCP,DMS/DMA), NOT their sum.
Each experimental 2D projection is a necessary consistency check,
but simultaneous membership in 3 projected regions does NOT establish
compatibility with the unavailable correlated 6D NuFIT likelihood.

The model's one-loop neutrino scale is free via f_e_mu: the DMS/DMA
component is profiled along the fixed neutrino mass-splitting ratio.
During optimization use a dense precomputed *approximate* ratio lookup;
re-evaluate each winning candidate with a denser direct numerical
profile, never confusing the lookup score with exact theory/exclusion.

Model parameters: M_l=[[a,b,c],[0,d,0],[0,0,e]], antisymmetric
f=[0,f_e_mu,f_e_tau], exact source family-Z2 basis/rotations; no
unrestricted B2 f/Y. 4 continuous variables (d,e,|f_e_tau/f_e_mu|,
relative phase) at EACH selected fixed tanbeta.

IMPORTANT:
- This is LEPTON-ONLY. High tanbeta does not preserve P2's old
  scalar lambda1, EW vacuum, widths or 2026 quark-flavor fit.
- No full NuFIT6.1 likelihood, LFV, modern cosmology, HiggsTools or
  modern Zee two-state b->s gamma is implemented.
- Source NuFIT tables must have exact pinned SHA256+size.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import differential_evolution

from zee_section8_family_z2_neutrino_texture_pilot import (
    candidate_from_unit,forward,mixing_observables
)
from zee_section8_IO_first_octant_witness import WITNESS
from zee_section8_nufit61_IO_witness_profiles import (
    TABLES,THRESHOLD_3SIGMA_2DOF,read_tables,verify,profile_ratio,
)

STATUS="FAMILY_Z2_NUFIT61_IO_TEXTURE_NECESSARY_2D_FEASIBILITY_NOT_JOINT_FIT_OR_ALLOWED"
BOUNDS=((-24.,24.),(-24.,24.),(-5.,5.),(-math.pi,math.pi))
R_RANGE=(.010,.080)
# Angular-domain starting points from INDEPENDENT LOCAL GEOMETRY-PROXY
# searches, not NuFIT fits and NOT physically allowed Zee benchmarks.
# Each approx reproduces [sin²12~.3445,sin²13~.02539,
# sin²23~.4813,delta~-174°,r~.0297] at its listed tanbeta.
# Initial seeds merely help DE get inside the finite official grid.
START_ANGULAR_SEEDS={
    5.597170833164245:(-1.329141, .888322, -2.032898, -3.055481),
    10.0:(-1.329461, .815955, -2.021894, -3.055875),
    15.0:(-1.329547, .796736, -2.018981, -3.055988),
    20.0:(-1.329579, .789920, -2.017949, -3.056030),
}


def independent_dirac_phase(point,obs):
    """Delta_CP from both phase-invariant sin(delta) and cos(delta)."""
    U=point["U_sorted_mass_columns"][:,[1,2,0]]
    s12=obs["sin2theta12"]
    s13=obs["sin2theta13"]
    s23=obs["sin2theta23"]
    t=math.sqrt(s12*(1-s12)*s23*(1-s23)*s13)
    if not(t>1e-15 and s13<1):
        raise ValueError("Singular PMNS Dirac phase")
    sin_delta=obs["J_CP"]/(t*(1-s13))
    cos_delta=(abs(U[1,0])**2-s12*(1-s23)-(1-s12)*s23*s13)/(2*t)
    if not math.isclose(sin_delta*sin_delta+cos_delta*cos_delta,
                        1.,rel_tol=1e-7,abs_tol=1e-7):
        raise ValueError("Inconsistent independently extracted Dirac phase")
    return float(((math.degrees(math.atan2(sin_delta,cos_delta))+180)%360)-180)

def source_shape(tanbeta,coordinates):
    pars=candidate_from_unit(coordinates)
    point=forward(tanbeta=tanbeta,mH1=300.,mH2=700.,
                  gamma=1.089,**pars)
    obs=mixing_observables(point,"IO")
    delta=independent_dirac_phase(point,obs)
    ratio=float(obs["mass_ratio"])
    if not (math.isfinite(ratio) and ratio>0):
        raise ValueError("Invalid IO mass splitting ratio")
    return {"parameters":pars,"observables":obs,
            "deltaCP_degrees_signed":delta,
            "solar_over_abs_atm_ratio":ratio,
            "charged_mass_closure_GeV":point[
                "charged_mass_closure_max_GeV"]}

class ProfileGate:
    def __init__(self,table_path,variant,r_nodes=2401,y_samples=601):
        if variant not in TABLES:raise ValueError("Unknown NuFIT IO variant")
        self.provenance=verify(table_path,variant)
        self.variant=variant
        self.grids=read_tables(table_path)
        if r_nodes<101 or y_samples<101:
            raise ValueError("Insufficient numeric resolution")
        self.r_axis=np.linspace(*R_RANGE,r_nodes)
        grid=self.grids["DMS/DMA"]
        z=np.asarray([[grid.z[x,y] for y in grid.y] for x in grid.x])
        interpolator=RegularGridInterpolator(
            (grid.x,grid.y),z,bounds_error=False,fill_value=np.nan,
            method="linear")
        # IO has Delta m32^2<0. Array is a ratio-by-atmospheric-scale
        # mesh; the same common mass-splitting scale is a nuisance.
        y=np.linspace(grid.y[0],grid.y[-1],y_samples)
        if np.max(y)>=0: raise ValueError("IO NuFIT atmospheric axis must be negative")
        x=np.log10(self.r_axis[:,None]*(-y[None,:])*1e-3)
        points=np.column_stack((x.ravel(),np.broadcast_to(
            y[None,:],x.shape).ravel()))
        vals=interpolator(points).reshape(x.shape)
        valid=np.isfinite(vals)
        # Official DMS/DMA tables cover only a finite mass-splitting
        # interval; unsupported ratio rows must penalize optimization,
        # not abort loading the otherwise valid experimental table.
        # Never extrapolate a marginalized NuFIT likelihood.
        self.profile_approx=np.min(
            np.where(valid,vals,1e7),axis=1)
        self.ratio_supported=np.any(valid,axis=1)
        if not np.any(self.ratio_supported):
            raise ValueError("No intersection of ratio scan and NuFIT support")

    def scores(self,shape,precise=False):
        o=shape["observables"]
        v={
            "T13/T12":self.grids["T13/T12"].interpolate(
                o["sin2theta13"],o["sin2theta12"]),
            "T23/DCP":self.grids["T23/DCP"].interpolate(
                o["sin2theta23"],shape["deltaCP_degrees_signed"]),
        }
        r=shape["solar_over_abs_atm_ratio"]
        if not (R_RANGE[0]<=r<=R_RANGE[1]):
            raise ValueError("Mass ratio outside supported optimization domain")
        if precise:
            v["DMS/DMA_ratio_profile"]=profile_ratio(
                self.grids["DMS/DMA"],r,steps=10001)["delta_chi2"]
        else:
            supported_ratio_axis=self.r_axis[self.ratio_supported]
            if r<supported_ratio_axis[0] or r>supported_ratio_axis[-1]:
                raise ValueError("Mass ratio outside NuFIT data support")
            v["DMS/DMA_ratio_profile"]=float(np.interp(
                r,self.r_axis,self.profile_approx))
            if v["DMS/DMA_ratio_profile"]>=1e6:
                raise ValueError("Ratio lies in unobserved NuFIT table gap")
        return v

    def score_one(self,shape,precise=False):
        scores=self.scores(shape,precise=precise)
        return float(max(scores.values()))

    def soft_domain_search_score(self,shape):
        """Optimization-only continuation outside official finite grids.

        Clip for a distance-to-domain SEARCH HEURISTIC and penalize the
        dimensionless outside distance. NEVER report this as a NuFIT
        Delta-chi2 or extrapolate the official likelihood. Final points
        must pass strict self.scores() in-range checks and be rescored.
        """
        o=shape["observables"]
        def clip_penalty(grid,x,y):
            xlo,xhi=grid.x[0],grid.x[-1]
            ylo,yhi=grid.y[0],grid.y[-1]
            xc=min(max(float(x),xlo),xhi)
            yc=min(max(float(y),ylo),yhi)
            dx=abs(x-xc)/(xhi-xlo)
            dy=abs(y-yc)/(yhi-ylo)
            penalty=1000.*(dx+dy+dx*dx+dy*dy)
            return grid.interpolate(xc,yc)+penalty
        t12=clip_penalty(self.grids["T13/T12"],
                         o["sin2theta13"],o["sin2theta12"])
        dcp=clip_penalty(self.grids["T23/DCP"],
                         o["sin2theta23"],shape["deltaCP_degrees_signed"])
        r=float(shape["solar_over_abs_atm_ratio"])
        supported=self.r_axis[self.ratio_supported]
        rc=min(max(r,float(supported[0])),float(supported[-1]))
        # Do not bridge isolated missing ratio-profile rows.
        i=int(np.searchsorted(self.r_axis,rc,side="left"))
        i=min(max(i,0),len(self.r_axis)-1)
        if not self.ratio_supported[i]:
            allowed_idx=np.flatnonzero(self.ratio_supported)
            i=int(allowed_idx[np.argmin(abs(self.r_axis[allowed_idx]-rc))])
            rc=float(self.r_axis[i])
        rr=float(np.interp(rc,self.r_axis,self.profile_approx))
        dr=abs(r-rc)/(supported[-1]-supported[0])
        mass=rr+1000.*(dr+dr*dr)
        score=max(t12,dcp,mass)
        if not math.isfinite(score):
            raise ValueError("Invalid domain-continuation score")
        return float(score)

def optimize_case(gate,*,tanbeta,seed,maxiter,popsize):
    if not(math.isfinite(tanbeta) and tanbeta>0 and
           isinstance(seed,int) and seed>=0 and
           1<=maxiter<=2000 and 3<=popsize<=100):
        raise ValueError("Invalid scan settings")
    best_valid={"approx_score":float("inf"),"coordinates":None}
    strict_valid_evaluations=0
    def objective(x):
        nonlocal strict_valid_evaluations
        try:
            shape=source_shape(tanbeta,x)
            search_score=gate.soft_domain_search_score(shape)
            # The continuation is ONLY a heuristic. Remember the best
            # strictly supported point in case the DE result is outside.
            try:
                strict_score=gate.score_one(shape,precise=False)
                strict_valid_evaluations+=1
                if strict_score<best_valid["approx_score"]:
                    best_valid["approx_score"]=strict_score
                    best_valid["coordinates"]=np.asarray(x,dtype=float).copy()
            except ValueError:
                pass
            return search_score
        except (ValueError,OverflowError,ZeroDivisionError,
                FloatingPointError,np.linalg.LinAlgError):
            return 1e9

    # A valid-region seed is essential: unseeded DE saw all-invalid
    # populations and a constant 1e9 objective even in synthetic tests.
    anchors=[np.asarray(WITNESS["coordinates"],float)]
    anchors += [np.asarray(p,float) for p in START_ANGULAR_SEEDS.values()]
    ranked=[]
    for x in anchors:
        score=objective(x)
        if math.isfinite(score) and score<1e8:
            ranked.append((score,x))
    if not ranked:
        raise ValueError("No source-texture anchor could be evaluated")
    init_x=min(ranked,key=lambda pair:pair[0])[1]
    res=differential_evolution(
        objective,BOUNDS,seed=seed,maxiter=maxiter,popsize=popsize,
        x0=init_x,polish=True,updating="immediate",workers=1,tol=.005)
    if best_valid["coordinates"] is None:
        raise ValueError(
            "No strictly in-range NuFIT point found; cannot report "
            "clipped-domain proxy as an experimental profile result")
    # Optimizer can terminate slightly outside a finite NuFIT table.
    # Strictly re-score the best IN-RANGE candidate instead.
    selected=best_valid["coordinates"]
    shape=source_shape(tanbeta,selected)
    precise=gate.scores(shape,precise=True)
    if shape["charged_mass_closure_GeV"]>1e-9:
        raise ValueError("Charged-lepton closure failed")
    out={
        "status":STATUS,"NuFIT_variant_optimized":gate.variant,
        "tanbeta":tanbeta,"seed":seed,
        "search_coordinates":selected.tolist(),
        "optimizer_terminal_coordinates":res.x.tolist(),
        "reported_coordinates_equal_optimizer_terminal":bool(
            np.array_equal(selected,res.x)),
        "strictly_in_range_evaluations":strict_valid_evaluations,
        "domain_continuation_is_search_heuristic_NOT_experimental_Delta_chi2":True,
        "source_texture_parameters":shape["parameters"],
        "ordering":"IO",
        "oscillation_observables":shape["observables"],
        "deltaCP_degrees_signed":shape["deltaCP_degrees_signed"],
        "mass_splitting_ratio":shape["solar_over_abs_atm_ratio"],
        "charged_mass_closure_GeV":shape["charged_mass_closure_GeV"],
        "approximate_optimizer_search_heuristic_NOT_Delta_chi2":float(res.fun),
        "selected_strict_in_domain_approx_worst_profile":float(best_valid["approx_score"]),
        "source_verified_2D_profiles_DO_NOT_SUM":{
          name:{"delta_chi2":float(value),
                "outside_3sigma_2dof":bool(value>THRESHOLD_3SIGMA_2DOF)}
          for name,value in precise.items()
        },
        "worst_2D_profile_delta_chi2_NOT_JOINT":max(precise.values()),
        "all_three_2D_profiles_at_or_below_3sigma":all(
            v<=THRESHOLD_3SIGMA_2DOF for v in precise.values()),
        "optimizer_global_optimum_proved":False,
        "mass_scale_profile_method":"10001 finite samples along source ratio; no continuous minimum certificate",
        "full_NuFIT6p1_joint_likelihood":False,
        "all_Zee_model_constraints_checked":False,
        "physical_Zee_allowed":None,
    }
    return out

def parse_positive_floats(v):
    x=[float(t) for t in v.split(",")]
    if not x or any(not math.isfinite(k) or k<=0 for k in x) or len(set(x))!=len(x):
        raise ValueError("tanbetas must be distinct positive floats")
    return x

def parse_seeds(v):
    x=[int(t) for t in v.split(",")]
    if not x or any(k<0 for k in x) or len(set(x))!=len(x):
        raise ValueError("seeds must be distinct nonnegative integers")
    return x

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tb-off-io",required=True,type=Path)
    ap.add_argument("--tb-yes-io",required=True,type=Path)
    ap.add_argument("--optimize-variant",choices=tuple(TABLES),
                    default="TBoff-IO")
    ap.add_argument("--tanbetas",default="5.597170833164245,10,15,20")
    ap.add_argument("--seeds",default="20261018,20261019,20261020")
    ap.add_argument("--maxiter",type=int,default=120)
    ap.add_argument("--popsize",type=int,default=12)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists():ap.error("Refuse to overwrite existing results")
    betas=parse_positive_floats(a.tanbetas)
    seeds=parse_seeds(a.seeds)
    gs={
        "TBoff-IO":ProfileGate(a.tb_off_io,"TBoff-IO"),
        "TByes-IO":ProfileGate(a.tb_yes_io,"TByes-IO"),
    }
    primary=gs[a.optimize_variant]
    rows=[]
    print("STATUS",STATUS,flush=True)
    print("PRIMARY_VARIANT",primary.variant,"RUNS",len(betas)*len(seeds),flush=True)
    for tb in betas:
        for seed in seeds:
            result=optimize_case(primary,tanbeta=tb,seed=seed,
                                 maxiter=a.maxiter,popsize=a.popsize)
            shape=source_shape(tb,result["search_coordinates"])
            for name,gate in gs.items():
                if name==primary.variant:continue
                vals=gate.scores(shape,precise=True)
                result["other_variant_"+name+"_profiles_DO_NOT_SUM"]={
                    k:float(v) for k,v in vals.items()}
            rows.append(result)
            print("SOURCE61_CASE","tanbeta",tb,"seed",seed,
                  "worst_chi2_projection",round(result[
                      "worst_2D_profile_delta_chi2_NOT_JOINT"],5),
                  "all_projection_3sigma",result[
                      "all_three_2D_profiles_at_or_below_3sigma"],
                  "ratio",round(result["mass_splitting_ratio"],6),
                  "sin2theta23",round(result[
                      "oscillation_observables"]["sin2theta23"],6),
                  "deltaCP",round(result["deltaCP_degrees_signed"],3),
                  flush=True)
    best={}
    for tb in betas:
        cases=sorted((r for r in rows if r["tanbeta"]==tb),
            key=lambda r:r["worst_2D_profile_delta_chi2_NOT_JOINT"])
        best[str(tb)]=cases[0]
        print("BEST_TANBETA",tb,
              "WORST_PROJECTION",cases[0]["worst_2D_profile_delta_chi2_NOT_JOINT"],
              "SCORES",json.dumps(cases[0][
                  "source_verified_2D_profiles_DO_NOT_SUM"],sort_keys=True),
              flush=True)
    result={
        "status":STATUS,
        "purpose":"necessary 2D marginalized projection screen, not joint fit",
        "provenance":{key:g.provenance for key,g in gs.items()},
        "optimized_variant":a.optimize_variant,
        "minimax_not_sum":True,
        "threshold_3sigma_two_dof":THRESHOLD_3SIGMA_2DOF,
        "selected_tanbetas":betas,
        "seeds":seeds,
        "model_note":"restricted family-Z2 symmetry-basis Yukawa texture; no unrestricted B2",
        "scalar_high_tanbeta_BFB_unitarity_vacuum":"NOT_EVALUATED",
        "modern_cosmology":"NOT_EVALUATED",
        "LFV":"NOT_EVALUATED",
        "HiggsTools_and_quark_flavor":"NOT_EVALUATED",
        "NuFIT6p1_complete_joint_likelihood":"NOT_AVAILABLE",
        "physical_Zee_allowed":None,
        "cases":rows,
        "best_by_tanbeta":best,
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("FULL_JOINT_LIKELIHOOD_DONE False")
    print("FULL_ZEE_ALLOWED False")
    print("OUTPUT",a.output)

if __name__=="__main__":
    main()

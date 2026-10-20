#!/usr/bin/env python3
"""E6: original-Zee cubic scalar hgamma gamma and full mixed-mass hZgamma LO.

Both charged Higgs scalar one-loop subsets are included; the hZgamma
finite mixed-mass PV formula includes offdiagonal Z H1 H2 couplings.
HiggsTools original E5 chi2 and full widths are reproduced first.
The gamma gamma correction is a charged-scalar amplitude ratio applied to
HiggsTools base width; Zgamma uses the full LO ratio including modified
W/fermion and all charged-scalar loops over the higher-order SM width.

This remains a conditional mixed-order 125 GeV HiggsSignals fit:
heavy HiggsBounds, higher-order loop matching, complete CLFV,
B->Xs gamma, exact neutrino likelihood, global vac all remain absent.
"""
from __future__ import annotations
import argparse,cmath,csv,hashlib,json,math,os,sys,traceback
from pathlib import Path
import numpy as np
from gate6_benchmark import benchmark
from gate6_width_inventory import trilinears
from gate7_map_p2_to_yangwu import map_point
from zee_gateE6_zgamma_mixed_PV import zgam_ratio
import zee_gateE5_309_h125_higgssignals_effective as e5

STATUS="E6_309_ZEE_CHARGED_SCALAR_GAMGAM_ZGAM_MIXEDPV_HS_NOT_ALLOWED"
MH=125.0
VEV=246.21965
MZ=91.1876
SW2=.23122
LO_MASSES={"W":80.379,"t":172.5,"b":4.18,"c":1.27,"tau":1.77686}
TARGETS=("B4_0004143","B4_0003582","B4_0004173",
         "B4_0006862","B4_0006962")
SCALAR_KEYS=("alpha","beta","gamma","m12sq","mH1","mH2","mh2","ma",
             "lc","k1","k2","k12")
EXPERIMENTAL_NOT_COMPLETED=(
 "full_hZgamma_higher_order_SM_BSM_EWQCD_matching",
 "heavy_neutral_charged_HiggsBounds",
 "complete_model_lepton_flavor_and_B_to_Xs_gamma_likelihood",
 "global_tree_vacuum_minimum_proof",
 "fully_matched_production_and_higher_order_hgamma_gamma",
)


def stable(x,label):
 z=float(x)
 if not math.isfinite(z):raise ValueError("Nonfinite "+label)
 return z


def potential_parameters(p):
 if not all(k in p for k in SCALAR_KEYS):
  raise ValueError("Original B4 scalar point has incomplete Zee potential")
 kw={k:float(p[k]) for k in
     ("alpha","gamma","m12sq","mh2","ma","lc","k1","k2","k12")}
 return benchmark(beta=float(p["beta"]),mH1=float(p["mH1"]),
                  mH2=float(p["mH2"]),**kw)


def physical_vectors(beta,gamma):
 sb,cb=math.sin(beta),math.cos(beta)
 sg,cg=math.sin(gamma),math.cos(gamma)
 g=np.array([cb,sb,0.])
 light=np.array([-sb*cg,cb*cg,sg])
 heavy=np.array([sb*sg,-cb*sg,cg])
 U=np.column_stack((g,light,heavy))
 if not np.allclose(U.T@U,np.eye(3),atol=1e-13):
  raise ValueError("Charged Zee rotation not orthonormal")
 return U


def mass_matrix_fixed_lagrangian(p,v1,v2):
 """Gauge charged Hessian with fixed LAGRANGIAN quadratic coefficients.

 Independently differentiate this potential when calculating cubic vertices;
 never differentiate physical mass eigenvalues while holding beta fixed.
 """
 q=p["quartics"];x=p["inputs"]
 b=x["beta"];v=x["v"];m12=x["m12sq"]
 s,c=math.sin(b),math.cos(b)
 l1,l2,l3,l4,l5=[q["lambda"+str(i)] for i in range(1,6)]
 l345=l3+l4+l5
 m11=m12*s/c-.5*v*v*(l1*c*c+l345*s*s)
 m22=m12*c/s-.5*v*v*(l2*s*s+l345*c*c)
 mC=p["mc2_GeV2"];mu=p["mu4_GeV"]
 return np.array([
  [m11+.5*(l1*v1*v1+l3*v2*v2),
       -m12+.5*(l4+l5)*v1*v2,
       mu*v2/math.sqrt(2)],
  [-m12+.5*(l4+l5)*v1*v2,
       m22+.5*(l2*v2*v2+l3*v1*v1),
       -mu*v1/math.sqrt(2)],
  [mu*v2/math.sqrt(2),-mu*v1/math.sqrt(2),
       mC+.5*(x["k1"]*v1*v1+x["k2"]*v2*v2
              -2*x["k12"]*v1*v2)],
 ],float)


def hcharged_trilinears(point):
 """Independent gauges: full 3x3 Hessian derivative AND Higgs-basis quartics."""
 p=potential_parameters(point)
 x=p["inputs"];b=x["beta"];a=x["alpha"];g=x["gamma"];v=x["v"]
 sb,cb=math.sin(b),math.cos(b)
 U=physical_vectors(b,g)
 H=mass_matrix_fixed_lagrangian(p,v*cb,v*sb)
 masses=U.T@H@U
 expected=np.diag([0.,x["mH1"]**2,x["mH2"]**2])
 if np.max(abs(masses-expected))>2e-6*max(1.,x["mH2"]**2):
  raise ValueError("Original Zee charged mass eigenvectors do not close")
 # Independent numerical differentiation of fixed potential's charged Hessian
 eps=1e-3
 Np=mass_matrix_fixed_lagrangian(p,v*cb+eps*math.cos(a),
                                  v*sb+eps*math.sin(a))
 Nm=mass_matrix_fixed_lagrangian(p,v*cb-eps*math.cos(a),
                                  v*sb-eps*math.sin(a))
 G_fd=U.T@((Np-Nm)/(2*eps))@U
 # Higgs basis analytically reconstructed from the SAME scalar potential,
 # independent of the gauge-basis cubic expression.
 mapping=map_point(beta=b,mH1=x["mH1"],mH2=x["mH2"],
                   **{k:float(point[k]) for k in ("alpha","gamma","m12sq","mh2",
                                       "ma","lc","k1","k2","k12")})
 m=mapping["map"]["ZEELAMS"]
 Z3,Z7,K1,K12=(m[2],m[3],m[4],m[6])
 delta=a-b
 c,s=math.cos(delta),math.sin(delta)
 dHD=v*(Z3*c+Z7*s)
 dS=v*(K1*c+K12*s)
 dMix=-p["mu4_GeV"]*c/math.sqrt(2)
 R=np.array([[math.cos(g),-math.sin(g)],
             [math.sin(g),math.cos(g)]],float)
 G_higgs=R.T@np.array([[dHD,dMix],[dMix,dS]])@R
 G_num=G_fd[1:,1:]
 if np.max(abs(G_num-G_higgs))>2e-6*max(1.,np.max(abs(G_num))):
  raise ValueError("Independent gauge/Higgs-basis h charged cubic mismatch")
 # Separate prior LO charged 3x3 Hessian (off-diagonal hH1H2).
 previous=trilinears(p)["h125"]
 if not math.isclose(G_num[0,1],previous,rel_tol=2e-7,abs_tol=1e-5):
  raise ValueError("Existing Gate6 offdiagonal charged trilinear differs")
 # Photon charge generator is proportional to identity -> only diagonal g.
 # Nonzero h12 couples to Z12 in full mixed-mass Zgamma.
 z_D=(.5-SW2);z_S=-SW2
 Z=R.T@np.diag([z_D,z_S])@R
 if abs(Z[0,1])<1e-8:
  raise ValueError("Offdiagonal Zee Z current unexpectedly absent")
 if not math.isclose(float(Z[0,1]),-.25*math.sin(2*g),
                     rel_tol=2e-12,abs_tol=1e-13):
  raise ValueError("Offdiagonal ZH1H2 current violates gauge rotation identity")
 if not np.isfinite(G_num).all():
  raise ValueError("Nonfinite hH+H- vertex")
 return {
  "g_h_H1plus_H1minus_GeV":float(G_num[0,0]),
  "g_h_H2plus_H2minus_GeV":float(G_num[1,1]),
  "g_h_H1plus_H2minus_GeV":float(G_num[0,1]),
  "hessian_Higgs_basis_max_abs_residual_GeV":
      float(np.max(abs(G_num-G_higgs))),
  "mass_eigensystem_max_abs_residual_GeV2":
      float(np.max(abs(masses-expected))),
  "Z_generator_T3_minus_sW2_mass_basis":Z.tolist(),
  "offdiagonal_Z_H1_H2_nonzero":True,
  "lambda_definition":"V includes +g_hij*h*H_i^-H_j^+; L=-V",
  "source":"gate6 tree potential, fixed-mass gauge Hessian, gate7 Higgs basis",
 }


def f_triangle(tau):
 if tau<=0:raise ValueError("Loop tau nonpositive")
 if tau<=1.:
  return complex(math.asin(math.sqrt(tau))**2)
 q=math.sqrt(1.-1./tau)
 return -.25*(cmath.log((1.+q)/(1.-q))-1j*math.pi)**2


def a_scalar(tau):
 f=f_triangle(tau)
 return -(tau-f)/(tau*tau)


def a_fermion(tau):
 f=f_triangle(tau)
 return 2*(tau+(tau-1.)*f)/(tau*tau)


def a_fermion_odd(tau):
 return 2*f_triangle(tau)/tau


def a_vector(tau):
 f=f_triangle(tau)
 return -(2*tau*tau+3*tau+3*(2*tau-1.)*f)/(tau*tau)


def gamma_lo_amplitudes(c):
 """LO SM particle amplitudes with complex diagonal Yukawas.

 Fermion complex input real=CP even, imaginary=CP odd and does not
 interfere with scalar/W. This is LO amplitude-matched to HiggsTools'
 reference BR (NOT claiming its higher-order amplitude implemented).
 """
 def tau(m):return MH*MH/(4*m*m)
 scalar=c["WW"]*a_vector(tau(LO_MASSES["W"]))
 odd=0j
 terms=(("tt","t",4./3.),("bb","b",1./3.),
        ("cc","c",4./3.),("tautau","tau",1.))
 for name,m,charge in terms:
  k=complex(c[name])
  scalar+=charge*k.real*a_fermion(tau(LO_MASSES[m]))
  odd+=charge*k.imag*a_fermion_odd(tau(LO_MASSES[m]))
 return scalar,odd


def gamma_ratio(package,trilinears):
 cs=package["effective_couplings"]
 even,odd=gamma_lo_amplitudes(cs)
 scalar=[]
 for mass,coupling in (
     (package["scalar"]["mH1"],trilinears["g_h_H1plus_H1minus_GeV"]),
     (package["scalar"]["mH2"],trilinears["g_h_H2plus_H2minus_GeV"])):
  if mass<=MH/2.:raise ValueError("Charged scalar below h gamma loop threshold")
  z=VEV*coupling/(2*mass*mass)*a_scalar(MH*MH/(4*mass*mass))
  scalar.append(z)
 den=abs(even)**2+abs(odd)**2
 if not den>1e-10:raise ValueError("Vanishing SM-particle h gamma amplitude")
 ratio=(abs(even+sum(scalar))**2+abs(odd)**2)/den
 if not math.isfinite(ratio) or ratio<=0:
  raise ValueError("Invalid scalar-added h gamma gamma width")
 return {
  "SM_particle_even_LO_amplitude":[even.real,even.imag],
  "SM_particle_odd_LO_amplitude":[odd.real,odd.imag],
  "H1_charged_scalar_LO_amplitude":[scalar[0].real,scalar[0].imag],
  "H2_charged_scalar_LO_amplitude":[scalar[1].real,scalar[1].imag],
  "new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio":ratio,
  "charged_scalar_amplitudes_with_BOTH_mass_eigenstates":True,
  "Zgamma_offdiagonal_loop_not_part_of_diphoton_subamplitude":True,
 }


def base_model_verified(signals,HP,pack,original,smwidth):
 pred,h,old,tot=e5.build_predictions(HP,pack)
 chi=e5.finite(signals(pred),"E6 reproduce E5 chi2")
 saved=e5.finite(original["h125_effective_HiggsSignals_chi2"],"E5 old chi2")
 if not math.isclose(chi,saved,rel_tol=1e-9,abs_tol=5e-6):
  raise ValueError("E5 old chi2 not reproducible")
 if not math.isclose(tot,original["h125_total_width_with_h_LFV_GeV"],
                     rel_tol=1e-8,abs_tol=1e-9):
  raise ValueError("E5 total width source drift")
 return pred,h,chi,tot


def evaluate(signals,HP,pack,original,SM_reference_width):
 p,h,base_chi,old_total=base_model_verified(
  signals,HP,pack,original,SM_reference_width)
 # First verify the gamma partial width supplied by source HiggsTools.
 oldgam=e5.finite(h.totalWidth()*h.br("gamgam"),"baseline gamma partial")
 if oldgam<=0:raise ValueError("Baseline HiggsTools gamgam width nonpositive")
 # Cross-check the LO amplitude RATIO against the actual HiggsTools
 # baseline gamma width scaling (higher-order differences permitted).
 refgam=SM_reference_width.get("sm_gamma_GeV")
 LO_ratio_deviation=None
 if refgam is not None:
  even,odd=gamma_lo_amplitudes(pack["effective_couplings"])
  unity=dict(pack["effective_couplings"])
  for key in ("tt","bb","cc","tautau"):
   unity[key]=1+0j
  unity["WW"]=1.
  smeven,_=gamma_lo_amplitudes(unity)
  approx=(abs(even)**2+abs(odd)**2)/abs(smeven)**2
  actual=oldgam/e5.finite(refgam,"SM reference gamma width")
  LO_ratio_deviation=abs(actual-approx)/max(1e-8,abs(actual))
  if LO_ratio_deviation>.08:
   raise ValueError("E5 HiggsTools vs LO SM-particle diphoton normalization drift")
 tri=hcharged_trilinears(pack["scalar"])
 loop=gamma_ratio(pack,tri)
 newgam=oldgam*loop["new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"]
 h.setDecayWidth("gamgam",newgam)
 gammachi=e5.finite(signals(p),"HiggsSignals gamma-only corrected chi2")
 # Complete charged Zee scalar Zgamma form factor includes unequal-mass
 # i!=j loops and coherent SM W/fermion amplitudes, using Florentino D.20.
 oldzgam=e5.finite(h.totalWidth()*h.br("Zgam"),"baseline Zgamma partial")
 if oldzgam<=0:raise ValueError("HiggsTools baseline Zgamma width unavailable")
 refz=SM_reference_width.get("sm_Zgamma_GeV")
 if refz is not None and not math.isclose(oldzgam,refz,rel_tol=2e-8,abs_tol=1e-12):
  raise ValueError("E5 Zgamma reference not SM-like despite effective Zgam=1")
 zloop=zgam_ratio(pack,tri)
 zrat=zloop["full_charged_scalar_plus_modified_SM_LO_hZgamma_over_SM_LO_width"]
 newzgam=oldzgam*zrat
 h.setDecayWidth("Zgam",newzgam)
 total=e5.finite(h.totalWidth(),"HiggsTools post-gamma+Zgamma total")
 if not math.isclose(total,old_total-oldgam+newgam-oldzgam+newzgam,
                     rel_tol=2e-8,abs_tol=1e-9):
  raise ValueError("HiggsTools total width not updated after both loop corrections")
 for key,val in (("gamgam",newgam),("Zgam",newzgam)):
  if not math.isclose(h.br(key),val/total,
                      rel_tol=2e-9,abs_tol=1e-12):
   raise ValueError("HiggsTools loop decay BR not propagated: "+key)
 newchi=e5.finite(signals(p),"HiggsSignals gamma+Zgamma corrected chi2")
 return {
  "candidate_id":pack["candidate_id"],
  "E5_original_chisq_reproduced":base_chi,
  "h_gamma_gamma_and_Zgamma_scalar_corrected_chisq":newchi,
  "delta_chisq_vs_original_E5":newchi-base_chi,
  "chi2_after_charged_gamma_only":gammachi,
  "delta_chisq_additional_from_full_mixed_Zgamma":newchi-gammachi,
  "E5_original_delta_chisq_vs_SM":
      original["delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL"],
  "charged_scalar_trilinears":tri,
  "loop_amplitudes":loop,
  "HiggsTools_vs_LO_gamma_scaling_relative_deviation":LO_ratio_deviation,
  "Zgamma_full_mixed_mass_PV_amplitudes":zloop,
  "gamma_gamma_original_partial_GeV":oldgam,
  "gamma_gamma_corrected_partial_GeV":newgam,
  "gamma_gamma_corrected_BR":float(h.br("gamgam")),
  "Zgamma_original_partial_GeV":oldzgam,
  "Zgamma_corrected_partial_GeV":newzgam,
  "Zgamma_corrected_BR":float(h.br("Zgam")),
  "h125_corrected_total_width_GeV":total,
  "delta_chisq_vs_same_SM":
      newchi-SM_reference_width["smchi"],
  "source_type":"h125 LO charged scalar diphoton and mixed-mass Zgamma subsets plus E5 HiggsTools",
  "h_Zgamma_full_one_loop_charged_scalar_mixed_mass_completed":True,
  "h_Zgamma_higher_order_matching_uncertified":True,
  "charged_scalar_QED_photon_offdiagonal":False,
  "full_Zee_allowed_or_excluded":None,
 }


def source_inputs(e2,e3,e4h,e5dir,hs):
 pts,src,refs,hashes=e5.validated_sources(e2,e3,e4h)
 old=e5.load(e5dir/"summary.json")
 manifest=e5.load(e5dir/"manifest.json")
 measured=e5.dataset_provenance(hs)
 contract={
   "source":hashes,
   "dataset":{"dataset_sha256_manifest":measured["dataset_sha256_manifest"],
       "file_count":measured["file_count"],"path":measured["path"]},
   "main_source_script_sha256":e5.sha256(Path(e5.__file__)),
   "h125_mass_GeV":float(e5.MH),
   "partial_model_flags":e5.VALIDITY,
 }
 if (old.get("status")!=e5.STATUS or
     old.get("HiggsSignals_chi2_evaluated_in_effective_coupling_approx")!=309 or
     old.get("HiggsSignals_number_loaded_observables")!=159 or
     old.get("full_model_allowed_points") is not None or
     manifest.get("status")!=e5.STATUS or
     manifest.get("summary_SHA256")!=e5.sha256(e5dir/"summary.json")):
  raise ValueError("E5 309-case original experimental source status drift")
 oldprov=manifest.get("provenance",{})
 for key,value in contract.items():
  if oldprov.get(key)!=value:
   raise ValueError("E5 source/dataset mismatched: "+key)
 path=e5dir/"E5_309_h125_conditional_HS_chi2_NOT_ALLOWED.jsonl"
 if e5.sha256(path)!=old.get("output_sha256",{}).get(path.name):
  raise ValueError("Original E5 row evidence SHA mismatch")
 orig={}
 with path.open() as f:
  for line in f:
   row=json.loads(line);key=row["candidate_id"]
   if key in orig or key not in pts or (
      row.get("full_Zee_physical_allowed_or_excluded") is not None):
    raise ValueError("Invalid E5 old spectrum identifier")
   orig[key]=row
 if len(orig)!=309 or set(orig)!=set(pts):
  raise ValueError("Original E5 cohort source IDs incomplete")
 return pts,src,refs,orig,{
  "E5_summary_SHA256":e5.sha256(e5dir/"summary.json"),
  "E5_evidence_SHA256":e5.sha256(path),
  "E5_manifest_SHA256":e5.sha256(e5dir/"manifest.json"),
  "input_source_E5":oldprov,
  "dataset_SHA256":measured["dataset_sha256_manifest"],
  "E6_script_SHA256":e5.sha256(Path(__file__)),
  "E6_mixed_PV_source_SHA256":e5.sha256(
      Path(__file__).with_name("zee_gateE6_zgamma_mixed_PV.py")),
 }


def resume_read(file,ids):
 rows={}
 if file.exists():
  with file.open() as f:
   for line in f:
    rec=json.loads(line);k=rec["candidate_id"]
    if k in rows or k not in ids or rec.get("full_Zee_allowed_or_excluded") is not None:
     raise ValueError("Invalid E6 saved checkpoint")
    rows[k]=rec
 return rows


def finish(folder,rows,cohort,proof,smchi,nobs):
 if len(rows)!=309 or set(rows)!=set(cohort):
  raise ValueError("E6 cannot finalize partial cohort")
 js=folder/"E6_309_gamma_Zgamma_loop_corrected_HS_NOT_ALLOWED.jsonl"
 with js.open("w") as f:
  for key in sorted(rows):
   f.write(json.dumps(rows[key],sort_keys=True,allow_nan=False)+"\n")
 data=[]
 for key,entry in rows.items():
  scal=cohort[key]["scalar"]
  data.append({
   "candidate_id":key,"mH1_GeV":scal["mH1"],"mH2_GeV":scal["mH2"],
   "gamma":scal["gamma"],"alpha_minus_beta":scal["alpha"]-scal["beta"],
   "cascade_proxy_NOT_event_yield":cohort[key]["cascade_proxy_not_xsec"],
   "old_HiggsSignals_delta_vs_SM":entry["E5_original_delta_chisq_vs_SM"],
   "gamma_Zgamma_loop_corrected_delta_vs_SM":entry["delta_chisq_vs_same_SM"],
   "delta_chisq_change_gamma_and_Zgamma_loops":entry["delta_chisq_vs_original_E5"],
   "delta_chisq_additional_Zgamma":
       entry["delta_chisq_additional_from_full_mixed_Zgamma"],
   "gamma_partial_width_ratio":
     entry["loop_amplitudes"]["new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"],
   "Zgamma_LO_over_SM_width_ratio":
     entry["Zgamma_full_mixed_mass_PV_amplitudes"][
       "full_charged_scalar_plus_modified_SM_LO_hZgamma_over_SM_LO_width"],
   "ghH1H1_GeV":entry["charged_scalar_trilinears"]["g_h_H1plus_H1minus_GeV"],
   "ghH2H2_GeV":entry["charged_scalar_trilinears"]["g_h_H2plus_H2minus_GeV"],
   "g_hH1H2_GeV":entry["charged_scalar_trilinears"]["g_h_H1plus_H2minus_GeV"],
   "full_Zee_allowed":None})
 data.sort(key=lambda p:(p["gamma_Zgamma_loop_corrected_delta_vs_SM"],
                          -p["cascade_proxy_NOT_event_yield"]))
 csvfile=folder/"E6_309_gamma_Zgamma_loop_HS_ranked_NOT_ALLOWED.csv"
 with csvfile.open("w",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=list(data[0]))
  writer.writeheader();writer.writerows(data)
 delta=np.array([x["gamma_Zgamma_loop_corrected_delta_vs_SM"] for x in data])
 old=np.array([x["old_HiggsSignals_delta_vs_SM"] for x in data])
 rate=np.array([x["gamma_partial_width_ratio"] for x in data])
 zrate=np.array([x["Zgamma_LO_over_SM_width_ratio"] for x in data])
 obj={
  "status":STATUS,"original_source_models":309,
  "updated_HiggsSignals_hgamma_gamma_models":309,
  "SM_chi2_reference":smchi,"same_HiggsSignals_observables":nobs,
  "old_E5_delta_chi2_median":float(np.median(old)),
  "scalar_gamma_Zgamma_corrected_delta_chi2_min":float(np.min(delta)),
  "scalar_gamma_Zgamma_corrected_delta_chi2_median":float(np.median(delta)),
  "scalar_gamma_Zgamma_corrected_delta_chi2_max":float(np.max(delta)),
  "scalar_gamma_partial_width_ratio_min_median_max":[
       float(np.min(rate)),float(np.median(rate)),float(np.max(rate))],
  "full_mixed_scalar_Zgamma_LO_width_ratio_min_median_max":[
       float(np.min(zrate)),float(np.median(zrate)),float(np.max(zrate))],
  "descriptive_gamma_Zgamma_corrected_delta_less_than_1":int(np.sum(delta<1)),
  "descriptive_gamma_Zgamma_corrected_delta_less_than_4":int(np.sum(delta<4)),
  "descriptive_gamma_Zgamma_corrected_delta_less_than_10":int(np.sum(delta<10)),
  "target_benchmarks":{tag:rows[tag] for tag in TARGETS},
  "no_cut_is_a_physical_exclusion":True,
  "full_h_to_Zgamma_one_loop_scalar_subset_with_mixed_mass_completed":True,
  "full_h_to_Zgamma_higher_order_model_prediction_NOT_completed":True,
  "missing_physics":EXPERIMENTAL_NOT_COMPLETED,
  "full_Zee_allowed_or_excluded":None,
  "source":proof,
  "output_hashes":{p.name:e5.sha256(p) for p in (js,csvfile)},
 }
 e5.save(folder/"summary.json",obj)
 return obj


def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for label in ("e2-dir","e3-dir","e4h-dir","e5-dir","hs-dataset","output-dir"):
  ap.add_argument("--"+label,type=Path,required=True)
 ap.add_argument("--resume",action="store_true")
 a=ap.parse_args()
 out=a.output_dir.resolve()
 if not e5.ROOT.resolve().is_relative_to(Path("/home")):
  ap.error("Only execute work in /home")
 if not out.is_relative_to(e5.ROOT.resolve()/"work"):
  ap.error("Output outside /home/aalida/zee/work")
 if out.exists() and any(out.iterdir()) and not a.resume:
  ap.error("Refuse existing E6 output; use fresh path or --resume")
 if a.resume and not (out/"manifest.json").exists():
  ap.error("Cannot resume without source manifest")
 out.mkdir(parents=True,exist_ok=True)
 try:
  import Higgs.predictions as HP
  import Higgs.signals as HS
  pts,src,refs,old,proof=source_inputs(
      a.e2_dir.resolve(),a.e3_dir.resolve(),a.e4h_dir.resolve(),
      a.e5_dir.resolve(),a.hs_dataset.resolve())
  hsp=str(Path(HP.__file__).resolve())
  hss=str(Path(HS.__file__).resolve())
  old_e5=e5.load(a.e5_dir/"summary.json")
  if (hsp!=old_e5["provenance"]["Higgs_pred_module_path"] or
      hss!=old_e5["provenance"]["Higgs_signals_module_path"]):
   raise ValueError("Compiled HiggsTools changed since E5")
  manifest={"source":proof,"Higgs_pred_module":hsp,"Higgs_signals_module":hss,
            "cohort_ids":sorted(pts)}
  if a.resume:
   prev=e5.load(out/"manifest.json")
   if prev.get("source")!=manifest or (out/"summary.json").exists():
    raise ValueError("E6 cannot resume different script, E5 or completed data")
  else:e5.save(out/"manifest.json",{"status":"E6_RUNNING_NOT_ALLOWED",
                                   "source":manifest})
  signals,smchi,nobs=e5.sm_baseline(HP,HS,a.hs_dataset.resolve())
  smpred=HP.Predictions()
  smh=smpred.addParticle(HP.BsmParticle("e6_SM",charge="neutral",cp="even"))
  smh.setMass(float(MH))
  HP.effectiveCouplingInput(smh,HP.smLikeEffCouplings)
  smref={"smchi":smchi,
         "sm_gamma_GeV":float(smh.totalWidth()*smh.br("gamgam")),
         "sm_Zgamma_GeV":float(smh.totalWidth()*smh.br("Zgam"))}
  if min(smref["sm_gamma_GeV"],smref["sm_Zgamma_GeV"])<=0:
   raise ValueError("SM reference gamma/Zgamma widths missing")
  if nobs!=159 or not math.isclose(
      smchi,old_e5["HiggsSignals_chi2_SM_at_identical_125GeV_and_dataset"],
      rel_tol=1e-9,abs_tol=1e-6):
   raise ValueError("E5/E6 SM reference or dataset disagrees")
  packs={key:e5.model_couplings(pts[key],src[key],refs[key])
         for key in sorted(pts)}
  for key in packs:
   packs[key]["scalar"].update(
       {q:float(pts[key][q]) for q in SCALAR_KEYS})
  cp=out/"E6_309_checkpoint.jsonl"
  done=resume_read(cp,packs)
  with cp.open("a") as stream:
   for idx,key in enumerate(sorted(packs),1):
    if key in done:continue
    row=evaluate(signals,HP,packs[key],old[key],smref)
    stream.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
    stream.flush();os.fsync(stream.fileno())
    done[key]=row
    print("E6_GAMMA_ZGAM_LOOP_HS",idx,"/309",key,
          "DCHI2_OLD",row["E5_original_delta_chisq_vs_SM"],
          "DCHI2_UPDATED",row["delta_chisq_vs_same_SM"],
          "R_GAMGAM",row["loop_amplitudes"][
              "new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"],
          "R_ZGAM",row["Zgamma_full_mixed_mass_PV_amplitudes"][
            "full_charged_scalar_plus_modified_SM_LO_hZgamma_over_SM_LO_width"],
          "FULL_MODEL_NOT_ALLOWED",flush=True)
  summary=finish(out,done,packs,proof,smchi,nobs)
  e5.save(out/"manifest.json",{"status":STATUS,"source":manifest,
                  "summary_SHA256":e5.sha256(out/"summary.json")})
  print("E6_STATUS",STATUS,"COMPLETED",309,
        "HIGGSSIGNALS_OLD_AND_NEW",True,
        "Z_GAMMA_OFFDIAGONAL_MIXED_SCALAR_LO_INCLUDED",True,
        "HIGHER_ORDER_LOOPS_UNCALIBRATED",True,
        "FULL_ZEE_ALLOWED_UNKNOWN",flush=True)
  print("E6_SUMMARY",out/"summary.json",flush=True)
  return 0
 except Exception as exc:
  e5.save(out/"error.json",{"status":"E6_BLOCKED_NOT_FULL_ZEE_ALLOWED",
                             "error":repr(exc),"traceback":traceback.format_exc(),
                             "full_Zee_allowed_or_excluded":None})
  print("E6_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
  return 1


if __name__=="__main__":
 raise SystemExit(main())

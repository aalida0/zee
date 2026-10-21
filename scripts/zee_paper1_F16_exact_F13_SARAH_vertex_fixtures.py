#!/usr/bin/env python3
"""F16: Three exact F13/F14 points -> independently auditable SARAH vertices.

SOURCE: three original *complex* optimized f,Y, original F13 scalar
potential, F14 production. Reconstruct actual two-VEV potential and
gauge-invariant SU2 quartics; serialize numeric SARAH tree-level model
input matrices and source widths into a Wolfram fixture.

Run the actual SARAH vertex check on the user's local Mathematica host
using scripts/zee_paper1_F16_sarah_vertex_audit.m (after transferring
the generated source-hashed directory). No UFO and no physical
complete-5-state MadWidth BR exists until these gates and full card
matching. The output is a reproducible independent calculation input,
not a MadGraph parameter card.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from gate6_benchmark import benchmark
from gate6_width_inventory import trilinears,vector_width,scalar_width,MZ
from gateA1b_hierarchical_no_seed import ME,MMU,MTAU
from zee_paper1_F15_charged_width_CKM_mass_scheme_audit import (
    TARGETS,join_origins,source_b3,close)
from zee_p1_scalar_higgs_basis_map import check_quartic
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import ROOT,digest,writejson
from gateB3_general_zee_charged_lepton_widths import complex_matrix

STATUS="F16_THREE_EXACT_ZEE_SARAH_SCALAR_FLAVOR_VERTEX_FIXTURES_NOT_MADWIDTH_BR"
FIXTURE="F16_three_exact_F13_Zee_SARAH_charged_vertices.m"
CHECK="F16_three_exact_F13_Zee_input_reconstruction.json"
MISSING=(
 "local Mathematica SARAH must actually run vertex/SLHA mass-matrix checks",
 "SARAH MakeUFO successful export + complete complex-quark/CKM parametrization",
 "source-matched SLHA physical mass/mixing/SM/lepton Yukawa parameter card",
 "independent MadWidth 2- and 3-body width closure in full gauge model",
 "QCD-corrected fermionic decays and off-shell/loop contributions",
 "2026 full matched B->Xs gamma, LFV and Higgs/CP vacuum constraints",
)
def wlreal(v):
    x=float(v)
    if not math.isfinite(x):raise ValueError("Nonfinite Wolfram input")
    return f"{x:.17e}".replace("e","*^")
def wlcomplex(v):
    z=complex(v)
    return "("+wlreal(z.real)+" + I*("+wlreal(z.imag)+"))"
def wlmatrix(value):
    a=np.asarray(value)
    if a.ndim!=2:raise ValueError("Expected 2D Wolfram matrix")
    return "{"+",".join("{"+",".join(wlcomplex(z) for z in row)+"}"
         for row in a)+"}"
def wlrules(mapping):
    return "{"+",".join(str(k)+" -> "+wlreal(v) for k,v in mapping.items())+"}"
def expected_sarah(point,b3,*,random_trials=36):
    """Independent Gate6 physical source->SARAH parameter and coupling gate."""
    scalar={key:float(point[key]) for key in
        ("beta","alpha","gamma","mH1","mH2","mh2","ma",
         "m12sq","lc","k1","k2","k12")}
    full=benchmark(**{
       "beta":scalar["beta"],"alpha":scalar["alpha"],
       "gamma":scalar["gamma"],"mH1":scalar["mH1"],"mH2":scalar["mH2"],
       "mh2":scalar["mh2"],"ma":scalar["ma"],
       "m12sq":scalar["m12sq"],"lc":scalar["lc"],"k1":scalar["k1"],
       "k2":scalar["k2"],"k12":scalar["k12"]})
    rotated=check_quartic(point,trial_count=random_trials,seed=20261022)
    if rotated["quartic_max_relative_residual"]>4e-11:
        raise ValueError("Higgs basis source potential no longer closes")
    inputs=full["inputs"];q=full["quartics"]
    b=scalar["beta"];a=scalar["alpha"];g=scalar["gamma"]
    v=inputs["v"];cb,sb=math.cos(b),math.sin(b)
    c,s=math.cos(g),math.sin(g)
    v1,v2=v*cb,v*sb
    l345=sum(q["lambda"+str(k)] for k in (3,4,5))
    m112=inputs["m12sq"]*(v2/v1)-.5*q["lambda1"]*v1**2-.5*l345*v2**2
    m222=inputs["m12sq"]*(v1/v2)-.5*q["lambda2"]*v2**2-.5*l345*v1**2
    rules={"v1":v1,"v2":v2,"M112":m112,"M222":m222,
           "M12Sq":inputs["m12sq"],
           "MCS2":full["mc2_GeV2"],"Mu4":full["mu4_GeV"],
           "LambdaC":inputs["lambda_c"],"K1":inputs["k1"],
           "K2":inputs["k2"],"K12":inputs["k12"]}
    rules.update({"Lambda"+str(k):q["lambda"+str(k)] for k in range(1,6)})
    cA,sA=math.cos(a),math.sin(a)
    mhh=np.array([
      [inputs["mh1"]**2*cA*cA+inputs["mh2"]**2*sA*sA,
       (inputs["mh1"]**2-inputs["mh2"]**2)*sA*cA],
      [(inputs["mh1"]**2-inputs["mh2"]**2)*sA*cA,
       inputs["mh1"]**2*sA*sA+inputs["mh2"]**2*cA*cA]])
    direction=np.array([-sb,cb])
    maa=inputs["ma"]**2*np.outer(direction,direction)
    chargedGoldstone=np.array([cb,sb,0.])
    hd=np.array([-sb,cb,0.]); singlet=np.array([0.,0.,1.])
    doublet=inputs["mH1"]**2*c*c+inputs["mH2"]**2*s*s
    other=inputs["mH1"]**2*s*s+inputs["mH2"]**2*c*c
    off=-full["mu4_GeV"]*v/math.sqrt(2)
    mhm=(doublet*np.outer(hd,hd)+other*np.outer(singlet,singlet)+
         off*(np.outer(hd,singlet)+np.outer(singlet,hd)))
    rot=np.array([[cb,sb,0.],[-sb*c,cb*c,s],[sb*s,-cb*s,c]])
    if not np.allclose(rot@mhm@rot.T,
         np.diag([0.,scalar["mH1"]**2,scalar["mH2"]**2]),
         rtol=2e-10,atol=1e-5):
        raise ValueError("Gate6 charged mass matrix not numerically diagonal")
    if not np.allclose(np.linalg.eigvalsh(mhh),
         [125.**2,scalar["mh2"]**2],atol=1e-6):
        raise ValueError("Expected scalar CP-even masses not closed")
    angle=b-a
    zh=np.array([[math.cos(a),math.sin(a)],
                 [-math.sin(a),math.cos(a)]])
    za=np.array([[cb,sb],[-sb,cb]])
    couplingZ=MZ/v*c*s
    tric=trilinears(full)
    expected={
      "masses_GeV":[125.,scalar["mh2"],scalar["ma"],
                   scalar["mH1"],scalar["mH2"]],
      "charged_Goldstone_H1_H2_rotation":rot,
      "CP_even_h125_H_rotation":zh,
      "CP_odd_Goldstone_A_rotation":za,
      "expected_mass_matrix_hh_GeV2":mhh,
      "expected_mass_matrix_Ah_GeV2":maa,
      "expected_mass_matrix_Hm_GeV2":mhm,
      "gZ_H1H2_derivative_abs":couplingZ,
      "h125_H1_H2_trilinear_abs_GeV":abs(tric["h125"]),
      "H_H1_H2_trilinear_abs_GeV":abs(tric["hheavy"]),
      "h125_H1_H2_trilinear_signed_GeV":tric["h125"],
      "H_H1_H2_trilinear_signed_GeV":tric["hheavy"],
    }
    widths=b3["partial_widths_included_GeV"]
    for k,ref in (("H2_H1_Z",widths["H2"]["H1_Z"]),
                  ("H2_H1_h125",widths["H2"]["H1_h125"]),
                  ("H2_H1_H",widths["H2"]["H1_hheavy"])):
        if k.endswith("_Z"): x=vector_width(scalar["mH2"],scalar["mH1"],
                                       MZ,couplingZ)
        else:
            name="h125" if k.endswith("h125") else "hheavy"
            ms=125. if name=="h125" else scalar["mh2"]
            x=scalar_width(scalar["mH2"],scalar["mH1"],ms,tric[name])
        close(x,ref,"Gate6 SARAH physical two-body source "+k,
              rtol=2e-10,atol=1e-8)
    return full,rules,expected,rotated

def build_case(name,row,rec,proof):
    b3,p,origin=source_b3(proof["f13dir"],name,row)
    full,rules,expected,rotation=expected_sarah(p,b3)
    record=rec[name]
    close(record["13TeV_TypeII_sigma_times_included_cascade_proxy_pb"],
          float(record["TypeII_Santander_NLO13TeV_sigma_pb"])*
          b3["production_weighted_partial_cascade_proxy"],
          "F16 source F14 cascade",rtol=5e-9,atol=1e-11)
    from pathlib import Path
    priority=json.loads(next(f for f in sorted(
        Path(proof["f13dir"]).glob("F13_priority_*_NOT_ALLOWED.json"))
        if json.loads(f.read_text())["scalar"]["id"]==name).read_text())
    best=priority["neutrino_and_partial_lfv"]["best"]
    f=complex_matrix(best["optimized_f"],"f")
    Y=complex_matrix(best["optimized_Y"],"Y")
    beta=p["beta"];v=full["inputs"]["v"]
    s,c=math.sin(beta),math.cos(beta)
    sY=np.diag(np.sqrt(2.)*np.asarray([ME,MMU,MTAU],float)/v)
    dY=np.sqrt(2.)*Y
    ye=c*sY-s*dY
    ye2=s*sY+c*dY
    fs=2*f
    if np.max(abs(c*ye+s*ye2-sY))>1e-12:
        raise ValueError("SARAH mass basis lepton Ye/Ye2 conversion failed")
    if np.max(abs(-s*ye+c*ye2-dY))>1e-12:
        raise ValueError("SARAH charged doublet Yukawa Y conversion failed")
    if np.max(abs(fs+fs.T))>1e-12:
        raise ValueError("SARAH antisymmetric Fzee conversion failed")
    if max(float(np.max(abs(ye))),float(np.max(abs(ye2))))>100:
        raise ValueError("Unphysical complex couplings in fixture")
    matrices={
        "FSARAH":fs,"YeSARAH":ye,"Ye2SARAH":ye2,
        "FChen":f,"YChen":Y}
    wid=b3["partial_widths_included_GeV"]
    meta={
        "id":name,"scalar":p,"source":origin,
        "complex_Y_and_f_reconstructed_from_exact_F13":True,
        "SARAH_E3_FSARAH_eq_2_fChEN":True,
        "SARAH_weak_vev_basis_Y_mass_rotated":True,
        "sarah_2VEV_lagrangian_rules":rules,
        "expected_Gate6_vertices":{k:(v.tolist() if isinstance(v,np.ndarray)
                                        else v) for k,v in expected.items()},
        "expected_Gate6_diagnostic_partial_widths_GeV":{
           "H2_H1Z":wid["H2"]["H1_Z"],
           "H2_H1h":wid["H2"]["H1_h125"],
           "H2_H1H":wid["H2"]["H1_hheavy"],
           "H1_tb":wid["H1"]["tb"],
           "H2_tb":wid["H2"]["tb"]},
        "full_model_madwidth_physical_totals":None,
        "complete_UFO_and_Ward_amplitudes_validated":False,
        "source_SU2_higgs_basis_rotation_relative_error":
              rotation["quartic_max_relative_residual"],
    }
    entries=[
      '"ID" -> "'+name+'"',
      '"ScalarRules" -> '+wlrules(rules),
      '"Beta" -> '+wlreal(beta),
      '"Alpha" -> '+wlreal(p["alpha"]),
      '"Gamma" -> '+wlreal(p["gamma"]),
      '"V" -> '+wlreal(v),
      '"M1" -> '+wlreal(p["mH1"]),
      '"M2" -> '+wlreal(p["mH2"]),
      '"MA" -> '+wlreal(p["ma"]),
      '"MH" -> '+wlreal(p["mh2"]),
      '"ExpectedHH" -> '+wlmatrix(expected["expected_mass_matrix_hh_GeV2"]),
      '"ExpectedAh" -> '+wlmatrix(expected["expected_mass_matrix_Ah_GeV2"]),
      '"ExpectedHm" -> '+wlmatrix(expected["expected_mass_matrix_Hm_GeV2"]),
      '"MixCharged" -> '+wlmatrix(expected["charged_Goldstone_H1_H2_rotation"]),
      '"MixCPeven" -> '+wlmatrix(expected["CP_even_h125_H_rotation"]),
      '"MixCPodd" -> '+wlmatrix(expected["CP_odd_Goldstone_A_rotation"]),
      '"ExpectedZ12" -> '+wlreal(expected["gZ_H1H2_derivative_abs"]),
      '"ExpectedH1h" -> '+wlreal(expected["h125_H1_H2_trilinear_signed_GeV"]),
      '"ExpectedH1H" -> '+wlreal(expected["H_H1_H2_trilinear_signed_GeV"]),
      '"FSARAH" -> '+wlmatrix(matrices["FSARAH"]),
      '"YeSARAH" -> '+wlmatrix(matrices["YeSARAH"]),
      '"Ye2SARAH" -> '+wlmatrix(matrices["Ye2SARAH"]),
      '"YChen" -> '+wlmatrix(matrices["YChen"]),
      '"LeptonMasses" -> '{'+','.join(wlreal(z) for z in
                                 (ME,MMU,MTAU))+'}',
      '"LeptonicWidths" -> '+wlmatrix(
             [[b3["leptonic_widths_GeV"][state][lept] for state in
               ("H1","H2")] for lept in ("e","mu","tau")]),
      '"ExpectedWidths" -> {'+','.join(wlreal(wid[state][key]) for state,key
          in (("H2","H1_Z"),("H2","H1_h125"),("H2","H1_hheavy"),
             ("H1","tb"),("H2","tb")))+'}',
    ]
    return meta,"<|"+",\n".join(entries)+"|>"

def make(f13dir,f14dir,out):
    if out.exists():raise FileExistsError("Never overwrite SARAH original F16 inputs")
    byid,production,pr=join_origins(f13dir,f14dir)
    if len(byid)!=8 or len(production)!=8:raise ValueError("F13/F14 source cohort lost")
    records={};wolfram=[]
    for key in TARGETS:
        case,serialized=build_case(key,byid[key],production,{
            "f13dir":Path(f13dir)})
        records[key]=case;wolfram.append(serialized)
    out.mkdir(parents=True,exist_ok=False)
    fixture=out/FIXTURE
    fixture.write_text(
      "(* All 3 exact F13 physics inputs, checked against F14, from ORIGINAL "+
      "complex neutrino Y/f. Not a UFO/MadWidth card. *)\n"+
      "zeeF16Cases = {\n"+",\n".join(wolfram)+"\n};\n")
    writejson(out/CHECK,records)
    report={
      "status":STATUS,
      "exact_F13_candidates":list(TARGETS),
      "source":pr,
      "all_three_source_Gate6_SU2_scalar_and_complex_E3_flavor_verified":True,
      "all_three_local_SARAH_numeric_vertex_checks_passed":False,
      "actual_generated_complex_Zee_UFO_exists":False,
      "physical_full_MadWidth_total_widths":None,
      "full_Zee_model_allowed_or_excluded":None,
      "missing":MISSING,
      "original_F13_dir":str(Path(f13dir).resolve()),
      "original_F14_dir":str(Path(f14dir).resolve()),
      "SARAH_ZeeTypeII_source_SHA256":digest(ROOT/"models"/"SARAH"/
                                          "ZeeTypeII"/"ZeeTypeII.m"),
      "numeric_fixture_SHA256":digest(fixture),
      "source_reconstruction_SHA256":digest(out/CHECK),
      "F16_generator_SHA256":digest(Path(__file__)),
    }
    writejson(out/"summary.json",report)
    writejson(out/"manifest.json",{
      "status":STATUS,"summary_SHA256":digest(out/"summary.json"),
      "fixture_SHA256":digest(fixture),
      "all_three_local_SARAH_numeric_vertex_checks_passed":False})
    print("F16_REAL_SOURCE_INPUTS",len(TARGETS),FIXTURE)
    for k in TARGETS:
        x=records[k]
        print("F16_CASE",k,"mH1",x["scalar"]["mH1"],
              "mH2",x["scalar"]["mH2"],
              "Gamma_H2_H1Z_GeV",x[
                "expected_Gate6_diagnostic_partial_widths_GeV"]["H2_H1Z"])
    print("F16_SARAH_LOCAL_INPUT_DIR",out)
    print("F16_STATUS",STATUS,"ACTUAL_SARAH_NUMERIC",False)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--f13-dir",type=Path,default=ROOT/"work"/
       "zee_paper1_F13_heavy_final_20261021T125623Z")
    p.add_argument("--f14-dir",type=Path,default=ROOT/"work"/
       "zee_paper1_F14_LHCHXSWG_13TeV_production_20261021T133239Z")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    make(args.f13_dir,args.f14_dir,args.output)
if __name__=="__main__":main()

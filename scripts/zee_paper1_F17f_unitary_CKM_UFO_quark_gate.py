#!/usr/bin/env python3
"""F17f: replace F17d CKM=I test basis with a unitary complex CKM candidate,
and evaluate the real SARAH UFO's 9x W/u/d and H1/H2/u/d couplings.

A local *numerical* F17f PASS is mandatory before calling these physical
quark cards. The down weak-basis index convention is explicit and must be
confirmed by the W vertices, not assumed from an invented SLHA CKM block.
For neutrino/charged lepton amplitudes, export diagnostic channel-resolved
norms and exact F16/B3 target widths without assuming a duplicate-vertex
count. No complete MadWidth widths are claimed at this stage.
"""
from __future__ import annotations
import argparse,cmath,json,math
from pathlib import Path
import numpy as np
from zee_paper1_F17_inspect_real_SARAH_UFO import (
    TGT, UFO_SUBDIR, SOURCE_COMPLEX, parse_objects, cmat, consistency)
from zee_paper1_F17_verify_complex_json import verify_json
from zee_paper1_F17c_real_UFO_scalar_photon import hashfile,source_ew,get_ufo_couplings
from zee_paper1_F17d_source_matched_prevalidation_cards import (
    slots_from_real_ufo,put_matrix,check_slots,render,lepton_mass_error,
    UP,DOWN,COMPLEX)
from zee_paper1_F17e_real_UFO_amplitude_gate import (
    UFOCalculator,read_f17d_card,parse_3body_vertices,evaluate_vertices,
    vertex_set,lorentz_chirality,scalar_vector_width,STATUS as E_STATUS)
from zee_paper1_F15_charged_width_CKM_mass_scheme_audit import (
    VABS,charged_quark_width,GF)

STATUS="F17F_UNITARY_CKM_REAL_UFO_QUARK_AMPLITUDE_GATE_AND_LEPTON_INVENTORY_NOT_MADWIDTH"
UP_PDG=(2,4,6)
DOWN_PDG=(1,3,5)
UP_NAME=("u","c","t")
DOWN_NAME=("d","s","b")
LEP_PDG=(11,13,15)
NEU_PDG=(12,14,16)


def unitary_ckm_from_f15():
    """PDG convention s12,s23,s13 and delta fitted to |Vtd| from F15.

    Original F15 magnitudes were NOT exactly unitary; the input here is
    their unitary completion, not a new CKM fit or an experimental limit.
    """
    s12,s23,s13=float(VABS[0,1]),float(VABS[1,2]),float(VABS[0,2])
    c12,c23,c13=(math.sqrt(1-s*s) for s in (s12,s23,s13))
    a=s12*s23
    b=c12*c23*s13
    cosdelta=(a*a+b*b-float(VABS[2,0])**2)/(2*a*b)
    if abs(cosdelta)>1:raise ValueError("F15 CKM magnitudes not unitary-completable")
    delta=math.acos(cosdelta)
    z=cmath.exp(1j*delta)
    mat=np.array([
        [c12*c13,s12*c13,s13*z.conjugate()],
        [-s12*c23-c12*s23*s13*z,
         c12*c23-s12*s23*s13*z,s23*c13],
        [s12*s23-c12*c23*s13*z,
         -c12*s23-s12*c23*s13*z,c23*c13],
    ],dtype=complex)
    residual=float(np.max(abs(mat@mat.conj().T-np.eye(3))))
    magnitudes=float(np.max(abs(abs(mat)-VABS)))
    if residual>1e-13 or magnitudes>3e-5:
        raise ValueError("F15-completed CKM unitarity/magnitudes fail")
    return mat,{"s12":s12,"s23":s23,"s13":s13,"delta_rad":delta,
                "unitarity_max_abs":residual,
                "F15_input_magnitude_max_abs_delta":magnitudes,
                "V_abs":abs(mat).tolist()}


def make_quark_basis(original,source_row,ckm):
    """Mass-down left-rotation ansatz ZDL=V_CKM^dagger, up left identity.

    Weak-space Yd_ij = y(d_R_i) * (ZDL)_ij. Verify that
    Yd ZDL^dagger is diagonal and that UFO W amplitudes select this CKM.
    """
    vals=dict(original)
    beta=source_row["beta_rad"]
    v=source_row["vev_GeV"]
    s,c=math.sin(beta),math.cos(beta)
    if min(s,c)<=0:raise ValueError("Unphysical Type-II VEV")
    zdl=ckm.conj().T
    yup=np.diag([math.sqrt(2)*m/(v*s) for m in UP]).astype(complex)
    ydown=np.diag([math.sqrt(2)*m/(v*c) for m in DOWN]).astype(complex)
    Ydown=ydown@zdl
    identity=np.eye(3,dtype=complex)
    # Reconstruct masses in this declared convention prior to UFO test.
    if np.max(abs(Ydown@zdl.conj().T-ydown))>1e-13:
        raise ValueError("Down Yukawa non-diagonal in declared mass basis")
    for block,data in (("YU",yup),("YD",Ydown),("UDLMIX",zdl),
                       ("UDRMIX",identity),("UULMIX",identity),
                       ("UURMIX",identity)):
        put_matrix(vals,block,data)
    return vals,{"assumed_matter_sector_rotation":"ZDL=V_CKM^dagger, ZUL=ZDR=ZUR=I",
                 "down_mass_basis_residual":float(np.max(abs(Ydown@zdl.conj().T-ydown)))}


def vertex_group(vertices,signatures):
    return [v for v in vertices if tuple(sorted(map(abs,v["pdgs"]))) in signatures]


def compare_W_to_ckm(vrows,ckm,g2):
    """Check BOTH moduli and relative complex CKM phases of actual W vertices.

    The common Feynman-rule phase cancels by dividing by the ud vertex.
    W+ and W- must have mutually conjugate *CKM* flavor matrices; fail
    closed if only the magnitudes match.
    """
    errors=[];samples=[];signed={1:{},-1:{}}
    for i,u in enumerate(UP_PDG):
        for j,d in enumerate(DOWN_PDG):
            matches=vertex_set(vrows,[24,u,d])
            if not matches:raise ValueError("Missing real UFO W u%d d%d"%(i,j))
            strengths=[]
            for vert in matches:
                coef=0j
                for coupling in vert["couplings"]:
                    structure=coupling["structure"]
                    amp=complex(coupling["value_re"],coupling["value_im"])
                    if "ProjP(" in structure and "ProjM(" not in structure:
                        if abs(amp)>1e-12:
                            raise ValueError("Right-handed charged W current "+vert["vertex"])
                        continue
                    if "ProjM(" not in structure:
                        raise ValueError("Unknown charged W Lorentz "+str(structure))
                    coef+=amp
                sign=next(1 if p>0 else -1 for p in vert["pdgs"] if abs(p)==24)
                if (i,j) in signed[sign]:
                    raise ValueError("Ambiguous duplicate W flavor vertex "+str((sign,i,j)))
                signed[sign][(i,j)]=coef
                strengths.append(abs(coef))
            target=g2/math.sqrt(2)*abs(ckm[i,j])
            err=max(abs(value-target)/max(target,1e-10) for value in strengths)
            errors.append(err)
            samples.append({"up":UP_NAME[i],"down":DOWN_NAME[j],
                            "PDG":[u,d],"UFO_W_vertices":matches,
                            "expected_coefficient_abs":target,
                            "relative_error_max":err})
    phase_err={};hypotheses={}
    for sign,found in signed.items():
        if set(found)!={(i,j) for i in range(3) for j in range(3)}:
            raise ValueError("Incomplete signed W/CKM amplitude matrix "+str(sign))
        if abs(found[(0,0)])<1e-9:raise ValueError("Cannot fix W/CKM ud reference phase")
        observed=np.array([[found[(i,j)]/found[(0,0)] for j in range(3)]
                           for i in range(3)])
        ref=ckm/ckm[0,0]
        choices={"CKM":ref,"CKM_CONJ":ref.conjugate()}
        ranking={name:float(np.max(abs(observed-target)/np.maximum(
            abs(target),1e-10))) for name,target in choices.items()}
        best=min(ranking,key=ranking.get)
        hypotheses[sign]=best
        phase_err[sign]=ranking[best]
    if hypotheses[1]==hypotheses[-1]:
        raise ValueError("Wplus and Wminus do not carry conjugate complex CKM phases")
    return samples,max(errors),phase_err,hypotheses


def spin_half_quark_width(vertex,vals,u,d,h):
    """Exact one-charge two-body scalar width with both chiralities.

    For signs of fermion legs, require the SARAH-matched F17e convention.
    """
    terms={}
    for amp in vertex["couplings"]:
        if amp["colour"]!=0:raise ValueError("Unexpected colour structure")
        key=lorentz_chirality(amp["structure"])
        if key in terms:raise ValueError("Duplicate chiral projector")
        terms[key]=complex(amp["value_re"],amp["value_im"])
    if set(terms)!={"M","P"}:raise ValueError("Missing quark chiral projector")
    M=vals[("MASS",(h,))]
    mu=vals[("MASS",(u,))]
    md=vals[("MASS",(d,))]
    ru=(mu/M)**2;rd=(md/M)**2
    lam=(1-ru-rd)**2-4*ru*rd
    if lam<=0:return 0.
    left,right=terms["M"],terms["P"]
    return (3*M/(16*math.pi)*math.sqrt(lam)*
            ((abs(left)**2+abs(right)**2)*(1-ru-rd)
             -4*(left*right.conjugate()).real*mu*md/M**2))


def check_charged_quarks(allvertices,vals,row,ckm):
    tanbeta=math.tan(row["beta_rad"])
    gamma=row["gamma_rad"]
    coupling_checks=[];errors=[]
    for H,label,doublet2 in ((37,"H1",math.cos(gamma)**2),
                             (9000037,"H2",math.sin(gamma)**2)):
        for i,u in enumerate(UP_PDG):
            for j,d in enumerate(DOWN_PDG):
                m=vertex_set(allvertices,[H,u,d])
                if not m:raise ValueError("Missing charged Higgs quark vertex: "+str((H,u,d)))
                computed=[spin_half_quark_width(v,vals,u,d,H) for v in m]
                expected=charged_quark_width(
                    vals[("MASS",(H,))],UP_NAME[i],DOWN_NAME[j],
                    tanbeta,doublet2,mb=DOWN[2])*(abs(ckm[i,j])/float(VABS[i,j]))**2
                relative=max(abs(x-expected)/max(1e-13,expected) for x in computed)
                # F15 uses a fixed Gf, whereas the actual F16 UFO derives it from v.
                if relative>5e-5:
                    raise ValueError("Charged Higgs "+label+" "+UP_NAME[i]+DOWN_NAME[j]+
                                     " UFO/F15 source width mismatch "+str((computed,expected,relative)))
                errors.append(relative)
                coupling_checks.append({"H":label,"up":UP_NAME[i],"down":DOWN_NAME[j],
                                        "UFO_vertices":[v["vertex"] for v in m],
                                        "source_F15_CKM_completed_width_GeV":expected,
                                        "computed_UFO_charges_widths_GeV":computed,
                                        "max_relative_residual":relative})
    return coupling_checks,max(errors)


def expected_lepton_widths(row):
    """Independent F16/B3 source formula; report but do not presume charge multiplicity."""
    y=np.asarray(cmat(row,"YChen",(3,3)),dtype=complex)
    f=np.asarray(cmat(row,"FSARAH",(3,3)),dtype=complex)/2
    if np.max(abs(f+f.T))>1e-11:raise ValueError("F16 exact antisymmetric f corrupted")
    gamma=row["gamma_rad"]
    results={}
    for H,label,doublet2,singlet2,mass in (
        (37,"H1",math.cos(gamma)**2,math.sin(gamma)**2,row["mH1_GeV"]),
        (9000037,"H2",math.sin(gamma)**2,math.cos(gamma)**2,row["mH2_GeV"])):
        results[label]={}
        for l,flavor in enumerate(("e","mu","tau")):
            ml=row["lepton_masses_GeV"][l]
            mode=mass/(16*math.pi)*(
                2*doublet2*float(np.sum(abs(y[l,:])**2))+
                4*singlet2*float(np.sum(abs(f[:,l])**2))) * (1-(ml/mass)**2)**2
            results[label][flavor]=mode
    return results


def inspect_lepton_norms(evaluated,row):
    """All actual UFO lepton vertices grouped with sign and chirality.

    Numerical amplitude sums are recorded as diagnostics. F17e inventory
    had 36 vertices per charged state; naive sums double-count conjugate
    charge legs and therefore are NOT declared physical branching widths.
    """
    output={}
    for H in (37,9000037):
        subset=[v for v in evaluated if any(abs(p)==H for p in v["pdgs"])]
        modes={}
        for v in subset:
            l=next((abs(p) for p in v["pdgs"] if abs(p) in LEP_PDG),None)
            n=next((abs(p) for p in v["pdgs"] if abs(p) in NEU_PDG),None)
            if l is None or n is None:continue
            charge=next(p for p in v["pdgs"] if abs(p)==H)
            key=f"{charge}:{l}:{n}"
            d=modes.setdefault(key,{"vertices":[],"sum_abs2":0.,"projectors":{}})
            d["vertices"].append(v["vertex"])
            for amp in v["couplings"]:
                chir=lorentz_chirality(amp["structure"])
                d["projectors"][chir]=d["projectors"].get(chir,0)+1
                d["sum_abs2"]+=amp["absolute"]**2
        output[str(H)]={"n_evaluated_vertices":len(subset),"channels":modes}
    return output



def lepton_width_closure(evaluated,vals,expected):
    """Coherently sum identical signed field/Lorentz amplitudes.

    Different incoming scalar charge signs are separately cross-checked;
    neutrino and antineutrino final states remain distinct. This is the
    same m_neutrino=0 LO mass-suppressed two-body formula used in F16/B3.
    Fails closed for duplicate interpretations or incomplete final states.
    """
    details={}
    errs=[]
    for H,label in ((37,"H1"),(9000037,"H2")):
        mass=vals[("MASS",(H,))]
        for sign in (-1,1):
            for li,lpdg in enumerate(LEP_PDG):
                rows=[v for v in evaluated if
                      sign*H in v["pdgs"] and
                      any(abs(p)==lpdg for p in v["pdgs"]) and
                      any(abs(p) in NEU_PDG for p in v["pdgs"])]
                if not rows:raise ValueError("No UFO lepton vertices "+str((H,sign,lpdg)))
                # Within identical signed external particle content, each
                # Lorentz projector contributes coherently.
                amplitudes={}
                nus=set()
                for vertex in rows:
                    signed_neu=next((p for p in vertex["pdgs"]
                                     if abs(p) in NEU_PDG),None)
                    if signed_neu is None:raise ValueError("UFO lepton neutrino missing")
                    nus.add(abs(signed_neu))
                    content=tuple(vertex["pdgs"])
                    for a in vertex["couplings"]:
                        if a["colour"]!=0:
                            raise ValueError("Unexpected lepton colour structure")
                        chir=lorentz_chirality(a["structure"])
                        key=(content,chir)
                        amplitudes[key]=amplitudes.get(key,0j)+complex(
                            a["value_re"],a["value_im"])
                if nus!=set(NEU_PDG):
                    raise ValueError("Incomplete neutrino flavors "+str((H,sign,lpdg,nus)))
                norm=sum(abs(z)**2 for z in amplitudes.values())
                ml=vals[("MASS",(lpdg,))]
                width=mass/(16*math.pi)*norm*(1-(ml/mass)**2)**2
                ref=expected[label][("e","mu","tau")[li]]
                rel=abs(width-ref)/max(1e-12,ref)
                k=f"{label}_sign{sign:+d}_{('e','mu','tau')[li]}"
                details[k]={"ufo_width_GeV":width,"source_F16_B3_width_GeV":ref,
                            "relative_residual":rel,"n_raw_UFO_vertices":len(rows),
                            "n_coherent_signature_projectors":len(amplitudes),
                            "neutrino_species":sorted(nus)}
                errs.append(rel)
    # Match BOTH charge-conjugate channels to the six independent source
    # widths, not arbitrary halves/averages of the 36 UFO vertex entries.
    maximum=max(errs)
    if maximum>2e-5:
        raise ValueError("UFO general complex Zee lepton width mismatch: "+
                         str(sorted(details.items(),key=lambda t:-t[1]["relative_residual"])[:3]))
    return details,maximum

def run(f16_dir,f17e_report,f17d_dir,output):
    source=Path(f16_dir).expanduser().resolve()
    root=source/UFO_SUBDIR
    dest=Path(output).expanduser().resolve()
    out=dest/"report.json"
    if dest.exists():raise FileExistsError("Refuse overwriting previous physical CKM candidate files")
    f17=verify_json(source/SOURCE_COMPLEX)
    f16=json.loads((source/"F16_three_exact_F13_Zee_input_reconstruction.json").read_text())
    consistency(f16,f17)
    d_dir=Path(f17d_dir).expanduser().resolve()
    d=json.loads((d_dir/"summary.json").read_text())
    e=json.loads(Path(f17e_report).read_text())
    if e.get("status")!=E_STATUS or e.get("Z_scalar_tb_amplitude_gate_3_of_3") is not True:
        raise ValueError("F17e numerical original-UFO result not accepted")
    if e.get("F17d_original_summary_SHA256")!=hashfile(d_dir/"summary.json"):
        raise ValueError("F17e and F17d original exact source disagree")
    for filename,key in (("parameters.py","UFO_parameters_SHA256"),
                         ("vertices.py","UFO_vertices_SHA256"),
                         ("couplings.py","UFO_couplings_SHA256")):
        if hashfile(root/filename)!=e[key]:
            raise ValueError("Original UFO "+filename+" changed since passed F17e")
    params=parse_objects(root,"parameters.py","Parameter")
    slots=slots_from_real_ufo(params)
    ufo_couplings=get_ufo_couplings(root)
    lorentz=parse_objects(root,"lorentz.py","Lorentz")
    raw_vertices=parse_3body_vertices(root)
    ckm,metadata=unitary_ckm_from_f15()
    cases={r["candidate_id"]:r for r in f17["matrices"]}
    cards=d.get("candidate_cards")
    if len(cards)!=3 or {a["id"] for a in cards}!=set(TGT):
        raise ValueError("F17d exact three cases missing")
    answers=[];errors={};prepared={}
    for item in cards:
        key=item["id"]
        try:
            original_card=d_dir/item["file"]
            if original_card.name!=item["file"] or hashfile(original_card)!=item["sha256"]:
                raise ValueError("F17d original card SHA mismatch")
            old=read_f17d_card(original_card,slots)
            values,conv=make_quark_basis(old,cases[key],ckm)
            check_slots(slots,values)
            lepton_mass_error(cases[key],values)
            calc=UFOCalculator(params,{name:values[ident] for ident,name in slots.items()})
            w_verts=vertex_group(raw_vertices,{tuple(sorted((24,u,d)))
                for u in UP_PDG for d in DOWN_PDG})
            w=evaluate_vertices(w_verts,ufo_couplings,lorentz,calc)
            Wresults,Wmax,Wphase,Whyp=compare_W_to_ckm(
                w,ckm,source_ew(cases[key])["g2"])
            if Wmax>5e-5 or max(Wphase.values())>5e-5:
                raise ValueError("UFO physical W/CKM complex amplitude mismatch "+
                                 str((Wmax,Wphase,Whyp)))
            charged_vertices=[v for v in raw_vertices if
                len(v["pdgs"])==3 and any(abs(p) in (37,9000037) for p in v["pdgs"])
                and any(abs(p) in UP_PDG for p in v["pdgs"])
                and any(abs(p) in DOWN_PDG for p in v["pdgs"])]
            charged=evaluate_vertices(charged_vertices,ufo_couplings,lorentz,calc)
            qmode,qr=check_charged_quarks(charged,values,cases[key],ckm)
            lepton_vertices=[v for v in raw_vertices if
                len(v["pdgs"])==3 and any(abs(p) in (37,9000037) for p in v["pdgs"])
                and any(abs(p) in LEP_PDG for p in v["pdgs"])
                and any(abs(p) in NEU_PDG for p in v["pdgs"])]
            lnum=evaluate_vertices(lepton_vertices,ufo_couplings,lorentz,calc)
            lnorm=inspect_lepton_norms(lnum,cases[key])
            lreference=expected_lepton_widths(cases[key])
            leptonic_widths,lepton_max=lepton_width_closure(lnum,values,lreference)
            result={"candidate_id":key,"original_F17d_card_SHA256":item["sha256"],
                    "CKM_source_mass_basis_convention":conv,
                    "actual_UFO_W_physical_CKM_checks":Wresults,
                    "W_CKM_max_rel":Wmax,
                    "W_CKM_complex_phase_relative_errors":{str(k):v for k,v in Wphase.items()},
                    "W_charge_conjugate_CKM_phase_hypotheses":{str(k):v for k,v in Whyp.items()},
                    "actual_UFO_charged_H_quark_width_checks":qmode,
                    "charged_quark_width_max_rel":qr,
                    "independent_F16_B3_complex_lepton_width_target_GeV":lreference,
                    "actual_UFO_lepton_vertex_norm_diagnostics_NOT_WIDTHS":lnorm,
                    "actual_UFO_complex_lepton_per_charge_widths":leptonic_widths,
                    "actual_UFO_lepton_width_max_relative_residual":lepton_max,
                    "all_quark_9x2_modes_passed":True,
                    "complex_lepton_full_width_gate_passed":True,
                    "physical_MadWidth_ready":False}
            answers.append(result)
            prepared[key]=values
        except (ValueError,KeyError,TypeError,IndexError,OverflowError,ZeroDivisionError) as ex:
            errors[key]=str(ex)
    dest.mkdir(parents=True,exist_ok=False)
    entries=[]
    # Only write numeric physical-CKM candidate cards for passing individual
    # quark audits. They remain explicitly NOT MadWidth validated.
    for key,values in sorted(prepared.items()):
        file=dest/(key+"_UNITARY_CKM_QUARK_CHECKED_LEPTON_PENDING_NOT_MADWIDTH.slha")
        file.write_text(render(slots,values,key).replace(
            "CKM=IDENTITY DIAGNOSTIC BASIS, NOT PHYSICAL F15 CKM",
            "UNITARY COMPLEX CKM NUMERICALLY MATCHED VIA ACTUAL UFO W AND HQQ"))
        entries.append({"candidate_id":key,"file":file.name,"sha256":hashfile(file)})
    report={"status":STATUS,"source_F17e_SHA256":hashfile(f17e_report),
            "source_F17d_SHA256":hashfile(d_dir/"summary.json"),
            "unitary_CKM_convention_F15_magnitudes":metadata,
            "CKM_matrix_re_im":[[[float(z.real),float(z.imag)] for z in line] for line in ckm],
            "cases":answers,"errors":errors,"CKM_numerical_3_of_3":len(answers)==3 and not errors,
            "CKM_candidate_cards":entries,
            "full_complex_lepton_physical_widths_validated":len(answers)==3 and not errors
                and all(case["complex_lepton_full_width_gate_passed"] for case in answers),
            "complete_2_and_3_body_MadWidth_ready":False}
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    for case in answers:
        print("F17F_QUARK",case["candidate_id"],
              "W_MAX_REL",case["W_CKM_max_rel"],
              "W_PHASE_MAX_REL",max(case["W_CKM_complex_phase_relative_errors"].values()),
              "HQQ_MAX_REL",case["charged_quark_width_max_rel"],
              "LEPTON_MAX_REL",case["actual_UFO_lepton_width_max_relative_residual"])
    for key,err in errors.items():print("F17F_BLOCKER",key,err)
    print("F17F_STATUS",STATUS,"CKM_3_OF_3",report["CKM_numerical_3_of_3"],
          "LEPTON_FULL_WIDTH_MATCH",report["full_complex_lepton_physical_widths_validated"],"MADWIDTH_READY",False)
    print("F17F_REPORT",out)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ("f16-dir","f17e-report","f17d-dir","output"):
        p.add_argument("--"+flag,type=Path,required=True)
    args=p.parse_args()
    report=run(args.f16_dir,args.f17e_report,args.f17d_dir,args.output)
    if not report["CKM_numerical_3_of_3"]:raise SystemExit(2)


if __name__=="__main__":main()

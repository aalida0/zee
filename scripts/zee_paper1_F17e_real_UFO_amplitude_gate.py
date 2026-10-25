#!/usr/bin/env python3
"""F17e: numerical *actual SARAH UFO* scalar and fermion vertex gate.

Read the immutable F16/F17/F17c source and the three F17d CKM=I diagnostic
SLHA files. Check true vertices/coupling expressions at all 258 actual UFO
external values, without importing generated UFO modules. Compare the
Z H2 H1, h/H H2 H1 and charged-Higgs tb couplings/widths to independent
F16 references, and enumerate/evaluate all charged-lepton-neutrino vertices.

A failure is a scientific blocker, NEVER a MadWidth-ready certification.
The quark basis is CKM=I, NOT the F15 CKM physical hypothesis.
"""
from __future__ import annotations
import argparse,ast,cmath,json,math,re
from pathlib import Path
from zee_paper1_F17_inspect_real_SARAH_UFO import (
    TGT,UFO_SUBDIR,SOURCE_COMPLEX,parse_objects,consistency)
from zee_paper1_F17_verify_complex_json import verify_json
from zee_paper1_F17c_real_UFO_scalar_photon import (
    hashfile,NumericUFO,get_ufo_couplings,source_ew)
from zee_paper1_F17d_source_matched_prevalidation_cards import (
    slots_from_real_ufo,check_slots,lepton_mass_error,STATUS as D_STATUS)

STATUS="F17E_ACTUAL_UFO_Z_SCALAR_TB_LEPTON_COUPLINGS_DIAGNOSTIC_NOT_MADWIDTH"
H1=37;H2=9000037
CHARGED={H1,H2}
LEPTONS={11,13,15}
NEUTRINOS={12,14,16}
QUP={2,4,6}
QDOWN={1,3,5}


class UFOCalculator(NumericUFO):
    """F17c safe arithmetic plus standard UFO function_library primitives."""
    def _walk(self,n):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and not n.keywords:
            name=n.func.id
            if name in ("complexconjugate","re","im","sec","csc","cot",
                        "asec","acsc","acot") and len(n.args)==1:
                z=self._walk(n.args[0])
                if name=="complexconjugate":return complex(z).conjugate()
                if name=="re":return complex(z).real
                if name=="im":return complex(z).imag
                if name=="sec":return 1/cmath.cos(z)
                if name=="csc":return 1/cmath.sin(z)
                if name=="cot":return 1/cmath.tan(z)
                if name=="asec":return cmath.acos(1/z)
                if name=="acsc":return cmath.asin(1/z)
                if name=="acot":return cmath.atan(1/z)
        return super()._walk(n)


def read_f17d_card(path,slots):
    path=Path(path)
    if not path.is_file():raise FileNotFoundError(str(path))
    values={};block=None
    for line_no,raw in enumerate(path.read_text().splitlines(),1):
        source=raw.split("#",1)[0].strip()
        if not source:continue
        words=source.split()
        if words[0].upper()=="BLOCK":
            if len(words)!=2:raise ValueError("Unsupported block definition at line "+str(line_no))
            block=words[1].upper()
            continue
        if words[0].upper()=="DECAY":
            if len(words)!=3:raise ValueError("Malformed DECAY "+str(line_no))
            ident=("DECAY",(int(words[1]),))
            number=float(words[2]);block=None
        else:
            if block is None or len(words)<2:
                raise ValueError("Malformed SLHA line "+str(line_no))
            try:
                ident=(block,tuple(int(x) for x in words[:-1]))
                number=float(words[-1].replace("D","E").replace("d","e"))
            except ValueError as ex:
                raise ValueError("Malformed numeric SLHA line "+str(line_no)) from ex
        if ident in values:raise ValueError("Duplicate SLHA entry "+str(ident))
        values[ident]=number
    check_slots(slots,values)
    return values


def parse_3body_vertices(root):
    particles=parse_objects(root,"particles.py","Particle")
    tree=ast.parse((root/"vertices.py").read_text(encoding="utf-8"))
    result=[]
    for node in tree.body:
        if not isinstance(node,ast.Assign) or len(node.targets)!=1:continue
        if not isinstance(node.value,ast.Call) or not isinstance(node.value.func,ast.Name) or node.value.func.id!="Vertex":
            continue
        args={k.arg:k.value for k in node.value.keywords if k.arg}
        fields=args.get("particles")
        if not isinstance(fields,(ast.List,ast.Tuple)) or len(fields.elts)!=3:continue
        pdgs=[]
        for item in fields.elts:
            if not isinstance(item,ast.Attribute) or item.attr not in particles:
                raise ValueError("Unknown particle reference in "+node.targets[0].id)
            pdgs.append(particles[item.attr]["pdg_code"])
        target=args.get("couplings")
        lor=args.get("lorentz")
        if not isinstance(target,ast.Dict) or not isinstance(lor,(ast.List,ast.Tuple)):
            raise ValueError("UFO vertex lorentz/coupling AST unsupported")
        lnames=[]
        for name in lor.elts:
            if not isinstance(name,ast.Attribute):
                raise ValueError("Unknown Lorentz object")
            lnames.append(name.attr)
        couples=[]
        for pair,ref in zip(target.keys,target.values):
            if (not isinstance(pair,ast.Tuple) or len(pair.elts)!=2 or
                not all(isinstance(t,ast.Constant) and type(t.value)==int for t in pair.elts) or
                not isinstance(ref,ast.Attribute)):
                raise ValueError("Unknown Lorentz/colour coupling reference in "+node.targets[0].id)
            colour,li=(t.value for t in pair.elts)
            if li>=len(lnames):raise ValueError("UFO Lorentz index overflow")
            couples.append({"colour":colour,"lorentz":lnames[li],"name":ref.attr})
        result.append({"vertex":node.targets[0].id,"pdgs":pdgs,"couplings":couples})
    return result


def vertex_set(vertices,abs_pdgs):
    target=sorted(abs_pdgs)
    return [v for v in vertices if sorted(map(abs,v["pdgs"]))==target]


def evaluate_vertices(vertices,couplings,lorentz,calc):
    evaluated=[]
    for vert in vertices:
        cc=[]
        for row in vert["couplings"]:
            if row["name"] not in couplings:
                raise ValueError("UFO Coupling "+row["name"]+" absent")
            if row["lorentz"] not in lorentz:
                raise ValueError("UFO Lorentz "+row["lorentz"]+" absent")
            z=complex(calc.eval(couplings[row["name"]]))
            if not (math.isfinite(z.real) and math.isfinite(z.imag)):
                raise ValueError("Nonfinite UFO coupling "+row["name"])
            cc.append(dict(row,value_re=z.real,value_im=z.imag,
                           absolute=abs(z),structure=lorentz[row["lorentz"]].get("structure"),
                           UFO_expression=couplings[row["name"]]))
        evaluated.append({"vertex":vert["vertex"],"pdgs":vert["pdgs"],"couplings":cc})
    return evaluated


def one_scalar_amplitude(vertex_results,expected,label,tolerance=4e-7):
    values=[item["absolute"] for row in vertex_results for item in row["couplings"]]
    if not values:raise ValueError("No scalar UFO coupling for "+label)
    maxerr=max(abs(g-abs(expected))/max(1.,abs(expected)) for g in values)
    if maxerr>tolerance:
        raise ValueError(label+" UFO/source coupling differs: "+str(values)+
                         " expected="+str(expected)+" err="+str(maxerr))
    return maxerr


def lorentz_chirality(structure):
    if not isinstance(structure,str):raise ValueError("No Lorentz structure")
    left="ProjM(" in structure
    right="ProjP(" in structure
    if left==right:raise ValueError("Unknown/ambiguous scalar-fermion chirality "+structure)
    return "M" if left else "P"


def tb_width_from_ufo_scalar(vertex,masses):
    """One-charge H1 -> tb 2-body unpolarized tree spin trace.

    Requires exactly one colour structure, one coefficient for each
    chiral projector, and a bona-fide scalar-fermion Lorentz basis.
    """
    if sorted(map(abs,vertex["pdgs"])) != [5,6,37]:
        raise ValueError("Not H1 tb")
    chirals={}
    for item in vertex["couplings"]:
        if item["colour"]!=0:
            raise ValueError("Unexpected multi-colour tb amplitude")
        chir=lorentz_chirality(item["structure"])
        if chir in chirals:raise ValueError("Duplicate tb projector "+chir)
        chirals[chir]=complex(item["value_re"],item["value_im"])
    if set(chirals)!={"M","P"}:raise ValueError("Both tb chirality structures required")
    m=mass_get(masses,37)
    mt=mass_get(masses,6);mb=mass_get(masses,5)
    rt=(mt/m)**2; rb=(mb/m)**2
    kallen=(1-rt-rb)**2-4*rt*rb
    if kallen<=0:raise ValueError("H1 tb closed")
    l,r=chirals["M"],chirals["P"]
    width=(3*m/(16*math.pi)*math.sqrt(kallen)*
           ((abs(l)**2+abs(r)**2)*(1-rt-rb)-4*(l*r.conjugate()).real*mt*mb/m**2))
    if width<=0 or not math.isfinite(width):
        raise ValueError("Negative/nonfinite tb partial width")
    return width,{"M": [l.real,l.imag], "P":[r.real,r.imag]}


def mass_get(vals,pdg):
    return vals[("MASS",(abs(pdg),))]


def scalar_vector_width(m,m1,mz,g):
    if m<=m1+mz:return 0.0
    lam=(m*m-(m1+mz)**2)*(m*m-(m1-mz)**2)
    return abs(g)**2*lam**1.5/(16*math.pi*m**3*mz**2)


def source_case_reference(source):
    refs=source.get("expected_Gate6_vertices")
    widths=source.get("expected_Gate6_diagnostic_partial_widths_GeV")
    if not isinstance(refs,dict) or not isinstance(widths,dict):
        raise ValueError("No exact source F16 scalar/width references")
    return refs,widths


def inspect_one(id,row,source,slots,parameters,lorentz,vertices,couplings,vals):
    ref,wref=source_case_reference(source)
    calc=UFOCalculator(parameters,{label:vals[key] for key,label in slots.items()})
    z=evaluate_vertices(vertex_set(vertices,[23,37,9000037]),couplings,lorentz,calc)
    h=evaluate_vertices(vertex_set(vertices,[25,37,9000037]),couplings,lorentz,calc)
    heavy=evaluate_vertices(vertex_set(vertices,[35,37,9000037]),couplings,lorentz,calc)
    tb=evaluate_vertices(vertex_set(vertices,[5,6,37]),couplings,lorentz,calc)
    if not all((z,h,heavy,tb)):
        raise ValueError("Missing exact F16 amplitude channel in original UFO "+id)
    checks={
        "Z":one_scalar_amplitude(z,ref["gZ_H1H2_derivative_abs"],id+"/Z"),
        "h125":one_scalar_amplitude(h,ref["h125_H1_H2_trilinear_abs_GeV"],id+"/h"),
        "H":one_scalar_amplitude(heavy,ref["H_H1_H2_trilinear_abs_GeV"],id+"/H"),
    }
    mH1=mass_get(vals,37);mH2=mass_get(vals,9000037);mZ=mass_get(vals,23)
    zwidth=scalar_vector_width(mH2,mH1,mZ,z[0]["couplings"][0]["absolute"])
    wz=float(wref["H2_H1Z"])
    zres=abs(zwidth-wz)/max(wz,1e-15)
    if zres>4e-6:raise ValueError(id+" actual UFO H2-H1Z width != F16: "+str((zwidth,wz,zres)))
    tbwidths=[]
    for vertex in tb:
        width,coeff=tb_width_from_ufo_scalar(vertex,vals)
        tbwidths.append({"vertex":vertex["vertex"],"width_GeV":width,
                         "UFO_chiral_coefficients_re_im":coeff})
    wtb=float(wref["H1_tb"])
    rel=[abs(item["width_GeV"]-wtb)/max(wtb,1e-15) for item in tbwidths]
    if max(rel)>5e-4:
        raise ValueError(id+" actual UFO H1-tb width mismatches F16: "+str((tbwidths,wtb,rel)))
    lep=[v for v in vertices if len(v["pdgs"])==3 and
         any(abs(p) in CHARGED for p in v["pdgs"]) and
         any(abs(p) in LEPTONS for p in v["pdgs"]) and
         any(abs(p) in NEUTRINOS for p in v["pdgs"])]
    if not lep:raise ValueError("Missing charged-lepton-neutrino actual UFO vertices")
    numeric=evaluate_vertices(lep,couplings,lorentz,calc)
    nmodes={k:0 for k in (37,9000037)}
    max_imag=0.
    for vertex in numeric:
        h_id=next(abs(p) for p in vertex["pdgs"] if abs(p) in CHARGED)
        nmodes[h_id]+=1
        for amp in vertex["couplings"]:
            lorentz_chirality(amp["structure"])
            max_imag=max(max_imag,abs(amp["value_im"]))
    if any(nmodes[k]<9 for k in CHARGED):
        raise ValueError("Incomplete 3x3 charged lepton UFO vertices "+str(nmodes))
    # A complex coefficient's imaginary part can arise solely from the
    # universal Feynman-rule factor i; it is NOT a CP-phase observable.
    # Full complex-lepton width matching to the F16 independent 36-vertex
    # reference is therefore deliberately left unclaimed.
    return {
        "candidate_id":id,
        "actual_UFO_Z_H2H1_vertices":z,
        "actual_UFO_h_H2H1_vertices":h,
        "actual_UFO_H_H2H1_vertices":heavy,
        "actual_UFO_H1_tb_vertices":tb,
        "scalar_vertex_abs_relative_residuals":checks,
        "actual_UFO_H2_H1Z_partial_width_GeV":zwidth,
        "source_F16_H2_H1Z_partial_width_GeV":wz,
        "Z_width_relative_residual":zres,
        "actual_UFO_H1_tb_partial_widths_GeV":tbwidths,
        "source_F16_H1_tb_partial_width_GeV":wtb,
        "tb_width_max_relative_residual":max(rel),
        "charged_lepton_neutrino_vertex_count_by_state":{str(k):v for k,v in nmodes.items()},
        "charged_lepton_neutrino_max_imaginary_UFO_coefficient_NOT_CP_PHASE":max_imag,
        "charged_lepton_amplitudes_evaluated_not_yet_independently_F16_width_matched":True,
        "CKM_identity_diagnostic_not_F15_physical_quark_basis":True,
        "full_physical_MadWidth_card":False,
    }


def run(f16_dir,f17_report,f17c_report,f17d_dir,output):
    source=Path(f16_dir).expanduser().resolve()
    ufo=source/UFO_SUBDIR
    f17d_dir=Path(f17d_dir).expanduser().resolve()
    out=Path(output).expanduser().resolve()
    if out.exists():raise FileExistsError("F17e refuses overwrite historical reports")
    original=verify_json(source/SOURCE_COMPLEX)
    f16=json.loads((source/"F16_three_exact_F13_Zee_input_reconstruction.json").read_text())
    consistency(f16,original)
    f17=json.loads(Path(f17_report).read_text())
    f17c=json.loads(Path(f17c_report).read_text())
    f17d=json.loads((f17d_dir/"summary.json").read_text())
    if (f17d.get("status")!=D_STATUS or not f17c.get("all_three_photon_checks_pass")
        or f17d.get("full_physical_UFO_card_validated") is not False
        or f17d.get("MadWidth_ready") is not False):
        raise ValueError("Source F17d/F17c status incompatible with diagnostic gate")
    if f17d.get("original_F17c_report_SHA256")!=hashfile(f17c_report):
        raise ValueError("F17d did not consume same F17c")
    if (Path(f17["actual_SARAH_export_UFO_interface"]["ufo_dir"]).resolve()!=ufo
        or Path(f17c["original_UFO_directory"]).resolve()!=ufo):
        raise ValueError("F16 exact UFO directory provenance mismatch")
    for filename,digest in f17["actual_SARAH_export_UFO_interface"]["ufo_python_source_SHA256"].items():
        if hashfile(ufo/filename)!=digest:raise ValueError("UFO mutated since F17 "+filename)
    for filename,key in (("parameters.py","original_UFO_parameters_SHA256"),
                         ("couplings.py","original_UFO_couplings_SHA256"),
                         ("vertices.py","original_UFO_vertices_SHA256")):
        if hashfile(ufo/filename)!=f17c[key]:raise ValueError("UFO mutated since F17c "+filename)
    pars=parse_objects(ufo,"parameters.py","Parameter")
    slots=slots_from_real_ufo(pars)
    couplings=get_ufo_couplings(ufo)
    lorentz=parse_objects(ufo,"lorentz.py","Lorentz")
    vertices=parse_3body_vertices(ufo)
    rows={r["candidate_id"]:r for r in original["matrices"]}
    if set(rows)!=set(TGT):raise ValueError("Not three exact F16 cases")
    cards=f17d.get("candidate_cards")
    if not isinstance(cards,list) or len(cards)!=3 or set(r["id"] for r in cards)!=set(TGT):
        raise ValueError("F17d exactly three same cards required")
    results=[];errors={}
    for entry in cards:
        id=entry["id"]
        try:
            card=f17d_dir/entry["file"]
            if card.name!=entry["file"] or hashfile(card)!=entry["sha256"]:
                raise ValueError("F17d source card SHA mismatch")
            vals=read_f17d_card(card,slots)
            lepton_mass_error(rows[id],vals)
            results.append(inspect_one(id,rows[id],f16[id],slots,pars,lorentz,vertices,couplings,vals))
        except (ValueError,KeyError,TypeError,IndexError,OverflowError,ZeroDivisionError) as exc:
            errors[id]=str(exc)
    payload={
        "status":STATUS,"actual_UFO_dir":str(ufo),
        "F17d_original_summary_SHA256":hashfile(f17d_dir/"summary.json"),
        "source_F16_JSON_SHA256":hashfile(source/"F16_three_exact_F13_Zee_input_reconstruction.json"),
        "source_F17_complex_JSON_SHA256":hashfile(source/SOURCE_COMPLEX),
        "UFO_parameters_SHA256":hashfile(ufo/"parameters.py"),
        "UFO_couplings_SHA256":hashfile(ufo/"couplings.py"),
        "UFO_vertices_SHA256":hashfile(ufo/"vertices.py"),
        "three_original_UFO_numerical_amplitude_results":results,
        "errors":errors,
        "Z_scalar_tb_amplitude_gate_3_of_3":len(results)==3 and not errors,
        "full_CKM_physical_basis_verified":False,
        "complete_leptonic_widths_MadWidth_3body":False,
        "physical_parameter_cards_MadWidth_ready":False,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n")
    for row in results:
        print("F17E_CASE",row["candidate_id"],"Z_WIDTH",row["actual_UFO_H2_H1Z_partial_width_GeV"],
              "Z_REL",row["Z_width_relative_residual"],"TB_MAX_REL",row["tb_width_max_relative_residual"],
              "LEPTON_VERTICES",row["charged_lepton_neutrino_vertex_count_by_state"])
    for id,err in errors.items():print("F17E_BLOCKER",id,err)
    print("F17E_STATUS",STATUS,"NUMERIC_3_OF_3",payload["Z_scalar_tb_amplitude_gate_3_of_3"],
          "CKM_PHYSICAL",False,"MADWIDTH_READY",False)
    print("F17E_REPORT",out)
    return payload


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ("f16-dir","f17-report","f17c-report","f17d-dir","output"):
        ap.add_argument("--"+flag,type=Path,required=True)
    a=ap.parse_args()
    report=run(a.f16_dir,a.f17_report,a.f17c_report,a.f17d_dir,a.output)
    if not report["Z_scalar_tb_amplitude_gate_3_of_3"]:raise SystemExit(2)


if __name__=="__main__":main()

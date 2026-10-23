#!/usr/bin/env python3
"""F17: inspect *actual* SARAH ZeeTypeII UFO after F16 3/3 tree-vertex PASS.

Original F16 exact F13 scalar, anti-symmetric Fzee, fully complex Ye/Ye2,
mass matrices, F14 source provenance are read from the SHA-checked local
transfer, NOT approximated by model defaults.

Use Python AST only to inspect the UFO (never execute untrusted generated
modules). Check all 5 physical scalars, indispensable three-body vertices,
and external SLHA definitions. Map ZEEPOT/ZEEQUARTIC if and ONLY if the
actual UFO declares each slot external. Save *scalar-only fragments*, not
a complete param_card. Quark CKM/Yu/Yd/gauge mixing, full spectrum,
MASS/DECAY and all complex Yukawas must be matched before MadWidth.

Does not run MG5 or claim full decay widths/model allowed/excluded.
"""
from __future__ import annotations
import argparse,ast,csv,hashlib,json,math
from pathlib import Path
from collections import Counter,defaultdict
from zee_paper1_F16_verify_AF_to_local_bundle import verify as verify_f16
from zee_paper1_F16_verify_AF_to_local_bundle import sha as hashfile
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import writejson
STATUS="F17_SARAH_UFO_STATIC_EXTERNAL_INTERFACE_EXACT_F13_SOURCE_ONLY_NOT_MATCHED_CARD_OR_MADWIDTH"
TGT=("F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003")
SOURCE_COMPLEX="F17_three_F13_exact_complex_matrices_from_F16.json"
UFO_SUBDIR="F16_ZeeTypeII_LO_UFO_EXPORTED_UNVALIDATED"
F16_PASS="F16_THREE_HEAVY_SARAH_MASS_GAUGE_CUBIC_COMPLEX_LEPTON_PASS_NOT_MADWIDTH"
REQUIRED_PY=("parameters.py","particles.py","vertices.py","couplings.py","lorentz.py","object_library.py")
SCALAR_POT={
  ("ZEEPOT",(1,)):"M112",
  ("ZEEPOT",(2,)):"M222",
  ("ZEEPOT",(3,)):"M12Sq",
  ("ZEEPOT",(4,)):"MCS2",
  ("ZEEPOT",(5,)):"Mu4",
  **{("ZEEQUARTIC",(i,)):("Lambda"+str(i) if i<=5 else
         {6:"LambdaC",7:"K1",8:"K2",9:"K12"}[i])
       for i in range(1,10)},
}
SCALAR_PDGS={"h125":25,"H":35,"A":36,"H1plus":37,"H2plus":9000037}
SENSITIVE_SYMBOLS=("Fzee","Ye2","Ye","Yd","Yu","ZP","ZH","ZA","Vu",
    "Vd","Uu","Ud","Ve","Ue","TanBeta","M112","M222","M12Sq",
    "Mu4","Lambda","K12","Gf","g1","g2","g3")
REQUIRED_VERTEX_PDG={
    "offdiag_Z_H2_H1":(23,37,9000037),
    "tb_H1":(5,6,37),
    "tb_H2":(5,6,9000037),
    "H2_H1_h125":(25,37,9000037),
    "H2_H1_H":(35,37,9000037),
    "H2_H1_A_possible":(36,37,9000037),
    "photon_H2_H1_must_be_absent":(22,37,9000037),
    "W_H1_h125":(24,25,37),
    "W_H2_h125":(24,25,9000037),
    "H1_lepton_neutrino":(11,12,37),
    "H2_lepton_neutrino":(11,12,9000037),
}

def safe_eval(node):
    try:return ast.literal_eval(node)
    except (ValueError,TypeError,OverflowError,RecursionError):
        return {"python_expression":ast.unparse(node)}

def parse_objects(root,basename,kind):
    path=Path(root)/basename
    tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
    objects={}; anti=[]
    for node in tree.body:
        if not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name):
            continue
        label=node.targets[0].id
        call=node.value
        if not isinstance(call,ast.Call):continue
        if isinstance(call.func,ast.Name) and call.func.id==kind:
            if label in objects:raise ValueError("Duplicate UFO "+kind+" "+label)
            args={k.arg:safe_eval(k.value) for k in call.keywords if k.arg}
            objects[label]=args
        elif kind=="Particle" and isinstance(call.func,ast.Attribute) and call.func.attr=="anti":
            name=call.func.value
            if isinstance(name,ast.Attribute) and isinstance(name.value,ast.Name):
                name=name.attr
            elif isinstance(name,ast.Name):name=name.id
            else:continue
            anti.append((label,name))
    if kind=="Particle":
        for alias,primary in anti:
            if primary not in objects:raise ValueError("Missing UFO parent "+primary)
            p=objects[primary]
            if not isinstance(p.get("pdg_code"),int):
                raise ValueError("Original UFO particle PDG not literal "+primary)
            antirow=dict(p)
            antirow["pdg_code"]=-p["pdg_code"]
            antirow["name"]=p.get("antiname",alias)
            objects[alias]=antirow
    return objects

def extract_vertices(root,particle_names):
    tree=ast.parse((Path(root)/"vertices.py").read_text())
    out=[];missing=[]
    for node in tree.body:
        if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.Call):
            continue
        call=node.value
        if not isinstance(call.func,ast.Name) or call.func.id!="Vertex":
            continue
        key=node.targets[0].id if len(node.targets)==1 and isinstance(node.targets[0],ast.Name) else "anonymous"
        kwargs={k.arg:k.value for k in call.keywords if k.arg}
        items=kwargs.get("particles")
        if not isinstance(items,(ast.List,ast.Tuple)):
            raise ValueError("UFO Vertex particles not literal list "+key)
        ls=[]
        for el in items.elts:
            name=el.attr if isinstance(el,ast.Attribute) and isinstance(el.value,ast.Name) else None
            if name not in particle_names:
                missing.append((key,name,ast.unparse(el)))
                continue
            pdg=particle_names[name].get("pdg_code")
            if not isinstance(pdg,int):
                raise ValueError("PDG is not integer "+str(name))
            ls.append(pdg)
        if len(ls)==len(items.elts):
            out.append((key,tuple(ls)))
    if missing:raise ValueError("UFO unknown particle refs "+str(missing[:5]))
    return out

def inspect_ufo(ufo):
    ufo=Path(ufo).resolve()
    if not ufo.is_dir():raise FileNotFoundError("Missing original SARAH UFO "+str(ufo))
    absent=[f for f in REQUIRED_PY if not(ufo/f).is_file()]
    if absent:raise ValueError("Incomplete SARAH UFO "+repr(absent))
    names=sorted(x for x in ufo.iterdir() if x.suffix==".py")
    hashes={}
    for path in names:
        ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
        hashes[path.name]=hashfile(path)
    pars=parse_objects(ufo,"parameters.py","Parameter")
    parts=parse_objects(ufo,"particles.py","Particle")
    vertices=extract_vertices(ufo,parts)
    mass_pdgs={abs(v["pdg_code"]) for v in parts.values() if isinstance(v.get("pdg_code"),int)}
    scalars={name:int(pdg) in mass_pdgs for name,pdg in SCALAR_PDGS.items()}
    available=set(tuple(sorted(abs(z) for z in pdgs)) for _,pdgs in vertices)
    signatures={}
    for name,pdgs in REQUIRED_VERTEX_PDG.items():
        matching=tuple(sorted(pdgs))
        signatures[name]={
            "present":matching in available,
            "vertex_names":[n for n,p in vertices if tuple(sorted(abs(x) for x in p))==matching][:20],
        }
    byblock=defaultdict(dict)
    parametr=[]
    duplicates=[]
    for key,p in pars.items():
        mode=p.get("nature")
        block=p.get("lhablock")
        code=p.get("lhacode")
        if mode=="external":
            if not isinstance(block,str) or not isinstance(code,(list,tuple)) or not code or not all(isinstance(v,int) for v in code):
                duplicates.append(("invalid_external",key,block,code))
            else:
                ident=tuple(int(x) for x in code)
                b=block.upper()
                if ident in byblock[b]:duplicates.append(("duplicate_external",key,b,ident))
                byblock[b][ident]={"parameter":key,
                     "type":p.get("type"),"default_UFO_value_NOT_F13":p.get("value")}
        parametr.append({"name":key,"nature":mode,"type":p.get("type"),
            "lhablock":block if mode=="external" else None,
            "lhacode":code if mode=="external" else None,
            "expression_or_default":p.get("value"),
            "sensitive":any(z.lower() in key.lower() for z in SENSITIVE_SYMBOLS)})
    if duplicates:raise ValueError("Ambiguous external SLHA map "+repr(duplicates[:5]))
    scalar_slots={}
    for (block,code),expected in SCALAR_POT.items():
        d=byblock.get(block,{}).get(code)
        scalar_slots[expected]={
            "block":block,"code":list(code),
            "actual_UFO_external":d["parameter"] if d else None,
            "actual_UFO_type":d["type"] if d else None,
            "present":d is not None,
        }
    scalar_map_complete=all(x["present"] and x["actual_UFO_type"]=="real"
                            for x in scalar_slots.values())
    blocks={k:{"n":len(v),"entries":{
        ",".join(str(x) for x in idx):value for idx,value in sorted(v.items())}
        } for k,v in sorted(byblock.items())}
    return {
        "ufo_dir":str(ufo),"ufo_python_source_SHA256":hashes,
        "n_Python_modules":len(names),
        "n_parameters":len(pars),"n_vertices":len(vertices),
        "n_particles_including_antiparticles":len(parts),
        "scalar_species_found":scalars,
        "critical_vertex_signatures":signatures,
        "offdiag_Z_present":signatures["offdiag_Z_H2_H1"]["present"],
        "tb_both_charged_present":all(signatures[k]["present"] for k in ("tb_H1","tb_H2")),
        "offdiag_photon_absent":not signatures["photon_H2_H1_must_be_absent"]["present"],
        "all_14_scalar_lagrangian_slots_externally_present_and_real":scalar_map_complete,
        "scalar_external_slot_definitions":scalar_slots,
        "external_SLHA_blocks":blocks,
        "all_UFO_parameter_definitions":parametr,
        "original_SARAH_UFO_model_mass_and_Yukawa_default_NOT_physical_F13":True,
        "full_5state_Zee_slha_card_validated":False,
        "MadWidth_allowed":False,
    }

def cmat(payload,name,dims):
    raw=payload["matrices_re_im"].get(name)
    if not isinstance(raw,list) or len(raw)!=dims[0] or any(
            not isinstance(row,list) or len(row)!=dims[1] for row in raw):
        raise ValueError("Wrong original F16 complex matrix shape "+name)
    matrix=[]
    for row in raw:
        out=[]
        for z in row:
            if (not isinstance(z,list) or len(z)!=2 or
                any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in z)):
                raise ValueError("Bad F16 pair real/imag "+name)
            out.append(complex(z[0],z[1]))
        matrix.append(out)
    return matrix
def deviation(a,b):
    return max(abs(a[i][j]-b[i][j]) for i in range(len(a)) for j in range(len(a[0])))
def consistency(f13,f17):
    target=set(TGT)
    if (f17.get("status")!="F17_F16_SOURCE_EXACT_THREE_COMPLEX_MATRICES_NOT_UFO_PARAM_CARD"
        or set(f17.get("candidate_ids",[]))!=target
        or f17.get("full_Zee_param_card_validated") is not False):
        raise ValueError("F17 original complex matrices source status mismatch")
    rows=f17.get("matrices")
    if not isinstance(rows,list) or len(rows)!=3 or {
       r.get("candidate_id") for r in rows}!=target:
        raise ValueError("F17 exactly three original complex source records needed")
    checks={}
    for r in rows:
        key=r["candidate_id"]
        p=f13[key]
        beta=float(p["scalar"]["beta"])
        gamma=float(p["scalar"]["gamma"])
        masses=[r["mH1_GeV"],r["mH2_GeV"],r["mA_GeV"],r["mHeavyNeutral_GeV"]]
        refs=[p["scalar"]["mH1"],p["scalar"]["mH2"],p["scalar"]["ma"],p["scalar"]["mh2"]]
        if any(not math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-8)
              for a,b in zip(masses,refs)):
            raise ValueError("F16 source scalar spectrum changed in complex exporter "+key)
        if not math.isclose(beta,r["beta_rad"],rel_tol=1e-12,abs_tol=1e-12):
            raise ValueError("F16 source beta wrong in complex exporter "+key)
        if not math.isclose(gamma,r["gamma_rad"],rel_tol=1e-12,abs_tol=1e-12):
            raise ValueError("F16 source gamma wrong "+key)
        F=cmat(r,"FSARAH",(3,3));Ye=cmat(r,"YeSARAH",(3,3))
        Ye2=cmat(r,"Ye2SARAH",(3,3))
        y=cmat(r,"YChen",(3,3))
        charged=cmat(r,"MixCharged",(3,3))
        cp_even=cmat(r,"MixCPeven",(2,2))
        cp_odd=cmat(r,"MixCPodd",(2,2))
        anti=max(abs(F[i][j]+F[j][i]) for i in range(3) for j in range(3))
        if anti>1e-11:raise ValueError("Fzee antisymmetry F13->F17 error "+key)
        v=float(r["vev_GeV"])
        mass_errors=[];y_errors=[]
        for i in range(3):
            for j in range(3):
                originalmass=(math.cos(beta)*Ye[i][j]+math.sin(beta)*Ye2[i][j])*v/math.sqrt(2)
                expectedmass=float(r["lepton_masses_GeV"][i]) if i==j else 0.0
                mass_errors.append(abs(originalmass-expectedmass))
                yy=(-math.sin(beta)*Ye[i][j]+math.cos(beta)*Ye2[i][j])/math.sqrt(2)
                y_errors.append(abs(yy-y[i][j]))
        if max(mass_errors)>5e-9 or max(y_errors)>5e-12:
            raise ValueError("F17 complex lepton weak basis mass/Chen rotation fail "+key)
        b,g=beta,gamma
        expected_charged=[
          [math.cos(b),math.sin(b),0],
          [-math.sin(b)*math.cos(g),math.cos(b)*math.cos(g),math.sin(g)],
          [math.sin(b)*math.sin(g),-math.cos(b)*math.sin(g),math.cos(g)]
        ]
        angle=float(p["scalar"]["alpha"])
        expected_even=[[math.cos(angle),math.sin(angle)],
             [-math.sin(angle),math.cos(angle)]]
        expected_odd=[[math.cos(b),math.sin(b)],[-math.sin(b),math.cos(b)]]
        if (deviation(charged,expected_charged)>1e-11 or
            deviation(cp_even,expected_even)>1e-11 or
            deviation(cp_odd,expected_odd)>1e-11):
            raise ValueError("F16/F17 physical scalar mixing mismatch "+key)
        rules=p["sarah_2VEV_lagrangian_rules"]
        if not math.isclose(math.hypot(rules["v1"],rules["v2"]),v,
                            rel_tol=1e-12,abs_tol=1e-9):
            raise ValueError("F13 scalar physical VEV closure "+key)
        checks[key]={
          "Fzee_antisymmetry_max_abs":anti,
          "Ye_Ye2_physical_lepton_mass_max_abs_GeV":max(mass_errors),
          "Ye_Ye2_YChen_rotation_max_abs":max(y_errors),
          "charged_mixing_max_abs":deviation(charged,expected_charged),
          "all_three_neutrino_flavor_sources_complex_preserved":True,
          "f_and_Y_mass_basis_consistency_test_pass":True,
          "complex_matrices_SLHA_to_UFO_couplings_checked":False,
        }
    return checks

def scalar_fragments(ufo_report,f13,out):
    """Source-valued actual ZEEPOT + ZEEQUARTIC external declarations only.

    No physical mass block, CKM, split complex source, DECAY or alpha ew
    defaults. This is NOT a param_card accepted by MadWidth.
    """
    slots=ufo_report["scalar_external_slot_definitions"]
    if not ufo_report["all_14_scalar_lagrangian_slots_externally_present_and_real"]:
        return {"status":"NOT_ALL_SCALAR_LAGRANGIAN_SLOTS_UFO_EXTERNAL", "files":[]}
    files=[]
    for name in TGT:
        data=f13[name]["sarah_2VEV_lagrangian_rules"]
        lines=[
          "# SOURCE-VERIFIED F13 2-VEV ZEE SCALAR FRAGMENT ONLY; NOT MG5 param_card.",
          "# Mass, gauge inputs, CKM, full complex Ye/Ye2/Fzee AND WIDTHS NOT SET.",
          "# Never use this alone to compute a physical MadWidth rate.",
        ]
        for block in ("ZEEPOT","ZEEQUARTIC"):
            lines.append("BLOCK "+block)
            pairs=sorted(((info["code"][0],param)
                         for param,info in slots.items() if info["block"]==block))
            for idx,param in pairs:
                val=float(data[param])
                if not math.isfinite(val):raise ValueError("Nonfinite scalar "+param)
                lines.append(f" {idx:3d} {val:+.17e} # {param}")
        dest=out/(name+"_ZEEPOT_ZEEQUARTIC_SOURCE_ONLY_NOT_FULL_CARD.slha")
        dest.write_text("\n".join(lines)+"\n")
        files.append({"candidate_id":name,"path":dest.name,"sha256":hashfile(dest)})
    return {"status":"14_SOURCE_SCALAR_EXTERNS_MAPPED_ONLY_NOT_COMPLETE_MODEL_CARD","files":files}

def run(f16_dir,output):
    source=Path(f16_dir).expanduser().resolve()
    dest=Path(output).expanduser().resolve()
    if dest.exists():raise FileExistsError("F17 refuses overwriting prior source inventory")
    verify_f16(source,Path("models/SARAH/ZeeTypeII/ZeeTypeII.m"))
    sta=source/"F16_local_SARAH_vertex_status.txt"
    if not sta.is_file() or sta.read_text().strip()!=F16_PASS:
        raise ValueError("F16 complete independent three source vertex PASS missing")
    raw=json.loads((source/"F16_three_exact_F13_Zee_input_reconstruction.json").read_text())
    exported=source/SOURCE_COMPLEX
    if not exported.is_file():
        raise FileNotFoundError("First run local Mathematica F17 complex fixture exporter")
    cx=json.loads(exported.read_text())
    flavorchecks=consistency(raw,cx)
    ufo=inspect_ufo(source/UFO_SUBDIR)
    all5=all(ufo["scalar_species_found"].values())
    essential={
      "five_physical_scalars_present":all5,
      "H2_H1_Z_vertex":ufo["critical_vertex_signatures"]["offdiag_Z_H2_H1"]["present"],
      "H1_tb_H2_tb_vertices":ufo["tb_both_charged_present"],
      "charged_H1_H2_offdiag_photon_absent":ufo["offdiag_photon_absent"],
      "scalar_externals_14_declared":ufo["all_14_scalar_lagrangian_slots_externally_present_and_real"],
    }
    dest.mkdir(parents=True,exist_ok=False)
    with (dest/"F17_UFO_external_parameters.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=(
            "name","nature","type","lhablock","lhacode","expression_or_default","sensitive"))
        writer.writeheader()
        for row in ufo["all_UFO_parameter_definitions"]:
            x={**row,"lhacode":json.dumps(row["lhacode"]),
               "expression_or_default":json.dumps(row["expression_or_default"])}
            writer.writerow(x)
    scalar=scalar_fragments(ufo,raw,dest)
    report={
       "status":STATUS,
       "original_F16_path":str(source),
       "original_F16_summary_SHA256":hashfile(source/"summary.json"),
       "original_F16_three_complex_fixture_SHA256":hashfile(exported),
       "original_F16_three_source_JSON_SHA256":hashfile(
          source/"F16_three_exact_F13_Zee_input_reconstruction.json"),
       "three_real_complex_F13_mass_mix_fY_source_checks":flavorchecks,
       "actual_SARAH_export_UFO_interface":ufo,
       "essential_interface_checks":essential,
       "essential_static_structural_checks_pass":all(essential.values()),
       "mapped_exact_F13_scalar_external_SLHA_fragments":scalar,
       "complete_typeII_CKM_and_complex_matrices_external_SLHA_matching":False,
       "model_exact_physical_spectrum_after_UFO_parameter_evaluation":False,
       "Ward_identity_and_Goldstone_equivalence":False,
       "MadWidth_2body_3body_execution":False,
       "physical_Zee_total_widths_and_BR":None,
       "allowed_excluded_or_collider_reach":None,
       "next_blockers":[
          "Verify SARAH export external mass/mixing and quark CKM basis",
          "Construct all external LHA inputs with correct IM blocks for Fzee,Ye,Ye2,Yu,Yd",
          "Evaluate actual UFO parameter dependencies at each source F13 model",
          "Independently check H1/H2 physical spectrum and chirality amplitudes",
          "MadWidth 2-body and 3-body source-matched complete decays",
          "Modern calibrated two-state 2026 B->Xs gamma and full LFV",
       ],
    }
    writejson(dest/"summary.json",report)
    print("F17_ORIGINAL_3_COMPLEX_SCALAR_FLAVOR_SOURCE_REVALIDATED",len(flavorchecks))
    print("F17_UFO_PARAMS",ufo["n_parameters"],
         "EXTERNAL",sum(x["nature"]=="external" for x in ufo["all_UFO_parameter_definitions"]),
         "PARTICLES",ufo["n_particles_including_antiparticles"],
         "VERTICES",ufo["n_vertices"])
    print("F17_UFO_PDG",json.dumps(ufo["scalar_species_found"],sort_keys=True))
    print("F17_UFO_VERTICES",json.dumps({
        x:val["present"] for x,val in ufo["critical_vertex_signatures"].items()},sort_keys=True))
    print("F17_SCALAR_LHA",scalar["status"])
    print("F17_STATUS",STATUS,"STATIC_ESSENTIAL_PASS",all(essential.values()),
          "VALIDATED_FULL_ZEE_CARD",False,"MADWIDTH_READY",False)
    print("F17_REPORT",dest/"summary.json")
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--f16-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    run(args.f16_dir,args.output)
if __name__=="__main__":
    main()

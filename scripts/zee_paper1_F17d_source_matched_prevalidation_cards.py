#!/usr/bin/env python3
"""F17d: all-real-UFO-external SLHA candidates using the exact F16/F17 source.

NOT approved for MadWidth: quark sector is an explicit diagonal CKM=I
diagnostic basis, F15 quark masses are LO proxies, BSM widths are placeholders.
Never import/execute generated UFO Python; preserve SHA-pinned source files.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from zee_paper1_F17_inspect_real_SARAH_UFO import (
    TGT,UFO_SUBDIR,SOURCE_COMPLEX,parse_objects,consistency,cmat)
from zee_paper1_F17_verify_complex_json import verify_json
from zee_paper1_F17c_real_UFO_scalar_photon import (
    hashfile,source_ew,NumericUFO,photon_numeric,scalar_photon_vertices,get_ufo_couplings)

STATUS="F17D_EXACT_SCALAR_COMPLEX_LEPTON_ALL_UFO_EXTERNAL_SLOTS_CKM_I_TEST_NOT_MADWIDTH"
UP=(.0022,1.27,172.)
DOWN=(.0047,.093,4.7)
MASSES=(1,2,3,4,5,6,11,13,15,23,25,35,36,37,9000037)
COMPLEX=("YU","YD","YE","YEE2","FZEE","UDLMIX","UDRMIX",
         "UULMIX","UURMIX","UELMIX","UERMIX")
QUARTICS={**{"Lambda"+str(i):("ZEEQUARTIC",(i,)) for i in range(1,6)},
          "LambdaC":("ZEEQUARTIC",(6,)),"K1":("ZEEQUARTIC",(7,)),
          "K2":("ZEEQUARTIC",(8,)),"K12":("ZEEQUARTIC",(9,)),
          "Mu4":("ZEEPOT",(5,))}
SUPPORTED={"MASS","DECAY","SMINPUTS","HMIX","EFFHIGGSCOUPLINGS",
           "ZEEPOT","ZEEQUARTIC","SCALARMIX","PSEUDOSCALARMIX","CHARGEMIX"}
SUPPORTED.update(COMPLEX)
SUPPORTED.update("IM"+s for s in COMPLEX)

def slots_from_real_ufo(parameters):
    slots={}
    for name,p in parameters.items():
        if p.get("nature")!="external": continue
        block=str(p.get("lhablock","")).upper()
        code=p.get("lhacode")
        if (block not in SUPPORTED or p.get("type")!="real"
                or not isinstance(code,(list,tuple)) or not code
                or not all(type(x)==int for x in code)):
            raise ValueError("Unknown or nonreal UFO external slot "+name)
        ident=(block,tuple(code))
        if ident in slots:raise ValueError("Duplicate UFO external slot "+str(ident))
        slots[ident]=name
    if len(slots)!=258:raise ValueError("Expected 258 exact UFO external entries")
    return slots

def verify_csv(path,slots):
    with Path(path).open(newline="") as f:
        rows=list(csv.DictReader(f))
    actual={}
    for row in rows:
        if row["nature"]!="external":continue
        k=(row["lhablock"].upper(),tuple(json.loads(row["lhacode"])))
        if k in actual:raise ValueError("CSV duplicate "+str(k))
        if row["type"]!="real":raise ValueError("Nonreal CSV "+str(k))
        actual[k]=row["name"]
    if actual!=slots:raise ValueError("Original F17 CSV differs from actual UFO")
    return True

def put_matrix(target,block,mat):
    for i,line in enumerate(mat,1):
        for j,z in enumerate(line,1):
            z=complex(z)
            target[(block,(i,j))]=float(z.real)
            if block in COMPLEX:
                target[("IM"+block,(i,j))]=float(z.imag)
            elif abs(z.imag)>1.e-12:
                raise ValueError("Nonreal exported scalar rotation "+block)

def values_for_source(row,case):
    ew=source_ew(row)
    beta=row["beta_rad"]
    sb,cb=math.sin(beta),math.cos(beta)
    if min(sb,cb)<=0:raise ValueError("Invalid Type-II vevs")
    v=ew["v"]
    vals={}
    mass={1:DOWN[0],3:DOWN[1],5:DOWN[2],2:UP[0],4:UP[1],6:UP[2],
          11:row["lepton_masses_GeV"][0],13:row["lepton_masses_GeV"][1],
          15:row["lepton_masses_GeV"][2],23:91.1876,25:125.,
          35:row["mHeavyNeutral_GeV"],36:row["mA_GeV"],
          37:row["mH1_GeV"],9000037:row["mH2_GeV"]}
    if set(mass)!=set(MASSES) or min(mass.values())<=0:
        raise ValueError("Incomplete physical scalar/fermion MASS set")
    vals.update({("MASS",(k,)):float(z) for k,z in mass.items()})
    # SM widths are stated reference values; all BSM physical widths are
    # placeholders (zero) until independently computed by MadWidth.
    for k in (6,23,24,25,35,36,37,9000037):
        vals[("DECAY",(k,))]={6:1.51,23:2.4952,24:2.141}.get(k,0.)
    vals.update({("SMINPUTS",(1,)):ew["aEWinv"],
                 ("SMINPUTS",(2,)):ew["Gf"],
                 ("SMINPUTS",(3,)):0.119, # explicit LO reference, not F13
                 ("HMIX",(10,)):beta})
    rules=case["sarah_2VEV_lagrangian_rules"]
    for name,loc in QUARTICS.items():vals[loc]=float(rules[name])
    for src,blk,dims in (("MixCharged","CHARGEMIX",(3,3)),
                         ("MixCPeven","SCALARMIX",(2,2)),
                         ("MixCPodd","PSEUDOSCALARMIX",(2,2)),
                         ("FSARAH","FZEE",(3,3)),
                         ("YeSARAH","YE",(3,3)),
                         ("Ye2SARAH","YEE2",(3,3))):
        put_matrix(vals,blk,cmat(row,src,dims))
    # Deliberately diagonal CKM=I test basis, NOT F15 physical CKM.
    yu=[[complex(math.sqrt(2)*UP[i]/(v*sb)) if i==j else 0j
         for j in range(3)] for i in range(3)]
    yd=[[complex(math.sqrt(2)*DOWN[i]/(v*cb)) if i==j else 0j
         for j in range(3)] for i in range(3)]
    put_matrix(vals,"YU",yu)
    put_matrix(vals,"YD",yd)
    identity=[[complex(float(i==j)) for j in range(3)] for i in range(3)]
    for blk in ("UDLMIX","UDRMIX","UULMIX","UURMIX","UELMIX","UERMIX"):
        put_matrix(vals,blk,identity)
    for pdg in (25,35,36):
        for boson in (21,22):
            vals[("EFFHIGGSCOUPLINGS",(pdg,boson,boson))]=0.
    return vals

def check_slots(slots,values):
    if set(slots)!=set(values):
        raise ValueError("Unassigned UFO external slots: "+str(sorted(set(slots)-set(values))[:12])+
                         "; unknown "+str(sorted(set(values)-set(slots))[:12]))
    for ident,val in values.items():
        if type(val) not in (int,float) or not math.isfinite(val):
            raise ValueError("Bad UFO external "+str(ident))

def lepton_mass_error(row,vals):
    beta=row["beta_rad"];v=row["vev_GeV"];maximum=0.
    for i in range(1,4):
        for j in range(1,4):
            ye=complex(vals[("YE",(i,j))],vals[("IMYE",(i,j))])
            ye2=complex(vals[("YEE2",(i,j))],vals[("IMYEE2",(i,j))])
            m=v/math.sqrt(2)*(math.cos(beta)*ye+math.sin(beta)*ye2)
            expect=row["lepton_masses_GeV"][i-1] if i==j else 0.
            maximum=max(maximum,abs(m-expect))
    if maximum>5e-9:raise ValueError("Original complex lepton mass basis mismatch")
    return maximum

def actual_ufo_gauge(parameters,slots,values,row):
    resolver=NumericUFO(parameters,{name:values[slot] for slot,name in slots.items()})
    ew=source_ew(row)
    result={}
    for name in ("g1","g2","TW","v","MWm"):
        got=resolver.param(name)
        if abs(got-ew[{"MWm":"MW"}.get(name,name)])>3e-8*max(1,abs(ew[{"MWm":"MW"}.get(name,name)])):
            raise ValueError("Real UFO gauge internal "+name+" disagrees with F16")
        result[name]=[float(complex(got).real),float(complex(got).imag)]
    return result

def render(slots,vals,case):
    check_slots(slots,vals)
    lines=["# EXACT ORIGINAL F16 SCALAR + COMPLEX LEPTONS, ACTUAL UFO external slots",
           "# CKM=IDENTITY DIAGNOSTIC BASIS, NOT PHYSICAL F15 CKM",
           "# NOT VERIFIED H1->tb, H2->H1 Z, COMPLEX LEPTON AMPLITUDES",
           "# BSM DECAY widths ZERO are placeholders. NOT MADWIDTH READY.",
           "# Exact F13 case: "+case]
    blocks=sorted({b for b,_ in slots if b!="DECAY"})
    for block in blocks:
        lines.append("BLOCK "+block)
        for (b,idx),symbol in sorted(slots.items(),key=lambda x:x[0][1]):
            if b==block:
                lines.append("  "+" ".join(str(i) for i in idx)+
                             " "+format(vals[(b,idx)],"+.17e")+" # "+symbol)
    for (block,idx),symbol in sorted(slots.items(),key=lambda x:x[0][1]):
        if block=="DECAY":
            lines.append("DECAY "+str(idx[0])+" "+format(vals[(block,idx)],".17e")+" # "+symbol)
    return "\n".join(lines)+"\n"

def build(f16_dir,f17_report,f17c_report,csv_file,output):
    source=Path(f16_dir).expanduser().resolve()
    ufo=source/UFO_SUBDIR
    out=Path(output).expanduser().resolve()
    if out.exists():raise FileExistsError("Refuse overwrite F17d outputs")
    f17=verify_json(source/SOURCE_COMPLEX)
    f16_path=source/"F16_three_exact_F13_Zee_input_reconstruction.json"
    f16=json.loads(f16_path.read_text())
    source_checks=consistency(f16,f17)
    old=json.loads(Path(f17_report).read_text())["actual_SARAH_export_UFO_interface"]
    c=json.loads(Path(f17c_report).read_text())
    if (not c.get("all_three_photon_checks_pass")
        or c.get("complete_physical_card_validated") is not False
        or Path(old["ufo_dir"]).resolve()!=ufo
        or Path(c["original_UFO_directory"]).resolve()!=ufo):
        raise ValueError("F16/F17/F17c chain invalid or wrong original UFO")
    for name,expected in old["ufo_python_source_SHA256"].items():
        if hashfile(ufo/name)!=expected:raise ValueError("F17 UFO SHA changed "+name)
    for name,key in (("parameters.py","original_UFO_parameters_SHA256"),
                     ("vertices.py","original_UFO_vertices_SHA256"),
                     ("couplings.py","original_UFO_couplings_SHA256")):
        if hashfile(ufo/name)!=c[key]:raise ValueError("F17c pinned UFO SHA changed "+name)
    if hashfile(source/SOURCE_COMPLEX)!=c["exact_three_source_F17_json_SHA256"]:
        raise ValueError("F17 exact original matrix source mutated")
    if hashfile(f16_path)!=c["exact_three_source_F16_json_SHA256"]:
        raise ValueError("F16 exact original scalar source mutated")
    pars=parse_objects(ufo,"parameters.py","Parameter")
    slots=slots_from_real_ufo(pars)
    verify_csv(csv_file,slots)
    photons=scalar_photon_vertices(ufo)
    couplings=get_ufo_couplings(ufo)
    prepared={}
    for row in f17["matrices"]:
        key=row["candidate_id"]
        vals=values_for_source(row,f16[key])
        check_slots(slots,vals)
        err=lepton_mass_error(row,vals)
        gauge=actual_ufo_gauge(pars,slots,vals,row)
        # Additional recheck of original offdiagonal and diagonal photon.
        if not photon_numeric(pars,couplings,photons,row)["PASS"]:
            raise ValueError("Actual original UFO photon failed "+key)
        prepared[key]=(vals,err,gauge)
    if set(prepared)!=set(TGT):raise ValueError("Wrong exact F13 3-case set")
    out.mkdir(parents=True,exist_ok=False)
    files=[]
    for key,(vals,err,gauge) in sorted(prepared.items()):
        filename=key+"_FULL_EXTERNAL_TEST_BASIS_NOT_MADWIDTH.slha"
        path=out/filename
        path.write_text(render(slots,vals,key))
        files.append({"id":key,"file":filename,"sha256":hashfile(path),
                      "n_external":len(slots),"lepton_mass_error_GeV":err,
                      "derived_original_UFO_gauge":gauge})
        print("F17D_PREVALIDATION",key,"EXTERNAL",len(slots),
              "LEPTON_ERROR_GEV",err,"ORIGINAL_UFO_GAUGE_PASS",True)
    summary={"status":STATUS,"candidate_cards":files,
             "original_F17c_report_SHA256":hashfile(f17c_report),
             "original_F17_external_inventory_SHA256":hashfile(csv_file),
             "source_complex_checks":source_checks,
             "CKM":"IDENTITY_DIAGNOSTIC_ONLY",
             "F15_quark_masses":"EXPLICIT_LO_PROXIES_NOT_QCD_SCHEME",
             "SM_widths":"EXPLICIT_REFERENCE_VALUES",
             "BSM_widths":"ZERO_PLACEHOLDERS",
             "full_physical_UFO_card_validated":False,"MadWidth_ready":False,
             "next":"Independently validate UFO Type-II quark chirality/CKM basis, H2-H1-Z, H1-tb, complex lepton amplitudes."}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F17D_STATUS",STATUS,"PHYSICAL_CARDS_READY",False,"MADWIDTH_READY",False)
    print("F17D_OUTPUT",out)
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ("f16-dir","f17-report","f17c-report","external-csv","output"):
        p.add_argument("--"+flag,type=Path,required=True)
    x=p.parse_args()
    build(x.f16_dir,x.f17_report,x.f17c_report,x.external_csv,x.output)

if __name__=="__main__":main()

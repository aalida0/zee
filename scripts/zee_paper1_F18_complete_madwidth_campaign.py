#!/usr/bin/env python3
"""F18: ONE end-to-end original ZeeTypeII three-benchmark MadWidth campaign.

For each exact F13 point: verify immutable F16-F17f chain, run MG5 MadWidth
first for two-body (seed nonzero resonance widths), then for two- AND
three-body with on-shell cascades handled by MadWidth's narrow-width
algorithm, and independently compare the resulting physical channels with
the actually evaluated UFO tree amplitudes. Report the *model's* LO widths,
BRs and (only when original F14 is supplied) its 13-TeV production-normalized
cascade. Reject malformed or incomplete tables. DO NOT call these
QCD-improved widths, NNLO flavor-allowed points, or collider sensitivity.

Use actual SARAH scalar PDGs h=25,H=35,A=36,Hm[2]=37,Hm[3]=9000037.
The sign of the charged scalar field is obtained from particles.py,
not guessed from PDG labels. Zero BSM input widths are bootstrap values.
This deliberately runs real MG5; Python unit tests DO NOT substitute for it.
"""
from __future__ import annotations
import argparse,ast,csv,json,math,os,subprocess,sys,time
from pathlib import Path

from zee_paper1_F17_inspect_real_SARAH_UFO import (
    TGT,UFO_SUBDIR,SOURCE_COMPLEX,parse_objects,cmat,consistency)
from zee_paper1_F17_verify_complex_json import verify_json
from zee_paper1_F17c_real_UFO_scalar_photon import hashfile,NumericUFO,S2W_F16
from zee_paper1_F17d_source_matched_prevalidation_cards import slots_from_real_ufo
from zee_paper1_F17e_real_UFO_amplitude_gate import read_f17d_card

STATUS="F18_REAL_SARAH_ZEE_MADWIDTH_2AND3_BODY_3_CASES_MODEL_LO_NOT_EXCLUSION"
SCALARS=(25,35,36,37,9000037)
CHARGED=(37,9000037)
LEPTONS=(11,13,15)
NEUTRINOS=(12,14,16)
TOP_B=(5,6)
# Numerically integrated MadWidth channels can have nonzero integration
# error; compare SOURCE amplitudes to 2-body and 2+3 body channel results.
REL_TWO_BODY_TOL=0.05
REL_COMPLEX_LEPTON_TOL=0.05
SLHA_CLOSURE_TOL=0.005
MIN_BR="0.0"            # do not knowingly discard rare channels
PRECISION_CHANNEL="0.01" # request 1% integration relative precision


def read_slha(path):
    """Parse mass and decay blocks, including all 2/3-body BR entries.

    No duplicate physical channel, negative BR/width, or missing target
    may be treated as an acceptable complete decay table.
    """
    masses={};tables={};inputs={};block=None;parent=None
    for lineno,raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        line=raw.split("#",1)[0].strip()
        if not line:continue
        words=line.split()
        keyword=words[0].upper()
        if keyword=="BLOCK":
            if len(words)<2:raise ValueError("Invalid BLOCK line "+str(lineno))
            block=words[1].upper();parent=None
            continue
        if keyword=="DECAY":
            if len(words)<3:raise ValueError("Invalid DECAY line "+str(lineno))
            pdg=int(words[1]);width=float(words[2].replace("D","E").replace("d","e"))
            if pdg in tables or not math.isfinite(width) or width<0:
                raise ValueError("Duplicate/invalid DECAY "+str(pdg))
            tables[pdg]={"width_GeV":width,"modes":[]}
            parent=pdg;block=None
            continue
        if keyword=="QNUMBERS":
            parent=None;block=None;continue
        if parent is not None:
            if len(words)<3:raise ValueError("Malformed decay mode "+str((parent,lineno)))
            br=float(words[0].replace("D","E").replace("d","e"))
            n=int(words[1]);ds=tuple(int(x) for x in words[2:])
            if (n not in (2,3) or len(ds)!=n or not math.isfinite(br)
                    or not 0<=br<=1+1e-9):
                raise ValueError("Invalid or unsupported MadWidth decay mode "+
                                 str((parent,lineno,words)))
            tables[parent]["modes"].append({
                "daughters":ds,"multiplicity":n,"BR":br,
                "partial_width_GeV":br*tables[parent]["width_GeV"]})
            continue
        if block:
            try:
                index=tuple(int(x) for x in words[:-1])
                val=float(words[-1].replace("D","E").replace("d","e"))
            except (IndexError,ValueError):
                # SLHA may contain harmless informational blocks; always
                # require full parse for physical blocks used by the UFO.
                if block in {"MASS","SMINPUTS","ZEEPOT","ZEEQUARTIC",
                             "CHARGEMIX","SCALARMIX","PSEUDOSCALARMIX",
                             "YU","IMYU","YD","IMYD","YE","IMYE",
                             "YEE2","IMYEE2","FZEE","IMFZEE"}:
                    raise ValueError("Malformed model input "+str((block,lineno)))
                continue
            if not math.isfinite(val):raise ValueError("Nonfinite block entry")
            if block=="MASS":
                if len(index)!=1 or index[0] in masses:
                    raise ValueError("Duplicate/malformed MASS entry")
                masses[index[0]]=val
            k=(block,index)
            if k in inputs:raise ValueError("Duplicate numeric SLHA block entry "+str(k))
            inputs[k]=val
    return masses,tables,inputs


def check_original_card(path,slots,entry):
    if path.name!=entry["file"] or hashfile(path)!=entry["sha256"]:
        raise ValueError("Original F17f candidate card SHA mismatch")
    vals=read_f17d_card(path,slots)
    for pdg in SCALARS:
        if ("MASS",(pdg,)) not in vals or vals[("MASS",(pdg,))]<=0:
            raise ValueError("Missing original physical scalar mass "+str(pdg))
    return vals


def check_MadWidth_input_preserved(path,reference):
    mass,tables,slha=read_slha(path)
    for key,value in reference.items():
        if key[0]=="DECAY":continue
        # Zero elements may be omitted when MG5 normalizes output SLHA.
        if key not in slha:
            if abs(value)>1e-14:raise ValueError("MadWidth lost nonzero parameter "+str(key))
            continue
        if not math.isclose(slha[key],value,rel_tol=2e-7,abs_tol=2e-10):
            raise ValueError("MadWidth changed source external input "+str((key,value,slha[key])))
    return mass,tables,slha


def charged_field_sign(ufo):
    """Get charge sign of actual Hm2/Hm3 particle objects, PDGs 37/9000037."""
    particles=parse_objects(ufo,"particles.py","Particle")
    result={}
    for pdg in CHARGED:
        candidates=[v for v in particles.values()
                    if v.get("pdg_code")==pdg]
        if len(candidates)!=1:
            raise ValueError("Ambiguous actual SARAH particle charge for "+str(pdg))
        charge=candidates[0].get("charge")
        if type(charge) not in (int,float) or not math.isclose(abs(charge),1.,abs_tol=1e-12):
            raise ValueError("Original SARAH charged-scalar charge unknown "+str((pdg,charge)))
        result[pdg]=1 if charge>0 else -1
    if result[37]!=result[9000037]:
        raise ValueError("H1 H2 physical charge convention inconsistent")
    return result[37]



def derive_internal_W_mass(ufo,values):
    """Actual SARAH MWm derived parameter, not an invented UFO external slot.

    F16 electroweak inputs are already source-validated in F17d. PDG24 is
    nevertheless mandatory in MadWidth's parsed LHE mass inventory.
    """
    parameters=parse_objects(ufo,"parameters.py","Parameter")
    slots=slots_from_real_ufo(parameters)
    if ("MASS",(24,)) in slots or ("MASS",(24,)) in values:
        raise ValueError("MASS 24 is already external or present; refuse duplicate")
    physical_W=[p for p in parse_objects(ufo,"particles.py","Particle").values()
                if p.get("pdg_code")==24]
    if len(physical_W)!=1:
        raise ValueError("Original SARAH UFO W particle not uniquely identified")
    mass_expr=physical_W[0].get("mass")
    if not isinstance(mass_expr,dict) or mass_expr.get("python_expression")!="Param.MWm":
        raise ValueError("Original SARAH W is not sourced from internal Param.MWm: "+
                         str(mass_expr))
    if "MWm" not in parameters or parameters["MWm"].get("nature")!="internal":
        raise ValueError("Missing actual internal SARAH W mass MWm")
    resolver=NumericUFO(parameters,{name:values[key] for key,name in slots.items()})
    actual=complex(resolver.param("MWm"))
    expected=values[("MASS",(23,))]*math.sqrt(1.0-S2W_F16)
    if not (math.isfinite(actual.real) and math.isfinite(actual.imag)
            and actual.real>0 and abs(actual.imag)<1e-11
            and abs(actual.real-expected)<1e-8):
        raise ValueError("Actual-UFO internal W mass contradicts F16 electroweak convention "+
                         str((actual,expected)))
    return actual.real


def prepare_madwidth_W_mass_card(original_card,prepared_card,ufo,original_values):
    """Add solely internal MASS(24) to a NEW run-local card.

    Source F17f files and the original 258 UFO external slots remain
    untouched and SHA-pinned. The copied card is for MG5's internal LHE
    mass inventory, not a reparametrization of the scalar/gauge model.
    """
    original_card=Path(original_card)
    prepared_card=Path(prepared_card)
    if prepared_card.exists():
        raise FileExistsError("Refuse overwriting earlier MadWidth W-mass card")
    original_sha=hashfile(original_card)
    text=original_card.read_text(encoding="utf-8")
    mass=derive_internal_W_mass(ufo,original_values)
    sections=text.splitlines()
    headers=[i for i,line in enumerate(sections)
             if line.split("#",1)[0].strip().upper()=="BLOCK MASS"]
    if len(headers)!=1:
        raise ValueError("Expected exactly one original external MASS block")
    # The original validated card must not already contain MASS(24).
    masses,_,_=read_slha(original_card)
    if 24 in masses:
        raise ValueError("Original card already provides W mass")
    sections.insert(headers[0]+1,
                    "  24 "+format(mass,"+.17e")+" # derived UFO Param.MWm, "
                    "F16 electroweak convention; MG5 LHE mass inventory")
    prepared_card.write_text("\n".join(sections)+"\n",encoding="utf-8")
    if hashfile(original_card)!=original_sha:
        raise RuntimeError("Original F17f card unexpectedly modified")
    obtained,_,entries=read_slha(prepared_card)
    if not math.isclose(obtained[24],mass,rel_tol=1e-14):
        raise ValueError("MadWidth auxiliary W mass did not serialize")
    for key,val in original_values.items():
        if key[0]!="DECAY" and (key not in entries or
             not math.isclose(val,entries[key],rel_tol=1e-13,abs_tol=1e-13)):
            raise ValueError("W mass insertion changed an original external slot "+
                             str(key))
    return {"derived_internal_MWm_GeV":mass,
            "original_F17f_card_SHA256":original_sha,
            "madwidth_auxiliary_input":str(prepared_card),
            "madwidth_auxiliary_input_SHA256":hashfile(prepared_card),
            "original_external_slot_count_unchanged":len(original_values),
            "new_UFO_external_parameters":0}


def validate_table(tables,pdg,*,three_body):
    if pdg not in tables:raise ValueError("MadWidth missing DECAY "+str(pdg))
    data=tables[pdg]
    width=data["width_GeV"]
    seen=set()
    for mode in data["modes"]:
        if mode["multiplicity"]==3 and not three_body:
            raise ValueError("Three-body mode appeared in two-body-only MadWidth")
        signature=(mode["multiplicity"],tuple(sorted(mode["daughters"])))
        if signature in seen:raise ValueError("Duplicate physical decay channel "+str((pdg,signature)))
        seen.add(signature)
    total=sum(mode["BR"] for mode in data["modes"])
    if width>1e-12 and (not data["modes"] or abs(total-1)>SLHA_CLOSURE_TOL):
        raise ValueError("MadWidth DECAY table does not close "+str((pdg,width,total)))
    if width<=1e-12 and any(mode["partial_width_GeV"]>1e-11 for mode in data["modes"]):
        raise ValueError("Zero parent width with positive partial widths")
    return total


def mode_width(table,daughters,*,n=2,match_abs=False):
    """Sum channels sharing a defined observable; match sign when required."""
    query=tuple(sorted(abs(i) if match_abs else i for i in daughters))
    selected=[v for v in table["modes"] if v["multiplicity"]==n
        and tuple(sorted(abs(z) if match_abs else z for z in v["daughters"]))==query]
    return sum(v["partial_width_GeV"] for v in selected),selected


def check_two_body_against_f17f(case,f17e,decays,field_sign):
    """Confront MadWidth values with independent evaluated SARAH UFO couplings."""
    h1,h2=decays[37],decays[9000037]
    wZ,mZ=mode_width(h2,[37,23])
    if len(mZ)!=1:raise ValueError("H2 -> H1 Z missing or charge ambiguity")
    expected_Z=float(f17e["actual_UFO_H2_H1Z_partial_width_GeV"])
    if not expected_Z>0:raise ValueError("Source independent Z channel not open")
    # PDG 37 can denote H- in SARAH, unlike user's H+ notation.
    tb_expected=[-6,5] if field_sign<0 else [6,-5]
    wtb,mtb=mode_width(h1,tb_expected)
    if len(mtb)!=1:raise ValueError("H1 -> t bbar / tbar b sign-matched mode missing")
    matching=[x for x in case["actual_UFO_charged_H_quark_width_checks"]
             if x["H"]=="H1" and x["up"]=="t" and x["down"]=="b"]
    if len(matching)!=1:raise ValueError("F17f original physical CKM tb reference absent")
    ref_tb=matching[0]["source_F15_CKM_completed_width_GeV"]
    refs={"H2_H1Z":(wZ,expected_Z),"H1_tb":(wtb,ref_tb)}
    # Source has complete physically complex lepton amplitudes validated.
    charged_leptons={}
    for parent,label in ((37,"H1"),(9000037,"H2")):
        table=decays[parent]
        target=case["independent_F16_B3_complex_lepton_width_target_GeV"][label]
        for pdg,flavor in zip(LEPTONS,("e","mu","tau")):
            contributions=[m for m in table["modes"] if m["multiplicity"]==2
                and sorted(map(abs,m["daughters"])) in (
                    sorted((pdg,n)) for n in NEUTRINOS)]
            # In general Zee, doublet Y and antisymmetric f can connect
            # opposite neutrino helicity/particle-number assignments.
            # Do not require precisely three signed SLHA modes: sum all
            # physically distinct neutrino and antineutrino channels.
            species={abs(x) for m in contributions for x in m["daughters"]
                     if abs(x) in NEUTRINOS}
            if species!=set(NEUTRINOS):
                raise ValueError("Incomplete neutrino-flavor coverage "+
                                 str((label,flavor,sorted(species))))
            width=sum(m["partial_width_GeV"] for m in contributions)
            ref=float(target[flavor])
            relative=abs(width-ref)/max(1e-15,ref)
            if relative>REL_COMPLEX_LEPTON_TOL:
                raise ValueError("MadWidth complex lepton two-body mismatch "+
                                 str((label,flavor,width,ref,relative)))
            charged_leptons[label+"_"+flavor]={
                "MadWidth_GeV":width,"F16_B3_GeV":ref,"relative":relative}
    residuals={label:abs(measured-reference)/max(reference,1e-15)
               for label,(measured,reference) in refs.items()}
    if max(residuals.values())>REL_TWO_BODY_TOL:
        raise ValueError("MadWidth physical two-body amplitude mismatch "+str(residuals))
    return {
        "Z_and_tb":{k:{"MadWidth_GeV":x,"reference_actual_UFO_GeV":r,
                       "relative":residuals[k]} for k,(x,r) in refs.items()},
        "charged_leptons":charged_leptons,
        "Z_tb_max_relative":max(residuals.values()),
        "leptons_max_relative":max(x["relative"] for x in charged_leptons.values()),
    }


def ensure_consistent_2body_stage(first,last):
    # Test that 3-body integration does not silently rewrite the already
    # matched two-body amplitudes.
    deviations={}
    for pid in CHARGED:
        old={(tuple(sorted(x["daughters"]))):x["partial_width_GeV"]
             for x in first[pid]["modes"] if x["multiplicity"]==2}
        new={(tuple(sorted(x["daughters"]))):x["partial_width_GeV"]
             for x in last[pid]["modes"] if x["multiplicity"]==2}
        if set(old)!=set(new):
            raise ValueError("MadWidth two-body inventory changed when enabling 3body "+str(pid))
        for ds in old:
            denom=max(old[ds],new[ds],1e-13)
            rel=abs(old[ds]-new[ds])/denom
            if rel>REL_TWO_BODY_TOL:
                raise ValueError("MadWidth two-body channel shifted after 3body "+str((pid,ds,rel)))
            deviations[str((pid,ds))]=rel
    return max(deviations.values(),default=0.)


def summarize_decay_parent(first,final,pdg):
    data=final[pdg];width=data["width_GeV"]
    modes=sorted(data["modes"],key=lambda m:m["partial_width_GeV"],reverse=True)
    two=sum(m["partial_width_GeV"] for m in modes if m["multiplicity"]==2)
    three=sum(m["partial_width_GeV"] for m in modes if m["multiplicity"]==3)
    init=first[pdg]["width_GeV"]
    return {"total_GeV":width,"two_body_sum_GeV":two,"three_body_sum_GeV":three,
            "three_body_fraction":three/width if width>0 else None,
            "two_only_total_GeV":init,
            "delta_vs_two_only_GeV":width-init,
            "n_2body":sum(m["multiplicity"]==2 for m in modes),
            "n_3body":sum(m["multiplicity"]==3 for m in modes),
            "modes":modes}


def validate_case_outcomes(name,original_values,two_path,full_path,case,f17e_case,charge):
    masses1,first,_=check_MadWidth_input_preserved(two_path,original_values)
    masses2,final,_=check_MadWidth_input_preserved(full_path,original_values)
    for pid in SCALARS:
        for masses in (masses1,masses2):
            if pid not in masses or not math.isclose(masses[pid],original_values[("MASS",(pid,))],
                    rel_tol=1e-9,abs_tol=1e-8):
                raise ValueError("MadWidth changed physical scalar mass "+str(pid))
        validate_table(first,pid,three_body=False)
        validate_table(final,pid,three_body=True)
    # W is internal in the UFO but explicitly required by MadWidth's
    # LHE mass reader. It must survive both numeric integration passes.
    expected_W=original_values[("MASS",(23,))]*math.sqrt(1.0-S2W_F16)
    for label,observed in (("2body",masses1),("2plus3body",masses2)):
        if 24 not in observed or not math.isclose(
                observed[24],expected_W,rel_tol=2e-7,abs_tol=1e-7):
            raise ValueError("MadWidth lost/mutated derived MASS 24 "+label+
                             " "+str(observed.get(24)))
    consistency=ensure_consistent_2body_stage(first,final)
    source_matched_two=check_two_body_against_f17f(case,f17e_case,first,charge)
    source_matched_full=check_two_body_against_f17f(case,f17e_case,final,charge)
    charged={str(pid):summarize_decay_parent(first,final,pid) for pid in CHARGED}
    z,zm=mode_width(final[9000037],[37,23])
    tb_daughters=(-6,5) if charge<0 else (6,-5)
    tb,tm=mode_width(final[37],tb_daughters)
    br_z=z/final[9000037]["width_GeV"]
    br_tb=tb/final[37]["width_GeV"]
    result={"candidate_id":name,
        "source_amplitude_validation_two_only":source_matched_two,
        "source_amplitude_validation_two_plus_three":source_matched_full,
        "charged_H_mother_field_charge":charge,
        "max_2body_stability_relative":consistency,
        "all_five_scalar_decay_totals_GeV":{str(p):final[p]["width_GeV"] for p in SCALARS},
        "charged_H_decay_tables":charged,
        "BR_H2_H1_Z_model_LO_2plus3":br_z,
        "BR_H1_tb_model_LO_2plus3":br_tb,
        "cascade_BR_product_model_LO_2plus3":br_z*br_tb,
        "H2_doublet_weight_sin2gamma":case["H2_doublet_weight_sin2gamma"] if
              "H2_doublet_weight_sin2gamma" in case else None,
        "three_body_on_shell_cascade_subtraction_handled_by_MadWidth_NWA_not_independently_proven":True,
        "QCD_and_loop_corrected":False,
        "model_fully_allowed":False}
    if not 0<br_z<=1 or not 0<br_tb<=1:
        raise ValueError("Nonphysical MadWidth branching ratios "+name)
    return result


def f14_source_rows(path,original):
    """Optional, clearly labelled 13 TeV Type-II baseline from original F14."""
    if path is None:return None,None
    with Path(path).open(newline="") as fp:
        rows=list(csv.DictReader(fp))
    byid={}
    for r in rows:
        key=r.get("candidate_id")
        if key in TGT:
            if key in byid:raise ValueError("Duplicate F14 candidate "+key)
            if abs(float(r["mH2_GeV"])-float(original[key]["scalar"]["mH2"]))>1e-7:
                raise ValueError("F14/F16 source mH2 incompatible "+key)
            if abs(float(r["tanbeta"])-math.tan(original[key]["scalar"]["beta"]))>3e-7:
                raise ValueError("F14/F16 source tanbeta incompatible "+key)
            sigma=float(r["TypeII_Santander_NLO13TeV_sigma_pb"])
            if not math.isfinite(sigma) or sigma<=0:raise ValueError("Invalid F14 cross section")
            byid[key]=sigma
    if set(byid)!=set(TGT):raise ValueError("F14 missing F13 priority trio")
    return byid,hashfile(path)


def choose_mg5(value):
    if value:
        candidate=Path(value).expanduser().resolve()
        if candidate.is_file() and os.access(candidate,os.X_OK):return candidate
        raise ValueError("MG5 executable not found/executable "+str(candidate))
    names=[
        os.environ.get("ZEE_MG5_BIN",""),
        str(Path.home()/"MG5_aMC/bin/mg5_aMC"),
        str(Path.home()/"mg5/bin/mg5_aMC"),
    ] + [str(x) for pattern in ("MG5_aMC_v*/bin/mg5_aMC",
                                "MG5_aMC*/bin/mg5_aMC",
                                "MadGraph*/bin/mg5_aMC")
         for x in sorted(Path.home().glob(pattern),reverse=True)]
    for name in names:
        if name and Path(name).is_file() and os.access(name,os.X_OK):
            return Path(name).resolve()
    raise ValueError("Set --mg5-bin /absolute/path/to/MG5_aMC/bin/mg5_aMC")


def command_deck(ufo,card,output,*,body_decay,nb_core=None):
    if body_decay not in (2,3):raise ValueError("Only 2 and 3 body stages")
    if nb_core is not None and (type(nb_core)!=int or not 1<=nb_core<=64):
        raise ValueError("Invalid MadGraph requested core count")
    # Running MadGraph inside an HTCondor job: cap the child madevent
    # workers at the exact number of cores requested from HTCondor.
    # Never trigger nested MG5 cluster submission inside a worker.
    settings=("set auto_update 0\n"
              "set automatic_html_opening False\n"
              + ("set run_mode 2\nset nb_core "+str(nb_core)+"\n"
                 if nb_core is not None else ""))
    # Absolute paths and a new output path keep immutable source unchanged.
    return (settings
            "import model "+str(ufo)+"\n"
            "compute_widths "+" ".join(str(i) for i in SCALARS)+
            " --path="+str(card)+" --output="+str(output)+
            " --body_decay="+str(body_decay)+
            " --min_br="+MIN_BR+" --precision_channel="+PRECISION_CHANNEL+"\n")


def madwidth_log_diagnostic(log,job_dir,output,returncode=None):
    """Diagnose errors MG5 may log while returning shell exit code zero.

    Keep source material, missing requested --output, candidate extra cards,
    debug files, and nearby log context. Do not silently substitute a model
    default card for a requested output file.
    """
    text=Path(log).read_text(errors="replace") if Path(log).exists() else ""
    lines=text.splitlines()
    import re
    pattern=re.compile(
        r"(?i)(?:^\s*(?:ERROR|CRITICAL)\s*[: ]|Traceback \(most recent|"
        r"madgraph5error|invalidcmd|No module named|file not found|"
        r"unrecognized command|not valid options|invalid syntax|"
        r"cannot import model|no such file or directory)")
    interesting=[i for i,line in enumerate(lines) if pattern.search(line)]
    contexts=[]
    for i in interesting[-12:]:
        contexts.append({"log_line":i+1,"context":"\n".join(
            lines[max(0,i-2):min(len(lines),i+9)])[:2500]})
    nearby_cards=[]
    for folder in (Path(job_dir),Path(output).parent):
        if folder.exists():
            for pattern_name in ("*.slha","param_card*.dat","MG5_debug*"):
                for item in folder.rglob(pattern_name):
                    if item.is_file() and len(nearby_cards)<60:
                        nearby_cards.append({"path":str(item),
                                             "size":item.stat().st_size})
    diagnostic={
        "returncode":returncode,
        "expected_output":str(output),
        "expected_output_exists":Path(output).exists(),
        "log":str(log),
        "log_size":len(text),
        "log_error_contexts":contexts,
        "log_last_65_lines":"\n".join(lines[-65:])[-10000:],
        "nearby_candidate_cards_and_debug_files":nearby_cards,
    }
    return diagnostic


def do_madwidth(mg5,ufo,card,output,job_dir,stage,*,nb_core=None):
    job_dir.mkdir(parents=True,exist_ok=False)
    deck=job_dir/"compute_widths.mg5"
    deck.write_text(command_deck(ufo,card,output,body_decay=stage,nb_core=nb_core))
    log=job_dir/"madwidth.log"
    input_hash_before=hashfile(card)
    print("F18_MG5_START",stage,"CARD",card,"OUTPUT",output,flush=True)
    with log.open("w") as stream:
        process=subprocess.run([str(mg5),str(deck)],cwd=job_dir,stdout=stream,
                               stderr=subprocess.STDOUT,check=False)
    diagnostic=madwidth_log_diagnostic(log,job_dir,output,process.returncode)
    diagnostic_path=job_dir/"mg5_diagnostic.json"
    diagnostic_path.write_text(json.dumps(diagnostic,indent=2,sort_keys=True)+"\n")
    evidence={"returncode":process.returncode,"command":str(deck),
              "command_SHA256":hashfile(deck),"log":str(log),
              "log_SHA256":hashfile(log),"output":str(output),
              "source_input_SHA256":input_hash_before,
              "diagnostic":str(diagnostic_path)}
    if hashfile(card)!=input_hash_before:
        raise RuntimeError("MG5 modified immutable original input card; "
                           "quarantine this failed run and original source "
                           +str(evidence))
    if process.returncode or not output.is_file() or output.stat().st_size<250:
        for issue in diagnostic["log_error_contexts"][-4:]:
            print("F18_MG5_LOG_ERROR",stage,"LINE",issue["log_line"],
                  issue["context"][-1600:],flush=True)
        print("F18_MG5_LOG_TAIL",stage,diagnostic["log_last_65_lines"][-4000:],
              flush=True)
        print("F18_MG5_CANDIDATE_FILES",
              diagnostic["nearby_candidate_cards_and_debug_files"][:20],
              flush=True)
        raise RuntimeError("MG5 MadWidth "+str(stage)+"-body produced no "
            "valid requested output (MG5 returncode="+str(process.returncode)+
            "). See diagnostic JSON and actual MG5 log: "+str(evidence))
    evidence["output_SHA256"]=hashfile(output)
    return evidence


def diagnose_existing_campaign(folder):
    """Print archived F18 job failures without rerunning expensive MG5."""
    folder=Path(folder).expanduser().resolve()
    if not folder.is_dir():raise ValueError("Missing F18 campaign "+str(folder))
    for candidate in sorted(folder.glob("F13_heavy_*")):
        for stage in ("stage_2body","stage_2plus3body"):
            job=candidate/stage
            log=job/"madwidth.log"
            if not log.is_file():continue
            output=(candidate/("two_body.slha" if stage=="stage_2body"
                               else "two_plus_three_body.slha"))
            details=madwidth_log_diagnostic(log,job,output)
            print("F18_DIAGNOSE",candidate.name,stage,
                  "EXPECTED_OUTPUT_EXISTS",details["expected_output_exists"],
                  "LOG_SIZE",details["log_size"])
            for item in details["log_error_contexts"][-4:]:
                print("F18_DIAGNOSTIC_LOG_ERROR_LINE",item["log_line"],
                      item["context"])
            print("F18_DIAGNOSTIC_LOG_LAST_LINES",
                  "\n".join(details["log_last_65_lines"].splitlines()[-35:]))
            print("F18_DIAGNOSTIC_CANDIDATE_FILES",
                  details["nearby_candidate_cards_and_debug_files"][:12])
    print("F18_DIAGNOSIS_ONLY_NO_MG5_EXECUTION",folder)


def preflight(f16_dir,f17d_dir,f17e_file,f17f_dir):
    src=Path(f16_dir).resolve();ufo=src/UFO_SUBDIR
    f17=verify_json(src/SOURCE_COMPLEX)
    original=json.loads((src/"F16_three_exact_F13_Zee_input_reconstruction.json").read_text())
    consistency(original,f17)
    f17d=json.loads((Path(f17d_dir)/"summary.json").read_text())
    f17e=json.loads(Path(f17e_file).read_text())
    f17f_path=Path(f17f_dir)/"report.json"
    f17f=json.loads(f17f_path.read_text())
    if (f17e.get("Z_scalar_tb_amplitude_gate_3_of_3") is not True or
        f17f.get("CKM_numerical_3_of_3") is not True or
        f17f.get("full_complex_lepton_physical_widths_validated") is not True or
        f17f.get("complete_2_and_3_body_MadWidth_ready") is not False):
        raise ValueError("F17e/F17f actual UFO physical fermion gate not passed")
    if (f17f.get("source_F17e_SHA256")!=hashfile(f17e_file) or
        f17f.get("source_F17d_SHA256")!=hashfile(Path(f17d_dir)/"summary.json")):
        raise ValueError("F17d/e/f source integrity mismatch")
    for filename,key in (("parameters.py","UFO_parameters_SHA256"),
                         ("couplings.py","UFO_couplings_SHA256"),
                         ("vertices.py","UFO_vertices_SHA256")):
        if hashfile(ufo/filename)!=f17e[key]:
            raise ValueError("Original generated SARAH UFO changed: "+filename)
    params=parse_objects(ufo,"parameters.py","Parameter")
    slots=slots_from_real_ufo(params)
    entries=f17f.get("CKM_candidate_cards")
    cases=f17f.get("cases")
    originals=f17e.get("three_original_UFO_numerical_amplitude_results")
    if (not isinstance(entries,list) or not isinstance(cases,list)
        or not isinstance(originals,list) or len(entries)!=3 or len(cases)!=3 or len(originals)!=3
        or {r["candidate_id"] for r in entries}!=set(TGT)
        or {r["candidate_id"] for r in cases}!=set(TGT)
        or {r["candidate_id"] for r in originals}!=set(TGT)):
        raise ValueError("F17e/f cohort mismatch")
    mapping={}
    for entry in entries:
        name=entry["candidate_id"]
        card=Path(f17f_dir)/entry["file"]
        values=check_original_card(card,slots,entry)
        ref=next(c for c in cases if c["candidate_id"]==name)
        if not ref.get("all_quark_9x2_modes_passed") or not ref.get("complex_lepton_full_width_gate_passed"):
            raise ValueError("Physical F17f quark/lepton gate not passed "+name)
        if ref.get("original_F17d_card_SHA256") not in [x["sha256"] for x in f17d["candidate_cards"] if x["id"]==name]:
            raise ValueError("F17f card not tied to original F17d "+name)
        f17e_case=next(c for c in originals if c["candidate_id"]==name)
        mapping[name]={"card":card,"values":values,"f17f":ref,"f17e":f17e_case}
    return src,ufo,original,f17f_path,mapping


def run(args):
    src,ufo,original,f17f_report,points=preflight(args.f16_dir,args.f17d_dir,
                                                     args.f17e_report,args.f17f_dir)
    mg5=choose_mg5(args.mg5_bin)
    f14, f14_sha=f14_source_rows(args.f14_csv,original)
    if f14_sha is not None:
        f16_summary=json.loads((src/"summary.json").read_text())
        pinned=f16_summary.get("source",{}).get("F14_8_csv_SHA256")
        if not pinned or f14_sha!=pinned:
            raise ValueError("F14 13 TeV production CSV SHA256 not pinned to original F16 source")
    out=Path(args.output).expanduser().resolve()
    if out.exists():raise FileExistsError("Never overwrite a historical MadWidth campaign "+str(out))
    charge=charged_field_sign(ufo)
    out.mkdir(parents=True,exist_ok=False)
    manifest={"status":STATUS,"MG5_binary":str(mg5),"MG5_binary_SHA256":hashfile(mg5),
        "original_F16_dir":str(src),"original_SARAH_UFO":str(ufo),
        "original_F17f_report_SHA256":hashfile(f17f_report),
        "F14_original_13TeV_CSV_SHA256":f14_sha,
        "charged_scalar_field_charge_for_positive_PDG":charge,
        "MadWidth_NWA_on_shell_decay_filter":True,
        "MadWidth_min_br":float(MIN_BR),"MadWidth_precision_channel":float(PRECISION_CHANNEL),
        "source_independent_CKM_and_lepton_amplitudes_validated_before_run":True,
        "full_BSM_precision_QCD_loops_flavor_Higgs_constraints":False,
        "results":[],"errors":{}}
    (out/"initial_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    requested=(args.only_case,) if args.only_case else TGT
    manifest["requested_cases"]=list(requested)
    manifest["nb_core_per_job"]=args.nb_core
    for name in requested:
        point=points[name]
        work=out/name
        work.mkdir(exist_ok=False)
        steps={}
        try:
            card=point["card"]
            auxiliary=work/"F18_MadWidth_input_with_derived_MW.slha"
            steps["W_mass_card"]=prepare_madwidth_W_mass_card(
                card,auxiliary,ufo,point["values"])
            two=work/"two_body.slha";combined=work/"two_plus_three_body.slha"
            steps["two_body"]=do_madwidth(
                mg5,ufo,auxiliary,two,work/"stage_2body",2,nb_core=args.nb_core)
            # Fail closed if MG5 drops W mass before attempting 3-body.
            mass_from_2body,_,_=check_MadWidth_input_preserved(
                two,point["values"])
            if 24 not in mass_from_2body or not math.isclose(
                mass_from_2body[24],
                steps["W_mass_card"]["derived_internal_MWm_GeV"],
                rel_tol=2e-7,abs_tol=1e-7):
                raise ValueError("MG5 stage-2 output omitted derived W MASS 24; "+
                                 "do not launch 3-body stage")
            steps["two_plus_three_body"]=do_madwidth(
                mg5,ufo,two,combined,work/"stage_2plus3body",3,nb_core=args.nb_core)
            result=validate_case_outcomes(name,point["values"],two,combined,
                                          point["f17f"],point["f17e"],charge)
            result["provenance"]={"source_F17f_card_SHA256":hashfile(card),
                    "MadWidth_two_body":steps["two_body"],
                    "MadWidth_two_plus_three":steps["two_plus_three_body"]}
            if f14 is not None:
                # Baseline production is Type-II doublet 13TeV, rescaled
                # exactly once by H2 physical charged-doublet weight.
                spec=original[name]["scalar"]
                gamma=float(spec["gamma"])
                weight=math.sin(gamma)**2
                sigma=f14[name]
                result["13TeV_source_F14_LO_widths_cascade"]={
                    "TypeII_Santander_NLO13TeV_sigma_pb":sigma,
                    "H2_doublet_weight":weight,
                    "sigma_times_BR_H2_H1Z_BR_H1_tb_pb":
                        sigma*weight*result["cascade_BR_product_model_LO_2plus3"],
                    "sigma_times_BR_to_Z_ee_mumu_pb_approx":
                        sigma*weight*result["cascade_BR_product_model_LO_2plus3"]*.0673,
                    "NOT_a_14TeV_prediction":True}
            manifest["results"].append(result)
            (work/"validated_model_LO_widths.json").write_text(
                json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
            print("F18_BENCHMARK_PASS",name,
                  "GAMMA_H2_GEV",result["charged_H_decay_tables"]["9000037"]["total_GeV"],
                  "GAMMA_H1_GEV",result["charged_H_decay_tables"]["37"]["total_GeV"],
                  "BR_H2_H1Z",result["BR_H2_H1_Z_model_LO_2plus3"],
                  "BR_H1_TB",result["BR_H1_tb_model_LO_2plus3"],
                  "BR_PRODUCT",result["cascade_BR_product_model_LO_2plus3"],
                  flush=True)
        except Exception as exc:
            manifest["errors"][name]={"error_type":type(exc).__name__,
                                      "message":str(exc),"completed_steps":steps}
            print("F18_BENCHMARK_FAIL",name,type(exc).__name__,str(exc),flush=True)
            if not args.continue_after_failure:break
    manifest["requested_cases_passed"]=(
        len(manifest["results"])==len(requested) and not manifest["errors"])
    manifest["all_three_validated"]=(
        len(requested)==3 and manifest["requested_cases_passed"])
    manifest["complete_tree_two_plus_three_body_channels_up_to_MadWidth_precision"] = manifest["all_three_validated"]
    manifest["full_physical_precision_model_allowed"]=False
    (out/"summary.json").write_text(json.dumps(
        manifest,indent=2,sort_keys=True,allow_nan=False)+"\n")
    # A compact comparison table accompanies the full per-channel JSON.
    if manifest["results"]:
        table=out/"three_benchmarks_summary.csv"
        with table.open("w",newline="") as stream:
            columns=("candidate_id","Gamma_H2_GeV","Gamma_H1_GeV",
                     "H2_three_body_fraction","H1_three_body_fraction",
                     "BR_H2_H1Z","BR_H1_tb","BR_product",
                     "sigma13_cascade_pb_if_original_F14_available")
            writer=csv.DictWriter(stream,fieldnames=columns)
            writer.writeheader()
            for item in manifest["results"]:
                states=item["charged_H_decay_tables"]
                rate=item.get("13TeV_source_F14_LO_widths_cascade",{})
                writer.writerow(dict(
                    candidate_id=item["candidate_id"],
                    Gamma_H2_GeV=states["9000037"]["total_GeV"],
                    Gamma_H1_GeV=states["37"]["total_GeV"],
                    H2_three_body_fraction=states["9000037"]["three_body_fraction"],
                    H1_three_body_fraction=states["37"]["three_body_fraction"],
                    BR_H2_H1Z=item["BR_H2_H1_Z_model_LO_2plus3"],
                    BR_H1_tb=item["BR_H1_tb_model_LO_2plus3"],
                    BR_product=item["cascade_BR_product_model_LO_2plus3"],
                    sigma13_cascade_pb_if_original_F14_available=
                        rate.get("sigma_times_BR_H2_H1Z_BR_H1_tb_pb","")))
        print("F18_COMPARISON_CSV",table,flush=True)
    print("F18_STATUS",STATUS,"REQUESTED_CASES_PASS",manifest["requested_cases_passed"],
          "THREE_CASES_PASS",manifest["all_three_validated"],
          "TOTAL_RESULTS",len(manifest["results"]),"ERRORS",len(manifest["errors"]),
          "PRECISION_QCD",False,"ALLOWED",False,flush=True)
    print("F18_REPORT",out/"summary.json",flush=True)
    if not manifest["requested_cases_passed"]:raise SystemExit(2)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--diagnose-campaign",type=Path,
                   help="Inspect existing MG5 logs without launching any computation")
    p.add_argument("--f16-dir",type=Path)
    p.add_argument("--f17d-dir",type=Path)
    p.add_argument("--f17e-report",type=Path)
    p.add_argument("--f17f-dir",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--mg5-bin",type=Path)
    p.add_argument("--f14-csv",type=Path,help="Original F14 13 TeV CSV (optional, source validated)")
    p.add_argument("--continue-after-failure",action="store_true")
    p.add_argument("--only-case",choices=TGT,help="Run exactly one of the three source-verified benchmarks; intended for HTCondor job splitting")
    p.add_argument("--nb-core",type=int,help="Limit MadGraph worker cores to the HTCondor request_cpus value")
    a=p.parse_args()
    if a.nb_core is not None and not 1<=a.nb_core<=64:
        p.error("--nb-core must be 1..64")
    if a.diagnose_campaign:
        diagnose_existing_campaign(a.diagnose_campaign)
        return
    missing=[name for name in ("f16_dir","f17d_dir","f17e_report",
                              "f17f_dir","output") if getattr(a,name) is None]
    if missing:p.error("MG5 execution requires "+", ".join(missing))
    run(a)


if __name__=="__main__":main()

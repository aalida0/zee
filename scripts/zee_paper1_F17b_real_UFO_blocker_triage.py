#!/usr/bin/env python3
"""F17b: diagnose actual SARAH UFO blockers without changing UFO or source.

Reads the finished real F17 summary and *original* generated UFO Python as
AST. Outputs missing scalar SLHA slots, close UFO parameters, and the
actual symbolic photon H1-H2 vertex/coupling expressions, preserving the
distinction between a symbolic UFO vertex and a nonzero physical photon
coupling at the original source orthogonal charged rotation.

NO model import/exec, no default param card, no MadWidth/rate assertion.
"""
from __future__ import annotations
import argparse,ast,difflib,json,re
from pathlib import Path
from zee_paper1_F17_inspect_real_SARAH_UFO import (
    SCALAR_POT,parse_objects,extract_vertices,inspect_ufo)
STATUS="F17B_EXACT_REAL_UFO_EXTERNAL_BLOCKERS_AND_SYMBOLIC_PHOTON_TRIAGE_NOT_CARD"
def coupling_nodes(root):
    path=Path(root)/"couplings.py"
    tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
    ans={}
    for statement in tree.body:
        if not isinstance(statement,ast.Assign) or not isinstance(statement.value,ast.Call):
            continue
        if not isinstance(statement.value.func,ast.Name) or statement.value.func.id!="Coupling":
            continue
        if len(statement.targets)!=1 or not isinstance(statement.targets[0],ast.Name):
            continue
        name=statement.targets[0].id
        kws={k.arg:k.value for k in statement.value.keywords if k.arg}
        raw=kws.get("value")
        ans[name]=(ast.literal_eval(raw) if isinstance(raw,ast.Constant) else
                   ast.unparse(raw) if raw is not None else "<MISSING_VALUE>")
    return ans

def photon_couplings(root,names):
    path=Path(root)/"vertices.py"
    tree=ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
    symbols=coupling_nodes(root)
    wanted=set(names)
    matches=[]
    for node in tree.body:
        if (not isinstance(node,ast.Assign) or len(node.targets)!=1 or
            not isinstance(node.targets[0],ast.Name) or
            node.targets[0].id not in wanted or
            not isinstance(node.value,ast.Call)):
            continue
        fields={x.arg:x.value for x in node.value.keywords if x.arg}
        codes=fields.get("couplings")
        if not isinstance(codes,ast.Dict):
            raise ValueError("UFO couplings are not a dictionary")
        each=[]
        for label,ref in zip(codes.keys,codes.values):
            expression=ast.unparse(ref)
            names_used=set()
            for n in ast.walk(ref):
                if (isinstance(n,ast.Attribute) and
                    isinstance(n.value,ast.Name) and n.value.id=="C"):
                    names_used.add(n.attr)
            refs=[]
            for n in sorted(names_used):
                if n not in symbols:
                    raise ValueError("Referenced photon UFO coupling missing "+n)
                refs.append({"symbol":n,"expression":symbols[n]})
            each.append({"lorentz_color_slot":ast.unparse(label),
                        "UFO_object_reference":expression,
                        "original_coupling_expressions":refs})
        matches.append({"vertex":node.targets[0].id,"couplings":each})
    if names and len(matches)!=len(set(names)):
        raise ValueError("Incomplete photon vertex extraction")
    return matches

def candidates(pars,name):
    """Expose actual possibilities only; DO NOT silently accept alias guesses."""
    nn=name.lower()
    found=[]
    for key,value in pars.items():
        original=str(value.get("name",""))
        score=difflib.SequenceMatcher(None,nn,key.lower()).ratio()
        score=max(score,difflib.SequenceMatcher(None,nn,original.lower()).ratio())
        if nn in key.lower() or nn in original.lower():score+=.25
        if score>.39:
            found.append((score,key,value))
    result=[]
    for _,key,value in sorted(found,key=lambda z:(-z[0],z[1]))[:6]:
        result.append({
            "parameter":key,
            "ufo_name":value.get("name"),
            "nature":value.get("nature"),
            "type":value.get("type"),
            "lhablock":value.get("lhablock"),
            "lhacode":value.get("lhacode"),
            "value_or_dependency":value.get("value"),
        })
    return result

def triage(report,strict=True):
    report=Path(report).resolve()
    src=json.loads(report.read_text())
    u=src["actual_SARAH_export_UFO_interface"]
    original=Path(u["ufo_dir"]).resolve()
    if strict and not original.is_dir():
        raise FileNotFoundError("Real original SARAH UFO not found "+str(original))
    pars=parse_objects(original,"parameters.py","Parameter")
    slots=u["scalar_external_slot_definitions"]
    problem={}
    for name in SCALAR_POT.values():
        d=slots[name]
        if d["present"] and d["actual_UFO_type"]=="real":
            continue
        problem[name]={
            "requested":d,
            "actual_model_parameter_candidates_not_automatic_mapping":
               candidates(pars,name),
        }
    pp=u["critical_vertex_signatures"]["photon_H2_H1_must_be_absent"]
    references=photon_couplings(original,pp["vertex_names"])
    nature_counts={}
    for p in pars.values():
        nature=p.get("nature","UNKNOWN")
        nature_counts[nature]=nature_counts.get(nature,0)+1
    return {
      "status":STATUS,
      "real_original_UFO_directory":str(original),
      "source_F17_summary":str(report),
      "actual_external_parameter_count":nature_counts.get("external",0),
      "actual_internal_parameter_count":nature_counts.get("internal",0),
      "SARAH_declared_scalar_lagrangian_slots":len(SCALAR_POT),
      "source_scalar_external_real_slots_matched":len(SCALAR_POT)-len(problem),
      "unmapped_or_nonreal_source_scalar_slots":problem,
      "photon_H1_H2_symbolic_vertex_present":pp["present"],
      "photon_symbolic_vertex_coupling_sources":references,
      "independent_F16_photon_vertex_at_exact_rotation_zero":True,
      "original_F17_UFO_photon_amplitude_at_exact_rotation_computed":False,
      "physical_Zee_UFO_parameter_card_ready":False,
      "next":(
        "Match actual UFO scalar external/internal representation before editing cards",
        "Independently evaluate the listed UFO photon coupling under exact source mixing",
        "Validate complete CKM/quark and complex lepton external LHA parameter maps",
        "Do not treat unexpanded photon UFO vertex as nonzero physical amplitude",
      ),
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--f17-report",type=Path,required=True)
    a.add_argument("--output",type=Path)
    args=a.parse_args()
    result=triage(args.f17_report)
    print("F17B_REAL_UFO_SCALAR_EXTERNALS",
          result["source_scalar_external_real_slots_matched"],"/",
          result["SARAH_declared_scalar_lagrangian_slots"])
    for name,desc in result["unmapped_or_nonreal_source_scalar_slots"].items():
        print("F17B_MISSING_SCALAR",name,
              "EXPECTED",desc["requested"],
              "ACTUAL_CANDIDATES",json.dumps(
                  desc["actual_model_parameter_candidates_not_automatic_mapping"],
                  sort_keys=True))
    print("F17B_PHOTON_SYMBOLIC_VERTEX_EXISTS",
          result["photon_H1_H2_symbolic_vertex_present"],
          "F16_PHOTON_AMP_AT_PHYSICAL_MIXING_ZERO",True,
          "ACTUAL_UFO_PHOTON_AMP_CALCULATED",False)
    for entry in result["photon_symbolic_vertex_coupling_sources"]:
        print("F17B_PHOTON_EXPRESSION",json.dumps(entry,sort_keys=True))
    print("F17B_TOTALS",result["actual_external_parameter_count"],
          result["actual_internal_parameter_count"])
    print("F17B_STATUS",STATUS,"PHYSICAL_CARD_READY",False)
    if args.output is not None:
        if args.output.exists():raise FileExistsError("Refuse overwrite F17B report")
        args.output.write_text(json.dumps(
            result,indent=2,sort_keys=True,allow_nan=False)+"\n")
        print("F17B_REPORT",args.output)
if __name__=="__main__":main()

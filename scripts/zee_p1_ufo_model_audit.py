#!/usr/bin/env python3
"""Strict static (never execute model) Zee UFO physics-readiness audit.

Checks required two charged, three neutral scalar IDs, *actual* vertices
not just particle names: offdiagonal Z(H1,H2), charged tb(H1,2),
neutral Higgs charged pair and charged W neutral gauge couplings.
Requires 12 split-complex external f/Y parameter pairs, not merely
FeynRules internally complex symbols. An original real-only Yang/Wu
UFO is **not compatible** with general E3 optimized complex Y/f.
No model is certified mapped to Florentino scalar masses/trilinears,
no Ward identity or MadWidth has been run.
"""
from __future__ import annotations
import argparse,ast,hashlib,json
from pathlib import Path

STATUS="P1_ZEE_UFO_STATIC_INTERFACE_AUDIT_NO_PHYSICS_MATCH_CERTIFIED"
PDG={"h":25,"H":225,"A":226,"H2":227,"H1":228}
F=("fem","fet","fmt")
Y=("ylzee","ylzem","ylzet","ylzme","ylzmm",
   "ylzmt","ylzte","ylztm","ylztt")
FLAVOR_BLOCKS={"ZEEFR":F,"ZEEFI":F,"ZEEYR":Y,"ZEEYI":Y}

def astdata(node):
 if isinstance(node,ast.Constant):
  return node.value
 if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
  return -astdata(node.operand)
 if isinstance(node,(ast.List,ast.Tuple)):
  return [astdata(x) for x in node.elts]
 if isinstance(node,ast.Name):
  return node.id
 if isinstance(node,ast.Attribute):
  return ast.unparse(node)
 raise ValueError("Unexpected python AST in UFO external field")

def defs(path,kind):
 tree=ast.parse(Path(path).read_text(),filename=str(path))
 out={};aliases=[]
 for node in tree.body:
  if not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name):
   continue
  label=node.targets[0].id;expr=node.value
  if isinstance(expr,ast.Call) and isinstance(expr.func,ast.Name) and expr.func.id==kind:
   row={p.arg:astdata(p.value) for p in expr.keywords if p.arg}
   if label in out:raise ValueError("Duplicate UFO "+kind+" "+label)
   out[label]=row
  elif (kind=="Particle" and isinstance(expr,ast.Call) and
        isinstance(expr.func,ast.Attribute) and expr.func.attr=="anti" and
        isinstance(expr.func.value,ast.Name)):
   aliases.append((label,expr.func.value.id))
 if kind=="Particle":
  for alias,parent in aliases:
   if parent not in out:
    raise ValueError("UFO anti-particle target missing "+parent)
   row=dict(out[parent])
   row["pdg_code"]=-row["pdg_code"]
   row["name"]=row.get("antiname",alias)
   out[alias]=row
 return out

def particle_refs(path,particles):
 tree=ast.parse(Path(path).read_text(),filename=str(path))
 vertices=[]
 for node in tree.body:
  if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.Call):
   continue
  call=node.value
  if not isinstance(call.func,ast.Name) or call.func.id!="Vertex":
   continue
  kws={z.arg:z.value for z in call.keywords if z.arg}
  obj=kws.get("particles")
  if not isinstance(obj,(ast.List,ast.Tuple)):
   raise ValueError("UFO Vertex missing particles list")
  pdgs=[]
  for part in obj.elts:
   if not isinstance(part,ast.Attribute) or not isinstance(part.value,ast.Name) or part.value.id!="P":
    raise ValueError("Unsupported UFO particle vertex element")
   name=part.attr
   if name not in particles:
    raise ValueError("Unmapped UFO particle "+name)
   pdgs.append(int(particles[name]["pdg_code"]))
  vertices.append(tuple(pdgs))
 return vertices

def sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(root):
 root=Path(root).resolve()
 files=("parameters.py","particles.py","vertices.py","couplings.py","lorentz.py")
 if not root.is_dir() or any(not(root/f).is_file() for f in files):
  raise ValueError("Require actual complete extracted UFO directory")
 pars=defs(root/"parameters.py","Parameter")
 parts=defs(root/"particles.py","Particle")
 verts=particle_refs(root/"vertices.py",parts)
 active=set(abs(int(row["pdg_code"])) for row in parts.values())
 species={name:pdg in active for name,pdg in PDG.items()}
 keys={}
 for tag,pdg in PDG.items():
  matching=[name for name,dat in parts.items() if int(dat["pdg_code"])==pdg]
  keys[tag]=matching
 def match(*wanted):
  wanted=set(wanted)
  return any(wanted.issubset(set(abs(q) for q in v)) for v in verts)
 def offdiagZ():
  return any(len(v)==3 and set(abs(q) for q in v)=={23,227,228}
             and sum(1 for q in v if abs(q)==227)==1 and
             sum(1 for q in v if abs(q)==228)==1
             for v in verts)
 def tb(charged):
  return match(5,6,charged)
 def gauge(charged):
  return all(any(set([24,charged,neut]).issubset(set(abs(q) for q in v))
        for v in verts) for neut in (25,225,226))
 blocks={}
 for block,items in FLAVOR_BLOCKS.items():
  symbols={}
  for name,par in pars.items():
   if par.get("nature")!="external" or par.get("lhablock")!=block:
    continue
   code=par.get("lhacode")
   if not isinstance(code,list) or len(code)!=1:
    raise ValueError("UFO flavor input has non-single LHACODE "+name)
   if par.get("type")!="real":
    raise ValueError("UFO split flavor external is not real "+name)
   key=int(code[0])
   if key in symbols:raise ValueError("Duplicate LHACODE "+block)
   symbols[key]=name
  expected={i+1 for i in range(len(items))}
  blocks[block]={"code_to_parameter":symbols,
    "all_codes_present_once":set(symbols)==expected}
  for code,name in symbols.items():
   expect=("R" if block.endswith("R") else "I")+items[code-1]
   if name!=expect:
    blocks[block]["all_codes_present_once"]=False
 if species["H1"] and species["H2"]:
  kappa={"Z_H1_H2_three_point":offdiagZ(),
         "tb_H1_three_point":tb(228),
         "tb_H2_three_point":tb(227),
         "H1_neutral_W_25_225_226":gauge(228),
         "H2_neutral_W_25_225_226":gauge(227),
         "H_neutral_to_H1_H1":match(225,228),
         "H_neutral_to_H2_H2":match(225,227)}
 else:
  kappa={x:False for x in ("Z_H1_H2_three_point","tb_H1_three_point",
              "tb_H2_three_point","H1_neutral_W_25_225_226",
              "H2_neutral_W_25_225_226","H_neutral_to_H1_H1",
              "H_neutral_to_H2_H2")}
 real_only=any(p.get("nature")=="external" and p.get("lhablock") in (
   "ZEEYUKAF","ZEEYUKAWAF","ZEEYUKAWAY") for p in pars.values())
 flavor_ok=(all(z["all_codes_present_once"] for z in blocks.values()) and not real_only)
 essential=all(species.values()) and all(kappa.values()) and flavor_ok
 return {
  "status":STATUS,
  "UFO_root":str(root),
  "source_SHA256":{p:sha(root/p) for p in files},
  "physical_particles_present":species,
  "physical_particle_UFO_symbols":keys,
  "number_of_vertices":len(verts),
  "necessary_vertices_present":kappa,
  "split_complex_12_flavor_inputs":{
    "all_24_real_and_imaginary_entries_present":flavor_ok,
    "blocks":blocks,
    "unpatched_real_only_flavor_inputs_detected":real_only},
  "static_necessary_conditions_pass":essential,
  "full_scalar_potential_basis_matched_to_E2_E3":False,
  "complex_Yukawa_normalization_matched_to_E3":False,
  "Ward_and_MadWidth_crosscode_amplitudes_validated":False,
  "NNLO_and_complete_LFV_calculated":False,
  "valid_Zee_MadWidth_309_input_ready":False,
  "complete_global_Zee_allowed_excluded":None,
  "required_next":[
    "fresh FeynRules TypeII + complex-fY LO UFO export",
    "numerical source field rotation/potential and complex Y normalization checks",
    "complete missing amplitude tests with gauge/Ward identities",
    "automated MadWidth two/three-body validated parameter cards",
    "higher-order Higgs corrections and full collider production"],
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--ufo",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 if a.out.exists():p.error("Output exists; refuse overwrite")
 report=audit(a.ufo)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print("P1_ZEE_UFO_AUDIT",report["status"],
       "STATIC_SOURCE_PASS",report["static_necessary_conditions_pass"],
       "FLAVOR_24_ENTRIES",report["split_complex_12_flavor_inputs"][
            "all_24_real_and_imaginary_entries_present"],
       "FLOR_BASIS_MATCHED",False,"MADWIDTH_READY",False)
 print("P1_ZEE_UFO_REPORT",a.out)
if __name__=="__main__":main()

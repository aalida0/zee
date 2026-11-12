#!/usr/bin/env python3
"""Exact-source portable 64-family ZeeTypeII SPheno/FlavorKit LFV evaluator.

Generates 64 SLHA inputs from the *original* 16 scalar + four Yukawa cards
and, only with an exact hash-pinned local SPheno/FlavorKit installation,
executes the model's complete generated one-loop mu->3e and coherent mu-e
conversion observables.  No changing physics inputs to manufacture a pass.

Strong caveats: SPheno's generated conversion uses a historical nuclear
model and a documented scalar proton/neutron interchange.  The unpatched
source conversion is NEVER certified as physical; it remains a reference
diagnostic even when executed. A separate corrected-source conversion
backend is required for the model-accepted rate. Original scalar-loop
spectrum changes and incomplete output also invalidate physics matching.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

import numpy as np
from module1.scalar_constraints import reconstruct
from module2.interface import decode, evaluate as neutrino_evaluate
from module14.scan import digest

EXPECTED_SOURCES = {
    "FlavorKit_LFV_ZeeTypeII.f90":"2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d",
    "Couplings_ZeeTypeII.f90":"a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c",
    "LoopFunctions.f90":"8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24",
    "FlavorKit_Observables_ZeeTypeII.f90":"b179e6fea1fe3afe08e34e6d481380b7d4b669ffb904898ac6ee6f8555aa3784",
    "LowEnergy_ZeeTypeII.f90":"cf3552d25de21a6df0869d1fc013dded8efe26206195a08f84ab6ec251d63727",
}
# The previous native SPheno executable was built from a historically
# different experiment scope. A matching SHA alone does not establish that
# the generated five Fortran sources were used for the *current* build.
PRIOR_COMPILED_EXE_SHA="e25953b7c9ec778430cc096218334a7b212b62970a9e651231c922282b08b367"
LFV_INDICES={
    "mu_to_e_gamma":701,
    "mu_to_3e":901,
    "mu_to_e_conversion_Al27":800,
    "mu_to_e_conversion_Au197":804,
}
# Frozen input mapping from module14/physics_adapters/SPheno.m.
MINPAR={
    1:"Lambda1",2:"Lambda2",3:"Lambda3",4:"Lambda4",5:"Lambda5",
    6:"LambdaC",7:"K1",8:"K2",9:"K12",10:"TanBeta",
    11:"M12Sq",12:"MCS2",13:"Mu4",
}
ROOT=Path(__file__).resolve().parents[3]

def sha(path:Path)->str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check_source_bundle(source_paths:dict[str,Path]):
    if set(source_paths)!=set(EXPECTED_SOURCES):
        raise ValueError("Five exact model-specific source files required")
    result={}
    for name,expected in EXPECTED_SOURCES.items():
        p=Path(source_paths[name])
        if not p.is_file():raise FileNotFoundError("Missing full ZeeTypeII source "+name)
        h=sha(p)
        if h!=expected:
            raise ValueError("Wrong version or modified original native source "+name)
        result[name]=h
    return result

def split_slha(text, *, allowed_repeated=(), merge_repeated=()):
    """Parse input/output SLHA conservatively, handling repeated controls.

    Repeated native flavor matrix blocks can be skipped ONLY when the
    caller subsequently replaces every historical copy with one complete
    matrix. Repeated control blocks are combined only when their entries
    are mutually consistent (disjoint keys or identical values); conflicts
    are fatal. SLHA *output* is strict unless explicitly configured.
    """
    lines=text.splitlines()
    blocks={}
    positions=[]
    for ix,line in enumerate(lines):
        match=re.match(r"^[ \t]*BLOCK[ \t]+([A-Za-z0-9_]+)\b",line,re.I)
        if match:
            positions.append((ix,match.group(1).upper()))
    repeated={name.upper() for name in allowed_repeated}
    mergeable={name.upper() for name in merge_repeated}
    if repeated & mergeable:
        raise ValueError("Cannot both skip and merge repeated SLHA control blocks")
    for i,(start,name) in enumerate(positions):
        stop=positions[i+1][0] if i+1<len(positions) else len(lines)
        incoming=[lines[start],*lines[start+1:stop]]
        if name in blocks:
            if name in repeated:
                continue
            if name in mergeable:
                existing=block_values(blocks[name])
                addition=block_values(incoming)
                for key,value in addition.items():
                    if key in existing and existing[key]!=value:
                        raise ValueError(
                            f"Conflicting repeated SLHA control {name}[{key}]: "
                            f"{existing[key]:.17g} vs {value:.17g}")
                existing.update(addition)
                blocks[name]=render_block(name,existing).splitlines()
                continue
            raise ValueError("Duplicate SLHA input block "+name)
        blocks[name]=incoming
    return blocks

def raw_slha_sections(text, name):
    """Return complete verbatim SLHA sections of one name, including repeats.

    The slice ends at the next BLOCK or DECAY header. This allows a strict
    source-integrity check without assuming the native parser resolves
    duplicate SPhenoInput keys as first-wins or last-wins.
    """
    pattern=re.compile(r"(?im)^[ \t]*(?:BLOCK[ \t]+[A-Za-z0-9_]+\b|DECAY(?:1L)?[ \t]+)")
    matches=list(pattern.finditer(text))
    selected=[]
    for i,m in enumerate(matches):
        token=m.group(0).split()
        if len(token)>1 and token[0].upper()=="BLOCK" and token[1].upper()==name.upper():
            stop=matches[i+1].start() if i+1<len(matches) else len(text)
            selected.append(text[m.start():stop])
    return selected

def block_values(block):
    """Read numeric entries only from one isolated SLHA section."""
    res={}
    for line in block[1:]:
        base=line.partition("#")[0].strip()
        if not base:continue
        # A BLOCK may be immediately followed by DECAY without another
        # BLOCK. SLHA sections end at either sentinel, never interpret a
        # DECAY parent width or channel as a matrix entry.
        if re.match(r"(?i)^DECAY(?:1L)?\s+",base):
            break
        t=base.split()
        # No lines from DECAY blocks should be read here.
        if len(t)<2:continue
        if len(t)==2:key=(int(t[0]),);value=float(t[1].replace("D","E").replace("d","E"))
        elif len(t)==3:key=(int(t[0]),int(t[1]));value=float(t[2].replace("D","E").replace("d","E"))
        else:continue
        if key in res:raise ValueError("Duplicate SLHA numeric entry "+str(key))
        if not math.isfinite(value):raise ValueError("Nonfinite SLHA template entry")
        res[key]=value
    return res

def render_block(name,entries):
    head="Block "+name
    rows=[]
    for idx,val in sorted(entries.items()):
        if not isinstance(idx,tuple):idx=(idx,)
        z=float(val)
        if not math.isfinite(z):raise ValueError("Nonfinite new matrix/scalar input")
        rows.append("  "+" ".join(str(x) for x in idx)+f"  {z:.17e}")
    return "\n".join([head,*rows])+"\n"

def set_model_blocks(template, scalar, lepton):
    # Existing template must already be for the same validated model and
    # tree-scheme SPheno settings; no invented generic SPheno defaults.
    # The original tree-scheme SPheno input may repeat the matrix *input*
    # blocks FZEEIN/YEE2IN. Do NOT treat such blocks as observable
    # FZEE/YEE2 output or blindly append the latter as ignored input.
    # The input replacement below canonicalizes every repeated input block
    # to one source-exact matrix, preserving all SMINPUTS and control flags.
    aliases=("FZEEIN","FZEE","YEE2IN","YEE2")
    # The pinned original tree.in intentionally contains repeated
    # SPHENOINPUT blocks, including conflicting switches (11: 0 then 1).
    # Do NOT merge, delete, sort or reinterpret these sections. The native
    # SPheno input reader, not our Python writer, defines their precedence.
    # We preserve each control line *verbatim* and only replace model Yukawas.
    controls=("SPHENOINPUT",)
    permitted=tuple([*aliases,*("IM"+name for name in aliases),*controls])
    sec=split_slha(template,allowed_repeated=permitted)
    if "MINPAR" not in sec:
        raise ValueError("Validated ZeeTypeII input template lacks MINPAR")
    control_sections=raw_slha_sections(template,"SPHENOINPUT")
    flag57=[block_values(section.splitlines())[(57,)] for section in control_sections
            if (57,) in block_values(section.splitlines())]
    if not flag57 or any(value!=1. for value in flag57):
        raise ValueError("All explicitly specified SPhenoInput[57] switches must be 1 for LFV")
    def choose_input_block(stem):
        options=[name for name in (stem+"IN",stem) if name in sec]
        if len(options)!=1:
            raise ValueError("Ambiguous or missing original SARAH model flavor input block "+
                             stem+": "+repr(options))
        return options[0]
    fblock=choose_input_block("FZEE")
    yblock=choose_input_block("YEE2")
    parameters,_inherited,_audit=reconstruct(scalar["physical"])
    vals={ (i,): float(math.tan(scalar["physical"]["beta"]) if i==10 else
                      parameters[name])
          for i,name in MINPAR.items() }
    matrices={fblock:decode(lepton["F"]),yblock:decode(lepton["Ye2"])}
    def mat_block(arr,imag):
        return {(i+1,j+1):float(arr[i,j].imag if imag else arr[i,j].real)
                for i in range(3) for j in range(3)}
    new={"MINPAR":vals}
    # Deliberately leave every SPHENOINPUT section unchanged, including
    # conflicting values of input setting 11 in the validated native card.
    for name,arr in matrices.items():
        if arr.shape!=(3,3) or not np.all(np.isfinite(arr)):
            raise ValueError("Missing full complex Zee model Yukawas")
        new[name]=mat_block(arr,False)
        # The imaginary companion must use the SAME native input stem:
        # IMFZEEIN for FZEEIN, NOT IMFZEE output.
        new["IM"+name]=mat_block(arr,True)
    # The original template may have repeated native input blocks, but
    # replacing all copies with one canonical block is unambiguous.
    # All non-target blocks (including scale, SMINPUTS and SPhenoInput)
    # stay byte-for-byte unchanged except for inter-block whitespace.
    pattern=re.compile(r"(?im)^[ \t]*BLOCK[ \t]+([A-Za-z0-9_]+)\b")
    matches=list(pattern.finditer(template))
    if not matches:raise ValueError("No SLHA template blocks")
    text=""
    replaced=set()
    prev=0
    for i,m in enumerate(matches):
        text+=template[prev:m.start()]
        stop=matches[i+1].start() if i+1<len(matches) else len(template)
        name=m.group(1).upper()
        if name in new:
            if name not in replaced:
                text+=render_block(name,new[name])
                replaced.add(name)
            # Subsequent historical copies are removed, never left with
            # stale old Yukawas which may override a previously set matrix.
        else:
            text+=template[m.start():stop]
        prev=stop
    text+=template[prev:]
    for name,entries in new.items():
        if name not in replaced:
            text+="\n"+render_block(name,entries)
    # Replaced model inputs must occur exactly once. The original repeated
    # SPHENOINPUT controls are permitted only because their sections are
    # preserved byte-for-byte and in the same order.
    out=split_slha(text,allowed_repeated=controls)
    for name,entries in new.items():
        if name not in out or block_values(out[name])!=entries:
            raise ArithmeticError("Native generated SARAH SLHA input was not fully replaced: "+name)
    if raw_slha_sections(text,"SPHENOINPUT")!=control_sections:
        raise ArithmeticError("Validated native SPhenoInput block text/order modified")
    return text

def parse_observables(slha):
    sec=split_slha(slha)
    if "FLAVORKITLFV" not in sec:
        raise ValueError("SPheno output missing FlavorKitLFV block")
    entries=block_values(sec["FLAVORKITLFV"])
    results={}
    for label,idx in LFV_INDICES.items():
        value=entries.get((idx,))
        if value is None or not math.isfinite(value) or value<0:
            raise ValueError("Missing/nonfinite/negative generated LFV observable "+label)
        results[label]=float(value)
    return results

def tree_scheme_mass_gate(slha,p,rtol=2e-4):
    sec=split_slha(slha)
    if "MASS" not in sec:raise ValueError("Missing native ZeeTypeII masses")
    masses=[float(x) for x in block_values(sec["MASS"]).values() if x>1]
    expected=(p["mh1"],p["mh2"],p["ma"],p["mH1"],p["mH2"])
    if len(masses)<len(expected):raise ValueError("Generated SLHA spectrum incomplete")
    # One-to-one bipartite mass matching so close heavy scalar masses cannot
    # spuriously match the same printed mass multiple times.
    candidates=[(i,v) for i,v in enumerate(masses)]
    used=set()
    residuals={}
    for target in sorted(expected,reverse=True):
        choices=sorted(((abs(v-target)/target,i,v) for i,v in candidates if i not in used))
        if not choices or choices[0][0]>rtol:
            raise ValueError(f"Native spectrum drift: expected m={target:.8f} GeV, nearest={choices[:1]}")
        err,i,v=choices[0]
        used.add(i);residuals[str(target)]={"native_mass_GeV":v,"relative_drift":err}
    return residuals

def matrix_from_native(blocks,name):
    if name not in blocks:
        raise ValueError("Model-specific native SLHA does not expose matrix "+name)
    reals=block_values(blocks[name])
    im=block_values(blocks["IM"+name]) if "IM"+name in blocks else {}
    if set(reals)!={(i,j) for i in range(1,4) for j in range(1,4)}:
        raise ValueError("Model-specific native lepton matrix is not complete: "+name)
    if set(im)-set(reals):
        raise ValueError("Native imaginary matrix has mismatched indices")
    z=np.array([[reals[(i,j)]+1j*im.get((i,j),0.)
                 for j in range(1,4)] for i in range(1,4)],dtype=complex)
    if not np.all(np.isfinite(z)):
        raise ValueError("Native model returned a nonfinite complex Yukawa")
    return z

def native_yukawa_gate(slha,p,lepton,relative_tolerance=5e-4,
                       absolute_offdiagonal_tolerance=5e-9):
    """Verify the generator really used the physical F,D source, not just masses.

    In SPheno model conventions D=-sin(beta)*Ye+cos(beta)*Ye2.
    Source tree model should preserve scalar mixings and complex flavor
    matrices; per-entry e-mu texture zeros are checked independently.
    """
    sec=split_slha(slha)
    for name in ("YE","YEE2","FZEE","MINPAR"):
        if name not in sec:raise ValueError("Native model Yukawa output absent: "+name)
    native_beta=math.atan(block_values(sec["MINPAR"])[(10,)])
    if not math.isclose(native_beta,p["beta"],rel_tol=1e-8,abs_tol=1e-8):
        raise ValueError("SPheno tanbeta basis not the native scalar source")
    ye=matrix_from_native(sec,"YE")
    ye2=matrix_from_native(sec,"YEE2")
    f=matrix_from_native(sec,"FZEE")
    d=-math.sin(native_beta)*ye+math.cos(native_beta)*ye2
    expected={"FZEE":decode(lepton["F"]),"YEE2":decode(lepton["Ye2"]),
              "physical_D":decode(lepton["D"])}
    actual={"FZEE":f,"YEE2":ye2,"physical_D":d}
    mismatch={}
    for name,target in expected.items():
        scale=max(float(np.max(abs(target))),1e-12)
        err=float(np.max(abs(actual[name]-target)))
        mismatch[name]=err/max(scale,1e-12)
        if err>relative_tolerance*scale:
            raise ValueError("Model-specific output Yukawa source mismatch "+name)
    if max(abs(d[0,1]),abs(d[1,0]))>absolute_offdiagonal_tolerance:
        raise ValueError("Generated native model lost algebraic e-mu LFV suppression")
    return {"native_tanbeta_beta_residual":native_beta-p["beta"],
            "relative_f_Ye2_physicalD_max_difference":mismatch,
            "native_e_mu_offdiag_max_abs":float(max(abs(d[0,1]),abs(d[1,0]))),
            "source_Yukawa_basis_validated":True}


def source_families(dataset):
    s=json.loads(Path(dataset).read_text())
    if s.get("new_neutrino_family_count")!=64 or len(s.get("families",[]))!=64:
        raise ValueError("Only original complete 16x4 source ensemble accepted")
    if s.get("global_acceptance") is not None:
        raise ValueError("Source improperly declared globally allowed")
    cards={x["scalar_id"]:x for x in s["scalars"]}
    if len(cards)!=16:raise ValueError("Missing 16 independently certified scalar cards")
    emitted=[]
    for f in s["families"]:
        sid=f["id"]
        original=cards[sid]
        if original["scalar_sha256"]!=f["scalar_sha256"] or (
                digest(original["scalar_input"])!=f["scalar_sha256"]):
            raise ValueError("Neutrino/scalar identity mismatch")
        nu=neutrino_evaluate(f["algebraic_texture_input"])
        if nu["inverse"]["family_relative_residual"]>2e-9:
            raise ArithmeticError("Source neutrino construction does not close")
        from module2.interface import canonical_hash
        if canonical_hash(f["algebraic_texture_input"])!=f["algebraic_texture_input_sha256"]:
            raise ValueError("Source original inverse coefficients modified")
        emitted.append({"id":sid,"ordering":f["ordering"],"seed":f["seed"],
            "scalar_sha256":f["scalar_sha256"],
            "original_neutrino_input_sha256":f["algebraic_texture_input_sha256"],
            "neutrino_relative_residual":nu["inverse"]["family_relative_residual"],
            "scalar":original["scalar_input"],"lepton":nu})
    if len(emitted)!=64 or len({(r["id"],r["ordering"],r["seed"]) for r in emitted})!=64:
        raise ValueError("Duplicate source card keys")
    return emitted

def compile_cards(source,template,directory):
    if directory.exists():raise FileExistsError("Source 64-card output already exists")
    data=source_families(source)
    directory.mkdir(parents=True)
    report={"status":"64_SLHA_INPUTS_BUILT_NO_LFV_CALCULATION",
        "source_64_sha256":sha(source),"source_template_sha256":sha(template),
        "model_name":"ZeeTypeII","new_family_count":64,
        "original_Fortran_executed":False,"physical_LFV":None,
        "global_acceptance":None,"cards":[]}
    string=template.read_text()
    for r in data:
        stem=f"zee_{r['id']}_{r['ordering']}_{r['seed']}"
        path=directory/(stem+".in")
        path.write_text(set_model_blocks(string,r["scalar"],r["lepton"]))
        report["cards"].append({"scalar_id":r["id"],"ordering":r["ordering"],
         "seed":r["seed"],"source_scalar_sha256":r["scalar_sha256"],
         "original_neutrino_sha256":r["original_neutrino_input_sha256"],
         "neutrino_relative_residual":r["neutrino_relative_residual"],
         "slha_file":path.name,"slha_sha256":sha(path),
         "model_gamma_br":None,"native_mu3e_BR":None,
         "native_Al_conversion":None,"native_Au_conversion":None,
         "physical_mu3e":None,"physical_conversion":None,
         "global_acceptance":None})
    (directory/"source-manifest.json").write_text(json.dumps(report,allow_nan=False,indent=2,sort_keys=True)+"\n")
    return report

def attest_compiled_nuclear_correction(attestation,exe):
    """Require a forced original-source rebuild, never a merely patched file."""
    if attestation is None:
        return False
    if attestation.get("original_five_sha256")!=EXPECTED_SOURCES:
        raise ValueError("Attested original five source hashes have changed")
    if attestation.get("original_observable_sha256")!=EXPECTED_SOURCES["FlavorKit_Observables_ZeeTypeII.f90"]:
        raise ValueError("Attested pre-correction nuclear source unknown")
    if attestation.get("patched_observable_sha256")!="fd6e4ba58206e0f5d1be8f3993a469a018d0cd3a77160001000b73858f427293":
        raise ValueError("Nuclear observable scalar sign correction has different source SHA")
    if attestation.get("force_complete_rebuild") is not True or attestation.get("build_exit_code")!=0:
        raise ValueError("No completed forced rebuild of corrected native source")
    if attestation.get("binary_sha256")!=sha(exe) or sha(exe)==PRIOR_COMPILED_EXE_SHA:
        raise ValueError("Source-corrected executable not matched and freshly built")
    return True

def evaluate_cards(source,template,cards_dir,exe,source_paths,out_dir,corrected_nuclear_attestation=None):
    if out_dir.exists():raise FileExistsError("Native execution output exists")
    verified=check_source_bundle(source_paths)
    if not exe.is_file():raise FileNotFoundError(exe)
    corrected_nuclear_source=attest_compiled_nuclear_correction(corrected_nuclear_attestation,exe)
    # Executable content provenance must be provided by the user and
    # is recorded separately from source verification; cannot infer a link
    # from source files to executable from a checksum alone.
    data=source_families(source)
    bykey={(r["id"],r["ordering"],r["seed"]):r for r in data}
    manifest=json.loads((cards_dir/"source-manifest.json").read_text())
    if manifest["source_64_sha256"]!=sha(source) or manifest["source_template_sha256"]!=sha(template):
        raise ValueError("Source/model template SHA mismatch")
    if len(manifest["cards"])!=64:
        raise ValueError("Compiled source card list incomplete")
    out_dir.mkdir()
    rows=[]
    for r in manifest["cards"]:
        key=(r["scalar_id"],r["ordering"],r["seed"])
        native_input=cards_dir/r["slha_file"]
        if key not in bykey or sha(native_input)!=r["slha_sha256"]:
            raise ValueError("Wrong or altered source SLHA card "+str(key))
        spc=out_dir/(native_input.stem+".spc")
        log=out_dir/(native_input.stem+".log")
        completed=subprocess.run([str(exe),str(native_input.resolve()),str(spc.resolve())],
                                 capture_output=True,text=True,timeout=180,check=True)
        log.write_text(completed.stdout+"\nSTDERR\n"+completed.stderr)
        if not spc.is_file():
            raise RuntimeError("SPheno returned zero without FlavorKit output")
        txt=spc.read_text()
        rates=parse_observables(txt)
        spectrum=tree_scheme_mass_gate(txt,bykey[key]["scalar"]["physical"])
        yukawa=native_yukawa_gate(txt,bykey[key]["scalar"]["physical"],bykey[key]["lepton"])
        rec=dict(r,native_output_sha256=sha(spc),log_sha256=sha(log),
             native_source_yukawa_matching=yukawa,
             native_one_loop_FlavorKitLFV=rates,physical_mu3e=None,
             physical_conversion=None,global_acceptance=None,
             spectrum_mass_matching=spectrum,
             source_verified_5_original_hashes=verified,
             native_executable_sha256=sha(exe),
             native_executable_is_old_tree_reference=(sha(exe)==PRIOR_COMPILED_EXE_SHA),
             historical_conversion_scalar_proton_neutron_swap_UNCORRECTED=not corrected_nuclear_source,
             original_source_nuclear_rebuild_attestation_sha256=None if corrected_nuclear_attestation is None else hashlib.sha256(json.dumps(corrected_nuclear_attestation,sort_keys=True).encode()).hexdigest(),
             original_FlavorKit_finite_q2_and_nuclear_precision_unknown=True)
        rows.append(rec)
        print("NATIVE_ZEE_64_LFV",*key,"MU3E",rates["mu_to_3e"],
          "AL_HISTORICAL",rates["mu_to_e_conversion_Al27"],
          "AU_HISTORICAL",rates["mu_to_e_conversion_Au197"],
          "PHYSICAL_CONVERSION_UNKNOWN",flush=True)
    report={"schema":"zee-2026-native-source-64-tree-scheme-Flavorkit-observables-attested-nuclear-repair-v2",
      "number_original_cases":len(rows),"source_64_sha256":sha(source),
      "source_SPheno_template_sha256":sha(template),
      "native_binary_sha256":sha(exe),"verified_5_original_source_sha256":verified,
      "native_observables_computed":len(rows)==64,
      "source_couplings_and_scalar_masses_recomputed":True,
      "SPheno_historical_scalar_pn_conversion_swap_unrepaired":not corrected_nuclear_source,
      "source_nuclear_patch_compiler_attestation_matched":corrected_nuclear_source,
      "physical_mu3e":None,"physical_mu_e_conversion":None,
      "full_LFV":"UNKNOWN","global_acceptance":None,
      "cards":rows}
    (out_dir/"native-lfv-64-result.json").write_text(json.dumps(report,allow_nan=False,indent=2,sort_keys=True)+"\n")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--template",required=True,type=Path)
    p.add_argument("--cards-dir",required=True,type=Path)
    p.add_argument("--execute",default=None,type=Path,help="Existing built model-specific SPhenoZeeTypeII binary")
    p.add_argument("--result-dir",type=Path,default=None)
    for name in EXPECTED_SOURCES:
        p.add_argument("--"+name.replace(".f90","").replace("ZeeTypeII","ZeeTypeII"),default=None,type=Path)
    a=p.parse_args()
    if a.execute is None:
        rec=compile_cards(a.source,a.template,a.cards_dir)
        print("ZEE_64_GENERATED",len(rec["cards"]),"NO_NATIVE_PHYSICS_EXECUTION",flush=True)
    else:
        sources={}
        for k in EXPECTED_SOURCES:
            value=getattr(a,k[:-4])
            if value is None:
                p.error("Native execution requires all five original hash-pinned source paths: --"+k[:-4])
            sources[k]=value
        if a.result_dir is None:p.error("--result-dir needed for native SPheno execution")
        rec=evaluate_cards(a.source,a.template,a.cards_dir,a.execute,sources,a.result_dir)
        print("ZEE_64_NATIVE_EXECUTED",len(rec["cards"]),"PHYSICAL_CONVERSION_UNKNOWN",flush=True)
if __name__=="__main__":main()

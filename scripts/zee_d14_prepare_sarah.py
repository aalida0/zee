#!/usr/bin/env python3
"""Prepare an isolated neutrino-rotation model correction; no scan or runtime."""
import argparse
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from module14.scan import file_sha, encode
from module14.conditional_scan.workflow import load

ROOT=Path(__file__).resolve().parents[1]


def prepare(sarah, output):
    sarah=Path(sarah).resolve();output=Path(output).resolve()
    lock=load(ROOT/'module14/public_source_lock.json')['tools']['sarah']
    for name,want in lock['files_sha256'].items():
        if file_sha(sarah/name)!=want:raise ValueError('Pinned SARAH source mismatch: '+name)
    output.mkdir(parents=True,exist_ok=False)
    model=output/'models/ZeeTypeII';model.mkdir(parents=True)
    original={}
    for name in ('ZeeTypeII.m','parameters.m','particles.m'):
        source=ROOT/'models/SARAH/ZeeTypeII'/name
        original[name]=file_sha(source)
        expected=load(ROOT/'module14/physics_adapters/spheno_build_evidence.json')['original_model_sha256'][name]
        if original[name] != expected:raise ValueError('Pinned original model mismatch: '+name)
        shutil.copyfile(source,model/name)
    config=ROOT/'module14/physics_adapters/SPheno.m'
    if file_sha(config) != load(ROOT/'module14/public_spheno_evidence.json')['files_sha256']['model/SPheno.m']:
        raise ValueError('Pinned SPheno configuration mismatch')
    shutil.copyfile(config,model/'SPheno.m')
    edits={
        'ZeeTypeII.m': [('{{phi1,phi2},{hh,ZH}},','{{vL},{VL,UV}},\n {{phi1,phi2},{hh,ZH}},'),
                       ('Fv -> {vL,conj[vL]}','Fv -> {VL,conj[VL]}')],
        'parameters.m': [('ParameterDefinitions = {','ParameterDefinitions = {\n {UV,{Description -> "Neutrino-Mixing-Matrix"}},')],
        'particles.m': [('WeylFermionAndIndermediate = {','WeylFermionAndIndermediate = {\n {VL,{LaTeX -> "N_L"}},')]
    }
    for name,replacements in edits.items():
        path=model/name;text=path.read_text()
        for old,new in replacements:
            if text.count(old)!=1:raise ValueError('Original model contract changed: '+name)
            text=text.replace(old,new)
        path.write_text(text)
    # quote paths as Mathematica string literals using the JSON string syntax
    import json
    script=f'''Get[{json.dumps(str(sarah/'SARAH.m'))}];
SARAH[OutputDirectory] = {json.dumps(str(output/'output'))};
SARAH[InputDirectories] = Prepend[SARAH[InputDirectories],{json.dumps(str(output/'models'))}];
Start["ZeeTypeII"];
Print["D14_MIXING: ",getMixingMatrix[Fv]];
MakeSPheno[IncludeFlavorKit -> True];
Print["D14_SPHENO_RETURNED"];
MakeVevacious[Version->"++"];
Print["D14_VEVACIOUS_RETURNED"];
'''
    (output/'generate.m').write_text(script)
    receipt={'original_model_sha256':original,'corrected_model_sha256':{p.name:file_sha(p) for p in model.iterdir()},
             'sarah_version':'4.15.4','status':'PREPARED_RESEARCH_ONLY','operative_constraint':False}
    (output/'preparation.json').write_text(encode(receipt)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sarah',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    print(encode(prepare(a.sarah,a.output)))

#!/usr/bin/env python3
"""Same-input LO numerical audit; does not certify external operator conventions.

Builds a small client against the *existing* upstream CLI link dependencies.
No upstream source is changed. Detailed outputs belong in an ignored directory.
"""
import argparse
import json
import math
from pathlib import Path
import re
import shlex
import subprocess
import sys

from zee_module5_hyperiso_runtime import verify_checkout, verify_build, sha
from zee_module5_dipole_projection import coefficients
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from module5.bsgamma_lo import compute
import mpmath as mp


def run(cmd,cwd):
    r=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=240)
    if r.returncode or r.stderr.strip():
        raise ValueError(f"Command failed: {cmd}: {r.stderr[-2000:]}")
    return r.stdout


def spectrum(text,mass,tanb,flip=False):
    """Change only charged mass, beta and the explicitly read real Yukawa blocks."""
    block="";out=[]
    for line in text.splitlines():
        if line.lower().startswith("block "):
            block=line.split()[1].upper()
        cols=line.split("#")[0].split()
        value=None
        if block=="MASS" and cols and cols[0]=="37":value=mass
        if block=="MINPAR" and cols and cols[0]=="3":value=tanb
        if block=="MINPAR" and cols and cols[0]=="24":value=2
        if block in ("UCOUPL","DCOUPL","LCOUPL") and len(cols)==3:
            value=(1/tanb if block=="UCOUPL" else -tanb) if cols[0]==cols[1] else 0.
            if flip and block=="DCOUPL":value=-value
        if value is not None:
            line="  "+" ".join(cols[:-1])+f" {value:.17e}"
        out.append(line)
    return "\n".join(out)+"\n"


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream",type=Path,required=True)
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();root=a.upstream.resolve();binary=a.binary.resolve()
    verify_checkout(root);provenance=verify_build(root,binary)
    build=Path(provenance["build_directory"])
    dest=a.output.resolve();dest.parent.mkdir(parents=True,exist_ok=True)
    source=Path(__file__).resolve().with_name("zee_module5_hyperiso_probe.cpp")
    commands=json.loads((build/"compile_commands.json").read_text())
    cli=next(x for x in commands if x["file"].endswith("/UserInterface/main.cpp"))
    args=shlex.split(cli["command"])
    obj=dest.parent/"hyperiso_probe.o";exe=dest.parent/"hyperiso_probe"
    args[args.index("-o")+1]=str(obj);args[args.index("-c")+1]=str(source)
    run(args,build)
    link=run(["ninja","-C",str(build),"-t","commands","hyperiso-ui"],root).splitlines()[-1]
    # Extract argv, never execute shell syntax from the build description.
    args=shlex.split(link);args=args[args.index("&&")+1:args.index("&&",args.index("&&")+1)]
    args[args.index("-o")+1]=str(exe)
    args=[str(obj) if x.endswith("/hyperiso-ui.dir/main.cpp.o") else x for x in args]
    run(args,build)
    base=(root/"reproducibility/inputs/thdm_reference.lha").read_text()
    rows=[];mp.mp.dps=70
    points=[(m,2.) for m in (300.,550.,900.,2000.,100000.)]
    points += [(550.,t) for t in (.2,1.,10.,50.)]
    for mass,tanb in points:
        for flip in (False,True):
            label=f"m{mass:g}_tb{tanb:g}_flip{int(flip)}"
            inp=dest.parent/(label+".lha");inp.write_text(spectrum(base,mass,tanb,flip))
            raw=run([str(exe),"--model","THDM","--lha",str(inp),"--spectrum","true",
                     "--patch-probe","true"],root)
            (dest.parent/(label+".log")).write_text(raw)
            mt=float(re.search(r"GATE_B mt (\S+)",raw)[1])
            patch_match=re.search(r"GATE_B PATCH \(([^,]+),([^\)]+)\)",raw)
            if patch_match is None or abs(complex(*map(float,patch_match.groups()))-complex(-.002,.006))>2e-14:
                raise ValueError("Generic complex matching patch API failed")
            actual={}
            for name,values in re.findall(r"GATE_B (C\d) ([^\n]+)",raw):
                z=[complex(float(r),float(i)) for r,i in re.findall(r"\(([^,]+),([^\)]+)\)",values)]
                if len(z)!=3 or any(v.imag!=0 or not math.isfinite(v.real) for v in z):
                    raise ValueError("Invalid coefficient probe")
                sm,bsm,total=[v.real for v in z]
                if not math.isclose(sm+bsm,total,abs_tol=2e-14,rel_tol=2e-13):
                    raise ValueError("SM+BSM composition failed")
                actual[name]=bsm
            if set(actual)!={f"C{i}" for i in range(1,9)} or any(actual[f"C{i}"]!=0 for i in range(1,7)):
                raise ValueError("Unexpected LO four-quark matching")
            projected=coefficients((mp.mpf(mt)/mass)**2,mp.mpf(1)/tanb**2,
                                   -1 if flip else 1,qt=mp.mpf(2)/3)
            zee=compute(mass,1234.,math.atan(tanb),0.,mt,160.)
            residuals=[abs(actual[f"C{i}"]-float(v)) for i,v in zip((7,8),projected)]
            if not all(math.isclose(actual[f"C{i}"],float(v),rel_tol=2e-11,abs_tol=2e-14) for i,v in zip((7,8),projected)):
                raise ValueError("Independent diagram comparison failed")
            if not flip and any(not math.isclose(actual[f"C{i}"],zee[f"delta_C{i}_LO_at_matching_scale"],rel_tol=2e-11,abs_tol=2e-14) for i in (7,8)):
                raise ValueError("Frozen gamma=0 comparison failed")
            rows.append({"mH_GeV":mass,"tanbeta":tanb,"ld_sign_falsifier":flip,
                         "mt_MSbar_160_GeV":mt,"hyperiso_delta_C7":actual["C7"],
                         "hyperiso_delta_C8":actual["C8"],"absolute_residuals":residuals,
                         "input_sha256":sha(inp)})
    mass_scan=sorted((r for r in rows if not r["ld_sign_falsifier"] and r["tanbeta"]==2.),key=lambda r:r["mH_GeV"])
    beta_scan=sorted((r for r in rows if not r["ld_sign_falsifier"] and r["mH_GeV"]==550.),key=lambda r:r["tanbeta"])
    for key in ("hyperiso_delta_C7","hyperiso_delta_C8"):
        for scan in (mass_scan,beta_scan):
            if not all(abs(a[key])>abs(b[key]) for a,b in zip(scan,scan[1:])):
                raise ValueError("Mass/beta limit falsifier failed")
    payload={"status":"SAME_INPUT_LO_NUMERICAL_PASS_OPERATOR_CONVENTION_UNCERTIFIED",
             "matching_convention_status":"MATCHING_CONVENTION_UNKNOWN",
             "generic_complex_matching_patch":"EXECUTABLE_PASS_NONPHYSICAL_API_VALUES",
             "qmatch_GeV":160,"gamma_rad":0,"order":"alpha_s^0",
             "relative_tolerance":2e-11,"absolute_tolerance":2e-14,
             "independent_mass_and_beta_monotonicity":"PASS",
             "probe_source_sha256":sha(source),"probe_binary_sha256":sha(exe),"rows":rows}
    dest.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(payload["status"])


if __name__=="__main__":main()

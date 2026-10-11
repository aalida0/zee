#!/usr/bin/env python3
"""Gate A1O: version-pinned isolated SuperIso v5 bsgamma internal-C0w bridge.

The code modifies ONLY a copy of the already-verified Gate A1M NLO
isolated source. The original vendor tree and A1M copy remain unchanged.
New thread-local override is a diagnostic bridge, not a public API or
certified physical flavor prediction. It is never used without explicit
set+clear by a dedicated driver. It overrides only C0w[7] and [8] at
their hidden internal recomputation site for N(E0) and P_em.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import shutil
import difflib
import re

EXPECTED_BSGAMMA_SHA256="ab754c8596d0610a3efe3920acefb18ff34b5cc7bac66072a965d6a1e971c196"
MATCHING_LINE="CW_calculator(2,C0w,C1w,C2w,mu_W,param);"
INCLUDE_LINE='#include "include.h"'

BRIDGE_DECL='''

/* Gate A1O: controlled single-thread/one-process diagnostics ONLY.
 * The original ABI and normal execution remain unchanged when inactive.
 * Keep explicit set/clear around the one bsgamma call in the external
 * Gate A1O driver. Never call on concurrent workers without testing.
 */
static _Thread_local int gateA1o_c0w_override_active=0;
static _Thread_local double complex gateA1o_c0w7=0.;
static _Thread_local double complex gateA1o_c0w8=0.;

void gateA1o_set_internal_C0w78(double complex c7, double complex c8)
{
    gateA1o_c0w7=c7;
    gateA1o_c0w8=c8;
    gateA1o_c0w_override_active=1;
}

void gateA1o_clear_internal_C0w78(void)
{
    gateA1o_c0w_override_active=0;
    gateA1o_c0w7=0.;
    gateA1o_c0w8=0.;
}
'''
BRIDGE_OVERRIDE='''
    /* Gate A1O: replace the hidden single-Higgs matching values with
       the *same* coherent high-scale C0w used by external RG. */
    if(gateA1o_c0w_override_active) {
        C0w[7]=gateA1o_c0w7;
        C0w[8]=gateA1o_c0w8;
    }
'''

def digest(bs): return hashlib.sha256(bs).hexdigest()

def patch(source):
    lines=source.splitlines(keepends=True)
    internal=[i for i,line in enumerate(lines)
              if line.strip()==MATCHING_LINE]
    if len(internal)!=1:
        raise ValueError(f"Expected exactly one internal matching call (not container), got {internal}")
    include=[i for i,line in enumerate(lines) if line.strip()==INCLUDE_LINE]
    if len(include)!=1:
        raise ValueError(f"Cannot identify one canonical include line: {include}")
    if not 600<internal[0]+1<720:
        raise ValueError("Unexpected bsgamma internal matching location")
    if 'gateA1o_' in source:
        raise ValueError("Refuse to patch already modified SuperIso bsgamma.c")
    # Keep existing call as baseline for non-override use; only replace
    # its C7/C8 with explicitly supplied matching coefficients.
    lines[internal[0]]=lines[internal[0]]+BRIDGE_OVERRIDE
    lines[include[0]]=lines[include[0]]+BRIDGE_DECL
    return ''.join(lines),internal[0]+1

def create(root,destination,manifest):
    root=pathlib.Path(root).expanduser().resolve()
    destination=pathlib.Path(destination).expanduser().resolve()
    if destination.exists():
        raise FileExistsError(f"Refuse existing output copy: {destination}")
    if root==destination or root in destination.parents or destination in root.parents:
        raise ValueError("Output must be fully separate from A1M source tree")
    if not (root/"Makefile").is_file():
        raise ValueError("Expected compiled Gate A1M complete SuperIso source")
    data=json.loads(pathlib.Path(manifest).read_text())
    if data.get("isolated_dir")!=str(root):
        raise ValueError("A1M provenance does not identify this isolated source")
    wilson=(root/"src/wilson.c").read_bytes()
    if digest(wilson)!=data["patched_wilson_sha256"]:
        raise ValueError("A1M isolated NLO source has unexpected SHA256")
    f=root/"src/bsgamma.c"
    original_bytes=f.read_bytes()
    if digest(original_bytes)!=EXPECTED_BSGAMMA_SHA256:
        raise ValueError("Not the audited SuperIso v5.0 bsgamma.c")
    source=original_bytes.decode("utf-8")
    patched,internal_line=patch(source)
    shutil.copytree(root,destination)
    (destination/"src/bsgamma.c").write_text(patched)
    if digest(f.read_bytes())!=EXPECTED_BSGAMMA_SHA256:
        raise RuntimeError("Original A1M source was modified while copying")
    if (destination/"src/wilson.c").read_bytes()!=wilson:
        raise RuntimeError("A1M NLO Wilson matching changed in A1O")
    diff=''.join(difflib.unified_diff(
        source.splitlines(keepends=True),patched.splitlines(keepends=True),
        fromfile="A1M/src/bsgamma.c",tofile="A1O/src/bsgamma.c",n=3))
    return {
        "status":"GATE_A1O_SOURCE_ONLY_INTERNAL_C0W_BRIDGE_NOT_PHYSICAL",
        "source_A1M_root":str(root),"isolated_A1O_root":str(destination),
        "a1m_wilson_sha256":digest(wilson),
        "bsgamma_original_sha256":digest(original_bytes),
        "bsgamma_modified_sha256":digest((destination/"src/bsgamma.c").read_bytes()),
        "only_source_file_modified":"src/bsgamma.c",
        "internal_matching_line":internal_line,
        "override_indices":[7,8],
        "thread_local_diagnostic_override":True,
        "original_or_a1m_source_mutated":False,
        "source_diff":diff,
        "physical_branching_ratio_certified":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a1m-source",type=pathlib.Path,required=True)
    p.add_argument("--a1m-provenance",type=pathlib.Path,required=True)
    p.add_argument("--isolated-output",type=pathlib.Path,required=True)
    p.add_argument("--report",type=pathlib.Path,required=True)
    args=p.parse_args()
    result=create(args.a1m_source,args.isolated_output,args.a1m_provenance)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n")
    print("Wrote",args.report)
    print("STATUS:",result["status"])

if __name__=="__main__":
    main()

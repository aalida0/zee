#!/usr/bin/env python3
"""Source-integrity-checked extractor of *upstream* GPL HEPfit THDM Wilson
coefficient matching, compiled in the CI's temporary directory.

No HEPfit source is committed or redistributed in this repository; users
obtain it from its original GPL-3.0+ publisher at pinned git commit.

The generated C++ wraps exactly HEPfit's three-loop matching formula
THDMMatching::setWCbsg with its cache code removed. This is a standalone
upstream matching coefficient oracle, not a HEPfit full branching ratio.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import hashlib

UPSTREAM_COMMIT="add26f5ac16cec688021d95226ece6397de29e5e"
UPSTREAM_BLOB_SHA="8029be52c3e2f83490dfe3199f80e5db484dd23b"
UPSTREAM="https://raw.githubusercontent.com/silvest/HEPfit/"+UPSTREAM_COMMIT+"/THDM/src/THDMMatching.cpp"

def git_blob(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\\0"+b).hexdigest()

def extract_text(path:Path):
    if git_blob(path.read_bytes()) != UPSTREAM_BLOB_SHA:
        raise RuntimeError("HEPfit source diverges from pinned Git blob")
    s=path.read_text()
    anchor="double THDMMatching::setWCbsg("
    if s.count(anchor)!=1:
        raise RuntimeError("Upstream HEPfit matching function ambiguous")
    start=s.index(anchor)
    brace=s.index("{",start)
    depth=0; end=None
    for i in range(brace,len(s)):
        if s[i]=="{":depth+=1
        elif s[i]=="}":
            depth-=1
            if depth==0:
                end=i+1;break
    if not end:raise RuntimeError("HEPfit matching function unbalanced")
    body=s[brace+1:end-1]
    cache_end="    double x = mt*mt/mhp/mhp;"
    if body.count(cache_end)!=1:
        raise RuntimeError("Upstream HEPfit matching starts with changed expression")
    body=body[body.index(cache_end):]
    requirements=("n72ct","n82fr","CWbsgArrayNNLO[6]","CWbsgArrayNNLO[7]",
                  "CWbsgArrayNLO[3]","CWbsgArrayLO[7]",
                  "gsl_sf_dilog(1.-1./x)")
    for pattern in requirements:
        if pattern not in body:
            raise RuntimeError("Upstream three-loop matching source changed: "+pattern)
    return body

def write(source:Path,out:Path):
    if out.exists():raise FileExistsError("No overwrite of source extraction")
    body=extract_text(source)
    wrapper=r"""// This file is GENERATED from the pinned official HEPfit GPL-3.0+ source
// at https://github.com/silvest/HEPfit and is NOT committed into zee.
// All mathematical three-loop matching expressions below are HEPfit's.
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <iomanip>
#include <sstream>
#include <gsl/gsl_sf_dilog.h>
enum orders { LO=0, NLO=1, NNLO=2 };
double hepf_upstream_wc(int i,double tan,double mt,double mhp,double mu,orders order)
{
    if(i < 0 || i>=8) throw std::runtime_error("invalid Wilson index");
    double CWbsgArrayLO[8]={},CWbsgArrayNLO[8]={},CWbsgArrayNNLO[8]={};
"""
    end=r"""
}
int main(int argc,char **argv) {
  if(argc!=5){std::cerr<<"usage: probe tanbeta mtMSbar chargedmass mu0"<<std::endl;return 2;}
  const double tanb=std::atof(argv[1]);
  const double mt=std::atof(argv[2]);
  const double mH=std::atof(argv[3]);
  const double mu=std::atof(argv[4]);
  if(!(tanb>0 && mt>100 && mH>100 && mu>50))return 3;
  std::cout<<std::scientific<<std::setprecision(17);
  for(int ord=0;ord<3;++ord) {
     for(int i=0;i<8;++i) {
        auto value=hepf_upstream_wc(i,tanb,mt,mH,mu,static_cast<orders>(ord));
        if(!std::isfinite(value))return 4;
        std::cout<<ord<<" "<<i<<" "<<value<<"\\n";
     }
  }
  return 0;
}
"""
    out.write_text(wrapper+body+end)
    print("HEPFIT_NNLO_UPSTREAM_ORACLE_SOURCE_VALIDATED",
          "sha",git_blob(source.read_bytes()),"generated_CXX",out,flush=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    write(args.source,args.output)

if __name__=="__main__":main()

#!/usr/bin/env python3
"""Extract an INDEPENDENT Type-II LO/NLO/NNLO matching implementation.

Source: HEPfit Collaboration THDMMatching::setWCbsg(), licensed GPL.
The upstream code is NOT committed into this project. Fetch the pinned
source file, verify its Git BLOB SHA, then generate a disposable C++
harness under work/. Do not alter HEPfit mathematics.

This extracts matching ONLY, not HEPfit's RG evolution or physical BR.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HEPFIT_REPOSITORY="https://github.com/silvest/HEPfit"
HEPFIT_FILE="THDM/src/THDMMatching.cpp"
HEPFIT_BLOB="8029be52c3e2f83490dfe3199f80e5db484dd23b"
FUNCTION_SIGNATURE="double THDMMatching::setWCbsg("

HEADER=r"""// Gate A1P generated source; do not distribute independently of HEPfit GPL.
// This is an isolated compilation shim around an unmodified upstream method.
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <gsl/gsl_sf_dilog.h>

enum orders {LO=0,NLO=1,NNLO=2};
class THDMMatching {
public:
  double tanbsg=std::numeric_limits<double>::quiet_NaN();
  double mtbsg=std::numeric_limits<double>::quiet_NaN();
  double mhpbsg=std::numeric_limits<double>::quiet_NaN();
  double mubsg=std::numeric_limits<double>::quiet_NaN();
  double CWbsgArrayLO[8]={};
  double CWbsgArrayNLO[8]={};
  double CWbsgArrayNNLO[8]={};
  double setWCbsg(int i, double tan, double mt, double mhp,
                  double mu, orders order);
};

"""

MAIN=r"""
int main(int argc, char** argv) {
  if(argc!=5) {
    std::cerr<<"Usage: hepfit_reference tanbeta mt_running_muW muW charged_mass\n";
    return 2;
  }
  try {
    const double tan=std::stod(argv[1]),mt=std::stod(argv[2]),
                 mu=std::stod(argv[3]),mh=std::stod(argv[4]);
    if(!(std::isfinite(tan)&&tan>0&&std::isfinite(mt)&&mt>1&&
         std::isfinite(mu)&&mu>1&&std::isfinite(mh)&&mh>mt))
      throw std::invalid_argument("Invalid inputs; require mh > mt");
    THDMMatching match;
    std::cout<<std::setprecision(17);
    std::cout<<"HEPFIT_SOURCE_ONLY_NOT_PHYSICAL_BR\n";
    std::cout<<"INPUT mass="<<mh<<" tanbeta="<<tan
             <<" mt_muW="<<mt<<" muW="<<mu<<"\n";
    for(int order=2;order>=0;order--) {
      // First requesting NNLO fills all arrays via intentional fallthrough.
      // Each separate order returns one term C_i^(order) (no alpha_s factors).
      for(int i=0;i<8;i++) {
        const double value=match.setWCbsg(i,tan,mt,mh,mu,
                                           static_cast<orders>(order));
        if(!std::isfinite(value)) throw std::runtime_error("Nonfinite HEPfit matching");
        std::cout<<"HEPFIT order="<<order<<" op="<<(i+1)
                 <<" delta="<<value<<" mass="<<mh<<"\n";
      }
    }
    return 0;
  } catch(const std::exception& exc) {
    std::cerr<<"HEPFIT_REFERENCE_ERROR: "<<exc.what()<<"\n";
    return 1;
  }
}
"""

def git_blob_sha(raw:bytes)->str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()

def extract(text:str)->str:
    index=text.find(FUNCTION_SIGNATURE)
    if index < 0 or text.find(FUNCTION_SIGNATURE,index+1)>=0:
        raise ValueError("Expected precisely one original HEPfit setWCbsg definition")
    start=text.find("{",index)
    if start<0:
        raise ValueError("No matching function body")
    depth=0
    end=None
    for j in range(start,len(text)):
        if text[j]=="{": depth+=1
        elif text[j]=="}":
            depth-=1
            if depth==0:
                end=j+1
                break
    if end is None:
        raise ValueError("Unbalanced HEPfit function")
    result=text[index:end]
    for required in ("gsl_sf_dilog","CWbsgArrayNNLO[6]",
                     "CWbsgArrayNLO[6]","CWbsgArrayLO[6]",
                     "CWbsgArrayNNLO[7]","CWbsgArrayNLO[7]",
                     "CWbsgArrayLO[7]"):
        if required not in result:
            raise ValueError(f"HEPfit formula contract changed: {required}")
    if "myTHDM" in result or "StandardModelMatching" in result:
        raise ValueError("Function not isolated: still needs HEPfit model state")
    return result

def generate(source:Path,destination:Path,manifest:Path,expected_blob=HEPFIT_BLOB):
    raw=source.read_bytes()
    actual=git_blob_sha(raw)
    if actual!=expected_blob:
        raise ValueError(f"Unrecognized independent HEPfit source blob {actual}; expected {expected_blob}")
    text=raw.decode("utf-8")
    function=extract(text)
    # Preserve the original HEPfit copyright notice in the generated
    # temporary translation unit; the original full GPL source
    # is kept alongside the extracted shim under work/.
    copyright_notice=text[:text.find("#include")]
    if "HEPfit Collaboration" not in copyright_notice:
        raise ValueError("Missing original upstream HEPfit copyright notice")
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(copyright_notice+HEADER+function+"\n"+MAIN)
    details={
        "status":"HEPFIT_INDEPENDENT_REFERENCE_SHIM_GENERATED_NOT_PHYSICAL_BR",
        "upstream_repo":HEPFIT_REPOSITORY,"upstream_file":HEPFIT_FILE,
        "upstream_git_blob":actual,
        "upstream_source_sha256":hashlib.sha256(raw).hexdigest(),
        "extracted_member_function_sha256":hashlib.sha256(function.encode()).hexdigest(),
        "reference_source_path":str(source),
        "generated_cpp_path":str(destination),
        "method":"Exact upstream setWCbsg() formula embedded at run time in a "
                 "minimal independent harness; original code retains its GPL provenance",
        "operation":"Type-II C1..C8 LO/NLO/NNLO matching only",
        "not_validated":["top running mass and renormalization scheme",
                         "Wilson-operator basis normalization",
                         "full RG evolution and inclusive BR",
                         "Zee benchmark physical validity"],
        "independent_matching_ready":False,
        "physical_BtoXs_gamma_validated":False,
    }
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(details,indent=2)+"\n")
    return details

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hepfit-source",type=Path,required=True)
    p.add_argument("--cpp-output",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    a=p.parse_args()
    r=generate(a.hepfit_source,a.cpp_output,a.manifest)
    print("Wrote",a.cpp_output,"and",a.manifest)
    print("STATUS:",r["status"])

if __name__=="__main__":
    main()

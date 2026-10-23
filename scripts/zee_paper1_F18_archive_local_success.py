#!/usr/bin/env python3
"""Archive one completed local F18 MadWidth case for reuse in Condor merge.

Do not rerun a validated local 2+3 body calculation. Preserve the actual
binary result SHA and both SLHA output hashes in a portable archive.
Cannot promote mere F18_BENCHMARK_PASS console text: requires the original
F18 machine-readable summary and a complete consistent case report.
"""
from __future__ import annotations
import argparse,hashlib,io,json,tarfile
from pathlib import Path

CASES=("F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003")
STATUS="F18_REAL_SARAH_ZEE_MADWIDTH_2AND3_BODY_3_CASES_MODEL_LO_NOT_EXCLUSION"
ARCHIVE_STATUS="F18_LOCAL_SUCCESS_PRESERVED_FOR_MIXED_CONDOR_MERGE_NOT_QCD_ALLOWED"


def sha(path):
    dig=hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda:fh.read(1024*1024),b""):
            dig.update(block)
    return dig.hexdigest()


def pack(source,benchmark,out):
    source=Path(source).expanduser().resolve()
    out=Path(out).expanduser().resolve()
    if benchmark not in CASES:raise ValueError("Only exact original F13 cohort accepted")
    if out.exists():raise FileExistsError("Refuse overwrite original F18 local archive")
    summary=json.loads((source/"summary.json").read_text())
    result_path=source/benchmark/"validated_model_LO_widths.json"
    result=json.loads(result_path.read_text())
    if (summary.get("status")!=STATUS or summary.get("errors",{}).get(benchmark)
        or not any(x==result for x in summary.get("results",[]))
        or result.get("candidate_id")!=benchmark):
        raise ValueError("No verified locally completed matching F18 result")
    meta=result.get("provenance",{})
    files={}
    for label,filename,ref in (
        ("two_body","two_body.slha","MadWidth_two_body"),
        ("two_plus_three","two_plus_three_body.slha","MadWidth_two_plus_three")):
        path=source/benchmark/filename
        expected=meta.get(ref,{}).get("output_SHA256")
        if not expected or sha(path)!=expected:
            raise ValueError("Local MadWidth SLHA is not hash-pinned "+filename)
        files[label]={"name":filename,"sha256":expected,
                      "size":path.stat().st_size}
    if not summary.get("MG5_binary_SHA256") or not summary.get(
        "original_F17f_report_SHA256"):
        raise ValueError("Missing source and MG5 provenance in local F18 summary")
    manifest={"status":ARCHIVE_STATUS,"benchmark":benchmark,
              "original_campaign":source.name,
              "original_summary_SHA256":sha(source/"summary.json"),
              "original_case_JSON_SHA256":sha(result_path),
              "MG5_binary_SHA256":summary["MG5_binary_SHA256"],
              "original_F17f_report_SHA256":summary["original_F17f_report_SHA256"],
              "F14_original_13TeV_CSV_SHA256":summary.get("F14_original_13TeV_CSV_SHA256"),
              "source_independent_CKM_and_lepton_amplitudes_validated_before_run":
                  summary.get("source_independent_CKM_and_lepton_amplitudes_validated_before_run"),
              "original_SLHA_SHA256":files,
              "model_tree_only_not_QCD_or_exclusion":True}
    out.parent.mkdir(parents=True,exist_ok=True)
    with tarfile.open(out,"w:gz") as tar:
        for file,name in (
            (source/"summary.json","summary.json"),
            (result_path,"validated_model_LO_widths.json"),
            (source/benchmark/"two_body.slha","two_body.slha"),
            (source/benchmark/"two_plus_three_body.slha","two_plus_three_body.slha")):
            tar.add(file,arcname=benchmark+"/"+name,recursive=False)
        raw=(json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode()
        item=tarfile.TarInfo(benchmark+"/local_archive_manifest.json")
        item.size=len(raw);item.mode=0o644
        tar.addfile(item,io.BytesIO(raw))
    print("F18_LOCAL_REUSE_PACKED",benchmark,"TARBALL",out,
          "SHA256",sha(out),"NO_MG5_RERUN",True)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--local-campaign",type=Path,required=True)
    p.add_argument("--benchmark",choices=CASES,default="F13_heavy_0001330")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    pack(a.local_campaign,a.benchmark,a.output)


if __name__=="__main__":main()

#!/usr/bin/env python3
"""F18 HTCondor 3-job merge: verify one result per original F13 case.

Strictly merge completed per-case MadWidth 2/3 body physics outputs.
Never infer experimental allowance, NLO precision, or detector sensitivity.
No MG5 is launched. Run on the HTCondor submit node after all three
result_<case>.tar.gz archives have arrived.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,tarfile
from pathlib import Path
# Standalone stdlib merger: submit host does not need the repository's
# large physics/Python dependencies merely to combine successful archives.
TGT=("F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003")
STATUS="F18_REAL_SARAH_ZEE_MADWIDTH_2AND3_BODY_3_CASES_MODEL_LO_NOT_EXCLUSION"


def member_data(archive,name,maxbytes=150_000_000):
    try:item=archive.getmember(name)
    except KeyError as ex:raise ValueError("Missing archived file "+name) from ex
    if not item.isfile() or not 0<=item.size<=maxbytes:
        raise ValueError("Unexpected member size or type "+name)
    stream=archive.extractfile(item)
    if stream is None:raise ValueError("Unreadable archived member "+name)
    return stream.read()



LOCAL_ARCHIVE_STATUS="F18_LOCAL_SUCCESS_PRESERVED_FOR_MIXED_CONDOR_MERGE_NOT_QCD_ALLOWED"


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def import_local_success(folder,name):
    """Accept a validated precomputed LOCAL F18 two+three body benchmark.

    Local provenance is reported distinctly from HTCondor. Require the
    original full F18 summary, exact successful result, source SHA hashes,
    and two genuine source SLHAs matching the F18 stage hashes.
    """
    archive_path=folder/("F18_local_completed_"+name+".tar.gz")
    if not archive_path.is_file():raise FileNotFoundError(str(archive_path))
    with tarfile.open(archive_path,"r:gz") as tar:
        root=name+"/"
        manifest=json.loads(member_data(tar,root+"local_archive_manifest.json"))
        manifest_source=manifest.get("source_summary_filename")
        if manifest_source not in ("summary.json","initial_manifest.json"):
            raise ValueError("Local archive has unrecognized F18 manifest source")
        original_summary=member_data(tar,root+manifest_source)
        case_text=member_data(tar,root+"validated_model_LO_widths.json")
        if (manifest.get("status")!=LOCAL_ARCHIVE_STATUS
            or manifest.get("benchmark")!=name
            or sha_bytes(original_summary)!=manifest.get("original_summary_SHA256")
            or sha_bytes(case_text)!=manifest.get("original_case_JSON_SHA256")):
            raise ValueError("Local original F18 result archive hashes/source invalid "+name)
        summary=json.loads(original_summary)
        case=json.loads(case_text)
        if (summary.get("status")!=STATUS
            or summary.get("errors",{}).get(name)
            or case.get("candidate_id")!=name
            or (manifest_source=="summary.json" and not any(
                row==case for row in summary.get("results",[])))):
            raise ValueError("Local F18 benchmark was not fully validated "+name)
        if manifest.get("original_F17f_report_SHA256_in_verified_source")!=summary.get(
                "original_F17f_report_SHA256"):
            raise ValueError("Completed local case not bound to validated F17f report")
        expected_cases=manifest["original_SLHA_SHA256"]
        for label,filename,ref in (
                ("two_body","two_body.slha","MadWidth_two_body"),
                ("two_plus_three","two_plus_three_body.slha","MadWidth_two_plus_three")):
            data=member_data(tar,root+filename,maxbytes=150_000_000)
            record=expected_cases[label]
            if (record.get("name")!=filename or len(data)!=record.get("size")
                or sha_bytes(data)!=record.get("sha256")
                or sha_bytes(data)!=case["provenance"][ref]["output_SHA256"]):
                raise ValueError("Local real MG5 output SHA mismatch "+filename)
        src={k:summary.get(k) for k in (
             "MG5_binary_SHA256","original_F17f_report_SHA256",
             "F14_original_13TeV_CSV_SHA256",
             "source_independent_CKM_and_lepton_amplitudes_validated_before_run")}
        if any(manifest.get(k)!=src[k] for k in src):
            raise ValueError("Local archive does not preserve original MG5/source provenance")
        evidence={"origin":"previously_completed_LOCAL_F18_not_a_Condor_job",
                  "local_success_archive_SHA256":
                       hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                  "local_F18_summary_SHA256":manifest["original_summary_SHA256"],
                  "source_MadWidth_two_body_SHA256":
                       case["provenance"]["MadWidth_two_body"]["output_SHA256"],
                  "source_MadWidth_two_plus_three_body_SHA256":
                       case["provenance"]["MadWidth_two_plus_three"]["output_SHA256"]}
    return summary,case,src,evidence


def merge(folder,out):
    folder=Path(folder).expanduser().resolve()
    out=Path(out).expanduser().resolve()
    if out.exists():raise FileExistsError("Refuse overriding old F18 merge")
    results=[]
    provenance=None
    sources={}
    for name in TGT:
        archive_path=folder/("F18_result_"+name+".tar.gz")
        local_archive=folder/("F18_local_completed_"+name+".tar.gz")
        if archive_path.exists() and local_archive.exists():
            raise ValueError("Both Condor and local F18 outputs exist for "+name+
                             "; explicitly select one without hiding provenance")
        if local_archive.exists():
            summary,case,src,evidence=import_local_success(folder,name)
        else:
            if not archive_path.is_file():raise FileNotFoundError(str(archive_path))
            with tarfile.open(archive_path,"r:gz") as tar:
                root=name+"/"
                exit_code=member_data(tar,root+"worker_exit_code.txt").decode().strip()
                if exit_code!="0":
                    raise ValueError("Condor MadWidth job not successful "+name+
                                     " exit_code="+exit_code)
                summary=json.loads(member_data(tar,root+"summary.json"))
                case=json.loads(member_data(tar,root+"validated_model_LO_widths.json"))
                if (summary.get("status")!=STATUS
                    or summary.get("requested_cases")!=[name]
                    or summary.get("requested_cases_passed") is not True
                    or summary.get("errors")):
                    raise ValueError("F18 Condor job cannot be promoted to successful "+name)
                if len(summary.get("results",[]))!=1 or summary["results"][0]!=case:
                    raise ValueError("Archive summary and per-case physics disagree "+name)
                src={k:summary.get(k) for k in (
                    "MG5_binary_SHA256","original_F17f_report_SHA256",
                    "F14_original_13TeV_CSV_SHA256",
                    "source_independent_CKM_and_lepton_amplitudes_validated_before_run")}
                evidence={"origin":"HTCONDOR",
                    "condor_result_tar_SHA256":
                         hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                    "source_MadWidth_two_body_SHA256":
                         case["provenance"]["MadWidth_two_body"]["output_SHA256"],
                    "source_MadWidth_two_plus_three_body_SHA256":
                         case["provenance"]["MadWidth_two_plus_three"]["output_SHA256"]}
        if case["candidate_id"]!=name or not (
            0<case["BR_H2_H1_Z_model_LO_2plus3"]<=1 and
            0<case["BR_H1_tb_model_LO_2plus3"]<=1):
            raise ValueError("Invalid original benchmark decay result "+name)
        if not all(src[k] for k in ("MG5_binary_SHA256",
                                    "original_F17f_report_SHA256")):
            raise ValueError("Missing immutable F18 provenance "+name)
        if provenance is None:provenance=src
        elif src!=provenance:
            raise ValueError("Condor/local jobs differ in physics/software provenance")
        results.append(case)
        sources[name]=evidence
    if {c["candidate_id"] for c in results}!=set(TGT):
        raise ValueError("Incomplete original cohort")
    report={"status":"F18_THREE_CASES_CONDOR_OR_LOCAL_MERGED_TREE_LO_NOT_ALLOWED",
            "source_campaign_status":STATUS,
            "three_original_benchmarks_LO_MadWidth_completed":True,
            "software_and_flavor_source_provenance":provenance,
            "per_benchmark_source_archives":sources,
            "benchmarks":results,
            "full_tree_MadWidth_2_and_3_body_computed":True,
            "QCD_NLO_or_loop_corrected":False,
            "physical_Zee_model_allowed_or_excluded":None}
    out.mkdir(parents=True,exist_ok=False)
    (out/"F18_CONDOR_three_source_verified.json").write_text(
        json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    with (out/"F18_CONDOR_three_summary.csv").open("w",newline="") as f:
        keys=("candidate_id","Gamma_H2_GeV","Gamma_H1_GeV",
              "BR_H2_H1Z","BR_H1_tb","BR_product",
              "H2_3body_fraction","H1_3body_fraction",
              "13TeV_product_pb_if_F14_pinned")
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for r in results:
            h=r["charged_H_decay_tables"]
            rate=r.get("13TeV_source_F14_LO_widths_cascade",{})
            writer.writerow(dict(candidate_id=r["candidate_id"],
               Gamma_H2_GeV=h["9000037"]["total_GeV"],
               Gamma_H1_GeV=h["37"]["total_GeV"],
               BR_H2_H1Z=r["BR_H2_H1_Z_model_LO_2plus3"],
               BR_H1_tb=r["BR_H1_tb_model_LO_2plus3"],
               BR_product=r["cascade_BR_product_model_LO_2plus3"],
               H2_3body_fraction=h["9000037"]["three_body_fraction"],
               H1_3body_fraction=h["37"]["three_body_fraction"],
               **{"13TeV_product_pb_if_F14_pinned":rate.get(
                   "sigma_times_BR_H2_H1Z_BR_H1_tb_pb","")}))
    print("F18_CONDOR_OR_LOCAL_THREE_CASES_MERGED",True,"QCD_PRECISION",False,
          "FULL_MODEL_ALLOWED",False)
    print("F18_CONDOR_FINAL_JSON",out/"F18_CONDOR_three_source_verified.json")
    print("F18_CONDOR_FINAL_CSV",out/"F18_CONDOR_three_summary.csv")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    merge(a.results_dir,a.output_dir)


if __name__=="__main__":main()

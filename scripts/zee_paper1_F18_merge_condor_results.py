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
from zee_paper1_F17_inspect_real_SARAH_UFO import TGT
from zee_paper1_F18_complete_madwidth_campaign import STATUS


def member_data(archive,name,maxbytes=8_000_000):
    try:item=archive.getmember(name)
    except KeyError as ex:raise ValueError("Missing archived file "+name) from ex
    if not item.isfile() or not 0<=item.size<=maxbytes:
        raise ValueError("Unexpected member size or type "+name)
    stream=archive.extractfile(item)
    if stream is None:raise ValueError("Unreadable archived member "+name)
    return stream.read()


def merge(folder,out):
    folder=Path(folder).expanduser().resolve()
    out=Path(out).expanduser().resolve()
    if out.exists():raise FileExistsError("Refuse overriding old F18 merge")
    results=[]
    provenance=None
    sources={}
    for name in TGT:
        archive_path=folder/("F18_result_"+name+".tar.gz")
        if not archive_path.is_file():raise FileNotFoundError(str(archive_path))
        with tarfile.open(archive_path,"r:gz") as tar:
            root=name+"/"
            exit_code=member_data(tar,root+"worker_exit_code.txt").decode().strip()
            if exit_code!="0":
                raise ValueError("Condor MadWidth job not successful "+name+
                                 " exit_code="+exit_code)
            summary=json.loads(member_data(tar,root+"summary.json"))
            case=json.loads(member_data(tar,root+"validated_model_LO_widths.json"))
            if summary.get("status")!=STATUS or summary.get("requested_cases")!=[name] or (
                summary.get("requested_cases_passed") is not True) or summary.get("errors"):
                raise ValueError("F18 Condor job cannot be promoted to successful "+name)
            if len(summary.get("results",[]))!=1 or summary["results"][0]!=case:
                raise ValueError("Archive summary and per-case physics disagree "+name)
            if case["candidate_id"]!=name or not (
                0<case["BR_H2_H1_Z_model_LO_2plus3"]<=1 and
                0<case["BR_H1_tb_model_LO_2plus3"]<=1):
                raise ValueError("Invalid original benchmark decay result "+name)
            src={"MG5_binary_SHA256":summary.get("MG5_binary_SHA256"),
                 "original_F17f_report_SHA256":summary.get(
                     "original_F17f_report_SHA256"),
                 "F14_original_13TeV_CSV_SHA256":summary.get(
                     "F14_original_13TeV_CSV_SHA256"),
                 "source_independent_CKM_and_lepton_amplitudes_validated_before_run":
                     summary.get("source_independent_CKM_and_lepton_amplitudes_validated_before_run")}
            if not all(src[k] for k in ("MG5_binary_SHA256",
                                        "original_F17f_report_SHA256")):
                raise ValueError("Missing immutable F18 provenance "+name)
            if provenance is None:provenance=src
            elif src!=provenance:
                raise ValueError("Three Condor jobs differ in physics/software provenance")
            results.append(case)
            sources[name]={"condor_result_tar_SHA256":
                hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                "source_MadWidth_two_body_SHA256":
                    case["provenance"]["MadWidth_two_body"]["output_SHA256"],
                "source_MadWidth_two_plus_three_body_SHA256":
                    case["provenance"]["MadWidth_two_plus_three"]["output_SHA256"]}
    if {c["candidate_id"] for c in results}!=set(TGT):
        raise ValueError("Incomplete original cohort")
    report={"status":"F18_HTCONDOR_THREE_CASES_MERGED_TREE_LO_NOT_ALLOWED",
            "source_campaign_status":STATUS,
            "three_original_benchmarks_LO_MadWidth_completed":True,
            "software_and_flavor_source_provenance":provenance,
            "condor_source_archives":sources,
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
    print("F18_CONDOR_THREE_CASES_MERGED",True,"QCD_PRECISION",False,
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

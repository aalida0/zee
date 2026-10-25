#!/usr/bin/env python3
"""F23b: ONE final provenance+physics audit of all 157 completed HyperIso F23 spectra.

Real saved data only. No HyperIso recompilation, new scan, imagined NNLO
95%-CL, or synthetic source reconstruction. Input F22 and source SHA;
193 actual HyperIso observable traces; real gamma endpoints, equal mass;
spectra LHA and Type-II quark coupling checks; independent tagged R3/R6
source references; comprehensive shell-dependent tables and figures.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,re,statistics,subprocess
from collections import Counter
from pathlib import Path

PIN="09d26ac6e71d1528922097a896d15693589f636b"
F22_STATUS="F22_F21C_FULL_COMPLEX_YUKAWA_157_BENCHMARK_FREEZE_NOT_ALLOWED"
F23_STATUS="F23_NATIVE_HYPERISO_TWO_ZEE_HIGGS_CONDITIONAL_V103_NOT_2026_EXCLUSION"
EDGES=(450,700,1000,1400,1900,2500.001)
RESULT="F23_157_two_state_HyperIso_legacy_NNLO_NOT_2026_CL.csv"
TRACE="F23_native_matching_audit_traces.jsonl"
REPORT="F23_conditional_157_model_summary.json"

def sha(path):
    d=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):d.update(chunk)
    return d.hexdigest()
def require(condition,message):
    if not condition:raise ValueError("F23b source/physics failure: "+message)
def approximately(a,b,*,rtol=1e-8,atol=1e-12):
    return math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=rtol,abs_tol=atol)
def number(x,name):
    try: v=float(x)
    except (ValueError,TypeError) as e:raise ValueError("invalid numerical "+name) from e
    require(math.isfinite(v),"nonfinite "+name)
    return v
def summary_pins(f22,f23):
    mf22=json.loads((f22/"F22_freeze_SHA256_manifest.json").read_text())
    mf23=json.loads((f23/REPORT).read_text())
    require(mf22.get("status")==F22_STATUS and mf22.get("preserved_real_complex_neutrino_and_partial_LFV_cases")==157
            and mf22.get("priority_benchmarks")==9 and mf22.get("model_fully_allowed_or_excluded") is None,
            "invalid original F22 full-complex Yukawa provenance")
    require(mf23.get("status")==F23_STATUS and mf23.get("calculations")==157 and mf23.get("priority_inputs")==9
            and mf23.get("physical_Zee_allowed_or_excluded") is None
            and mf23.get("HyperIso_PIN")==PIN
            and mf23.get("all_nine_gamma_and_equal_mass_native_limit_checks") is True,
            "invalid completed real HyperIso source provenance")
    require(mf23.get("source_F22_real_157_freeze_SHA256")==mf22["output_SHA256"],
            "F23 and real F22 independent source manifests mismatch")
    f22_names=("F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz",
               "F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json")
    for n in f22_names:
        require(sha(f22/n)==mf22["output_SHA256"][n],"F22 original source bytes differ "+n)
    for n in (RESULT,TRACE):
        require(sha(f23/n)==mf23["outputs_SHA256"][n],"F23 actual native results bytes differ "+n)
    started=json.loads((f23/"F23_input_source_sha256.json").read_text())
    require(started.get("F22_sha256")==mf22["output_SHA256"]
            and started.get("HyperIso_release_commit_PIN")==PIN
            and started.get("final_model_allowed") is None,
            "F23 original native campaign source start manifest invalid")
    if (f23/"F23_resume_source_sha256.json").exists():
        resumed=json.loads((f23/"F23_resume_source_sha256.json").read_text())
        require(resumed.get("original_F22_sha256")==mf22["output_SHA256"]
                and resumed.get("HyperIso_PIN")==PIN
                and resumed.get("full_model_allowed") is None,
                "F23 resumed C++ scientific source manifests mismatch")
    upstream=f23/"hyperiso-v1.0.3"
    check=subprocess.run(["git","-C",str(upstream),"rev-parse","HEAD"],
                         capture_output=True,text=True,check=True)
    require(check.stdout.strip()==PIN,"HyperIso actual C++ source/tag commit differs")
    return mf22,mf23

def tagged_r6_log(actual,reference):
    pat=re.compile(r"^\s*(C7|C8|C9|C10)\s+matching=\(([-+0-9.eE]+),([-+0-9.eE]+)\)"
                   r"\s+running=\(([-+0-9.eE]+),([-+0-9.eE]+)\)",re.M)
    rows={}
    for label,data in (("real",actual.read_text()),("tag",reference.read_text())):
        dic={m.group(1):tuple(float(m.group(i)) for i in range(2,6)) for m in pat.finditer(data)}
        require(set(dic)=={"C7","C8","C9","C10"},
                "R6 actual or source THDM WC printed operator set incomplete "+label)
        rows[label]=dic
    for name,vals in rows["tag"].items():
        for a,b in zip(rows["real"][name],vals):
            require(approximately(a,b,rtol=2e-5,atol=3e-8),
                    "R6 native Type-II tag NNLO Wilson reference deviates "+name)
    return rows["real"]

def physical_lha(path):
    d={};block=None
    for line in path.read_text().splitlines():
        stripped=line.partition("#")[0].strip()
        if not stripped:continue
        f=stripped.split()
        if f[0].upper()=="BLOCK":
            block=f[1].upper();continue
        if f[0].upper()=="DECAY":
            block=None;continue
        if block not in ("MASS","MINPAR","YU","YD","YE"):continue
        try:
            k=tuple(int(x) for x in f[:-1]);v=float(f[-1])
        except(ValueError,TypeError):continue
        require(math.isfinite(v),"nonfinite LHA scalar source "+str(path))
        require((block,k) not in d,"duplicate LHA physics coefficient "+block+str(k))
        d[block,k]=v
    return d

def math_rank(values):
    n=len(values)
    order=sorted(range(n),key=lambda i:values[i])
    ranks=[0.]*n;k=0
    while k<n:
        j=k+1
        while j<n and values[order[j]]==values[order[k]]:j+=1
        score=(k+1+j)/2.
        for idx in order[k:j]:ranks[idx]=score
        k=j
    return ranks
def correlation(xx,yy):
    if len(xx)<3:return None
    mx=statistics.mean(xx);my=statistics.mean(yy)
    ax=[x-mx for x in xx];ay=[y-my for y in yy]
    q=math.sqrt(sum(x*x for x in ax)*sum(y*y for y in ay))
    return sum(x*y for x,y in zip(ax,ay))/q if q else None
def execute(args):
    f22=Path(args.f22).expanduser().resolve()
    f23=Path(args.f23).expanduser().resolve()
    out=Path(args.output).expanduser().resolve()
    require(not out.exists(),"output already exists; refuse overwrite")
    _,report=summary_pins(f22,f23)
    with gzip.open(f22/"F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz","rt") as f:
        originals=[json.loads(line) for line in f if line.strip()]
    priorities=json.loads((f22/"F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json").read_text())
    require(len(originals)==157 and len(priorities["entries"])==9,
            "frozen 157/9 spectrum benchmark counts changed")
    original_map={r["campaign_key"]:r for r in originals}
    priority=[r["campaign_key"] for r in priorities["entries"]]
    require(len(original_map)==157 and len(set(priority))==9
            and set(priority)<=original_map.keys(),
            "frozen F22 point identities failed uniqueness/source join")
    with (f23/RESULT).open(newline="") as f: rows=list(csv.DictReader(f))
    traces=[json.loads(line) for line in (f23/TRACE).read_text().splitlines() if line.strip()]
    require(len(rows)==157 and len(traces)==36+157,"expected actual 9x4 plus 157 native C++ BR calls")
    keys=set()
    for i,(row,src) in enumerate(zip(rows,originals)):
        key=row["key"]
        require(key not in keys and key==src["campaign_key"],"F23 row/F22 scan identity/order "+str(i))
        keys.add(key)
        orig=src["F21c_ranked_source_csv"]
        for rk,fk in (("m1","mH1_GeV"),("m2","mH2_GeV"),
                      ("tanb","tanbeta"),("gamma","gamma_rad"),
                      ("LO_flavor_x1e4_NOT_CL","analytic_LO_Bsgamma_BR_x1e4_NOT_CL"),
                      ("cascade_included_proxy_NOT_pb","complex_Yukawa_included_cascade_proxy_NOT_MadWidth"),
                      ("partial_LFV_Wgamma_ratio_NOT_CL","partial_LFV_Wgamma_max_ratio_NOT_CL")):
            require(approximately(number(row[rk],key+rk),number(orig[fk],key+fk),rtol=1e-12),
                    "F23/F22 actual model changed "+key+" "+rk)
        require(row["full_model_allowed_or_excluded"]=="UNKNOWN_NOT_EVALUATED"
                and row["is_original_F22_priority"]==str(key in priority),
                "F23 source falsely allowed or priority mislabeled "+key)
        require(0<number(row["legacy_HyperIso_v103_BR_BXs_gamma_conditional"],key)<.1,
                "F23 nonphysical conditional BR "+key)
        require(approximately(number(row["SM_HyperIso_R3_reference_BR"],key),
                              report["R3_SM_BR"]), "SM reference drift "+key)
    require(set(keys)==set(original_map),"F23 157 full exact F22 points missing")

    endpoint={}
    for i,key in enumerate(priority):
        src=original_map[key]["F21c_ranked_source_csv"]
        mass1=number(src["mH1_GeV"],key);mass2=number(src["mH2_GeV"],key)
        original_gamma=number(src["gamma_rad"],key)
        four=traces[4*i:4*i+4]
        require(len(four)==4,"shortened saved real native endpoints")
        light,eq,heavy,heavyzero=[number(z["BR_HyperIso_v103_legacy_NNLO_conditional_NOT_CL"],key) for z in four]
        expected=[(mass1,mass2,0.),(mass1,mass1,original_gamma),
                  (mass1,mass2,math.pi/2),(mass2,mass2,0.)]
        for k,(rec,params) in enumerate(zip(four,expected)):
            require(rec["campaign_key"]==key and rec["trace"]==4*i+k,
                    "native endpoint wrong point/order "+key)
            for field,v in zip(("mass1_input_GeV","mass2_input_GeV","gamma_rad"),params):
                require(approximately(number(rec[field],key+field),v,rtol=1e-12),
                        "wrong original native endpoint value "+key+field)
        require(approximately(light,eq,rtol=1e-7,atol=2e-10)
                and approximately(heavy,heavyzero,rtol=1e-7,atol=2e-10),
                "HyperIso charged benchmark endpoint/equal mass identity "+key)
        endpoint[key]={"pure_H1_TypeII_BR":light,"pure_H2_TypeII_BR":heavy,
                       "H1_equal_mass_BR":eq,"H2_gamma0_BR":heavyzero,
                       "wH2":math.sin(original_gamma)**2}

    scalar_dir=f23/"F23_THDM_quark_only_surrogate_inputs"
    for pos,rec in enumerate(traces):
        require(rec["trace"]==pos,"native trace indices missing or out of order")
        require("n_patches 13" in rec["matching_patch_log"]
                and "FULL_MODEL_ALLOWED UNKNOWN" in rec["matching_patch_log"],
                "original actual native 13 patch and model-allowance status missing")
        source=scalar_dir/f"typeII_for_{pos:05d}.lha"
        require(source.is_file() and sha(source)==rec["LHA_SHA256"],
                "genuine original HyperIso LHA surrogate source missing/modified "+str(pos))
        actual=physical_lha(source)
        tb=number(rec["tanbeta"],"tanbeta trace")
        m1=number(rec["mass1_input_GeV"],"mass1 trace")
        for block,key,v in (("MASS",(37,),m1),("MINPAR",(3,),tb),
                            ("YU",(2,2),1/tb),("YD",(2,2),-tb),
                            ("YE",(2,2),-tb)):
            require((block,key) in actual
                    and approximately(actual[block,key],v,rtol=5e-12),
                    "actual C++ TypeII flavor source not equal F22 "+str(pos)+block)
        if pos>=36:
            row=rows[pos-36]
            require(rec["campaign_key"]==row["key"],"mixed native trace not same F22 point")
            for field,v in (("mass1_input_GeV",number(row["m1"],"mass1")),
                            ("mass2_input_GeV",number(row["m2"],"mass2")),
                            ("gamma_rad",number(row["gamma"],"gamma"))):
                require(approximately(number(rec[field],field),v,rtol=1e-12),
                        "native mixed gamma/mass input mismatch "+row["key"])
            require(approximately(number(rec["BR_HyperIso_v103_legacy_NNLO_conditional_NOT_CL"],"trace BR"),
                                  number(row["legacy_HyperIso_v103_BR_BXs_gamma_conditional"],"CSV BR"),rtol=1e-12),
                    "F23 real native trace/CSV numerical result mismatch "+row["key"])

    real_r6=tagged_r6_log(
        f23/"F23_upstream_R6_single_THDM_NNLO.log",
        f23/"hyperiso-v1.0.3/reproducibility/expected_outputs/wilson_b_thdm_spectrum_nnlo.txt")
    require(approximately(report["R3_SM_BR"],.00032967,rtol=2e-5),
            "tagged HyperIso R3 standard-model reference mismatch")

    # Interpret *conditional* flavor predictions only. Flavor/cascade
    # preference weights cannot be converted to detector sensitivity.
    priority_rows=[];actual={r["key"]:r for r in rows}
    for key in priority:
        rec=actual[key]
        endpoints=endpoint[key]
        flavor=number(rec["legacy_HyperIso_v103_BR_BXs_gamma_conditional"],key)
        w=endpoints["wH2"]
        linear=(1-w)*endpoints["pure_H1_TypeII_BR"]+w*endpoints["pure_H2_TypeII_BR"]
        require(abs(endpoints["pure_H1_TypeII_BR"]-endpoints["pure_H2_TypeII_BR"])>1e-8,
                "single H1/H2 endpoints unexpectedly degenerate for "+key)
        require(abs(flavor-endpoints["pure_H1_TypeII_BR"])>1e-10,
                "nontrivial mixing caused zero physics response "+key)
        priority_rows.append({
           "campaign_key":key,"mH1_GeV":rec["m1"],"mH2_GeV":rec["m2"],
           "tanbeta":rec["tanb"],"gamma_rad":rec["gamma"],
           "wH2_sin2gamma":w,
           "cascade_included_proxy_NOT_pb":rec["cascade_included_proxy_NOT_pb"],
           "HyperIso_v103_two_charged_BR_NOT_2026_CL":flavor,
           "HyperIso_v103_pure_H1_BR":endpoints["pure_H1_TypeII_BR"],
           "HyperIso_v103_pure_H2_BR":endpoints["pure_H2_TypeII_BR"],
           "BR_average_of_single_states_INVALID_PREDICTION":linear,
           "nonlinear_interference_BR_minus_invalid_BR_average":flavor-linear,
           "F19d_2026_center_plus_LO_linearized_BR_x1e4_NOT_CL":rec["LO_flavor_x1e4_NOT_CL"],
           "partial_LFV_Wgamma_ratio_NOT_CL":rec["partial_LFV_Wgamma_ratio_NOT_CL"]})
    by_mass={}
    for low,high in zip(EDGES[:-1],EDGES[1:]):
        shell=[r for r in rows if low<=number(r["m2"],"mH2")<high]
        require(shell,"unexpected empty heavy charged mass shell")
        rates=[number(r["legacy_HyperIso_v103_BR_BXs_gamma_conditional"],"BR") for r in shell]
        cascades=[number(r["cascade_included_proxy_NOT_pb"],"cascade") for r in shell]
        loc=[number(r["LO_flavor_x1e4_NOT_CL"],"LO") for r in shell]
        by_mass[f"{low:g}-{high:g}GeV"]={
          "scalar_plus_LFV_vacuum_triaged_count":len(shell),
          "conditional_legacy_BR_min":min(rates),
          "conditional_legacy_BR_median":statistics.median(rates),
          "conditional_legacy_BR_max":max(rates),
          "max_included_channel_cascade_proxy_NOT_pb":max(cascades),
          "pearson_cascade_vs_legacy_flavor_BR":correlation(cascades,rates),
          "spearman_cascade_vs_legacy_flavor_BR":correlation(math_rank(cascades),math_rank(rates)),
          "spearman_prior_LO_2026_linearized_x1e4_vs_HyperIso_old_BR":
            correlation(math_rank(loc),math_rank(rates)),
        }
    all_rate=[number(r["legacy_HyperIso_v103_BR_BXs_gamma_conditional"],"BR") for r in rows]
    all_cascade=[number(r["cascade_included_proxy_NOT_pb"],"cascade") for r in rows]
    independent_rate_corr=correlation(math_rank(all_rate),math_rank(all_cascade))

    out.mkdir(parents=True,exist_ok=False)
    priority_csv=out/"F23b_9_real_priorities_legacy_flavor_and_nonlinear_interference_NOT_CL.csv"
    with priority_csv.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(priority_rows[0]))
        writer.writeheader();writer.writerows(priority_rows)
    plotted=[]
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xs=[number(r["m2"],"mH2") for r in rows]
        fig,ax=plt.subplots(figsize=(8.1,5.0))
        ax.scatter(xs,[z*1e4 for z in all_rate],s=21,alpha=.7,label="157 frozen F22 points")
        ax.scatter([number(z["mH2_GeV"],"mass") for z in priority_rows],
                   [number(z["HyperIso_v103_two_charged_BR_NOT_2026_CL"],"rate")*1e4
                    for z in priority_rows],marker="*",s=110,label="9 priorities")
        ax.axhline(.00032967*1e4,linestyle="--",label="HyperIso v1.0.3 SM reference")
        ax.set_xlabel(r"$m_{H_2^\pm}$ [GeV]")
        ax.set_ylabel(r"$10^4\,\mathrm{BR}(B\to X_s\gamma)$ (HyperIso v1.0.3)")
        ax.set_title("Conditional historical-scheme result — NOT 2026 exclusion")
        ax.legend(fontsize=8);fig.tight_layout()
        fig.savefig(out/"F23b_heavy_mass_vs_legacy_BR_NOT_2026_CL.pdf");plt.close(fig)
        plotted.append("F23b_heavy_mass_vs_legacy_BR_NOT_2026_CL.pdf")
        fig,ax=plt.subplots(figsize=(8.1,5.0))
        ax.scatter(all_cascade,[z*1e4 for z in all_rate],s=21,alpha=.7)
        for z in priority_rows:
            ax.scatter(number(z["cascade_included_proxy_NOT_pb"],"cascade"),
                       1e4*number(z["HyperIso_v103_two_charged_BR_NOT_2026_CL"],"rate"),
                       marker="*",s=100)
        ax.set_xlabel("Included-channel cascade proxy (NOT cross section)")
        ax.set_ylabel(r"$10^4\,\mathrm{BR}(B\to X_s\gamma)$ (legacy HyperIso)")
        ax.set_title("Frozen F22 flavor-cascade comparison — screened sample only")
        fig.tight_layout()
        fig.savefig(out/"F23b_cascade_vs_legacy_BR_NOT_2026_CL.pdf");plt.close(fig)
        plotted.append("F23b_cascade_vs_legacy_BR_NOT_2026_CL.pdf")
    except ImportError:
        plotted.append("matplotlib_unavailable_no_figures")
    report_out={
       "status":"F23b_NATIVE_F23_157_PHYSICS_SOURCE_AND_NUMERICAL_VALIDATED_CONDITIONAL_NOT_2026_CL",
       "source_f22_model_cohort_sha256":sha(f22/"F22_freeze_SHA256_manifest.json"),
       "source_f23_summary_sha256":sha(f23/REPORT),
       "HyperIso_upstream_source_commit":PIN,
       "frozen_models_analysed":157,"full_complex_fY_source_models":157,
       "original_nine_priority_endpoint_tests_reverified":9,
       "genuine_Cplusplus_matching_calls_checked":len(traces),
       "native_13_matching_patch_trace_matches":len(traces),
       "real_lha_2HDM_frozen_YU_YD_mass_tanbeta_records_checked":len(traces),
       "source_reproduced_Single_TypeII_R6_NNLO_C7_C8_C9_C10":real_r6,
       "tagged_historical_HyperIso_SM_BR":report["R3_SM_BR"],
       "experimental_2026_comparison_or_95CL_performed":False,
       "exact_2026_reference_NNLO_SM_BSM_implemented":False,
       "physical_collider_production_times_cascade_BR_computed":False,
       "all_frozen_point_source_to_cpp_trace_consistent":True,
       "five_mass_shell_descriptive_statistics":by_mass,
       "sample_spearman_cascade_proxy_vs_legacy_flavor_BR":independent_rate_corr,
       "selection_biased_not_sampling_volume":True,
       "precision_F3_SuperIso_cross_code_coeff_residual_resolved":False,
       "full_general_Zee_LFV_conversion_HiggsTools_applied":False,
       "full_model_allowed_or_excluded":None,
       "individual_priority_records":priority_rows,
       "figure_files":plotted,
       "outputs_SHA256":{str(p.name):sha(p) for p in [priority_csv,*[out/p for p in plotted if (out/p).is_file()]]}}
    target=out/"F23b_157_native_trace_source_and_physics_audit_NOT_FULL_ALLOWED.json"
    target.write_text(json.dumps(report_out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F23B_157_SOURCE_AND_NATIVE_TRACE_PHYSICS_AUDIT_PASS",
          "ORIGINAL_FULL",len(rows),"REAL_NATIVE_RUNS",len(traces),
          "PRIORITY_ENDPOINTS",len(priority_rows),"HYPERISO_NATIVE_R6_C7_C8_C9_C10","PASS",
          "FULL_MODEL_ALLOWED",None,flush=True)
    for k,item in by_mass.items():
        print("F23B_MASS_REGION",k,"N",item["scalar_plus_LFV_vacuum_triaged_count"],
              "LEGACY_BR_MIN_MED_MAX",
              item["conditional_legacy_BR_min"],item["conditional_legacy_BR_median"],
              item["conditional_legacy_BR_max"],flush=True)
    for z in priority_rows:
        print("F23B_PRIORITY",z["campaign_key"],
              "M2",z["mH2_GeV"],"CASCADE_PROXY",z["cascade_included_proxy_NOT_pb"],
              "HYPERISO_LEGACY_BR",z["HyperIso_v103_two_charged_BR_NOT_2026_CL"],
              "NONLINEAR_BR_VS_INVALID_AVERAGE",
              z["nonlinear_interference_BR_minus_invalid_BR_average"],flush=True)
    print("F23B_RESULT",target,flush=True)
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--f22",type=Path,required=True)
    a.add_argument("--f23",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    execute(a.parse_args())
if __name__=="__main__":main()

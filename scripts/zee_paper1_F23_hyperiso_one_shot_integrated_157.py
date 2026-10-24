#!/usr/bin/env python3
"""F23 source-pinned SINGLE full HyperIso C++ two-Zee-state B->Xs gamma campaign.

One command clones and builds tagged HyperIso C++/CLI + a native BSM
matching-patch two-charged bridge; reproduces frozen SM R3 and native
THDM R6 references; checks endpoint/equal-mass/single-state degeneracy;
then calculates all 157 F22 true frozen f/Y model spectra (and 9
pre-ranked priors) WITHOUT performing any new model scan.

Conditional 2026-flavor cross-code validation ONLY. NO 95%-CL exclusion.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,os,re,shutil,subprocess,sys
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone

TAG="v1.0.3"
PIN="09d26ac6e71d1528922097a896d15693589f636b"
STATUS="F23_NATIVE_HYPERISO_TWO_ZEE_HIGGS_CONDITIONAL_V103_NOT_2026_EXCLUSION"
DEFAULT_REFERENCE_BR=0.00032967

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for x in iter(lambda:f.read(1048576),b""):h.update(x)
    return h.hexdigest()
def run(argv,*,cwd=None,logfile=None):
    cmd=list(map(str,argv))
    p=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,text=True)
    if logfile is not None:
        Path(logfile).write_text("$ "+" ".join(cmd)+"\n"+p.stdout)
    if p.returncode:
        raise RuntimeError(f"F23 command failed exit={p.returncode} cmd={cmd}\n"+
                           p.stdout[-8000:])
    return p.stdout
def verify_f22(source):
    paths={
        "manifest":source/"F22_freeze_SHA256_manifest.json",
        "priority":source/"F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json",
        "full":source/"F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz"}
    for key,p in paths.items():
        if not p.is_file():raise FileNotFoundError(f"Missing F22 {key}: {p}")
    m=json.loads(paths["manifest"].read_text())
    if (m.get("status")!="F22_F21C_FULL_COMPLEX_YUKAWA_157_BENCHMARK_FREEZE_NOT_ALLOWED"
        or m.get("model_fully_allowed_or_excluded") is not None
        or m.get("preserved_real_complex_neutrino_and_partial_LFV_cases")!=157
        or m.get("priority_benchmarks")!=9
        or m.get("complete_2026_Bsgamma_or_complete_general_Zee_LFV") is not False):
        raise ValueError("F22 source manifest missing frozen physical constraints")
    for key in ("full","priority"):
        if sha(paths[key])!=m["output_SHA256"].get(paths[key].name):
            raise ValueError("F22 input integrity SHA mismatch "+str(paths[key]))
    priority=json.loads(paths["priority"].read_text())
    if priority.get("status")!=m["status"] or len(priority.get("entries",[]))!=9:
        raise ValueError("F22 nine priority records invalid")
    with gzip.open(paths["full"],"rt") as f:
        full=[json.loads(line) for line in f if line.strip()]
    if len(full)!=157:raise ValueError("F22 unexpected real f/Y model count")
    def spectrum(entry):
        if (entry.get("fully_Zee_allowed_or_excluded") is not None
          or entry.get("physical_LHC_cross_section_pb_evaluated") is not False
          or entry.get("full_HiggsTools_applied") is not False):
            raise ValueError("F22 physically allowed false label")
        raw=entry["F21c_ranked_source_csv"]
        return {
          "key":entry["campaign_key"],
          "m1":float(raw["mH1_GeV"]),
          "m2":float(raw["mH2_GeV"]),
          "tanb":float(raw["tanbeta"]),
          "gamma":float(raw["gamma_rad"]),
          "LO_flavor_x1e4_NOT_CL":float(raw["analytic_LO_Bsgamma_BR_x1e4_NOT_CL"]),
          "cascade_included_proxy_NOT_pb":float(raw["complex_Yukawa_included_cascade_proxy_NOT_MadWidth"]),
          "partial_LFV_Wgamma_ratio_NOT_CL":float(raw["partial_LFV_Wgamma_max_ratio_NOT_CL"]),
        }
    good=[spectrum(x) for x in full]
    keys={x["key"] for x in good}
    if len(keys)!=157:raise ValueError("F23 repeated original F22 source model")
    chosen=[spectrum(x) for x in priority["entries"]]
    if len({x["key"] for x in chosen})!=9 or not set(x["key"] for x in chosen)<=keys:
        raise ValueError("F22 priorities absent from original cohort")
    for item in good:
        if not(200<=item["m1"]<=1200.01 and 450<=item["m2"]<=2500.01
            and item["m2"]>item["m1"]
            and .7<=item["tanb"]<=35.001
            and 0<=item["gamma"]<=math.pi/2):
            raise ValueError("F22 point is not in published scan window")
    return paths,m,good,chosen

def update_spectrum(reference,mass,tanb):
    """Prepare THDM *quark-flavor-only* surrogate: mass H1 + Type-II quark factors.

    Keep every SM/flavor nuisance constant from tagged 2HDMC reference.
    The model is NOT a reconstructed two-state Zee potential; ONLY quark
    charged matching and b->s gamma should be interpreted.
    """
    lines=Path(reference).read_text().splitlines(keepends=True)
    now=None
    counts=Counter()
    out=[]
    for line in lines:
        hit=re.match(r"^\s*BLOCK\s+([A-Z_0-9]+)",line,re.I)
        if hit:now=hit.group(1).upper()
        if re.match(r"^\s*DECAY\s",line,re.I):now=None
        body,_,comment=line.partition("#")
        toks=body.split()
        if now=="MINPAR" and toks and toks[0]=="3":
            line=f"    3 {tanb:.16e} # F23 native TypeII tanbeta\n"
            counts["tanb"]+=1
        if now=="MASS" and toks and toks[0]=="37":
            line=f"   37 {mass:.16e} # F23 charged scalar H1 baseline\n"
            counts["mass"]+=1
        if now in ("UCOUPL","DCOUPL") and len(toks)>2 and toks[0]==toks[1] and toks[0] in ("1","2","3"):
            v=1/tanb if now=="UCOUPL" else -tanb
            line=f"  {toks[0]} {toks[1]} {v:.16e} # F23 matching TypeII {now}\n"
            counts[now]+=1
        out.append(line)
    if counts["tanb"]!=1 or counts["mass"]!=1 or counts["UCOUPL"]!=3 or counts["DCOUPL"]!=3:
        raise ValueError("HyperIso tagged THDM sample no longer has required THDM source inputs "+str(counts))
    # THDMParametersHelper explicitly consumes YU/YD and YE blocks.
    # These Type-II diagonal couplings are set for full provenance;
    # do not rely on a neutral-sector EFT normalization to infer them.
    out.append("\nBLOCK YU # F23 direct quark charged-Higgs matching Yukawa ratios\n")
    for i in range(1,4):out.append(f" {i} {i} {1/tanb:.16e}\n")
    out.append("BLOCK YD # F23 direct quark charged-Higgs matching Yukawa ratios\n")
    for i in range(1,4):out.append(f" {i} {i} {-tanb:.16e}\n")
    out.append("BLOCK YE # F23 charged-lepton factors copied Type-II reference\n")
    for i in range(1,4):out.append(f" {i} {i} {-tanb:.16e}\n")
    return "".join(out)

def build_upstream(work,repo_root):
    upstream=work/"hyperiso-v1.0.3"
    if not upstream.exists():
        run(["git","clone","--quiet","--branch",TAG,"--depth","1",
            "https://github.com/Hyperiso/Hyperiso.git",upstream],
            logfile=work/"F23_clone.log")
    actual=run(["git","rev-parse","HEAD"],cwd=upstream).strip()
    if actual!=PIN or run(["git","status","--porcelain"],cwd=upstream).strip():
        raise ValueError("HyperIso v1.0.3 source commit/clean-tree mismatch "+actual)
    prefix=work/"hyperiso-install"
    source=upstream/"Hyperiso/Hyperiso/core"
    build=work/"hyperiso-cmake-build"
    # A failed bridge compilation must not rebuild the entire source-
    # verified upstream HyperIso project. The prior real run already
    # configured/compiled/installed the pinned C++ core and CLI.
    installed=list(prefix.rglob("HyperisoConfig.cmake")) if prefix.exists() else []
    cli_existing=[p for p in build.rglob("hyperiso-ui")
                  if p.is_file() and os.access(p,os.X_OK)] if build.exists() else []
    if len(installed)==1 and len(cli_existing)==1 and (work/"F23_cmake_HyperIso_build.log").exists():
        print("F23_UPSTREAM_PINNED_HYPERISO_BUILD_REUSED",str(build),flush=True)
    else:
        run(["cmake","-S",source,"-B",build,"-G","Ninja",
             "-DCMAKE_BUILD_TYPE=Release","-DBUILD_WITH_CLI=ON",
             "-DBUILD_WITH_MARTY=OFF","-DBUILD_WITH_SOFTSUSY=OFF",
             "-DBUILD_WITH_PYTHON=OFF",
             "-DCMAKE_INSTALL_PREFIX="+str(prefix)],
             logfile=work/"F23_cmake_HyperIso_configure.log")
        run(["cmake","--build",build,"--parallel","2"],
             logfile=work/"F23_cmake_HyperIso_build.log")
        run(["cmake","--install",build],
             logfile=work/"F23_cmake_HyperIso_install.log")
    own=work/"zee-native-cmake-build"
    run(["cmake","-S",repo_root/"cpp/F23_hyperiso","-B",own,"-G","Ninja",
         "-DCMAKE_BUILD_TYPE=Release",
         "-DCMAKE_PREFIX_PATH="+str(prefix)],
         logfile=work/"F23_cmake_Zee_bridge_configure.log")
    run(["cmake","--build",own,"--parallel","2"],
         logfile=work/"F23_cmake_Zee_bridge_build.log")
    binary=own/"zee_hyperiso_two_state"
    if not binary.is_file():raise ValueError("F23 C++ observable binary missing")
    cli=list(build.rglob("hyperiso-ui"))
    cli=[p for p in cli if p.is_file() and os.access(p,os.X_OK)]
    if len(cli)!=1:raise ValueError("HyperIso native CLI hyperiso-ui missing/ambiguous "+str(cli))
    return upstream,binary,cli[0]

def extract_br(output):
    hits=re.findall(r"BR_B__Xs_gamma\s*=\s*([0-9.eE+\-]+)",output)
    if not hits:raise ValueError("F23 original upstream BR_B__Xs_gamma reference output not parsed")
    return float(hits[-1])

def parse_native(output):
    found=[x for x in output.splitlines() if x.startswith(
         "F23_HYPERISO_V103_TWO_STATE_CONDITIONAL")]
    if len(found)!=1:raise ValueError("F23 actual C++ matching-patch output missing "+output[-1200:])
    a=found[0].split()
    if a[0]!="F23_HYPERISO_V103_TWO_STATE_CONDITIONAL" or len(a)%2!=1:
        raise ValueError("F23 malformed native output")
    data=dict(zip(a[1::2],a[2::2]))
    if data.get("FULL_MODEL_ALLOWED")!="UNKNOWN" or int(data["n_patches"])!=13:
        raise ValueError("F23 native patch count or physically allowed status incorrect")
    br=float(data["BR_B_XS_GAMMA"])
    if not math.isfinite(br) or br<1e-9 or br>0.1:
        raise ValueError("F23 impossible or zero native branching ratio")
    return br,data

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--f22-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--resume",action="store_true",
                    help="Continue interrupted F23 in its existing source-verified output; never overwrite finished calculations")
    args=ap.parse_args()
    repo=args.repo.expanduser().resolve()
    path=args.output.expanduser().resolve()
    _,manifest,points,priorities=verify_f22(args.f22_dir.expanduser().resolve())
    if not(repo/"cpp/F23_hyperiso/zee_hyperiso_two_state.cpp").is_file():
        raise FileNotFoundError("Missing F23 C++ bridge in Zee repository")
    if args.resume:
        if not path.is_dir():
            raise FileNotFoundError("F23 resume requested but prior build/results directory absent")
        if (path/"F23_conditional_157_model_summary.json").exists():
            raise FileExistsError("F23 finished run is immutable; refuse to resume/overwrite")
        p0=path/"F23_input_source_sha256.json"
        if not p0.is_file():
            raise ValueError("F23 resume missing original immutable SHA manifest")
        prior=json.loads(p0.read_text())
        if (prior.get("F22_sha256")!=manifest["output_SHA256"]
            or prior.get("HyperIso_release_commit_PIN")!=PIN
            or prior.get("final_model_allowed") is not None):
            raise ValueError("F23 resume original data source or version mismatch")
        (path/"F23_resume_source_sha256.json").write_text(json.dumps({
            "original_source_F23_Cpp_SHA256":prior["F23_Cpp_SHA256"],
            "resumed_F23_Cpp_SHA256":sha(repo/"cpp/F23_hyperiso/zee_hyperiso_two_state.cpp"),
            "resumed_F23_campaign_SHA256":sha(__file__),
            "original_F22_sha256":manifest["output_SHA256"],
            "HyperIso_PIN":PIN,"full_model_allowed":None},
            indent=2,sort_keys=True)+"\n")
        print("F23_RESUME_SOURCE_AUTHENTICATED_BUILD_DIRECTORY",path,flush=True)
    else:
        if path.exists():raise FileExistsError("F23 refuses to overwrite previous results")
        path.mkdir(parents=True,exist_ok=False)
        (path/"F23_input_source_sha256.json").write_text(json.dumps({
            "F22_sha256":manifest["output_SHA256"],
            "F23_Cpp_SHA256":sha(repo/"cpp/F23_hyperiso/zee_hyperiso_two_state.cpp"),
            "F23_campaign_SHA256":sha(__file__),
            "HyperIso_release_commit_PIN":PIN,
            "final_model_allowed":None},indent=2,sort_keys=True)+"\n")
    upstream,binary,cli=build_upstream(path,repo)
    print("F23_UPSTREAM_HYPERISO_CLONE_BUILD_OK",PIN,flush=True)
    ref=upstream/"reproducibility"
    sm=ref/"inputs/sm_reference.flha"
    th=ref/"inputs/thdm_reference.lha"
    log=run([cli,"observable","summary","--model","SM",
          "--lha",sm,"--observables","BR_B__Xs_gamma","--order","NNLO"],
          logfile=path/"F23_upstream_R3_SM_NNLO.log")
    br0=extract_br(log)
    if not math.isclose(br0,DEFAULT_REFERENCE_BR,rel_tol=.00015,abs_tol=1e-8):
        raise ValueError("F23 frozen tagged SM R3 reference BR disagreement "+str(br0))
    run([cli,"wilson","summary","--model","THDM","--lha",th,
        "--spectrum","true","--contribution","BSM",
        "--groups","BCoefficients","--coeffs","C7,C8,C9,C10",
        "--qmatch","81","--q","81","--order","NNLO"],
        logfile=path/"F23_upstream_R6_single_THDM_NNLO.log")
    print("F23_TAGGED_UPSTREAM_REFERENCE_R3_AND_R6_PASS SM_BR",br0,flush=True)
    spectra_dir=path/"F23_THDM_quark_only_surrogate_inputs"
    spectra_dir.mkdir(exist_ok=args.resume)
    if args.resume and any(spectra_dir.iterdir()):
        raise ValueError("F23 resume supports only source/build-stage failure before first native physics computation")
    traces=[]
    def calc(point,m1=None,m2=None,gamma=None,trace=False):
        m1=point["m1"] if m1 is None else m1
        m2=point["m2"] if m2 is None else m2
        gamma=point["gamma"] if gamma is None else gamma
        # Each native call is a fresh process because HyperIso has
        # singleton model/QCD parameter managers.
        number=len(traces)
        source=spectra_dir/f"typeII_for_{number:05d}.lha"
        source.write_text(update_spectrum(th,m1,point["tanb"]))
        output=run([binary,source,m1,m2,point["tanb"],gamma])
        br,fields=parse_native(output)
        traces.append({
            "trace":number,"campaign_key":point["key"],"mass1_input_GeV":m1,
            "mass2_input_GeV":m2,"tanbeta":point["tanb"],"gamma_rad":gamma,
            "BR_HyperIso_v103_legacy_NNLO_conditional_NOT_CL":br,
            "matching_patch_log":output[-550:],"LHA_SHA256":sha(source)})
        return br
    # ENDPOINT/DEGENERACY tests with real tagged native observable,
    # not a synthetic Python formula or algebra tautology.
    for ix,p in enumerate(priorities):
        zero=calc(p,gamma=0.)
        eq=calc(p,m2=p["m1"],gamma=p["gamma"])
        pi2=calc(p,gamma=math.pi/2)
        heavy0=calc(p,m1=p["m2"],gamma=0.)
        scale=1e-7
        if not math.isclose(zero,eq,rel_tol=scale,abs_tol=2e-10):
            raise ValueError("F23 equal mass / gamma zero checks fail for "+p["key"])
        if not math.isclose(pi2,heavy0,rel_tol=scale,abs_tol=2e-10):
            raise ValueError("F23 pi/2 limit disagrees with native single H2 "+p["key"])
        print("F23_NATIVE_ENDPOINTS_PASS",ix+1,"/9",p["key"],
              "single_light",zero,"single_heavy",heavy0,flush=True)
    print("F23_NINE_REAL_F22_ENDPOINT_AND_EQUAL_MASS_CHECKS_PASS",flush=True)
    complete=[]
    prior_keys={x["key"] for x in priorities}
    for ix,p in enumerate(points,1):
        br=calc(p)
        complete.append({**p,
          "legacy_HyperIso_v103_BR_BXs_gamma_conditional":br,
          "is_original_F22_priority":p["key"] in prior_keys,
          "SM_HyperIso_R3_reference_BR":br0,
          "full_model_allowed_or_excluded":"UNKNOWN_NOT_EVALUATED"})
        if ix%25==0 or ix==len(points):
            print("F23_NNLO_TWO_CHARGED_PROGRESS",ix,"/157",flush=True)
    if len(complete)!=157 or len([x for x in complete if x["is_original_F22_priority"]])!=9:
        raise ValueError("F23 full source-locked cohort completeness failure")
    summary_csv=path/"F23_157_two_state_HyperIso_legacy_NNLO_NOT_2026_CL.csv"
    with summary_csv.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(complete[0]))
        writer.writeheader();writer.writerows(complete)
    with (path/"F23_native_matching_audit_traces.jsonl").open("w") as f:
        for t in traces:f.write(json.dumps(t,sort_keys=True,allow_nan=False)+"\n")
    bins=[450,700,1000,1400,1900,2500.001]
    metrics={}
    for a,b in zip(bins[:-1],bins[1:]):
        subset=[p for p in complete if a<=p["m2"]<b]
        metrics[f"{a:g}-{b:g}GeV"]={
            "n":len(subset),
            "legacy_br_min":min(z["legacy_HyperIso_v103_BR_BXs_gamma_conditional"] for z in subset),
            "legacy_br_max":max(z["legacy_HyperIso_v103_BR_BXs_gamma_conditional"] for z in subset)}
    report={
      "status":STATUS,"calculations":157,"priority_inputs":9,
      "HyperIso_tag":TAG,"HyperIso_PIN":PIN,
      "source_F22_real_157_freeze_SHA256":manifest["output_SHA256"],
      "R3_SM_BR":br0,"R3_original_reference_BR":DEFAULT_REFERENCE_BR,
      "upstream_R6_THDM_single_WC_regression_executed":True,
      "all_nine_gamma_and_equal_mass_native_limit_checks":True,
      "two_state_HyperIso_NNLO_BR_region_summary":metrics,
      "only_CPconserving_TypeII_quark_Zee_ansatz":True,
      "full_precision_2026_SM_plus_BSM_matching_implemented":False,
      "full_CP_phases_general_Zee_LFV_and_2026_BXs_95CL":False,
      "independent_theory_vs_SuperIso":False,
      "physical_Zee_allowed_or_excluded":None,
      "outputs_SHA256":{str(p.name):sha(p) for p in [
         summary_csv,path/"F23_native_matching_audit_traces.jsonl"]}}
    (path/"F23_conditional_157_model_summary.json").write_text(json.dumps(
         report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F23_FULL_NATIVE_HYPERISO_TWO_ZEE_CHARGED_DONE",
          "REAL_MODELS",157,"PHYSICAL_95CL",None,
          "R3_SM",br0,flush=True)
    print("F23_RESULT",summary_csv,flush=True)
    print("F23_CONDITIONAL_SUMMARY",path/"F23_conditional_157_model_summary.json")
if __name__=="__main__":main()

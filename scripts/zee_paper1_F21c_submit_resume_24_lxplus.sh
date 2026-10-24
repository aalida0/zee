#!/usr/bin/env bash
# Resume F21b saved scalar scans using 24 CERN Condor jobs.
# Immutable original 24 x 10k scalar-screen outputs are NEVER rerun.
set -Eeuo pipefail
old="$HOME/zee_F21b_wide_stratified_24_20261024"
old_eos="/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21b_wide_24shards_20261024"
run="$HOME/zee_F21c_resume_24_20261025"
eos="/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21c_resumed_24shards_20261025"
[[ ! -e "$run" && ! -e "$eos" ]] || {
  echo "F21C_REFUSE_OVERWRITE_EXISTING $run $eos" >&2; exit 2; }
[[ -d "$old" && -s "$HOME/F21_scripts_bundle.tar.gz" &&
   -s "$HOME/zee_paper1_F21c_resume_worker.sh" ]] || {
  echo "F21C_INPUT_OR_NEW_WORKER_MISSING" >&2; exit 2; }
for k in F18.json F19.json F19b.json F19c.json F19d.json F20scalar.csv F20summary.json; do
  [[ -s "$old/$k" ]] || { echo "F21C_MISSING_SOURCE $k" >&2; exit 2; }
done
for n in {0..23}; do
  [[ -s "$old_eos/F21_result_shard_$n.tar.gz" ]] || {
    echo "F21C_MISSING_PRECOMPUTED_ORIGINAL_SCALAR_ARCHIVE $n" >&2;exit 2; }
done
# Source-hash check of all 24 ORIGINAL scalar result archives and
# shortlist field fix BEFORE submitting any Condor work.
tmp="$(mktemp -d "$HOME/.F21c_source_preflight_XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
tar -xzf "$HOME/F21_scripts_bundle.tar.gz" -C "$tmp"
export F21C_OLD="$old" F21C_OLD_EOS="$old_eos" F21C_TMP="$tmp"
PYTHONPATH="$tmp/scripts" python3 - <<'PY'
from pathlib import Path
import argparse,collections,os,hashlib
from zee_paper1_F21c_resume_saved_scalar_archive import (
    verify,f20_source,original_scalar_archive,select_stratified,scalar_row)
old=Path(os.environ["F21C_OLD"]);eos=Path(os.environ["F21C_OLD_EOS"])
args=lambda shard:argparse.Namespace(
    **{k:old/(k[0].upper()+k[1:]+".json") for k in ("f18","f19","f19b","f19c","f19d")},
    f20_csv=old/"F20scalar.csv",f20_summary=old/"F20summary.json",
    original_scalar_archive=eos/f"F21_result_shard_{shard}.tar.gz",
    shard=shard,global_draws=6000,local_draws=4000,quad=64,
    fits=40,vacuum=12,vacuum_starts=64)
x=args(0);verify(x.f18,x.f19,x.f19b,x.f19c,x.f19d)
pool,_=f20_source(x.f20_csv,x.f20_summary)
counts=collections.Counter();tot=0
for n in range(24):
    rows,_,raw,originalsha=original_scalar_archive(args(n))
    selected=select_stratified(rows,40)
    if not selected:
        raise ValueError("F21c cannot select any original physics point shard "+str(n))
    p=scalar_row(selected[0])
    assert all(k in p for k in ("mH1","mH2","beta","gamma"))
    for r in rows:counts[int(r["mH2_stratum"])]+=1
    tot+=len(rows)
    print("F21C_PREFLIGHT_SHARD",n,"SCREENED",len(rows),"FIT_SELECTION",len(selected),
          "ARCHIVE_SHA256",originalsha,flush=True)
print("F21C_24_ORIGINAL_SCREENED_SCALAR_ARCHIVES_AND_SHORTLIST_PASS",
      "SOURCE_F20",len(pool),"RESCUED_DISTINCT_RECORDS",tot,
      "HEAVY_MASS_SHELLS",dict(sorted(counts.items())),flush=True)
PY
rm -rf "$tmp"
trap - EXIT
mkdir -p "$run/logs" "$eos"
cp "$HOME/F21_scripts_bundle.tar.gz" "$run/"
cp "$HOME/zee_paper1_F21c_resume_worker.sh" "$run/F21c_worker.sh"
chmod +x "$run/F21c_worker.sh"
for f in F18.json F19.json F19b.json F19c.json F19d.json F20scalar.csv F20summary.json; do
  cp "$old/$f" "$run/$f"
done
for i in {0..23}; do
  cp "$old_eos/F21_result_shard_$i.tar.gz" "$run/F21_result_shard_$i.tar.gz"
done
(cd "$run";sha256sum F*.json F20scalar.csv F21_result_shard_*.tar.gz F21_scripts_bundle.tar.gz F21c_worker.sh >F21c_original_inputs_SHA256.txt)
cat >"$run/F21c_resume_24.sub" <<EOF
universe = vanilla
executable = F21c_worker.sh
arguments = \$(shard)
request_cpus = 2
request_memory = 12288MB
request_disk = 12000000KB
+MaxRuntime = 86400
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = F21_scripts_bundle.tar.gz,F18.json,F19.json,F19b.json,F19c.json,F19d.json,F20scalar.csv,F20summary.json,F21_result_shard_\$(shard).tar.gz
transfer_output_files = F21c_resumed_shard_\$(shard).tar.gz
output_destination = root://eosuser.cern.ch/${eos}/
output = logs/F21c_\$(ClusterId).\$(ProcId)_\$(shard).out
error = logs/F21c_\$(ClusterId).\$(ProcId)_\$(shard).err
log = logs/F21c_\$(ClusterId).log
queue shard from (
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
)
EOF
cd "$run"
condor_submit F21c_resume_24.sub
echo "F21C_SUBMITTED_RESCUE_ONLY_COMPLEX_NEUTRINO_LFV_VACUUM_24_SHARDS"
echo "F21C_ORIGINAL_240K_SCALAR_PROPOSALS_NOT_RECOMPUTED"
echo "F21C_EOS $eos"

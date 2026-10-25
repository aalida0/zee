# F21c — Recover real 240k-proposal scalar outputs from failed F21b

**Root cause (25 October 2026):** All 24 F21b HTCondor jobs progressed
past `F21_WIDE_all_scalar_LO_screen_NOT_ALLOWED.csv` serialization
and then failed in `select_stratified(records,a.fits)` because the
selector requested the nonexistent
`cascade_included_nonleptonic_proxy_NOT_MadWidth` while
`gateB4_adaptive_zee_scalar_scan.make_record()` returns the real
`production_weighted_nonleptonic_cascade_upper_proxy`. This is a
Python column-name mismatch, **not** a physics exclusion. The
failure traceback matches all 24 jobs; the no-data-loss opportunity
is to recover their already computed scalar screens and finish only
neutrino/LFV/vacuum, not to waste another 240k-proposal Monte Carlo.

The original saved tarballs are under
`/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21b_wide_24shards_20261024/F21_result_shard_{0..23}.tar.gz`
and contain `results/F21_shard_N/F21_manifest_start.json` and
`results/F21_shard_N/F21_WIDE_all_scalar_LO_screen_NOT_ALLOWED.csv`
produced **before** the bad shortlist selection. Since stage
statistics were dumped AFTER the crashing shortlist statement, the
complete proposal rejection counts and per-mass-bin attempt counts
were NOT saved; F21c marks them unavailable rather than fabricating
them. However, the original *surviving scalar records*, their physical
parameter values, and five heavy-mass-bin occupancy are retained
in full. The 10k proposals per shard have original manifest evidence.

The F21c resume driver performs:
- exact SHA joins of preserved real F18/F19/F19b/F19c/F19d/F20,
  and each original F21b scalar-start manifest;
- every scalar row source schema and physical-bounds check;
- independent BFB + correlated scalar STU reevaluation at three
  saved spectra per original 24 archive (72 replays total);
- selection of mass-stratified spectra using the corrected B4
  nonleptonic upper proxy field;
- original unchanged F21 downstream fixed-NO complex `f,Y`,
  coherently calculated **partial** LFV including W-photon Barr-Zee,
  included-channel lepton-width-adjusted cascade, and 64-start C5
  tree-vacuum witness subset;
- original scalar CSV bytes saved UNMODIFIED into recovery output,
  with original failed EOS archive SHA and reproducible new
  downstream RNG seed (the exact prior RNG stream was consumed by
  the missing 10k draws and cannot be reconstructed without rerun).

**No full model exclusions, fully allowed points, certified global
vacuum, modern higher-order b->s gamma or actual collider cross
sections result from F21c.** This is a scientifically scoped
source-retentive continuation, not a new scalar scan.

## Ubuntu: update and transfer one source bundle plus three small scripts

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only
tar -czf ~/F21_scripts_bundle.tar.gz scripts
scp ~/F21_scripts_bundle.tar.gz \
 scripts/zee_paper1_F21c_resume_worker.sh \
 scripts/zee_paper1_F21c_submit_resume_24_lxplus.sh \
 scripts/zee_paper1_F21c_merge_24_resumed.py \
 aalida@lxplus.cern.ch:~/
```

The F21c submission preflight verifies **ALL 24** actual scalar
archives and all original F18-F20 source pins. It also tests
the corrected mass-stratified selector and scalar-spectrum unpacker.
Any discrepancy stops before creating a new HTCondor job.

## CERN: one preflight and only the missing calculation stages

```bash
bash ~/zee_paper1_F21c_submit_resume_24_lxplus.sh
```

Success marker before any submission:
`F21C_24_ORIGINAL_SCREENED_SCALAR_ARCHIVES_AND_SHORTLIST_PASS`.

Immutable NEW production workspace:
`~/zee_F21c_resume_24_20261025`.
Immutable NEW EOS output:
`/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21c_resumed_24shards_20261025`.
The original F21b failed archives stay untouched.

Only 24 x up-to-40 complex (f,Y) fixed-NO/partial LFV and
24 x up-to-12 C5 multistart vacuum searches are run. No new
240k scalar proposals, no new B4 scalar mass walk.

## CERN: merge ONLY after 24 success markers are written

```bash
export F21C_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21c_resumed_24shards_20261025
python3 ~/zee_paper1_F21c_merge_24_resumed.py \
 --eos "$F21C_EOS" \
 --out "$HOME/zee_F21c_saved_240k_merged_20261025"
cat "$HOME/zee_F21c_saved_240k_merged_20261025/F21_WIDE_PRODUCTION_summary_NOT_ALLOWED.json"
```

The merger checks each archive's **internal** physics exit marker,
recovered original scalar CSV SHA, original five-source provenance,
coherent fixed-NO partial LFV/charged spectra records, and vacuum
outcome fields. New figures/shortlists are exploratory screens only.

After the recovered full wide scan, STOP scan proliferation:
implement consistent two-charged higher-order B->Xs gamma, bounded
full coherent LFV including conversion, and five-scalar HiggsTools
plus QCD-corrected real production `sigma x BR` for representative
traced points.

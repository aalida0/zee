# D14 scans on UChicago AF — compact runbook

These are the commands used for the 20k heavy-spectrum pass and the selected-point D9B + HiggsTools follow-up. Run from the AF login node; **submit Condor from `/home`**, store scan data under `/data`. Use a fresh output directory for each run (the generator and collector do not overwrite).

## Environment and source

```bash
source ~/zee/venvs/d14-py39/bin/activate
cd ~/zee/workspaces/zee-d14-af
git status --short
git fetch origin feature/zee-d14-integrated-scan
git merge --ff-only FETCH_HEAD
git rev-parse HEAD
```

The heavy scan used source commit `d45f179870fa93fabe9bc137b753cdfd2cf0478f` and `module14/heavy_scan_config.json` (20,000 proposals / 80 shards).

## 1. Generate and submit a first-pass scan

```bash
RUNROOT="/data/$USER/zee/d14_heavy_20k"
BATCH="$HOME/zee/condor/d14_heavy_20k"
mkdir -p "$RUNROOT"

python -m module14.scan generate \
  --config module14/heavy_scan_config.json --output "$RUNROOT/scan"

cat > "$RUNROOT/settings.json" <<'JSON'
{"families":2,"perturbativity_limit":3.5449077018110318,
 "lfv":true,"lfv_tree":false,"bsgamma":false,"higgs":false}
JSON

shards=()
for s in "$RUNROOT"/scan/shard_*.jsonl; do shards+=(--shard "$s"); done
python module14/condor/prepare.py \
  --commit HEAD --config module14/heavy_scan_config.json \
  --job-settings "$RUNROOT/settings.json" "${shards[@]}" --output "$BATCH"

cd "$BATCH"
sed -i '/^getenv = FALSE$/a environment = "PATH=/home/aalida/zee/venvs/d14-py39/bin:/usr/bin:/bin"' d14.sub
condor_submit -dry-run dryrun.ads d14.sub
condor_submit d14.sub
condor_q "$USER"
```

## 2. Verify and collect any completed batch

For the heavy first pass use `RUNROOT=/data/$USER/zee/d14_heavy_20k` and `BATCH=$HOME/zee/condor/d14_heavy_20k`; for the selected-point follow-up use `FOLLOW=/data/$USER/zee/d14_heavy_physics_225` and `BATCH=$HOME/zee/condor/d14_heavy_physics_225`.

```bash
cd ~/zee/workspaces/zee-d14-af
source ~/zee/venvs/d14-py39/bin/activate
FOLLOW="/data/$USER/zee/d14_heavy_physics_225"
BATCH="$HOME/zee/condor/d14_heavy_physics_225"

# Expected for this follow-up: 9 result files and 9 receipts.
find "$BATCH/results" -maxdepth 1 -name '*.jsonl' | wc -l
find "$BATCH/receipts" -maxdepth 1 -name '*.json' | wc -l
grep -nEi 'traceback|exception|error' "$BATCH"/logs/*.err || true

# `bash -s --` reads the heredoc as the script; `bash -` alone does NOT.
bash -s -- "$FOLLOW" "$BATCH" <<'BASH'
set -euo pipefail
shopt -s nullglob
FOLLOW="$1"
BATCH="$2"
parts=()
for shard in "$FOLLOW"/scan/shard_*.jsonl; do
    name="${shard##*/}"
    outs=( "$BATCH/results/$name".*.jsonl )
    recs=( "$BATCH/receipts/$name".*.json )
    (( ${#outs[@]} == 1 && ${#recs[@]} == 1 )) || { echo "Missing/duplicate $name"; exit 1; }
    parts+=(--part "$shard" "${outs[0]}" "${recs[0]}")
done
python -m module14.collect \
  --manifest "$FOLLOW/scan/manifest.jsonl" \
  --config "$FOLLOW/config.json" "${parts[@]}" \
  --source-commit "$(cat "$BATCH/source_commit.txt")" \
  --source-bundle-sha256 "$(cut -d' ' -f1 "$BATCH/bundle.sha256")" \
  --output "$FOLLOW/physics_225_report.json"
echo "HEAVY PHYSICS COLLECTION: PASS"
BASH
```

The collector checks manifest IDs, input/output hashes, source bundle, settings and per-family records. `COMPLETE` and `missing_points: 0` are required before physics interpretation. Each report is immutable: choose a new report path for a rerun.

## 3. Backend settings for the selected-point follow-up

Retain the **original manifest records, point IDs, seed and config hash** when reprocessing scalar survivors. The 225 eligible IDs are in `/data/$USER/zee/d14_heavy_20k/eligible_ids.json`. The follow-up used 9 shards of 25 records and these job settings:

```json
{
  "families": 2,
  "perturbativity_limit": 3.5449077018110318,
  "lfv": true,
  "lfv_tree": false,
  "bsgamma": true,
  "d9b_probe": "/data/aalida/zee/external/d9b/rate_probe",
  "higgs": true,
  "hb_data": "/data/aalida/zee/external/hbdataset_v1_7",
  "hs_data": "/data/aalida/zee/external/hsdataset"
}
```

Package the follow-up with `module14/condor/prepare.py --commit <original-scan-commit> --config <original-config> --job-settings <settings.json> --shard <each-shard> --output <new-batch-dir>`, then use the same `d14.sub` PATH amendment, dry run, submit and collector procedure.

**Interpretation limits:** vacuum `UNKNOWN` is not a PASS; D9B and the partial LFV predictions remain `DIAGNOSTIC_ONLY`; the h125 HiggsTools treatment is approximate and incomplete heavy-neutral/charged production inputs are `NOT_EVALUATED`. Scan acceptance fractions are proposal-dependent, not excluded model-space fractions.

# Manual AF commands

No commands below were submitted to HTCondor by Codex. Use the existing
AF Python environment. Paths and resources follow the original D14 runbook.
The original evidence is preserved; every output path must be fresh.

## Recollect original runs

The executed audit is frozen in `remote_audit.json`. To repeat with new
immutable reports, from the AF login node:

```bash
source ~/zee/venvs/d14-py39/bin/activate
cd ~/zee/workspaces/zee-d14-af
git fetch origin feature/zee-d14-conditional-cascade-scan
git switch --create d14-conditional-review --track origin/feature/zee-d14-conditional-cascade-scan
git status --short
python -m module14.conditional_scan.audit_existing \
  --data-root "/data/$USER/zee" --batch-root "$HOME/zee/condor" \
  --report-name conditional_audit_review_01.json \
  --output "/data/$USER/zee/conditional_audit_review_01.json"
```

This requires exactly 80 and 9 shards, exact source commit `d45f179`,
archive contents matching that Git commit, hashes, matching saved settings,
`COMPLETE` and zero missing points. It uses each archived collector, writes
new reports, and never invokes workers or external flavor programs.

## Reproduce the 225-point conditional dataset

Run from this branch's repository root, with the original AF data present.
This reads the completed outputs; it does not reevaluate scalar/neutrino workers.

```bash
FOLLOW="/data/$USER/zee/d14_heavy_physics_225"
BATCH="$HOME/zee/condor/d14_heavy_physics_225"
parts=()
shopt -s nullglob
for shard in "$FOLLOW"/scan/shard_*.jsonl; do
  name="${shard##*/}"
  outs=( "$BATCH/results/$name".*.jsonl )
  recs=( "$BATCH/receipts/$name".*.json )
  if (( ${#outs[@]} != 1 || ${#recs[@]} != 1 )); then
    echo "Missing/duplicate $name"; exit 1
  fi
  parts+=(--part "$shard" "${outs[0]}" "${recs[0]}")
done
python -m module14.conditional_scan.workflow \
  --manifest "$FOLLOW/scan/manifest.jsonl" --config "$FOLLOW/config.json" \
  "${parts[@]}" --matching-card module14/conditional_scan/matching_card.json \
  --source-commit "$(cat "$BATCH/source_commit.txt")" \
  --source-bundle-sha256 "$(cut -d' ' -f1 "$BATCH/bundle.sha256")" \
  --output "$FOLLOW/conditional_dataset_review_01.json"
```

Missing production keeps ranks and yield proxies null. To supply it, add
`--production-dir DIRECTORY`. Each `MODULE2_INPUT_SHA256.json` must bind
`scalar_sha256`, `yukawa_sha256` (F/D/Ye/Ye2) and `module2_input_sha256`.
It must specify `state="H2"`, `model="ZeeTypeII"`, numeric `sigma_pb` and
`energy_TeV`, and nonempty `process`, `charge_definition`, `order`, `pdf`,
`scale_scheme`, `documentation`, `uncertainty` strings. Include a nonempty
`artifacts_sha256` mapping of relative file paths to actual artifact hashes
under that directory. These are supplier-documented rates, not automatic
production validation. No old D13 rate or energy conversion is substituted.
Ranking groups must match energy/process/charge/order/PDF/scale exactly.
Integration error must not be presented as a theoretical uncertainty.

## Small local verification

```bash
python -m module14.conditional_scan.pilot --output /tmp/zee-conditional-review-01
python -m unittest discover -s tests -p 'test_module14_conditional_*.py' -v
git diff --check
```

The pilot evaluates 16 new proposals and a 100-point committed-pilot control,
each serially and in shards. It launches no jobs. Detailed datasets stay
under the selected scratch directory; the compact summary records hashes.

## Prepare the next scan; submission is manual

The frozen follow-up config has 20,000 proposals, 80 shards of 250:
7,500 sub-TeV, 7,500 higher-mass and 5,000 broad-control proposals.
Do not interpret these allocation weights as model-volume probabilities.
The broad arm includes both signs of mixing; the other arms stay away from
zero and endpoint mixing. Correlated proposals require an open Z cascade
with the original 20 GeV margin. No tuning follows the reference flavor test.

Run these only when choosing to prepare a new batch:

```bash
source ~/zee/venvs/d14-py39/bin/activate
cd ~/zee/workspaces/zee-d14-af
git status --short
COMMIT="$(git rev-parse HEAD)"
RUNROOT="/data/$USER/zee/d14_conditional_review_01"
BATCH="$HOME/zee/condor/d14_conditional_review_01"
mkdir -p "$RUNROOT"
python -m module14.scan generate \
  --config module14/conditional_scan/followup_config.json --output "$RUNROOT/scan"
cat > "$RUNROOT/settings.json" <<'JSON'
{"families":2,"perturbativity_limit":3.5449077018110318,
 "lfv":true,"lfv_tree":false,"bsgamma":false,"higgs":false}
JSON
shards=()
for shard in "$RUNROOT"/scan/shard_*.jsonl; do shards+=(--shard "$shard"); done
python module14/condor/prepare.py --commit "$COMMIT" \
  --config module14/conditional_scan/followup_config.json \
  --job-settings "$RUNROOT/settings.json" "${shards[@]}" --output "$BATCH"
cd "$BATCH"
sed -i '/^getenv = FALSE$/a environment = "PATH=/home/aalida/zee/venvs/d14-py39/bin:/usr/bin:/bin"' d14.sub
condor_submit -dry-run dryrun.ads d14.sub
# Review the dry run, paths and resources before this manual submission:
condor_submit d14.sub
condor_q "$USER"
```

The unchanged template requests 1 CPU, 2 GB RAM and 2 GB disk per job.
Original AF receipts peak below 173 MiB RSS, but this does not guarantee
resource usage for the new arms. Keep site runtime/dependencies provisioned.
No external flavor executable, HB/HS dataset or production card is assumed.

After completion, collect and apply the sidecar from the repository root:

```bash
cd ~/zee/workspaces/zee-d14-af
parts=()
shopt -s nullglob
for shard in "$RUNROOT"/scan/shard_*.jsonl; do
  name="${shard##*/}"
  outs=( "$BATCH/results/$name".*.jsonl )
  recs=( "$BATCH/receipts/$name".*.json )
  if (( ${#outs[@]} != 1 || ${#recs[@]} != 1 )); then
    echo "Missing/duplicate $name"; exit 1
  fi
  parts+=(--part "$shard" "${outs[0]}" "${recs[0]}")
done
python -m module14.collect --manifest "$RUNROOT/scan/manifest.jsonl" \
  --config "$BATCH/config.json" "${parts[@]}" \
  --source-commit "$(cat "$BATCH/source_commit.txt")" \
  --source-bundle-sha256 "$(cut -d' ' -f1 "$BATCH/bundle.sha256")" \
  --output "$RUNROOT/collection_review_01.json"
python -m module14.conditional_scan.workflow \
  --manifest "$RUNROOT/scan/manifest.jsonl" --config "$BATCH/config.json" \
  "${parts[@]}" --matching-card module14/conditional_scan/matching_card.json \
  --source-commit "$(cat "$BATCH/source_commit.txt")" \
  --source-bundle-sha256 "$(cut -d' ' -f1 "$BATCH/bundle.sha256")" \
  --output "$RUNROOT/conditional_dataset_review_01.json"
```

A collector failure, partial manifest, source mismatch or incomplete decay table must
be resolved or retained as unevaluated; it cannot establish acceptance.

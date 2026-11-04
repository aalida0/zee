# Heavy-spectrum proposal configuration

`heavy_scan_config.json` fixes the seed and defines 20,000 proposals in 80 shards of 250. Its repeating ten-index allocation assigns three proposals to each of the three charged-heavy mass intervals and one to a full-range control arm. These are proposal frequencies, not model-volume probabilities. Each scalar is seeded by the global seed and index; the arm, full configuration hash and scalar hash are recorded in every manifest row.

Within each arm, mH2 and the mH1/mH2 ratio are uniform, tan beta is log-uniform, and alpha is beta plus a uniform offset. The neutral masses are independent uniform additive GeV splittings around the charged-doublet reference mass. The soft term is the reference value multiplied by a uniform factor. The control arm uses larger neutral splittings (±400 GeV), misalignment (±0.4 rad) and soft factors (-1 to 3); the other arms use ±100 GeV, ±0.05 rad and factors 0.7 to 1.3. All other ranges are explicit in the configuration. These correlations are proposals, not theoretical constraints or optimized benchmarks. Invalid input-schema, neutral-ordering or cascade-threshold draws are rejected and redrawn from the same per-index random stream, without clamping. This conditioning can alter marginal proposal distributions, especially in the control arm. The template retains mh1 = 125 GeV and its electroweak convention.

From the repository root, after committing this code, generate the manifest and prepare an unsubmitted Condor directory:

```bash
python -m module14.scan generate --config module14/heavy_scan_config.json --output validation/module14/local/heavy_proposals
shards=()
for shard in validation/module14/local/heavy_proposals/shard_*.jsonl; do shards+=(--shard "$shard"); done
python module14/condor/prepare.py --commit HEAD --config module14/heavy_scan_config.json "${shards[@]}" --output validation/module14/local/heavy_condor
```

Generation does not evaluate physics, and preparation does not submit jobs. Use the exact committed source corresponding to the generator; inspect the Condor environment and settings before any later submission. Collection and worker instructions are in [COLLECTION.md](COLLECTION.md).

# Integrated scan scope

The existing generator, scalar gates, D10 certificate, NO/IO inverse solver and perturbativity screen, D4 charged decays and optional partial LFV run in one worker. B→Xsγ is a D9B NLO legacy rate, conditional on an explicitly supplied executable matching the pinned D9B binary; its uncertainty is not calibrated and its experimental comparison is diagnostic only. Its cache binds the scalar, probe, matching code, patch and numerical settings. Missing runtime is NOT_EVALUATED. Cache files must be on a filesystem supporting atomic hard links.

HiggsTools 1.1.3 and explicit HB/HS datasets are optional. The h125 effective-coupling fit omits charged-scalar loop effects and is diagnostic only. Charged searches require a per-family file named INPUT_SHA256.json in `--production-dir`, containing `scalar_sha256`, `yukawa_sha256` (F, D, Ye, Ye2), and `charged_Hpmtb_13TeV_pb` (H1/H2 entries). Rates must be externally model-matched and documented by the supplier. Only the 13 TeV tb-associated input is supported; other production and complete heavy-neutral inputs are NOT_EVALUATED. No D13 benchmark rates are used automatically. Mutable production directories cannot be resumed safely; use fresh output paths. The adapter does not currently implement heavy-neutral searches even when external inputs exist.

LFV omits Wγ and other amplitudes; the LFV comparisons are diagnostic, not exclusions. The D9B theory uncertainty and full flavor likelihood remain missing. HiggsBounds channel completeness, production and heavy-neutral widths remain incomplete. No global acceptance is asserted.

The pilot evidence `validation/module14/d14a_integrated_pilot.json` uses the existing 100-point pilot's two survivors and records exact cutflows and elapsed times. Original scalar, neutrino, LFV and decay outputs were compared; serial and two-shard output bytes matched. D9B and h125 reference rates matched D9B and D13. No remote Condor jobs were submitted. Runtime, external executables and datasets must be provisioned on the execution host; the Condor package does not transfer them. Paths in job settings refer to that host. The shipped job settings intentionally contain null external paths; stages report NOT_EVALUATED until provisioned.

Prepare a larger validation configuration by copying `module14/pilot_config.json` and changing `count`, `shard_size`, seed and ranges. Then:

```
python -m module14.scan generate --config CONFIG.json --output SCAN_DIR
python module14/condor/prepare.py --commit HEAD --config CONFIG.json --job-settings module14/condor/example_settings.json --shard SCAN_DIR/shard_000000.jsonl --output BATCH_DIR
```

Pass `--shard` once for each shard. Configure backend and dataset paths in a copied job settings file and review the site-specific HTCondor transfer/runtime setup before submission. This template does not validate an HTCondor installation or a remote environment. Collect with repeated `--part` options as described in COLLECTION.md.

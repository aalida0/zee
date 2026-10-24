# F23 — One integrated pinned HyperIso C++ two-charged-Higgs physics run

**Target:** final F22 157 source-authenticated CP-conserving Type-II-quark general-Zee scan points. This is **NOT** a 2026 NNLO flavor exclusion. The HyperIso public version 1.0.3 (2026-07-20) predates Misiak's 2026-08 calculation.

**Source:** https://github.com/Hyperiso/Hyperiso tag `v1.0.3`, exact commit `09d26ac6e71d1528922097a896d15693589f636b`.

**Implemented** (all from one invocation):
- Immutable F22 `F22_freeze_SHA256_manifest.json` authentication of both **9 priority** and **157 full actual complex-f/Y** sourced files.
- Clone exact `v1.0.3`, verify exact Git SHA and clean tree; configure/build/install HyperIso **native C++ libraries and CLI**, no Python wheel needed.
- Build one separate C++ bridge `cpp/F23_hyperiso/zee_hyperiso_two_state.cpp`.
- Reproduce native tagged `R3` `BR_B__Xs_gamma=0.00032967` and `R6` BSM THDM (C_7,C_8,C_9,C_{10}) frozen-source invocation.
- Generate charged-quark flavor-only THDM source surrogates for each F22 point, with input `MASS[37]=mH1`, `MINPAR[3]=tanbeta` and diagonal Type-II quark ratios `lambda_tt=cotbeta`, `lambda_bb=-tanbeta`.
- Evaluate **native HyperIso NNLO** inclusive (B\to X_s\gamma) with the built-in *single-H1 Type-II* coefficients and additive corrections to its physical standard BSM matching operators:
  \[
   C_i^{\rm Zee,(n)} =
   C_i^{\rm TypeII,(n)}(m_{H_1^+})+
   \sin^2\gamma\,[ C_i^{\rm TypeII,(n)}(m_{H_2^+}) -
                         C_i^{\rm TypeII,(n)}(m_{H_1^+})].
  \]
  The differential corrections are computed from **the same HyperIso public C++ `Math` kernel** used in `BWilsonTHDM.cpp`: C3..C6 nonzero NLO/NNLO, C7/C8 LO/NLO/NNLO, full matching-scale logs and running-top mass from the live model param cache. `WilsonMatchingPatch` decorates the matching coefficients **before** HyperIso B-sector RG and full nonperturbative/inclusive observable calculation.
- For each of 9 priority models, run actual-native endpoint tests: `gamma=0` equals same-mass no-mixing; `gamma=pi/2` equals physical pure-heavy THDM; `mH1=mH2` independent of gamma. Invalid endpoints halt before evaluating all 157.
- Evaluate all 157 F22 points sequentially with fresh native processes because of HyperIso model singleton state. Save full 157-row CSV, *all native observable trace outputs*, 5 mass-bin descriptive legacy-BR ranges, exactly tagged source/input SHA.
- No separate tiny test-run sequence. The same single execution compiles, performs its full test suite, and processes the actual data. An upstream GitHub Actions native scientific integration workflow also builds and runs the bridge against the genuine tagged HyperIso source.

## First-time Ubuntu dependencies

HyperIso C++ v1.0.3 builds without pyhyperiso or MARTY in this workflow. For Ubuntu 22.04+:

```bash
sudo apt-get update
sudo apt-get install -y \
 git cmake ninja-build g++ libgsl-dev libeigen3-dev \
 libboost-dev libboost-system-dev libboost-filesystem-dev \
 libboost-thread-dev libopenblas-dev liblapack-dev
```

### Stage the 3 original F22 files once from LXPLUS

On **Ubuntu**:

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only
mkdir -p ~/zee_F22_frozen_benchmarks_20261025
scp 'aalida@lxplus.cern.ch:/afs/cern.ch/user/a/aalida/zee_F22_frozen_benchmarks_20261025/F22_*' \
 ~/zee_F22_frozen_benchmarks_20261025/
```

The transferred files MUST be exactly:
- `F22_freeze_SHA256_manifest.json`
- `F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json`
- `F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz`

Do **not** reconstruct new f/Y, masses, gamma, tanbeta or mix generic 2HDM constraints into the actual Zee scan.

### ONE end-to-end native HyperIso 9+157 campaign

```bash
cd ~/zee
python3 scripts/zee_paper1_F23_hyperiso_one_shot_integrated_157.py \
 --f22-dir "$HOME/zee_F22_frozen_benchmarks_20261025" \
 --output "$HOME/zee_F23_hyperiso_157_20261025"
```

**NO additional commands** for the physics suite. Output is fail-closed on any source mismatch, build failure, nonfinite observable, malformed bridge response or endpoint discrepancy.

Expected success markers:

```text
F23_UPSTREAM_HYPERISO_CLONE_BUILD_OK 09d26ac6e71d1528922097a896d15693589f636b
F23_TAGGED_UPSTREAM_REFERENCE_R3_AND_R6_PASS SM_BR 0.00032967
F23_NINE_REAL_F22_ENDPOINT_AND_EQUAL_MASS_CHECKS_PASS
F23_NNLO_TWO_CHARGED_PROGRESS 157 /157
F23_FULL_NATIVE_HYPERISO_TWO_ZEE_CHARGED_DONE REAL_MODELS 157 PHYSICAL_95CL None
```

Result files under requested output directory:
- `F23_157_two_state_HyperIso_legacy_NNLO_NOT_2026_CL.csv`
- `F23_conditional_157_model_summary.json`
- `F23_native_matching_audit_traces.jsonl`
- `F23_upstream_R3_SM_NNLO.log`, `F23_upstream_R6_single_THDM_NNLO.log`
- Complete Git pinned source, CMake logs and build objects.

## Important scientific limits

1. **HyperIso 1.0.3 tagged SM reference is 3.2967e-4**. Misiak 2026 uses `(3.54+-0.14)e-4`. Different perturbative inputs/precision updates cannot be reconciled by shifting a constant. This is a *historical-scheme, higher-order conditional observable*, not the 2026 95% CL Zee exclusion.
2. The `MASS[37]` LHA input is a single charged Type-II flavor-only surrogate with the correct quark coupling ratios. It is **not** the complete two-charged / three-neutral Zee spectrum. Only matching contributions to inclusive `B->Xs gamma` are meaningful from this surrogate; do not run other 2HDM Higgs observables on it.
3. Both HyperIso and our SuperIso 4.1 heritage implement related analytic published matching kernels. Agreement does not constitute fully independent theory verification. Historic F3 NLO/WC discrepancies remain a validation priority.
4. This C++ implementation is deliberately scoped to **CP-conserving Type-II quark couplings** and single-loop charged eigenstate contributions weighted by cos²/sin² gamma. It does not include potential higher-order mixed-mass diagrams requiring a new two-state NNLO matching calculation, and does not handle arbitrary general Zee quark Yukawas.
5. **No confident experimental allowed status** is produced, even if any legacy numerical BR looks close to experiment.
6. Benchmark order and inputs are fixed by original F22 SHA; this campaign does not modify any original F18/F20/F21/F22 output and does not create F24 scan.

## Next publication-critical work

After actual backend execution, compare the LO/NLO coefficients and old-era BRs to the source-verified F3 SuperIso cross-code diagnostics at identical masses, scales and conventions. Then reconcile modern Misiak 2026 theory uncertainties, fully coherent general-Zee LFV and physical LHC rates. HyperIso v1.0.3 BR alone does not establish a paper-ready exclusion.

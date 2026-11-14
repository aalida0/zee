# Zee Type-II LFV closure audit — 14 November 2026

**Hard status: MODEL-SPECIFIC FULL PHYSICAL LFV NOT YET COMPLETED.** No unperformed private-SPheno source execution or new Zee-specific 2-loop EDM amplitude has been claimed. The purpose of this ledger is to prevent proxy-level evidence being silently promoted to experimental full-model acceptance.

## Corrected evidence

The original SHA-256-locked 64-card source file has hash
`dc8d462146dd1206e9a4e33aefd5b37673dbe052fdfad998b0d2034156f8b0f9`.
The original 16 vacuum-certified scalar cards are preserved.

On all 64 the one-loop Zee neutrino inversion is exact, their six 1D + one 3D NuFIT 6.1 scoped selection passes, and the leading Zee one-loop mu→eγ and tau radiative screens pass. The corrected public general-2HDM electron EDM *proxy* is below 4.1e-30 e cm for all 64. The original-source full mixed Zee EDM is not calculated.

We additionally select **55 / 64** with **|d_e^(published 2HDM proxy)| < 1% × 4.1e-30 e cm**. The 55 retain **all 16 scalar points** (31 NO, 24 IO), with:
- max BR(mu→eγ) from independently retained Zee 1-loop amplitudes = **6.3221752560915e-17**, vs MEGII 90% CL 1.5e-13.
- max published corrected 2HDM proxy electron EDM = **2.98840711335415e-32 e cm**.
- worst conditional sufficient missing mu→eγ amplitude norm (triangle inequality) = **47.70935 × retained amplitude**. This is a *conditional threshold*, **not** an independent estimate or bound on omitted diagrams.
- max missing absolute EDM budget = **4.07011592886646e-30 e cm** before reaching the quoted JILA eEDM-only bound. JILA molecular interpretation requires treating semileptonic CP-odd operators when material.

Verified original hashed SLHA source vs revised family matrices: maximum difference in F is **zero** on all 64, while max absolute change in any D element is **9.99800966044e-5**, with max relative whole-matrix norm **0.47774%**; max |ΔD_τe|=2.7181e-19, max |ΔD_eτ|=1.19455e-11. This supports a source-level cross-check but does **not** prove the old complete interfering one-loop rates apply to the new textures.

The attempted FOURTH complex exact D[e,tau]=0 condition was checked on the actual 64 frozen neutrino inputs. 0/64 gave an acceptable four-complex linear inverse. The original three-zero `D[e,mu]=D[mu,e]=D[e,e]=0` remains the viable texture construction; the fourth-zero failure should not be labeled exclusion of these original 64.

## Code and execution

- `robust55_evidence.py`: source-hash-locked 64→55 selection with complete F/D/ordering/Neutrino and no-acceptance gate. Tested on the authentic archived 64-card source in Actions [43586990485](https://github.com/aalida0/zee/actions/runs/43586990485) (PASS), exporting 64 full per-texture source receipts and retained 55 candidates.
- `finish_repaired64_local.py`: one-command entrypoint for the precompiled source-attested original generated ZeeTypeII/SPheno4.0.5 model and the revised 64. It uses the previously established validated template at `~/zee-conditional-cascade-scan/validation/module14/local/runtime/group0/tree.in` and isolated binary/work at `~/zee-lfv64-serial-20261112-094549`. Its three fail-closed fixture/control-flow tests and native-runner syntax checks passed in Actions [43586687205](https://github.com/aalida0/zee/actions/runs/43586687205). **That CI tests the runner, not the original private native Fortran on revised 64.**
- `stage_edm_repaired_native_64.py` / `run_repaired64_native_source.py`: stage 64 with full complex Yukawas and inspect signed source-generated one-loop mu→eγ, mu→3e and mu→e conversion, original SHA-256, mass and source Yukawa matching. The synthetic-input fixture is explicitly NOT PHYSICS.
- The original full 12 Nov source-derived one-loop mu3e/conversion numbers are for the **older 64**. They must not be copied to the repaired cards.

## Exact blockers to a full LFV-completed statement

1. Run the attested precompiled private native ZeeTypeII model on the *new* 64 input cards. We do not have remote access to the user's local original private Fortran source and already built executable.
2. Quantify or source-match genuine Zee singlet-F / mixed H1,H2 ± W/Goldstone/gauge higher-order LFV and EDM contributions. Do not silently apply the 2HDM-only source to the singlet sector.
3. For physical mu-e conversion exclusions, match the full complex source Wilsons to modern LEFT, CKM/quark and nuclear matrix elements (with uncertainties); old historical Au rates are not that calculation.
4. The eEDM bound assumes a separable molecular interpretation; check electron-nucleon CP-odd operators if material.

Current releasable statement: **leading Zee radiative LFV + published pure-2HDM electron-EDM proxy: scoped compatible for 55 strongly screened textures across all 16 scalar points**. **Full physical Zee LFV: UNKNOWN**. **Global Zee allowed parameter space: UNKNOWN**.

### Local source-execution command

```sh
cd ~/zee
git fetch origin
git switch research/zee-lfv64-closure-20261113
git pull --ff-only origin research/zee-lfv64-closure-20261113
python3 -m research.full_constraints.lfv_literature_closure_2026.finish_repaired64_local \
  --source ~/Downloads/zee-edm-suppressed-64-new-textures-full.zip
```

This one command starts a strict native **source 1-loop** calculation on the user's prebuilt corrected SPheno binary; it writes a separate, hash-verified 64-case source/observables receipt. A complete source 1-loop screen should be reported as `LFV_SOURCE_ONE_LOOP_SCREEN_COMPLETED` if all rates satisfy the named limits, **never as full physical Zee LFV COMPLETED**.

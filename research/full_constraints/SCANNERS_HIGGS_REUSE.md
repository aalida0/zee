# Reusing ScannerS/2HDMC/SusHi/anyHdecay to complete Zee Higgs constraints
**Research branch:** `research/zee-full-constraints`. **Scope:** reference and optional adapter work; no new scan. This supplement does **not** supersede the currently active HEPfit B-rate execution task.

## Source-verified finding

[ScannerS 2.0.1 documented models](https://jonaswittbrodt.gitlab.io/ScannerS/namespaceScannerS_1_1Models.html) include R2HDM/C2HDM, N2HDM (the singlet is neutral), and several SM singlet models, **not Zee Type-II with one charged singlet and two mixed charged states**. The ScannerS TwoHDM class has `nHplus=1`, while Zee has 2:
https://jonaswittbrodt.gitlab.io/ScannerS/classScannerS_1_1Models_1_1TwoHDM.html
ScannerS generic Higgs constraint requires a `Model::HiggsBoundsInput(p,hbhs)` and `nHplus`/names:
https://jonaswittbrodt.gitlab.io/ScannerS/classScannerS_1_1Constraints_1_1Higgs.html
Its public interface has `check` (existing points) and `scan` (new points); do NOT use `scan` to test this research work. It routes experimental tests to **HiggsBounds and HiggsSignals**; our HiggsTools already runs their modern equivalents, so re-implementing ScannerS as a scanner duplicates infrastructure.

ScannerS uses **tabulated SusHi** for ggF/bbH, **anyHdecay** for decay rates and **HiggsBounds** production parametrizations for charged tbH. Original source/paper:
https://link.springer.com/article/10.1140/epjc/s10052-022-10139-w
https://jonaswittbrodt.gitlab.io/ScannerS/index.html
No claim that its built-in 2HDM Yukawa-sector *flavor* or vacuum criteria apply to Zee charged mixtures.

Existing model-agnostic HiggsTools can take *both* charged particles and explicit matched neutral/charged rates/widths through `Higgs.tools.Input.predictionsFromDict(data,neutralIds,singleChargedIds,doubleChargedIds)`:
https://higgsbounds.gitlab.io/higgstools/alternative_input.html
This is the **recommended final consumer**.

## Ranked reuse route (not a new model-space scan)

1. **SusHi / ScannerS SushiTables**: calculate/cache matched 8/13 TeV neutral `h,H,A` ggF and bbH rates for real original Zee cards using the model's Type-II quark couplings and exact masses, checking CP, top/bottom interference, PDF/order and scales; compare to original UFO LO on a saved card. Source/coupling-scheme matching is necessary; do not apply neutral production tables blindly to charged H1/H2 or to new singlet-lepton couplings.
2. **HDECAY / anyHdecay**: extract *validated transferable* neutral h/H/A SM final-state QCD corrections and relevant off-shell methods. Preserve our source-matched total widths including additional **H/A→H1/H2 W** and other scalar channels, as well as non-standard LFV Yukawas; unmodified 2HDM/N2HDM output is **not** full Zee decay widths. Validate one-state/decoupling limit and nonzero two-state channels before operational use.
3. **2HDMC and ScannerS R2HDM**: independent control for one charged-doublet limit and neutral quark couplings/production/widths only; never use their automatic 2HDM vacuum/discriminant or single charged-Higgs B→Xsγ bound as a Zee exclusion.
4. **Existing SARAH restricted Zee UFO + MadGraph**: genuine exotic mixed charged production and decays. Existing 16 H2 13 TeV cards are frozen source evidence. H1 production and other required processes remain MISSING until model- and energy-matched native calculation is independently qualified. Do not start a broad production campaign now.
5. **Existing HiggsTools 1.1.3**: populate h125 full width including **validated h→γγ** result, still missing mixed-state `h→Zγ` (G12 Z21 nonzero), H/A full widths/production, H1/H2 sources at the applicable energies, and correct STXS/collider input. Only fully covered applicable analyses may give validated physical exclusion results; missing inputs are null, not zero.

## Fixed-card source validation gate

- Read `research/full_constraints/higgs/COVERAGE.json`, `HIGGS_COVERAGE.md`, `HIGGS_EXECUTION_REPORT.md` and frozen D13/D14 data.
- Source-pin libraries and reference tabulations, select only original **D7/F13 D12 witnesses and 16 D14 scalar cards**; no random proposals, no ScannerS `scan` or Condor jobs.
- For each matched process or decay record: energy, beam, process, CP, masses, Yukawa/coupling conventions, PDF/order/scale/scheme, loop order, total-width normalization, uncertainties, exact original input/output hashes and experimental analysis matching.
- Independent controls: SM/2HDM decoupling, both charged states and signed mixing, tree cascade and neutral exotic thresholds, no missing=0, correct HiggsTools branching-fraction/total-width preservation.
- Stop if model transfer is unproved. Emit exact `VALIDATED_SCOPED`, `REFERENCE_ONLY`, `NOT_EVALUATED`; the full Higgs exclusion stays blocked until all required applicable channels have justified model predictions.

**No full-physics status is changed by this source finding.** B→Xsγ and LFV remain blocked. The separately scheduled HEPfit B-rate execution stays active.

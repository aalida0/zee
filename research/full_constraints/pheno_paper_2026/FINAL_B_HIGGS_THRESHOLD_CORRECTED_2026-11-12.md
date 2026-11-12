# Final source-scoped Zee Higgs × B × threshold audit — 12 November 2026

## Scientific decision
**FULL_PHYSICAL_HIGGS_UNKNOWN; FULL_LFV_UNKNOWN; GLOBAL_ACCEPTANCE=null** on each of 64 purpose-constructed neutrino-compatible Zee points. This is a **leading-order phenom screening package**, not a globally allowed-space scan. No unqualified 95%-CL model acceptance is made.

**Reproduced passing source CI**: [43125501513](https://github.com/aalida0/zee/actions/runs/43125501513), branch `research/zee-full-constraints`. The source-locked, 64-case output is `zee-64-leading-B-Higgs-width-followup-TENTATIVE.json` in that run's artifact. This report supersedes earlier *one-sided B=64/64* counts, which mistakenly reused a two-sided source flag (now explicitly falsification-tested).

### Exact 64-row gated, but *engineered*, benchmark progression

| Criterion | Result | Interpretation |
|---|---:|---|
| 16 original scalar spectra, 4 tuned NO/IO Yukawa textures each | **64/64** | The construction is **not** a random parameter-space sample. |
| Source H1/H2/h125 and H/A selected HiggsBounds analyses below observed ratio 1 | **64/64** | Only modelled 13 TeV direct searches; no full Higgs exclusion. |
| Source Misiak-2026 Eq.4 one-sided upper 95% **approximate** Gaussian B screen | **40/64 (10 scalar centers)** | Requires pull < 1.64485362695; no full two-charged-NP NNLO covariance. |
| All relevant *open* charged Z and charged-W cascade thresholds ≥ **five times maximum of parent/daughter known widths** | **28/64 (7 scalar centers)** | Kinematic heuristic, **NOT a certified NWA**. |
| Intersect **B + direct Higgs subsets + five-width threshold buffer** | **16/64 (4 scalar centers)** | IDs **4611, 8850, 14074, 15673**. |
| Add optional restricted h125 `Δχ²≤9` relative-to-SM **tension diagnostic** | **12/64 (3 scalar centers)** | IDs **4611, 14074, 15673**. **Not a 95% CL h125 pass.** |
| Actual independently demonstrated globally allowed parameter points | **0 certified** | Physical status **UNKNOWN** for all 64; neither 0 allowed nor any allowed fraction has been established. |

The 64/64 two-sided-B value is **true for the two-sided `|z|<1.96` diagnostic only**. It must **not** be reported as 64/64 passing the separate one-sided Gaussian B screen. Falsification test `test_two_sided_B_interior_does_not_imply_one_sided_upper_95` is now in CI.

### Detailed important source checks

| Scalar ID | B 2026 Eq.4 normalized pull | Five-known-width cascade buffer | Restricted h125 Δχ² (NO, first seed) | Followup tier |
|---:|---:|---|---:|---|
| 2264 | 1.8245 | NEAR | 1.528 | B one-sided fails |
| 4611 | 1.4891 | FAR | 0.419 | **SOURCE_FOLLOWUP** |
| 8850 | 1.6176 | FAR | 11.276 | h125 relative fit tension |
| 9454 | 1.8122 | FAR | 0.477 | B one-sided fails |
| 14074 | 1.0540 | FAR | 0.597 | **SOURCE_FOLLOWUP** |
| 15591 | 1.6638 | FAR | 1.923 | B one-sided fails narrowly |
| 15673 | 1.2534 | FAR | 0.121 | **SOURCE_FOLLOWUP** |

The 2026 B central source prediction, experimental uncertainty and 1.64485 criterion are **not** a model-specific NNLO statistical exclusion. The restricted h125 Δχ² is **not** a Wilks statistic or calibrated confidence limit. The five-width criterion is **not** a physical NWA or interference validation.

## Components actually executed and independently tested

1. **HiggsTools 1.1.3 h125 HiggsSignals and HiggsBounds**: native Zee h125 loop inputs and corrected effective-coupling reference total; explicit computed LFV h→eμ/eτ/μτ added once; model heavy states absent. All 64 source cases run. [CI 43122649490](https://github.com/aalida0/zee/actions/runs/43122649490)
2. **HDECAY/AnyHdecay**: real source-matched transferable QCD quark and neutral-state partial widths for 16 original spectra, joined to 64 native Zee H/A tree+charged W+general-lepton channels. Do **not** replace native two charged species or general lepton Yukawas by 2HDM Type-II. [CI 43119479264](https://github.com/aalida0/zee/actions/runs/43119479264)
3. **SusHi 1.7.0**: real source-validated LO ggF+bbH at 13 TeV for all 16 original scalar spectra × H/A, 32 predictions. [CI 43122137634](https://github.com/aalida0/zee/actions/runs/43122137634)
4. **Charged H1/H2**: HiggsTools built-in public matched 4FS/5FS 13 TeV tbH± parametrization, correct Type-II doublet mixing, and native Zee D4 full *on-shell two-body* decay widths (including H2→H1Z). 64 cases. At 2264, selected H1 observed ratio ~0.793; at 15673 largest charged selected ratio ~0.0922. LO MG5 H2 rate differs by factor about two from public matched table, **not** a numerical error.
5. **Heavy H/A direct searches**: actual 13 TeV SusHi LO ggF/bbH multiplied by selected known Zee/HDECAY partial rates with *optimistic* positive known-sum denominators and explicit +10%,+25% omitted-width scenarios. 64 source cases. These are central-rate screens, **not complete physical BRs or certified exclusions**. [CI 43122931587](https://github.com/aalida0/zee/actions/runs/43122931587)
6. **All 64 H/A→γγ leading one-loop widths**: both charged mixed eigenstates, full source complex lepton Yukawas, fermion and W contributions, D7/F13 controls. Max Γγγ / known width sum = **8.577745902638706×10⁻⁶**, demonstrating materiality below 0.001% at exactly those 64 source configurations. [CI 43124545726](https://github.com/aalida0/zee/actions/runs/43124545726)
7. **Finite-width/threshold source audit**: 36/64 purpose-constructed points have a relevant near-two-body-cascade threshold under the **five-source-width** heuristic. For 15673, the H2→H1Z gap is about **9.94** maximum source widths, vs **4.15** for 2264; H/A known-sum Γ/M at 15673 **5.69%/4.75%**, so heavy neutral `ttbar` resonance interference is still material. [CI 43125501513](https://github.com/aalida0/zee/actions/runs/43125501513)

## Remaining irreducible scientific gaps (must be labelled in paper)

- **Full neutral physical widths and uncertainties:** heavy Zee Zγ loops with unequal-mass off-diagonal charged current; on/off-shell W virtual/finite-daughter effects near cascade thresholds; production/theory and potential overlap of heavy channels. The photon channel now has a numerical materiality bound, but it does not bound all other omissions.
- **Experimental coverage:** H/A→H_i^±W^∓ and H2→H1Z exotic cascades do not receive a dedicated public HiggsBounds full-model recast here. The t-tbar interference and signal-shape assumptions, non-tb charged production, and different collision energies remain unknown. Missing analysis ≠ absence of constraint.
- **h125 statistical treatment:** a physically calibrated effective-coupling likelihood for the *full* scalar hypothesis has not been constructed. Δχ² relative to SM is a diagnostic.
- **B-physics precision:** the source Eq.4 one-sided LO-NP central-rate screen is operational. Model-matched full NNLO B rate with correlated theory uncertainty is still unavailable.
- **LFV:** retained radiative dipole, tree/dipole subset `mu→3e`, and conversion dipole-dominance proxies do not replace complete `mu→3e` non-dipole and `mu-e` conversion operators/interference.
- **Publication's central question:** a **representative**, documented scalar and Yukawa sampling procedure and sensitivity maps against the 2021 charged-cascade paper have not been performed. **The 3 shortlisted scalar IDs cannot be used to calculate a survival fraction or global exclusion**.

### Publication decision

The public-code *implementation* and named practical Higgs screens are complete enough for a **conditional LO constrained-survival parameter scan**, if every omission is documented and uncertain points remain flagged `UNKNOWN`. For an unqualified statement “these Zee parameter-space regions are experimentally allowed at 95% CL,” the additional physical LFV/Higgs/experimental signal-hypothesis gaps above must be resolved or bounded.

**Immediate next analysis:** use actual complete model predictions to sample and compare meaningful scalar regions with the 2021 cascade paper; report conditional acceptance with declared approximation variations and separate model-wide unknowns. Do not start unneeded precision two-loop projects merely to make a LO pheno plot; prioritize material constraints first.

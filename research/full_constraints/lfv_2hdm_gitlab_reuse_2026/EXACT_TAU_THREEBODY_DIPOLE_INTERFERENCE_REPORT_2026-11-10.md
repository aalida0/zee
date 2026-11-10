# Exact finite-mass dipole phase space and tau three-lepton interference budgets

**10 November 2026 | Executed CI source-linked restricted diagnostics only. PHYSICAL_LFV=UNKNOWN.**

## New calculation

Added `tau_exact_dipole_phase_space.py` to integrate the full-mass **constant** photon-dipole
matrix element on the physical three-body phase space. This incorporates:
- exact electron and muon masses, `q² >= 4m_pair²`, and analytic logarithmic invariant-mass mapping;
- both photon permutations with the antisymmetric Fermi sign for `tau->3e` and `tau->3mu`;
- direct photon only for distinct daughter/pair flavours `tau->e mu mu` and `tau->mu e e`;
- complex K2L and K2R chirality interference, a 2×2 positive-semidefinite response quadratic form, and its spectral min/max for unknown phases;
- source alpha(MZ)=1/127.95 at the frozen radiative dipole and alpha(0)=1/137.035999084 for the virtual-photon pair conversion, in the original source approximation;
- a **conditional** Cauchy–Schwarz envelope that includes just the signed neutral h/H/A tree and photon-dipole norm, without pretending the relative source phase or missing full Zee diagrams are known.

Numerical photon rate `Gamma(tau->3e)/Gamma(tau->e gamma)` for one dipole chirality is **0.01049761444** at 64×24 Gaussian nodes and reproduces the classic leading-log
`alpha(0)/(3 pi) [ln(m_tau²/m_e²)-11/4]=0.01049758117` to 3.2 ppm.
`tau->3mu/tau->mu gamma` for one chirality is **0.00227621017**, versus leading-log 0.00224135358 (a 1.55% finite-mass correction).
The exact massive `3mu` kernel also has nonzero CL/CR interference: assuming only the *total* source BR(tau->mu gamma) is known, its possible conversion ratio spans **0.00215330287–0.00239911746**, based on exact kernel eigenvalues.

All independent cross-basis and QED checks passed in
GitHub Actions run https://github.com/aalida0/zee/actions/runs/42820939128 (8 tests PASS);
original D12 SHA256 and corrected official 2HDM/SARAH source provenance remain checked by upstream readers.

## Photon dipole conversion ratio spectrum

These values are `BR(3body)_constant_K2 / BR(tau->daughter gamma)`,
and cover any relative complex chiral phase consistent with a fixed radiative
rate under the saved analytic two-body normalization.

| Physical final state | kernel eigenvalue minimum | kernel eigenvalue maximum |
| --- | ---: | ---: |
| tau->3e | 0.010496946440 | 0.010498282446 |
| tau->3mu | 0.002153302872 | 0.002399117459 |
| tau->e- mu- mu+ | 0.002072020620 | 0.002072660999 |
| tau->mu- e- e+ | 0.010226192586 | 0.010360219197 |

The earlier leading-log multipliers `0.01049758117` (3e) and
`0.00224135358` (3mu) remain valuable approximations but omit chirality-sensitive finite-mass effects.

## Strictly conditional two-subset Cauchy norm intervals

For the original source radiative partial `B_gamma` and the exact tree-only
`B_tree`, define `B_dipole in [r_min B_gamma,r_max B_gamma]`.
The Hilbert-space triangle inequality implies
`(sqrt(B_dipole)-sqrt(B_tree))² <= B_(dipole+tree) <= (sqrt(B_dipole)+sqrt(B_tree))²`,
with the extrema optimized conservatively over the unknown dipole chirality.
**The actual common source-matched relative tree/dipole phase was not calculated**;
these intervals are necessary bounds within the assumed two-subset approximation,
**not full physical predictions, exclusions, or a bound on any omitted amplitude**.

| Card | tau->3e restricted lower–upper | tau->3mu restricted lower–upper |
| --- | --- | --- |
| D7 NO | [4.77232201, 4.77756851] × 10^-16 | [2.89363901, 5.66123504] × 10^-14 |
| D7 IO | [2.84512179, 2.84920492] × 10^-15 | [3.16746529, 6.71390535] × 10^-14 |
| F13 NO | [6.12765309, 6.13062142] × 10^-20 | [5.00700707, 6.11356815] × 10^-18 |
| F13 IO | [3.73429195, 3.73623051] × 10^-19 | [5.62500800, 7.14850759] × 10^-18 |

| Card | tau->e- mu- mu+ restricted lower–upper | tau->mu- e- e+ restricted lower–upper |
| --- | --- | --- |
| D7 NO | [6.81728602, 12.4569906] × 10^-17 | [1.87047959, 1.89683995] × 10^-13 |
| D7 IO | [3.86293889, 7.70687564] × 10^-16 | [2.14588767, 2.17685674] × 10^-13 |
| F13 NO | [1.14973554, 1.27171541] × 10^-20 | [2.49321211, 2.52678735] × 10^-17 |
| F13 IO | [6.85377645, 7.91284324] × 10^-20 | [2.86062240, 2.89925350] × 10^-17 |

**Important physics:** D7 `tau->3mu` tree-only rate is 1.97% (NO) or 2.55% (IO) of the earlier leading-log dipole rate, yet amplitude-level interference plus massive-dipole chirality can change the restricted combined rate by tens of percent. A comparison of *individual branching fractions* is therefore not a safe estimate of coherent interference.

## Fail-closed interpretation and next inputs

Current four-card radiative source gate records only total `BR(tau->l gamma)`
after coherent original SARAH Zee F+D one-loop and corrected neutral-fermion BZ contributions. It does not archive the **full complex combined** `K2L,K2R` in a source-matched common basis. It would be scientifically incorrect to assign arbitrary phases or reconstruct them from a rate alone.

Even a recovered complex pair and exact dipole+tree coherent integration would still omit:
the off-shell K1(q²), low-q² Z penguins, local charged/neutral boxes, scalar-penguin scheme, and gauge-complete Zee-specific charged-singlet F/W/H1/H2 two-loop terms.
Source normalization and electroweak scheme differences must remain explicit.

**Recommended next step:** archive all complex original native SARAH tau K2 components and the corrected authors' neutral-fermion BZ cL,cR components for these exact four cards, retaining the signed `+c/(8pi² v²)` bridge and original source file hashes. Only then implement an exact coherent dipole+neutral-tree matrix-element calculation; extend with source-matched one-loop four-lepton/monopole groups before a physical tau LFV rate.

## Commands

```sh
python3 -m unittest research.full_constraints.lfv_2hdm_gitlab_reuse_2026.test_tau_exact_dipole_phase_space -v
python3 -m research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_exact_dipole_phase_space --ns 64 --nz 24 --tree-order 14 --output tau_exact_dipole_and_envelopes.json
```

The exact 64×24 CI run uploaded JSON artifact `zee-exact-tau-dipole-and-conditional-tree-envelope`.
No scan or global LFV acceptance was performed: **physical_lfv=UNKNOWN; global_acceptance=null**.

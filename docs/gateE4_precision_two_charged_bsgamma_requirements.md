# Gate E4 — publication-level two-charged Zee B→Xₛγ: implementation readiness and numerical acceptance criteria

**Assessment date:** 2026-10-19. **Stage:** SCIENTIFIC BLOCKER / DESIGN ONLY — NOT AN EXECUTABLE NNLO KERNEL, NOT A PHYSICAL EXCLUSION.

## 1. Empirical result inherited from AF

E1, E2 and E3 are COMPLETE across the **27 selected, neutrino-mass-closed, D4 partial-LFV-suppressed, D3 one-loop-theory-screened** model spectra. This is a B4-biased set, not an unbiased sample of the general Zee parameter space.

| Observable/screen | Cohort result | What it is |
|---|---:|---|
| E1 legacy SuperIso two-state BR | [3.8632835890, 4.0419325398] × 10⁻⁴, median 3.9144226350 × 10⁻⁴ | Source-audited old SuperIso result; *not* the 2026 prediction |
| E1 NP shift versus its own SM | positive for 27/27; median +0.5319649109 × 10⁻⁴ | Matched *within the legacy code only* |
| E2 legacy gamma checks | 108; max BR polynomial residual 3.20×10⁻¹⁷ | Exact numerical quadratic response in x=cos²γ at fixed masses and tanβ |
| E2 legacy no Z-vertex-squared loss | 0/27 can lower legacy BR | Fixed-mass gamma *counterfactual*, not an allowed model fit |
| E2 legacy ≥50% original Z-vertex-squared | 27/27 lower BR; median minimum 3.8469429737×10⁻⁴ | This is *not* BR(H₂→H₁Z) |
| E3 2026 generic Eq.(4), LO NP matching | [4.1076069419, 4.2939200729] × 10⁻⁴, median 4.1614800568 × 10⁻⁴ | Published small-NP *linearized* expansion; not full NNLO two-charged prediction |
| E3 LO probes | 54 charged-state slots; 48 unique (mass,tanβ) evaluations, 6 cache hits | Independent SuperIso source-pinned C₇/C₈ matching at exactly μ₀=160 GeV |
| E3 lossless Z-vertex-squared | 0/27 reduce predicted rate | Same qualitative conclusion as E2 |
| E3 ≥50% original Z-vertex-squared | 27/27 reduce predicted rate; median minimum 4.0901481176 × 10⁻⁴ | Still systematically above 3.49×10⁻⁴ experimental central value; **not an exclusion** |
| E2/E3 best gamma at half strength | 27/27 agree | Robust within the two DIFFERENT approximations |

The median Eq.(4) decrease with half-strength retention is 0.0713319392 × 10⁻⁴ (~1.71% of median original Eq.(4) BR). The agreement on *which direction of gamma to move* is more robust than numerical predictions of the rate in either scheme. The 27 original gamma values are biased towards >π/4 and hence towards small doublet fraction of H₁. With both Type-II contributions positive and approximately monotonic, the 'no free reduction at same coupling' observation has an important **kinematic/mixing component**; do not oversell it as a new general theorem.

## 2. Authoritative 2026 precision reference

M. Misiak, H. M. Asatrian, et al., *The Inclusive B̄→Xₛγ Decay Rate with Higher Precision*, arXiv:2608.29863v1 (2026-08-30), https://arxiv.org/html/2608.29863 .

- Eq. (1): experimental central value (3.49±0.19)×10⁻⁴, Eγ>1.6 GeV.
- Eq. (3): SM (3.54±0.14)×10⁻⁴, Eγ>1.6 GeV.
- Eq. (4): BR×10⁴ ≈ (3.54±0.14) − 8.51 ΔC₇(μ₀=160 GeV) − 2.16 ΔC₈(μ₀=160 GeV); **explicitly omits quadratic terms in ΔC₇,₈** and higher-order generic NP matching.
- Type-II 2HDM mass result >670 GeV (95% CL) **uses known O(αₛ²) charged-Higgs C₇/C₈ matching**, not just Eq. (4).
- Their SM update includes dominant exact-charm-mass O(αₛ²) Q₁,₂–Q₇ interference, full O(αₛ) four/five-body channels, updated kinetic-scheme semileptonic inputs and non-perturbative components/correlations. The calculation is not equivalent to shifting the central value in old SuperIso.
- The preprint is a short Letter, not a released arbitrary-complex-Wilson-coefficient numerical likelihood or set of polynomial BR response tensors. The analysis has NOT established that complete numerical code or a 2-state kernel is available to us.

## 3. Existing engines — permitted uses and blockers

1. **A1M/A1P/A1U/A1V, isolated SuperIso v5**: has source-audited coherent two-charged Wilson matching and an old complete observable. The high-scale helper reload and original NLO limiter issues were audited; A1U closure and E1/E2 pure/degenerate limits passed. This engine can test algebra, mixing and numerics but its hadronic SM calculation is not the new 2026 improved SM prediction.
2. **A1S/E3 source-pinned SuperIso C7,C8 at μ₀=160 GeV**: independent, reproducible LO NP Wilson inputs into Eq. (4); cannot validate the full observable or 2026 95% CL.
3. **HEPfit independent Type-II source matching in A1P**: valuable independent C₇/C₈ matching check through stated perturbative orders. HEPfit's older `bsgammaTHDM.cpp` computes the Type-II BR by interpolating in tanβ and a **single charged-Higgs mass** using `THDMcache::ip_ex_bsgamma`; two such full BRs CANNOT be averaged. HEPfit's separate general `Bsgamma` observable has a Wilson-coefficient interface and is a *potential* alternate kernel, but does not establish an updated 2026 normalization without further work.
4. **SusyBSG / other archived 2HDM programs**: historical crosschecks, not automatically the 2026 update. No numerical '2026 NNLO Zee BR' may be produced by combining one of these old NP shifts with 3.54×10⁻⁴.

## 4. Define the actual calculation (ONE model-agnostic observable + TWO charged states)

Use a fixed, explicitly written `{Q₁,...,Q₈}` LEFT operator basis (especially Q₇ and Q₈ signs/factors), the same CKM and quark mass renormalization conventions and μ₀ as the 2026 source.

Within the TYPE-II quark-sector assumption and at common μ₀, at each QCD matching order n=0,1,2 add the two charged states **BEFORE** low-scale RG running:

```
ΔC_i^(n)(μ₀) =
   cos²γ × ΔC_i,TypeII^(n)(mH1,tanβ,μ₀)
 + sin²γ × ΔC_i,TypeII^(n)(mH2,tanβ,μ₀)
```

Check operator classes beyond C₇,C₈ wherever matching generates them and account for thresholds/scale logarithms consistently. If the exact model quark sector deviates from Type-II (e.g. alternative Yukawa alignment), abandon this formula and derive the matched coefficients for the correct interactions.

Only THEN feed the **combined single Wilson vector** to ONE common observable:

```
  BR_theory = BR_2026_compatible(C_SM + ΔC_combined,
       Eγ_cut=1.6 GeV, μ₀, μb, μc, kinetic scheme, HQE inputs, ...).
```

The observable must retain *all relevant* SM×NP and NP×NP interference terms at the claimed perturbative accuracy. Do not sum BR(H₁) and BR(H₂), use effective mass proxies, interpolate the independent pure-state BRs, or replace the old SuperIso SM central value by 3.54×10⁻⁴.

For general Zee f/Y lepton matrices, the quark side is independent of those Yukawas at leading charged-Higgs loop order. That does **not** remove the need to validate the charged mixing/symmetry-basis Type-II assumption, CKM rotations, collider widths or flavor-changing neutral Yukawa terms if allowed by the actual parameterization.

## 5. Acceptance gates before claiming a 2026 exclusion

**P0 — source completeness (currently NOT PASSED).**
Obtain an author-supported public implementation, relevant coefficient-level response tensors and covariance inputs, or independently implement/validate the needed 2026 observable pieces. The paper's Eq. (4) and its 670 GeV lower bound are insufficient to reconstruct them. An unpublished/not-found full kernel cannot be represented as existing.

**P1 — pure Type-II benchmark.**
Reproduce the 2026 SM central prediction and its uncertainty, the single-2HDM-II BR-vs-mass behavior, and the **published >670 GeV, 95% CL** outcome using the SAME model and uncertainty prescription. Do not fit the output to 670 GeV and declare the calculation reproduced; leave independent mass points blinded for validation. Use tanβ=50 as in Fig. 3 plus at least tanβ≈5.6 for the Zee cohort.

**P2 — coefficient matching and algebra.**
For masses 250–1200 GeV and representative tanβ (5.6,50), compare SuperIso A1M matching to independent HEPfit A1P matching *order by order*, including all operators the downstream BR requires; check scheme, μ₀ and running top mass. Ensure endpoint gamma=0,π/2 and degenerate mH1=mH2 algebra, plus two-state NP cross terms in the observable.

**P3 — uncertainty and likelihood.**
Implement the *source-supported* experimental and theory error model (including shared SM/HQE uncertainties and matching scales) and check coverage with the same 2HDM-II control. No experimental-only deviation / σ_exp and no generic Eq.(4) plug-in may be labeled χ²_2026 or a 95% CL.

**P4 — physical Zee spectra.**
Only after P0–P3 can the 27 E1/E3 original spectra be tested for proper quark-flavor constraints. For alternative mixing/mass hypotheses, regenerate an internally consistent scalar potential and one-loop neutrino closure, optimize complete LFV, re-run full 26-beta RGEs and BFB/55-channel unitarity, vacuum search and HiggsTools. Ensure Higgs/Z cascade BR and production are recalculated, not equated with sin²(2γ).

All stages must retain source SHA, order/mass/mixing inputs, numerical finite checks, and **UNKNOWN** allowed state until physically validated.

## 6. Go/no-go decision at E3

- **GO on qualitative physics motivation:** two independent observable approximations show the same significant positive NP direction and an unavoidable flavor-vs-cascade-mixing trade-off for these 27 *selected* spectra.
- **NO-GO on quoting a new exclusion, excluded benchmark fraction, or an improved Zee charged-Higgs lower bound:** full modern matching, observable, theory error and statistically correct likelihood are absent.
- **NEXT SCIENTIFIC ACTION:** acquire or reconstruct the 2026 full-observable kernel and validate the *pure Type-II* model using published benchmark points BEFORE extending it to two mass eigenstates. In parallel, a future genuinely model-consistent heavy-mass rescue scan is justified; gamma-only counterfactuals from E2/E3 are not physical models.
- **Do not add E4 as another legacy-vs-LO numerical rate adjustment.** It would not resolve the leading systematic/precision blocker.

**References checked Oct 19 2026:**
- Misiak et al., arXiv:2608.29863, Sections II–IV, Eqs. (1),(3),(4), Fig. 3: https://arxiv.org/html/2608.29863
- HEPfit historical Type-II single-mass interpolation source: https://hepfit.roma1.infn.it/doc/latest-release/de/da2/bsgamma_t_h_d_m_8cpp_source.html
- HEPfit general bsgamma class overview: https://hepfit.roma1.infn.it/doc/latest-release/d0/d13/class_bsgamma.html
- SuperIso historical tool description: https://superiso.in2p3.fr/

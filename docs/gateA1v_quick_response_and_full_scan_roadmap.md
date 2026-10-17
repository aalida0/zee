# Gate A1V — minimal response check and flavor-only charged-sector scan

**Implementation committed; exact AF compilation and numerical execution
still required.** This gate intentionally brings the project back to the
physics goal: a viable Zee-type scalar sector with large
`H2+ -> H1+ Z` branching ratio.

## Why A1U was necessary — and why not to extend it indefinitely

Standard SuperIso Type-II uses a *single* charged-doublet scalar
(`mass_H`). The Zee scalar sector has TWO charged mass eigenstates
with quark doublet fractions `cos(gamma)` and `sin(gamma)`. The
correct leading charged-scalar new-physics contribution is mixed
at the Wilson-coefficient level, not by averaging independent
single-Higgs branching ratios. Source-pinned A1U has now passed
the mandatory real AF endpoints and degenerate controls.

After that validation, further detailed source-level investigations
are **not the main program**. Gate A1V tests only two concise
remaining diagnostics:

1. **Nonlinear effects** in the legacy observable, by evaluating
   `C(k) = C_SM + k(C_Zee-C_SM)` at k=-1,0,0.5,1,2.
   For a quadratic observable at fixed scales:
   `L=[BR(+1)-BR(-1)]/2`,
   `Q=[BR(+1)+BR(-1)]/2-BR(0)`,
   `BR(+1)=BR_SM+L+Q`.
   Additional half/double points test polynomial closure. These
   bookkeeping values k are *not physical model scan points*.
2. **Limited scale diagnostic** at nominal `muW=2MW`,
   `mub=mbpole/2` and one-at-a-time factors
   0.75/1.25. Such variations are NOT a calibrated perturbative
   theory error or complete uncertainty prescription.

The v5 `bsgamma_Ecut()` internal matching is intercepted using
the exact same guarded A1U `--wrap=CW_calculator` bridge. Both
low-scale and hidden high-scale mixed coefficients use one coherent
Wilson vector. Original SuperIso sources/libraries stay unmodified.

At baseline k=1, Gate A1V must reproduce A1U's *actual AF*
`BR=0.0003931195407821`, and at k=0 reproduce the authentic A1R
SM control `BR=0.0003382457724`. These are checked against
the saved A1U report. No 2026 NNLO result, uncertainty band,
or exclusion likelihood is claimed.

## AF benchmark instructions

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_gateA1v_legacy_response.py' -v

python3 scripts/gateA1v_run_legacy_response.py \
  --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --a1u-result work/gateA1u_legacy_zee_br_v1/legacy_two_state_br.json \
  --output-dir work/gateA1v_legacy_scan
```

Outputs:
- `work/gateA1v_legacy_scan/gateA1v_legacy_response.json`
- `work/gateA1v_legacy_scan/gateA1v_nominal_raw.log`

If the program fails the independent 0.5/2 polynomial or SM closure,
investigate the failure. Do not widen its tolerances.

## Optional *flavor-only* CSV grid

This is an efficient way to evaluate **candidate charged-sector inputs**.
It is *not* a global Zee-model scan. A point is not viable until
the full neutral/potential/lepton sector and all constraints are checked.

```bash
cat > work/gateA1v_input_points.csv <<'CSV'
mH1,mH2,gamma,tanbeta
300,700,1.089,5.597170833164245
350,750,0.7853981633974483,5.0
400,850,1.10,4.0
CSV

python3 scripts/gateA1v_run_legacy_response.py \
  --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --a1u-result work/gateA1u_legacy_zee_br_v1/legacy_two_state_br.json \
  --output-dir work/gateA1v_legacy_scan \
  --grid-csv work/gateA1v_input_points.csv \
  --max-points 1000 --skip-scale-diagnostic
```

The CSV contains the complete legacy `BR`, its SM baseline, and
linear/quadratic new-physics contributions for each row. **There
is deliberately no “pass flavor” or “excluded” column.**

## Next: full Zee-model scan is the priority

The physical scan must generate complete scalar-potential and
fermion-coupling points and apply staged constraints.

1. Generate candidate potential parameters and neutral/charged
   masses/mixings in **one consistent convention**, verifying
   tadpoles, physical mass matrices, perturbativity/BFB, tree-level
   unitarity and (when available) global minimum. The existing
   Gate 6 reconstructed scalar potential provides a seed, not a
   ready-to-use general sample generator.
2. Apply the existing full scalar `S,T,U` and published correlated
   EWPO fit using Gate A1H.
3. Calculate *model-consistent* masses, widths, effective couplings
   and production cross sections, then supply to **HiggsTools**
   HiggsBounds/HiggsSignals. HiggsTools consumes predictions; it
   does not generate the Zee spectrum by itself. The BSM
   `H2 -> H1Z` search topology is not guaranteed to be covered
   by its installed experimental analyses.
4. Apply this source-pinned two-state SuperIso `B -> Xs gamma`
   interface as a **legacy filter/observable**, upgraded later to
   a documented precision likelihood. Do not substitute the
   published single-Higgs Type-II mass bound for this model.
5. Fit Zee antisymmetric `f` and generic lepton Yukawa structures
   to neutrino data; then complete neutral/charged 1-loop LFV
   amplitudes, leading two-loop contributions, and correlations.
   Existing Gates A1B–A1F are partial, **not an approved LFV filter**.
6. Calculate `Gamma(H2 -> H1Z)`, ALL competitive partial widths,
   and signal `sigma(pp -> tbH2) x BR(H2 -> H1Z) x BR(H1 -> tb)`.
   Only fully selected physically viable points should be advanced
   to full Zee-UFO event generation and detector study.

**ScannerS** can be a useful framework for this, but its standard
2HDM/singlet scalar models do not automatically include the
charged-singlet mixed Zee sector; it requires a dedicated model
implementation or an external Zee-specific scan driver.

Literature: Florentino et al., arXiv:2106.08332; Herrero-García
et al., arXiv:1701.05345; Misiak et al. arXiv:2608.29863.

References:
- HiggsTools https://higgsbounds.gitlab.io/higgstools/
- ScannerS arXiv:2007.02985

No numeric Gate A1V output exists until the AF commands succeed.

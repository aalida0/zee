# Gate 5B — FCC-hh associated tbH2± production proxy at 100 TeV

## Observed MG5 result (user-run AF, 2026-10-11)

100 TeV proton-proton Type-II 2HDM 4FS *production-only* LO proxy
generated with MG5_aMC 3.5.9, Key4hep, initial exploratory internal
nn23lo1 PDF, m(h±)=700 GeV, tanbeta=5.7294463.
Includes both charge-conjugate tb h± processes. Original MG5 output:

```text
- Current estimate of cross-section: 1.3676788800000002 +- 0.00731180133888942
     Cross-section :   1.368 +- 0.007312 pb
# original cross-section: 1.3676789000000311
```

**The LO Zee H2± associated-production proxy** under the specific Type-II-like
Yukawa mixing assumption is `sin²γ * sigma_2HDM` with γ=1.089:

- `sin²γ = 0.7852866098109527`
- `sigma_Zee = 1.07401992669 pb = 1074.01992669 fb` (using MG5's unrounded central value)
- Integration error ≈ `0.00574 pb`, NOT the PDF/scale/flavour-scheme theory error.

## Comparison with Gate 5A: 100 TeV

| channel | LO cross section |
|---|---:|
| tbH2± (Type-II production proxy × sin²γ) | 1074.02 fb |
| Z*→H1± H2∓ (analytic DY, sum of both charge assignments) | 4.84316 fb |

Associated tbH2± production is **~221.76 times larger at this screening point**.
That is a cross-section comparison, NOT a discovery-significance comparison.
The two processes have different kinematics and possibly efficiencies/systematics.

## Conditional yields, only to gauge event-count feasibility

Assume 30 ab−1, BR(H2±→H1±Z)=0.70, BR(H1±→tb)=0.95,
BR(Z→ee/μμ)=0.0673, and exactly one direct W→e/μ plus one
hadronic W: `2 × 0.216 × 0.674 = 0.291168`.

| stage | tbH2± | H1± H2∓ |
|---|---:|---:|
| Inclusive produced | ~32,220,598 | ~145,295 |
| After charged-Higgs cascade BR assumptions | ~21,426,698 | ~91,790 |
| Trileptons before detector | ~419,869 | ~1,799 |
| At *hypothetical* 5% total A×epsilon | ~20,993 | ~90 |

The 5% efficiency is **illustrative**, unmeasured and may differ strongly
between channels; it must NOT be used to claim discovery or limits.

## Critical blockers before signal simulation

1. Reconfirm 100 TeV param/run cards in the AF run: MASS 37=700 GeV,
   FRBlock 1=5.7294463, FRBlock 2=1, and 50000 GeV per beam.
2. Redo LO prediction with a consistent **nf=4 LHAPDF set** and scale
   variations; the internal 5-flavor LO set is not a final 4FS prediction.
3. Implement or obtain a gauge-consistent full 2HDM + charged-singlet
   **Zee-type** UFO with both charged mass eigenstates and ZH1H2.
4. Reconstruct a simultaneously allowed scalar-sector point, and
   either impose neutrino/LFV constraints or clearly restrict
   phenomenology to a consistent effective scalar/quark-sector scope.
5. Calculate actual **total widths and BRs** for all open H1/H2 decay
   channels, particularly H2→Wh2, before committing to decay-chain samples.
6. Determine realistic top/Z/multi-b acceptance and ttZ+bb backgrounds
   with systematic uncertainties before judging exclusion or discovery.

**Decision:** retain tbH2± as primary FCC-hh channel; keep
off-diagonal mixed-pair production as a secondary model-discrimination probe.
Priority moves from more LO rates to **full Zee benchmark + width validation**.

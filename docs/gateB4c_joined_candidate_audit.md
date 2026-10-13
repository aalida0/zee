# Gate B4C — joined B4/B2/B3/A1V evidence audit

**Status:** implementation and 9 pure data-integrity regression tests
committed, **not executed on AF**. Report is not an exclusion or
fully allowed-point classification.

## Evidence (user-provided AF runs, 13 October 2026)

- **B4 adaptive scalar/EWPO screen:** 1200 new proposals, 1008
  scalar-theory-screen passes, 992 passes of correlated STU
  ellipsoids, 314 *coarse-binned* distinct retained candidate spectra.
  Of the retained spectra, 160 descended from B1 seed 32, and 154
  from B1 manually inserted seed 0. High acceptance describes local
  adaptive proposals, NOT the fraction of Zee model parameter space
  physically allowed.
- The 30 mass/mixing-diverse shortlisted scalar spectra include
  18 descendants of 32 and 12 of 0:
  `mH1=203.364–350.520` GeV,
  `mH2=637.330–722.258` GeV,
  `mh2=574.944–603.567` GeV,
  `ma=579.583–676.584` GeV,
  `gamma=1.025–1.320`,
  `tanbeta=5.461–5.766`.
- **B2**: 100 algebraically neutrino-closed perturbative `f,Y`
  choices per spectrum, or 3000/3000 with the **SAME fixed**
  normal-ordering central target. The code saved the **five lowest
  *partial*-LFV-score** choices per spectrum; this sorting
  produces selection bias and cannot establish an LFV constraint.
  Across these *best* scores, ratios of included amplitudes/limits
  range approximately from 1.36e-8 to 3.14e-6.
- **B3**: 150 width inventory solutions complete; the old Type-II
  lepton tau width was replaced with general-Zee `f,Y` leptonic
  widths. These are **included LO channels only**, not complete
  physical BR predictions.
- **A1V**: 30 source-checked legacy SuperIso v5
  `B->Xs gamma` observables; 2026 NNLO validation and consistent
  theory/experimental likelihood remain absent.

The preliminary B4 proxy at the highest-ranked B4 spectrum
`B4_0000648` is `0.6804530` with nonleptonic included-only
BR(H2->H1Z) `0.7879982`. B3 should be used to replace these
nonleptonic upper-bound proxies, and A1V must be matched to
each candidate's charged spectrum rather than cited only via the
A1U reference benchmark.

## Run strict four-stage join

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_gateB4c_joined_candidate_audit.py' -v

python3 scripts/gateB4c_joined_candidate_audit.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --b3-csv work/gateB4_zee_adaptive_pilot/B3_widths/cascade_width_corrected_NOT_ALLOWED.csv \
  --a1v-csv work/gateB4_zee_adaptive_pilot/A1V_flavour/scan_flavour_only.csv \
  --output-dir work/gateB4c_zee_joined_audit
```

Expected 30 unique scalar IDs and 150 B2/B3 paired Yukawa rows.
The script rejects:
- missing or duplicated candidate IDs or Y-solution ranks;
- mismatching scalar spectra across B4 and B3;
- A1V flavor rows not **uniquely** matched to the B4
  `(mH1,mH2,gamma,tanbeta)` tuple, regardless of CSV order;
- disagreement between B2 and B3 partial LFV scores and
  neutrino-closure records;
- B3 partial-channel fractions outside [0,1] or exceeding their
  corresponding nonleptonic upper-bound proxy;
- legacy SuperIso total BR failing the saved SM+linear NP+quadratic NP
  decomposition.

Outputs:
- `joint_scalar_neutrino_width_flavour_NOT_ALLOWED.csv`: 30
  joined candidate records with **per-candidate minima/medians/maxima**
  across saved B2/B3 solutions, best *partial* LFV score,
  matched A1V full legacy BR, and detailed provenance.
- `summary.json`: count, ranges, seed ancestries and explicit
  `physically_allowed:null`, `complete_LFV_amplitudes:false`,
  `HiggsTools_applied:false`,
  `modern_BtoXsGamma_exclusion:false`.

**Important:** B4C is a data integrity and candidate prioritization
audit, not a paper-ready experimental constraint. Even if the
computed B3 widths barely reduce cascade fractions and legacy
SuperIso values appear close to measurements, no full-model viability
has been demonstrated.

## Scientific next gate

Validate complete Zee `mu->e gamma` dipoles, specifically independent
Barr–Zee neutral Higgs and fermionic loop coefficients, and other
low-energy LFV channels including `mu->3e`, `mu-e` conversion,
lepton universality; document one common gauge/flavor convention and
neutrino parameters. Build and validate the *same* full-model spectrum
and widths for HiggsTools and a matched modern-precision two-charged
`B->Xs gamma` likelihood. Only then derive a constrained
sigma(tbH2) x BR(H2->H1Z) x BR(H1->tb) envelope.

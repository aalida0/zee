# Zee global scan — minimal Priority‑1 integration branch

Branch: `zee-global-priority1-minimal`. Based on the original E2–F9 scientific implementations. The entire existing analysis remains unchanged.

## Already executable

- `scripts/zee_p1_minimal_pipeline.py`: single CLI, streaming JSONL scan records, five backend coverage statuses and SHA256 output. **No incomplete/legacy calculation can make a false experimental exclusion claim.**
- `scripts/zee_p1_existing_physics.py`: thin wrappers around existing B4 scalar mass/BFB/unitarity, EWPO, Gate6 leading-order **included** charged widths, and B2 exact-neutrino target with a single partial-LFV seed. These are physically calculated **subsets**, not final constraint decisions.
- `tests/test_zee_p1_minimal_pipeline.py`: seven dependency-free regressions.
- `.github/workflows/zee-priority1-minimal.yml`: isolated CI.

## Run the integration immediately

```bash
cd /home/aalida/zee
git fetch origin
git switch zee-global-priority1-minimal
git pull --ff-only
mkdir -p work/p1_smoke
printf '%s\n' '{"id":"B4_test0001"}' '{"id":"B4_test0002"}' > work/p1_smoke/points.jsonl
python scripts/zee_p1_minimal_pipeline.py --points work/p1_smoke/points.jsonl --output work/p1_smoke/coverage.jsonl
python -m unittest discover -s tests -p 'test_zee_p1_minimal_pipeline.py' -v
```

All backend results are JSON objects keyed by candidate ID and component (`bsgamma`, `lfv`, `higgs`, `rates`, `neutrino`). Merely marking a provider as `status: validated` does not make it reliable or produce allowed/excluded model classifications. The full suite of experimental comparisons must be independently validated before implementing a full global confidence-level test.

## Priority‑1 implementation ledger

| Component | Working backend from original branch | Missing for fully model-consistent final constraint |
|---|---|---|
| (B\to X_s\gamma) | F6 complete **legacy** SuperIso inclusive branching ratio + F3/F4/F5 Wilson audits | Independent modern 2026 order/scheme-consistent **two physical charged-state** NLO/NNLO full rate, model-dependent theory errors and calibrated experimental likelihood |
| LFV | B2, D1/D2/D4, D5, `zee_lfv_backend.py` partial coherent dipoles and partial Barr–Zee | Exhaustive one-/two-loop channels including `\mu\to e` conversion and independent double counting/operator-basis checks, validated experimental covariance |
| HiggsSignals/HiggsBounds | E5–E6 **125-GeV-only** HiggsSignals effective signals incl. charged loop photons | All charged/neutral heavy particle predictions, experimental HiggsBounds version/dataset checks, interference / SM-like and BSM channels as applicable |
| Charged and neutral widths | Gate6 leading-order **included charged** channels, B3 true general Zee leptons | Full charged/neutral tree/off-shell/QCD channels plus independent cross-validation (MadWidth where valid) |
| Hadronic rates | Yukawa/mass/coupling proxy from B4/E7 | Dedicated validated model-specific (pp\to H_{1,2}^{\pm},H,A) cross sections at specified LHC energy, QCD orders, PDFs and production modes |
| Neutrino oscillation constraints | Algebraic exact B2/E3 reconstruction of one target matrix | PMNS and mass-splitting experimental likelihood; ordering and parameter uncertainties sampled; LFV-minimized Yukawa solutions for each viable scalar point |

**What was not done:** no new modern NNLO matching calculation, no complete LFV two-loop/μ-e conversion, no actual HiggsBounds five-particle exclusion, no complete neutral/charged widths, no computed hadronic cross sections, and no multimillion-point physics campaign. Consequently none of those can truthfully be described as implemented or validated by this minimal integration branch.

## Next engineering milestones

1. Implement a real modern two-charged (B\to X_s\gamma) backend with the published same-order SM and Type-II reference controls, a complete BSM correction and uncertainty interface. Do not interpret a legacy-to-modern shift transplant as an exclusion.
2. Implement and independently regression-test the missing LFV operators/loop topologies and conversion nuclei, then a multi-ordering oscillation likelihood.
3. Implement all five Higgs state decay tables and hadronic productions from a consistent Lagrangian/UFO; validate partial widths/cross sections independently before sending any `Bounds` prediction.
4. Only then add physical, statistical comparison logic and large-scale persistent streaming/HTCondor orchestration with selection-bias coverage.

A single implementation sprint cannot certify these research-grade physics computations without formulas, independent references, cross-code tests and the AF physics datasets. This branch intentionally favors scientifically accurate and short code over fabricated completeness.

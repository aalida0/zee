# Gate 5A: FCC-hh off-diagonal mixed charged-Higgs production

## Inputs and observed results

Benchmarks used for analytic LO s-channel Z*-exchange only:

- m(H1±) = 300 GeV (illustrative, not a validated simultaneous P2 point)
- m(H2±) = 700 GeV (illustrative, not a validated simultaneous P2 point)
- gamma = 1.089 rad
- |g(ZH1H2)| = 0.1520746183402528 in the nominal Gate-5 coupling convention
- LHAPDF 6.5.5, NNPDF31_lo_as_0130, member 0, Q = 1000 GeV
- Includes H1+ H2- and H1- H2+, no decay or detector selection

| sqrt(s) | sigma(H1± H2∓), fb |
|---|---:|
| 80 TeV | 3.53615 |
| 100 TeV | 4.84316 |
| 100 TeV (90 × 60 integration nodes) | 4.84316 |

Comparison verifies *numerical* convergence to the reported six significant figures,
not perturbative or PDF/systematic accuracy.

## Conditional HL/FCC signal-event interpretation

These illustrative and unvalidated branching ratios are assumed:
BR(H2→H1Z)=0.70; BR(H1→tb)=0.95;
BR(Z→ee or μμ)=0.0673; BR(W→eν/μν)=0.216;
BR(W→hadrons)=0.674. Luminosity is assumed 30 ab−1.

| rate stage | 80 TeV events | 100 TeV events |
|---|---:|---:|
| Produced H1± H2∓ pairs | 106,085 | 145,295 |
| Full cascade H1+ H1- Z → tt̅ bb̅ Z | 67,019 | 91,790 |
| Z→ll, exactly one top W→direct e/μ, other hadronic | 1,313 | 1,799 |
| Above × hypothetical 5% acceptance × selection efficiency | 66 | 90 |
| Above × hypothetical 10% acceptance × selection efficiency | 131 | 180 |

None of the efficiencies has been simulated. No backgrounds or discovery significance evaluated.

## Changes after initial Gate-5A result

The first integration script accepted `--gamma` but previously only **reported**
the angle while using a fixed `g12`. The original gamma=1.089 output is
unchanged by the patch. Future gamma scans now use
`g12 = 0.15207461834 * sin(2*gamma)/sin(2*1.089)` by default;
an explicit `--g12` overrides this. A separate expression with alpha(MZ)
and sin²thetaW=0.23122 gives g12≈0.15261 at the same angle;
these slightly different EW input conventions should not be mixed
in a precision prediction. Their cross-section difference is approximately 0.7%.

## NEXT ACTIONS

1. Run the 100 TeV 4FS Yukawa-production **proxy**, applying sin²γ to
   the MG5 Type-II rate; check the run-card beams 50 TeV each.
2. Confirm theory systematics with a proper nf=4 PDF set and renormalization/
   factorization scale variations. Do not treat the internal LO PDF as final.
3. Implement a real Zee 2HDM+charged singlet UFO and obtain a *simultaneously*
   viable scalar-sector point, including neutrino/LFV conditions or an
   explicitly limited model interpretation.
4. Validate H2→H1Z vs H2→tb, H2→Wh2 (kinematically open at mH2=700 GeV,
   mh2=580.7 GeV), and all other open bosonic/leptonic channels.
5. Only then generate signal and at least ttZ+heavy flavour backgrounds
   for a multib and resonance reconstruction analysis.

# Zee Section 8 — Q2c UV versus hierarchical EFT source audit

**19 October 2026 — STATUS: HEAVY_SINGLET_EFT_NOT_APPLICABLE_TO_CURRENT_CANDIDATES, NOT A ZEE-MODEL EXCLUSION.**

## Scientific question

Our previous integrated Q2 numerical audit passed 108 tests and
matched 20 saved B2 Zee lepton solutions to the pure-2HDM RGEs,
with small toy radiative quark off-diagonal neutral Yukawas.
However it omitted the charged singlet f and treated the gauge
couplings as fixed. Before using those numbers for flavor limits
we must check whether an effective pure-2HDM description is
consistent with the actual mixed charged-scalar spectrum.

Primary research source: Schmidt and Vandeleur,
*Running of neutrino mass parameters in the Zee model*,
JHEP 06 (2026) 006, https://arxiv.org/html/2512.17235v2
(Eq.14 for the charged mixing/trilinear; Sec.3 for the
hierarchy and matching; Sec.3.1 for explicitly not
running the full Zee renormalizable theory; Appendix B.1
for RGEs of the **2HDM EFT**, not full UV Zee).

The authors primarily require the charged singlet
heavier than the extra Higgs doublet; they first integrate
out the singlet and only then the extra doublet.
They do not supply complete UV f-dependent Yukawa RGEs.
Their alternative hierarchy is discussed but does not
supply a quantitative ready-to-use matching for our
strongly mixed non-decoupling charged spectra.

## Exact charged-scalar mass matrix audit

Our project uses the charged mixing convention:
H1+ = cos(gamma) H_D+ + sin(gamma) chi+
H2+ = -sin(gamma) H_D+ + cos(gamma) chi+.

Thus M² in (H_D, chi) = R^T diag(mH1²,mH2²) R,
R=[[cosgamma,singamma],[-singamma,cosgamma]], and:

  M_DD² = mH1² cos²gamma + mH2² sin²gamma
  M_chichi² = mH1² sin²gamma + mH2² cos²gamma
  |M_Dchi²| = (mH2²-mH1²)|sin2gamma|/2
             = v |mu_Zee|/sqrt(2).

The last identity is source Eq.(14), up to irrelevant
rephasing of the dimensionful trilinear sign.

These entries are **broken-phase charged mass-matrix
elements**, NOT directly unbroken-theory bare masses
and NOT a complete EFT truncation error estimate.
Nonetheless, the necessary heavy-singlet diagonal
mass ordering is violated for both current points.

| Reconstructed quantity | B1 candidate 32 | B1 candidate 0 |
|---|---:|---:|
| mH1 [GeV] | 208.76954 | 300 |
| mH2 [GeV] | 681.85192 | 700 |
| gamma [rad] | 1.12012593 | 1.089 |
| sqrt(M_DD²) [GeV] | 620.47220 | 635.70012 |
| sqrt(M_chichi²) [GeV] | 351.45558 | 419.38688 |
| singlet/doublet diagonal mass ratio | 0.56643 | 0.65972 |
| sin²gamma (H1 singlet fraction) | 0.81028 | 0.78529 |
| |mu_Zee| from Eq.14 [GeV] | 948.84816 | 943.40015 |
| heavy-singlet ordering required by primary EFT | FAIL | FAIL |

Light H1 is singlet-dominated, and the primary
hierarchy of the 2026 EFT paper is reversed in both
candidate spectra. **The Zee model itself has
not failed**: it needs a source-validated fully
mixed one-loop UV/threshold treatment.

Do not interpret the large dimensional mu_Zee
on its own as proof of nonperturbativity or unstable
vacuum. Those require a scalar analysis, not just
the charged 2x2 mass matrix.

## One-loop UV gauge correction that can be calculated

The Zee charged scalar is a complex SU(2) singlet with
SM hypercharge Y=+1. Relative to two doublets, its
one-loop contribution in non-GUT gprime convention is
delta b_gprime = +1/3, delta b_g2=0, delta b_g3=0.

  b_2HDM = (7,-3,-7)
  b_Zee  = (22/3,-3,-7)

where the order is gprime,g2,g3 and each beta is
16pi² d(g_i)/dlnmu = b_i (g_i)^3.

This corrects *the gauge beta functions only*;
it does not supply the unknown f-dependent lepton
beta-functions. Illustrative fixed-content
running with gprime(700 GeV)=.36 gives
gprime(10 TeV)~.36562913 in 2HDM and
~.36590381 in Zee (+0.075%, NOT an observable).
Because threshold matching is deliberately
absent, neither value is a realistic experimental
running-coupling prediction.

## One large AF validation command (new Q2c)

Source and tests:
- scripts/zee_section8_Q2c_UV_EFT_scope_audit.py
- tests/test_zee_section8_Q2c_UV_EFT_applicability.py

After GitHub pull, run just:

    cd /home/aalida/zee
    git pull --ff-only
    python3 scripts/zee_section8_Q2c_UV_EFT_scope_audit.py \
      --output-dir work/zee_section8_Q2c_fullZee_EFT_scope_v1

The runner itself performs all 11 Q2c regression tests,
inverts the charged mass matrices for every saved
scalar candidate and checks eigenvalues, trilinear
and boundary controls, verifies the charged-singlet
one-loop gauge beta, and independently re-validates
all 20 stored matched B2 scalar/lepton combinations.
It refuses mismatched IDs or wrong counts; failure
returns nonzero with a diagnostic JSON.

Outputs:
- unit_tests.log
- summary.json (hashes of both input files,
  detailed mass/gauge reconstruction, all 20 B2
  solution checks, and the incomplete-physics flags).

The success label means that we have *correctly
identified the heavy-singlet hierarchical EFT
as inapplicable to these points*, not that the
full Zee model or radiative quark alignment has
been experimentally excluded.

## Next decisive step

Derive/source the COMPLETE renormalizable Zee
one-loop f- and leptonic-Yukawa beta functions
with correct two-component-fermion index
conventions, perhaps using RGBeta and an
independent PyR@TE/SARAH check. First demonstrate
the source-correct 2HDM f->0 limit.
Then treat running in the full unbroken model
above its charged thresholds; threshold matching
for a strongly mixed mass spectrum will require
its own controlled prescription, not the
hierarchical singlet-first approximation.

Next supply lepton solutions using modern NuFIT
and complete LFV including coherent 2-loop
Barr-Zee and mu-e conversion. Only then evaluate
physical mass-basis quark FCNCs with measured
CKM, masses, hadronic Wilson coefficients and
full b->s gamma scheme matching.

No physical Zee benchmark currently passes
ALL of those requirements. Avoid more arbitrary
toy scans as substitutes for these physics gates.

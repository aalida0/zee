# Q2d — general Zee Yukawas and restricted scalar-potential RG stability

**19 October 2026. STATUS: STRUCTURAL SOURCE AUDIT, NOT A COMPLETE ZEE RGE OR MODEL ACCEPTANCE.**

## Motivating theoretical issue

The Zee project retains a *restricted* two-Higgs-doublet
scalar potential with lambda6=lambda7=0 and general charged
lepton Yukawas necessary for neutrino masses, while imposing
Type-II quark alignment at a declared matching scale.
The original motivation is to analyze
pp -> t(b) H2+ -> t(b) H1+ Z -> t(b) tbZ.

However the lepton sector does not obey the same exact Z2
protecting these quartics in a Type-II NFC 2HDM.
Therefore **lambda6 and lambda7 may be radiatively
generated** even though they are set to zero at a
chosen boundary. This is a new necessary physical gate
in addition to the f-dependent Yukawa beta-functions
and radiatively induced quark FCNC.

**Caution**: The absence of a protection theorem is
not proof that beta_lambda6 and beta_lambda7 are
nonzero at every numerical point; cancellations
can occur. No beta-function coefficient or beta-value
is produced in this audit.

## Source anchors

1. Schmidt and Vandeleur, JHEP06(2026)006,
   arXiv:2512.17235v2, Sec.2 (full Zee Lagrangian)
   and Sec.3/App.B (hierarchical EFT matching and
   2HDM EFT running; NOT a full Zee UV RGE).
   https://arxiv.org/html/2512.17235v2
2. Ferreira, Lavoura and Silva, PLB688 (2010)
   341, arXiv:1001.2561. Quark Yukawa one-loop
   beta functions with general lepton Yukawas.
   https://arxiv.org/abs/1001.2561
3. Machacek and Vaughn, NPB236 (1984) 221,
   general renormalizable Yukawa beta functions.
   DOI:10.1016/0550-3213(84)90533-9
4. *New symmetries of the two-Higgs-doublet model*,
   EPJC (2024), Sec.2.4 Eqs.(2.23f-g):
   the scalar/gauge terms in beta_lambda6/lambda7
   are proportional to lambda6/lambda7, but the
   paper separately denotes **beta^F** fermion
   contributions. Its Z2 preservation result is
   in the context of a full symmetry, not a
   proof for an unsymmetrized general-lepton Zee.
   https://link.springer.com/article/10.1140/epjc/s10052-024-12561-8

## What is established without guessing f coefficients

At the quark Type-II Yukawa matching boundary,
Gamma=(Gamma1,0), Delta=(0,Delta2), generic
leptons Pi=(Pi1,Pi2), the one-loop **local
quark Yukawa** beta source is unchanged as an
explicit one-loop quark vertex by the f_LLchi
interaction: quarks have no charged-singlet
Yukawa vertex and the superrenormalizable
Zee scalar trilinear cannot be inserted as
a dimensionless one-loop Yukawa beta in MS.
This is a field-content and power-counting
inference, NOT a directly source-tabulated full
Zee RGE. The new singlet DOES affect one-loop
hypercharge running, confirmed in Q2c.
f may affect the coupled lepton Pi running and
therefore the eventual quark Yukawa evolution.

For any unknown corrections delta(D Pi1),
delta(D Pi2) to the rescaled beta functions
D=16pi² d/dln(mu), the exact algebraic
identity is:

    delta(D T21) = Tr[delta(D Pi2) Pi1^dagger
                       + Pi2 delta(D Pi1)^dagger].

This does NOT supply those unknown beta terms.
No fictitious f-dependent numerical coefficient
is fitted or used.

Nonzero, gauge-invariant lepton spurion contractions:

    T21 = Tr(Pi2 Pi1^dagger)
    I6  = Tr(Pi1 Pi1^dagger Pi1 Pi2^dagger)
    I7  = Tr(Pi2 Pi2^dagger Pi2 Pi1^dagger)

are characteristic doublet-index contractions
that can contribute to the one-loop scalar
four-point counterterms in the general 2HDM.
These are not a complete source for
beta_lambda6/7, and no quartic beta coefficients
are asserted. Their weak-lepton-flavor basis
invariance, complex conjugation conventions
and independence from spuriously assuming a
Hermitian Chen Yukawa are tested.
When Pi2=0 (exact Type-II lepton Z2 in this
doublet basis), T21=I6=I7=0 identically.

In the full Zee scalar potential the portal
k12/lambda10 may also explicitly break the
symmetry, so setting lambda6=lambda7=0 is
not symmetry protected in that generic
model even when a particular Yukawa invariant
happens to vanish. The full scalar + Yukawa
Lagrangian must be audited simultaneously.

## All 20 previous B2 solutions: single consolidated run

New source:
scripts/zee_section8_Q2d_lepton_spurion_scalar_RG_audit.py

New tests:
tests/test_zee_section8_Q2d_lepton_spurion_scalar_RG_audit.py

The main integrated runner has ALSO been upgraded
and is the user-preferred **ONE COMMAND**:

    cd /home/aalida/zee
    git pull --ff-only
    python3 scripts/zee_section8_run_integrated_Q2_validation.py \
      --output-dir work/zee_section8_Q2_integrated_v3

Expected if all tests succeed:
- 114 required regression tests (the previously
  successful 103 plus 11 Q2d).
- If SciPy remains installed, 16 optional subset
  Barr-Zee tests: **130 total**.
- 20/20 B2 matched scalar, neutrino,
  Yukawa, old Q2a truncated finite RG inputs.
- 20/20 Q2d complex lepton spurion reports,
  each with f Frobenius invariant, I6, I7,
  and T21, verified against Q2b.
- Type-II lepton control and RK4 convergence.
- Q2c reversed singlet-first EFT hierarchy.
- All complete Zee-lepton RGEs,
  full scalar lambda6/lambda7 RGEs,
  modern neutrino+LFV fit, hadronic FCNC and
  b->s gamma remain **NOT ESTABLISHED**.
- The summary records whether all 20 T,I6,I7
  happen to be nonzero at a stated tiny numerical
  threshold. Those values are *observations*
  rather than hard-coded expected physics or
  exclusion criteria. A vanishing I6 or I7
  would require investigating cancellations,
  not automatically accepting a protected symmetry.

The detailed JSON includes one record per
stored B2 solution, input SHA256, test failures,
strict missing-physics flags and physical
allowed status None. The runner never
silently calls a model point physically allowed.

## Subsequent theoretical calculation

The next genuine research step is an independently
cross-checked generation of COMPLETE UV Zee
one-loop beta_f, beta_Pi1/2, beta_lambda6/7
(and the scalar singlet quartics) in a single
specified MS renormalization convention.
Recommended sources and tools: Machacek-Vaughn
general RGE formulas, PyR@TE3 / RGBeta or
SARAH model implementation, and a separately
implemented diagrammatic or spurion check.
Reproduce the FLS 2HDM beta Pi/quark equations
as f->0 and test protected Type-II limits.
This must be done BEFORE finite-scale
phenomenological bounds on a general Zee
lepton parameter point.

No physical Zee benchmark has been certified
experimentally allowed. All 20 B2 Yukawa
sets are from an old fixed NO neutrino target
and have only partial LFV diagnostics.

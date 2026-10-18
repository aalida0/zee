# Zee Section 8 — quark-aligned EFT, theoretical gate Q1

**Status (2026-10-18): LOCAL_ONE_LOOP_QUARK_RGE_IDENTITY_PASS_NOT_FCNC_OR_MODEL_ALLOWED**

## Program

Retain the restricted CP-conserving 2HDM plus charged-singlet Zee scalar sector of Florentino–Romão–Silva (2021), with lambda6=lambda7=0, and target pp -> t(b) H2± -> t(b) H1± Z -> t(b) t b Z. The generic leptonic Zee Yukawas are allowed; Type-II quark alignment is a **matching-scale boundary condition**, not an exact full-theory protecting symmetry:

rho^u = cot(beta) kappa^u, rho^d = -tan(beta) kappa^d; rho^ell unrestricted and f^ell antisymmetric.

In the symmetry-doublet basis used in the one-loop source: Gamma=(Gamma1,0), Delta=(0,Delta2), Pi=(Pi1,Pi2) unrestricted. The old 2022 family-dependent exact Z2 model is a **different theory**: its symmetry also forces k12=0, whereas this finite-scale EFT may retain k12 != 0. The old family-Z2 NuFIT6.1 IO 12-run minimax profile screen found a best worst 2D Delta-chi2 ~25.09 compared with the usual 3-sigma two-dof threshold 11.83. That is a strong negative phenomenological screen, not a global exclusion.

## Source-derived Q1 RGE identity

Ferreira, Lavoura, Silva, Phys. Lett. B 688 (2010) 341, arXiv:1001.2561, Eqs. (3a–c),(4a–c), defines D=16 pi² d/dln(mu) and supplies the pure-2HDM one-loop quark Yukawa beta-functions. At the quark Type-II matching boundary:

D Gamma2 = T Gamma1,
D Delta1 = T Delta2,
T = Tr(Pi2 Pi1 dagger) = Tr(Pi1 dagger Pi2).

The lepton couplings in this basis are obtained from Higgs-basis kappa and rho by:
Pi1 = c_beta kappa^ell - s_beta rho^ell;
Pi2 = s_beta kappa^ell + c_beta rho^ell.

The generic T != 0 produces a radiative **wrong-doublet quark coupling**, but the newly generated first-order matrices are proportional to the parent quark Yukawas: this **alone is not an FCNC**. A special T=0 removes the local first-order source, but is NOT a proven RG-invariant condition after coupled evolution. This local tangent does not establish the survival of exact Type-II structure, nor finite-run flavor alignment. Do not infer dangerous quark neutral FCNC directly from a nonzero T, and do not infer no FCNC at finite scales from the proportional tangent.

The additional charged Zee singlet with f LL chi, singlet quartics, mu4, possible CP phases and thresholds are NOT part of the source's complete 2HDM quark Yukawa equations. The tool is a necessary boundary audit, not a complete Zee RGE calculation.

## References

1. Florentino, Romao, Silva, EPJC 81 (2021) 1148, Section 8: https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2
2. Ferreira, Lavoura, Silva, PLB688 (2010) 341: https://ar5iv.labs.arxiv.org/html/1001.2561
3. Braeuninger, Ibarra, Simonetto, PLB692 (2010) 189, RG-induced aligned-2HDM FCNC: https://www.sciencedirect.com/science/article/abs/pii/S0370269310008786
4. Herrero-Garcia, Ohlsson, Riad, Wiren, JHEP04 (2017) 130, general Zee neutrino and LFV scan: https://link.springer.com/article/10.1007/JHEP04%282017%29130

## Reproducible code

Source: scripts/zee_section8_quark_alignment_one_loop_gate.py
Tests: tests/test_zee_section8_quark_alignment_one_loop_gate.py

An independently implemented local NumPy check of the eight Q1 identities/tests passed. **The committed repository scripts themselves still require validation on AF**.

    cd /home/aalida/zee
    git pull --ff-only
    python3 -m unittest discover -s tests -p 'test_zee_section8_quark_alignment_one_loop_gate.py' -v
    python3 scripts/zee_section8_quark_alignment_one_loop_gate.py \
      --tanbeta 5.6 \
      --output work/zee_section8_quark_alignment_Q1_tangent_v1.json

The illustrative lepton matrices in this script are NOT a neutrino fit; its sample wrong-doublet ratios are NOT an FCNC limit.

## Subsequent mandatory physics gates

**Q2 complete quark RG and induced FCNC.** Independently derive/source the full coupled model's RG equations (especially the singlet f contributions to charged-lepton running), declare matching scale and renormalization scheme, integrate finite intervals with quark masses/CKM and scalar thresholds, re-diagonalize the running quark masses, extract physical off-diagonal neutral Higgs Yukawa couplings and validate them. One-loop local tangent alone cannot rule out all higher-order or long-distance effects.

**Q3 quark-flavor observables.** Compute Delta M_K, Delta M_Bd, Delta M_Bs, epsilon_K, rare flavor processes and both charged-scalar contributions to B -> X_s gamma using source-audited Wilson coefficients, matching scales and controlled QCD theory errors. The old single Type-II charged mass bound is NOT an allowed-point calculator.

**Q4 neutrinos, LFV and scalar.** Fit NuFIT6.1 and applicable newer neutrino data using general f and rho^ell; fully compute 1-loop and Barr-Zee LFV, mu-e conversion and lepton widths. Enforce scalar BFB, perturbative unitarity, global charge-breaking vacuum, oblique EWPO, HiggsTools, complete widths, collider direct bounds and model-consistent production. Recompute scalar constraints if tanbeta or k12 changes.

**Q5 collider.** Build narrow-width-checked NLO-informed 4FS/5FS production, Delphes acceptance, backgrounds, systematics and expected CLs in physically allowed benchmarks; assess novelty separately.

**If Q2–Q4 do not work:** do not fabricate allowed points or impose arbitrary Yukawa tunings. First fallback is a gauge-consistent **conditional** collider study with upper limits on sigma(pp -> t(b) H2±) x BR(H2± -> H1± Z) x BR(H1± -> tb) versus masses, finite widths, scalar mixing and production model, explicitly distinguishing it from a demonstrated minimal Zee interpretation. Second fallback is a *new, independently audited* flavor symmetry/UV completion; not another assumption silently identified with Type-II.

**No fully allowed Zee point exists in this project yet.** Q1 is an exact local beta-function consistency test only.


## Q2a: exploratory finite one-loop *pure 2HDM* Yukawa flow

Added scripts/zee_section8_quark_alignment_truncated_flow.py and
tests/test_zee_section8_quark_alignment_truncated_flow.py.
These integrate Ferreira–Lavoura–Silva (2010) Eqs. (3)–(5)
for Gamma1/2, Delta1/2 and Pi1/2 using SciPy-free RK4,
fixed illustrative gauge inputs and fixed tanbeta, then
diagonalize the quark mass Yukawas using complex SVD and
inspect off-diagonal Higgs-orthogonal rho^u/rho^d matrices.

**Illustrative independent local computation** (NOT a Zee benchmark):
Type-II quarks at 10 TeV, fake CKM-like matrices, general
illustrative lepton Pi and scales 10 TeV -> 700 GeV:
- initial down/offdiag neutral rho: exact 0
- initial up/offdiag neutral rho: ~1.4e-18
- final down max |rho_ij| (i!=j): ~6.15e-9
- final up max |rho_ij| (i!=j): ~1.67e-10.

Under an exactly Type-II lepton **control** (Pi2=0 at the
high scale), the same RG steps preserve approximate zero
off-diagonal rho_d (~1e-25) and rho_u (~1e-20).
The general-lepton example varies with its arbitrary
lepton Yukawa size, and is NOT a phenomenological
prediction or physical bound.

**NONNEGOTIABLE LIMITATIONS:**
- This is ONLY a pure-2HDM Yukawa-subsector beta flow,
  not a complete Zee coupled RGE with the f LL chi term,
  singlet quartics, charged mixing or scalar thresholds;
- no running of the gauge couplings or vev angle;
- synthetic quark/CKM-like values and **unfitted** leptons;
- no matching onto meson mixing or flavor EFT Wilson coefficients,
  no hadronic or experimental FCNC likelihood;
- no numerical proof that a physically fitted general Zee
  spectrum has acceptably small induced FCNC;
- output is a structural demonstration that *finite*
  pure-2HDM evolution can generate off-diagonal rho,
  despite local Q1 wrong-doublet tangent proportionality.

AF commands:

    cd /home/aalida/zee
    git pull --ff-only
    python3 -m unittest discover -s tests \
      -p 'test_zee_section8_quark_alignment_one_loop_gate.py' -v
    python3 -m unittest discover -s tests \
      -p 'test_zee_section8_quark_alignment_truncated_flow.py' -v
    python3 scripts/zee_section8_quark_alignment_truncated_flow.py \
      --tanbeta 5.6 --high 10000 --low 700 --steps 120 \
      --output work/zee_section8_quark_alignment_Q2a_generic_toy_v1.json
    python3 scripts/zee_section8_quark_alignment_truncated_flow.py \
      --tanbeta 5.6 --high 10000 --low 700 --steps 120 \
      --typeii-leptons-control \
      --output work/zee_section8_quark_alignment_Q2a_typeII_control_v1.json

**Next decision-critical work:** source or derive the **complete
Zee-model** coupled beta functions and feed in leptonic
Yukawa solutions that pass *modern* NuFIT and LFV before
any experimental quark-FCNC statement. Q2a does not
replace Q2 full coupled RGEs or Q3 experimental limits.


## Q2a user-run AF reproduction and 2026 EFT literature checkpoint (October 2026)

User ran \`scripts/zee_section8_quark_alignment_truncated_flow.py\`
with \`tanbeta=5.6, high=10000 GeV, low=700 GeV, steps=120\`.
Actual output:

    STATUS ZEE_TRUNCATED_PURE_2HDM_YUKAWA_FLOW_NOT_PHYSICAL_FCNC_BOUND
    initial down max |rho_offdiag| = 0
    initial up max |rho_offdiag| = 1.36337468407239e-18
    final down max |rho_offdiag| = 6.1545176620916696e-09
    final up max |rho_offdiag| = 1.6685582310783954e-10
    initial largest y_down = .024,  final = .029134207020041616
    initial largest y_up   = .95,   final = 1.0775225196883416
    FULL_ZEE_RGE_OR_FCNC_LIKELIHOOD False
    PHYSICAL_ZEE_ALLOWED False

Interpretation: the **toy truncated pure-2HDM Yukawa flow**
does generate flavor-off-diagonal neutral-quark Yukawa matrices
from the imposed matching-scale Type-II boundary in the
presence of unfitted general doublet lepton Yukawas.
Numerical agreement with independent prior local toy run
validates reproducibility, NOT physical Zee or
flavor-constraint viability. No meson mixing,
FCNC Wilson coefficient, full model running, error budget,
actual measured CKM input, scale-threshold uncertainty or
neutrino/LFV-fitted lepton parameters was computed.

**Critical new source (published 2026-06-01):**
Michael A. Schmidt and James Vandeleur,
"Running of neutrino mass parameters in the Zee model,"
JHEP 06 (2026) 006,
https://doi.org/10.1007/JHEP06(2026)006 ,
arXiv:2512.17235.
This **existing** work derives Zee-specific one-loop EFT
matching and uses the 2HDM RGEs to quantify corrections to
neutrino mass differences, mixing angles and phases across four
scenarios. It supplies an important source benchmark for
our eventual Zee EFT matching/threshold treatment and materially
limits novelty of a standalone neutrino RG-running paper.
It does NOT (from its published abstract) establish our
quark-alignment boundary's finite quark-FCNC
compatibility or validate current toy flavor numbers.
Do not imply the source contains complete UV Zee quark
FCNC constraints without auditing its full formulas.

Independent generic RGE generator:
PyR@TE 3 (Sartore & Schienbein CPC 2021),
https://github.com/LSartore/pyrate ;
capable of generating RGEs for generic renormalizable
nonsupersymmetric models. A faithful Zee model file,
charged-singlet leptonic f tensor, matching conventions
and independent beta-coefficient checks are prerequisites
before using its output physically. Another relevant
framework is RGBeta (referenced by the Schmidt-Vandeleur
paper). Do not imply these packages are already installed.

**Immediate inexpensive control:**

    cd /home/aalida/zee
    python3 -m unittest discover -s tests \
      -p 'test_zee_section8_quark_alignment_one_loop_gate.py' -v
    python3 -m unittest discover -s tests \
      -p 'test_zee_section8_quark_alignment_truncated_flow.py' -v
    python3 scripts/zee_section8_quark_alignment_truncated_flow.py \
      --tanbeta 5.6 --high 10000 --low 700 --steps 120 \
      --typeii-leptons-control \
      --output work/zee_section8_quark_alignment_Q2a_typeII_control_v1.json

The Type-II lepton control should stay near floating-point zero,
establishing that nonzero flavor offdiagonal entries in the generic
toy are induced by relaxing the lepton Yukawa texture rather than
SVD rotation noise. Step-halving stability is explicitly tested.
Next meaningful **physical** gate is not more toy iterations;
it is a source-validated Zee-matching/full-model RGE input
with general neutrino/LFV-compatible lepton Yukawas and actual
quark masses/CKM, followed by DeltaF2 and b->s gamma constraints.



## AF Q2a Type-II lepton CONTROL PASS — completed (2026-10-19)

User supplied actual AF command output for
\`scripts/zee_section8_quark_alignment_truncated_flow.py --typeii-leptons-control\`
with matching high=10 TeV, low=700 GeV, tanbeta=5.6,
steps=120 (same as prior generic-lepton toy).

At the high scale both toy configurations have
\`max_abs_rho_offdiag(down)=0\`, and
\`max_abs_rho_offdiag(up)=1.36337468407239e-18\`.

At low scale:

| Toy branch | down max \`|rho_offdiag|\` | up max \`|rho_offdiag|\` |
|---|---:|---:|
| **Unfitted generic doublet-lepton Yukawas** | **6.1545176620916696e-09** | **1.6685582310783954e-10** |
| **Exact Type-II doublet-lepton control** | **1.9650578367537174e-17** | **3.244755357147471e-17** |

Type-II control terminal quark mass-Yukawa singular values:
down [3.308658641177962e-05,6.862303850316814e-04,2.913201618464826e-02];
up [1.5149140120662072e-05,8.506807411421055e-03,1.077524737878739].
These are *running synthetic Yukawas*, not measured quark masses
or a benchmark with a flavor likelihood.

**Q2a control conclusion:** A structure-preserving
lepton control keeps FCNC-like neutral Yukawa offdiagonals
at roundoff in this pure-2HDM Yukawa flow.
The nonzero generic-lepton result is therefore
a genuine dependence on the lepton Yukawa
input in this controlled numerical experiment,
not a spurious SVD neutral-current rotation.
The pure-2HDM truncated solver is now
experimentally reproducible on AF for both
inputs. Neither branch is a physically constrained
full Zee solution, and no FCNC bound has been
calculated.

Source update relevant to Q2b:
Schmidt & Vandeleur, *Running of neutrino mass
parameters in the Zee model*, JHEP06(2026)006
https://doi.org/10.1007/JHEP06(2026)006
provides one-loop Zee-related *EFT matching*
and running of neutrino parameters, with an
appendix for the 2HDM EFT beta-functions;
it does NOT automatically supply complete
unbroken renormalizable Zee RGEs plus quark
FCNC Wilson coefficients. Full source
coefficients, thresholds and precise matching
conventions must be checked independently.

**Decision:** Stop extending toy-only Yukawa
running. Begin a physics-meaningful Q2b gate:
obtain a general-Zee \`f_ij,Pi1,Pi2\` solution
that passes current neutrino likelihood AND
complete 1L/2L LFV (with charged singlet scalar
normalization audited); match gauge/flavor-basis
conventions and the scalar spectrum; then
pass *the exact same lepton matrices* to
source-validated complete Zee running with
measured quark masses and CKM; calculate
the quark FCNC EFT/meson observables. Do not
use the old Chen B2 unrestricted Yukawa
solutions labeled fully allowed: their earlier
partial LFV screens failed, and B2 versus
2022 Yukawa conventions differ.

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


## Q2b-1: exact Chen-to-FLS lepton Yukawa basis matching (NEW, October 2026)

New runnable source:
- scripts/zee_section8_Q2b_chen_FLS_matching_gate.py
- tests/test_zee_section8_Q2b_chen_FLS_matching_gate.py

This is a *data-contract bridge* between the **existing** fixed-NO
B2 Zee neutrino family solutions and the **published** general
2HDM Yukawa beta-functions used in Q1/Q2a. It is not yet a complete
Zee beta-function calculation.

**Source conventions and independent normalization check:**
- Chen, arXiv:2508.18757 Eqs.(3-6), charged-lepton mass basis:
  the Higgs-orthogonal charged scalar couples as
  sqrt(2) bar(ell_R) Y_Chen nu_L H_perp^- + h.c.
  and Mnu = kappa_Chen [f Ml Y_Chen +(f Ml Y_Chen)^T].
- Ferreira–Lavoura–Silva, arXiv:1001.2561 Eq.(1),
  the lepton Yukawa matrices Pi_k multiply
  bar(L_L) Phi_k ell_R.
- Therefore the correct orientation and factor are
  **rho_e := Pi_perp = sqrt(2) Y_Chen dagger**,
  kappa_e := Pi_v = sqrt(2) diag(m_e,m_mu,m_tau)/v,
  Pi1=c_beta kappa_e-s_beta rho_e,
  Pi2=s_beta kappa_e+c_beta rho_e.
  Careless substitution Pi_perp=Y_Chen or Y_Chen^T
  changes both quark-trace magnitude and CP phase.
- The same normalization predicts the charged-doublet
  tree leptonic width factor
  m_H/(16pi) times ||rho_e||_F² =
  m_H/(16pi) times 2||Y_Chen||_F², before charged-mixing
  weights; this is checked against the already-written
  B3 charged-scalar lepton widths, including the f
  singlet contribution and physical lepton masses.
- Q1 quark beta source is
  T = Tr(Pi2 Pi1 dagger).
  The independent Higgs-basis identity is
  T = cs(||kappa_e||_F²-||rho_e||_F²)
      + c² X - s² X*,
  X=Tr(rho_e kappa_e dagger).
  Thus Im(T)=Im(X) for all real positive tanbeta
  at fixed kappa_e,rho_e. Exact conjugation and
  rephasing-invariance checks protect this mapping.

**Inputs:** exact matched B1/B4 scalar candidate CSV and the
corresponding stored B2
top_neutrino_Yukawa_matrices_NOT_ALLOWED.json.
Reject mismatched IDs/spectrum, antisymmetry violation,
missing target neutrino closure or large Yukawas.
NO assumption that the older B2 NO target passes
current NuFIT6.1 or full LFV is made.
The reported |T|/(16pi²) is a **local
wrong-doublet source per one unit of ln(mu)**, not
a physical FCNC coupling or a finite-scale
model-dependent prediction.
No arbitrary high-scale initial condition
or uncalibrated FCNC limit is introduced.

**Important paper scope warning:** Schmidt & Vandeleur
JHEP06(2026)006 (arXiv:2512.17235v2)
primarily calculate a **hierarchical** EFT,
charged-singlet scalar m_h >> second doublet m_H2
>> SM Higgs, using a threshold-matched 2HDM
effective theory. Our charged Higgs mass
eigenstates mH1~209-300 and mH2~680-700 GeV
are **mixed at gamma~1.1**, so the paper's
large-separation EFT matching cannot be
adopted as a quantitatively controlled
approximation to our benchmarks without
a separate hierarchy/power-counting audit.
The UV Zee charged-singlet f running and
its scalar thresholds are a different
remaining calculation.

Reproducibility commands (run tests BEFORE any interpretation):

    cd /home/aalida/zee
    git pull --ff-only
    python3 -m unittest discover -s tests \
      -p 'test_zee_section8_Q2b_chen_FLS_matching_gate.py' -v
    python3 scripts/zee_section8_Q2b_chen_FLS_matching_gate.py \
      --points work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv \
      --b2-json work/gateB2_zee_neutrino_family/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
      --top 10 \
      --output work/zee_section8_Q2b_chen_FLS_matching_B1_v1.json

If the B2 file is instead from the B4 pipeline,
use exactly its matching B4 CSV and B2 JSON paths,
never mix the two families of scalar inputs.
If the B1 CSV contains many candidates not present
in B2, filter to the exact B2 candidate-ID set
using an independently audited, reproducible
candidate-selection step rather than silently
dropping unmatched rows. Program fails closed
on any ID mismatch.

**Status:** Implementation and regression suite committed;
AF execution needed. The next scientifically
decisive step is full Zee UV RGE/threshold
validation plus 2026 NuFIT and full LFV
fits; this bridge merely makes it possible
to feed source-consistent lepton Yukawas
to that future machinery.


## AF Q2b-1 matched-B2 data bridge — SUCCESS; regression API fix (October 2026)

User reports successfully running
\`scripts/zee_section8_Q2b_chen_FLS_matching_gate.py\`
with
\`work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv\`
and
\`work/gateB2_zee_neutrino_family/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json\`.
The script matched **20 / 20** saved B2 Yukawa solutions:
10 for scalar candidate 32 and 10 for candidate 0.

Local FLS quark wrong-doublet source
\`T=Tr(Pi2 Pi1†)\`, computed from each correctly
conjugate/transposed Chen neutrino Y:
- Candidate 32: Re(T) from 1.795500456084206e-5
  to 1.8005370896868615e-5; source
  \`|T|/(16pi²)\` from 1.137014354144162e-7
  to 1.1402087448817508e-7.
- Candidate 0: Re(T) from 1.8125823073947113e-5
  to 1.821436094013654e-5; source
  from 1.1478314605634309e-7
  to 1.1534381603034936e-7.
- Neutrino-matrix algebraic closure across all 20:
  residuals about 1.2e-17 to 1.6e-16 eV.
- Full Zee running, quark FCNC observable likelihood,
  modern neutrino likelihood and complete LFV
  **NOT** calculated; physical allowed **FALSE/unknown**.
- These values are local one-loop beta-function
  coefficients per unit log scale, **not measured
  FCNC couplings, branching fractions, or exclusions**.
  They are from old fixed-NO central-input B2 solutions
  that are not established as modern 2026 viable.

AF regression in the same turn: 7/9 tests passed,
2 raised \`TypeError: validate_B2_solution() takes
2 positional arguments but 3 were given\`.
Root cause: \`validate_B2_solution(point,solution,*,target=None)\`
has keyword-only \`target\`, but three total test
call sites supplied target \`M\` positionally. The
production script ran all 20 solutions with
its valid two-positional-argument signature
and therefore was unaffected. Fixed all
three tests to use \`target=M\` in commit
\`c3f4e211281e7fb0c266d6b8b471188f394209db\`,
no source physics code changes. AF rerun pending.

    cd /home/aalida/zee
    git pull --ff-only
    python3 -m unittest discover -s tests \
      -p 'test_zee_section8_Q2b_chen_FLS_matching_gate.py' -v

**Next physics decision, not another toy scan:** (a)
validate complete Zee/full-model RGEs and f/lepton
terms or matching to EFT over a demonstrably
controlled hierarchy; (b) produce general Zee
leptons passing modern NuFIT and complete
1-/2-loop LFV; (c) compute induced quark
mass-basis FCNC and hadronic flavor observables
from the SAME matched Yukawas. Do not infer
flavor safety from the magnitude of \`T\`.


## Q2 integrated validation: ONE AF command instead of separate tests (2026-10-19)

At user request, further Q1/Q2a/Q2b/B2/B3/partial LFV consistency
tests are combined in a **single, fail-closed runner**:

- \`scripts/zee_section8_run_integrated_Q2_validation.py\`
- \`tests/test_zee_section8_run_integrated_Q2_validation.py\`

**Run ONE command** (default input paths are the same B1/B2 files
already proven to match successfully for candidates 32 and 0):

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 scripts/zee_section8_run_integrated_Q2_validation.py \
  --output-dir work/zee_section8_Q2_integrated_v1 \
  2>&1 | tee work/zee_section8_Q2_integrated_v1.console.log
\`\`\`

If using \`tee\` in a diagnostic script, enable \`set -o pipefail\`
first or inspect the script's own \`summary.json\`:
\`\`\`bash
set -o pipefail
python3 scripts/zee_section8_run_integrated_Q2_validation.py \
  --output-dir work/zee_section8_Q2_integrated_v1 \
  2>&1 | tee work/zee_section8_Q2_integrated_v1.console.log
\`\`\`

**Output path must not already exist**; choose \`v2\` rather than
overwrite existing results. This runner requires only Python3 and
NumPy for the core gate. If SciPy is available, two additional
partial Barr-Zee unit suites run. If not, they are explicitly
\`SCIPY_UNAVAILABLE_OPTIONAL_NOT_RUN\`, **never PASS**.

The single command:

1. Executes **13 required unittest suites**: A1b neutrino seed,
   A1c-f LFV components, B2 neutrino solution, B3 lepton
   widths, B5 partial LFV, thin pipeline, Q1 one-loop
   quark beta source, Q2a truncated finite evolution,
   Q2b Chen-to-FLS convention matching, and the runner's
   own synthetic integration tests.
2. If SciPy is available, executes 2 additional suites
   for the existing Barr-Zee *subset*, not complete LFV.
3. Loads saved candidate CSV and B2 JSON, refusing
   mismatched candidate IDs, insufficient saved solutions
   or unexpected neutrino closure.
4. Revalidates all **expected 20** stored B2 neutrino matrices,
   scalar masses, B3 lepton-width normalization and
   corresponding Chen-to-FLS leptonic Yukawa traces.
5. Unlike earlier generic toy Q2a, evolves the actual
   STORED B2 lepton Yukawa matrices through the
   **TRUNCATED pure-2HDM** quark + lepton Yukawa RGEs.
   Uses the same **toy** quark masses and CKM as Q2a,
   10 TeV -> 700 GeV with 120 RK4 steps.
6. Verifies quark-Yukawa local trace source with both
   direct beta function and converted Chen Yukawa.
   Cross-checks the first stored solution with 240 steps
   and a Type-II lepton control that must retain tiny
   neutral-quark offdiagonal entries.
7. Saves an **input-SHA256- and git-SHA-tagged report**
   in \`summary.json\` with all 20 individual numerical
   observations and the explicit **unimplemented**
   physical constraints. Logs of all unit tests are
   retained in \`unittest_suites.log\`.
8. Returns nonzero and writes a FAIL-CLOSED report
   if a required test suite, input identity, a numerical
   invariant, or the 20-case count fails. Missing
   optional SciPy tests are marked not run.

\`summary.json["overall_numerical_pass"]\` indicates
**software/numerical** consistency only.
It is NEVER a full theory or experimental pass.
\`full_Zee_RGE_done=False\`,
\`full_NuFIT61_fit=False\`,
\`full_LFV_done=False\`,
\`experimental_quark_FCNC_likelihood=False\`,
\`full_Zee_allowed=None\` remain hard-coded.

**Scientific next step after this combined run:** Work
towards complete model RGEs/threshold matching and modern
neutrino+LFV fit. More Q1/Q2a code-level tests alone
cannot establish physically viable Zee benchmarks.


## Integrated Q2 AF execution: 108 regression PASS, 20/20 matched flow PASS (19 October 2026)

User executed the consolidated Q2 validation on UChicago AF.
Actual printed Git HEAD:
\`579dc6de628b9e9aa96f347480d69c57e0e224eb\`.
This is **execution provenance**, not an independently accessed AF log.
The runner reports:
- All 13 required suites PASS, comprising 92 regression tests.
- SciPy installed: 2 additional available Barr–Zee-subset
  suites PASS (7 kernel + 9 fermion-photon tests), 108 tests in total.
  This is still NOT complete Barr–Zee LFV.
- All 20 old fixed-NO algebraic B2 solutions match the
  B1 scalar CSV, with source-matched Chen-to-FLS lepton
  Yukawa matrices, B3 charged lepton widths and
  neutrino reconstruction passing.
- Type-II leptonic control PASS; RK4 step doubling PASS.
- Generic saved B2 lepton Yukawas evolved using
  fixed toy CKM and quark mass inputs, pure-2HDM
  one-loop quark/lepton Yukawa equations only.
  The following are maximum absolute off-diagonal
  values of *orthogonal-Higgs* quark Yukawa matrices,
  NOT measured bounds or full Zee predictions:

| Old scalar candidate | down, largest absolute rho_ij (i!=j) across B2 ranks 1-10 | up, largest absolute rho_ij |
|---|---:|---:|
| 32 | 4.2419e-10 to 4.2538e-10 | 1.1500e-11 to 1.1532e-11 |
| 0 | 4.2108e-10 to 4.2314e-10 | 1.1416e-11 to 1.1471e-11 |

The exact reported terminal markers were:
\`INTEGRATED_REQUIRED_TESTS_PASS 92\`,
\`MATCHED_OLD_B2_CASES_PASS 20\`,
\`CONTROL_TYPEII_LEPTONS_PASS True\`,
\`RK4_STABILITY_PASS True\`,
\`COMPLETE_MODEL_AND_EXPERIMENTAL_CONSTRAINTS_PASS False\`,
\`FULL_ZEE_ALLOWED False\`.
Detailed machine-readable report:
\`work/zee_section8_Q2_integrated_v1/summary.json\`
on the user's AF (not transmitted to GitHub).

**Scientific decision:** mark Q1/Q2a/Q2b software/matching
VALIDATED; do not present this as *quark-aligned Zee
physically viable*. Avoid repeating already-validated
toy RG runs. Next substantial validation must source,
derive and independently check **UV renormalizable
Zee-specific RGE corrections**, match at
charge-scalar mass thresholds, modern neutrino
likelihood and complete LFV, then calculate
quark-mass-basis FCNC flavor constraints using
the SAME candidate. The 2026 JHEP Schmidt–Vandeleur
paper provides hierarchical Zee EFT matching and
2HDM EFT RGE, **not automatically an exact
mixed-spectrum full-Zee FCNC calculation**:
https://doi.org/10.1007/JHEP06(2026)006 .


## Q2c source-backed next physics gate: heavy singlet hierarchy INVERTED (Oct 19, 2026)

After the complete Q2 integrated (108 tests PASS, 20 B2 matrices
matched), an explicit literature reading changed the proper
next step. Schmidt & Vandeleur, JHEP06(2026)006,
arXiv:2512.17235v2:
- source Eq.14 specifies the broken-phase Zee charged-scalar
  mixing/trilinear relation;
- Sec.3 says the primary EFT expands with the charged singlet
  much heavier than the second doublet;
- Sec.3.1 explicitly does NOT run the full unbroken Zee theory;
- App.B contains the RGEs of its **2HDM EFT**.

**Our two current B1 scalar points have the opposite ordering**:
candidate 32: mD diagonal 620.47 GeV,
mChi diagonal 351.46 GeV, H1 singlet weight 0.8103,
|muZee| ~948.85 GeV;
candidate 0: mD diagonal 635.70 GeV,
mChi diagonal 419.39 GeV, H1 singlet weight 0.7853,
|muZee| ~943.40 GeV.
These are exactly reconstructed *broken-phase*
matrix entries, not bare unbroken mass parameters.
The singlet is **light and strongly mixed**. Therefore
the source's primary hierarchical
singlet-first 2HDM EFT cannot be presumed to model
our physics, independent of the earlier small
2HDM-truncated toy FCNC numbers.
**This does NOT exclude the underlying Zee model.**

Also source/group-theory checked the charged-singlet's
one-loop UV gauge correction: (b_gprime,b_g2,b_g3) =
(22/3,-3,-7) for full Zee versus (7,-3,-7)
for pure 2HDM with SM-normalized hypercharge.
Full f-dependent lepton Yukawa beta-functions
still need independent derivation (RGBeta/PyR@TE
cross-check) and threshold handling; NO invented
f coefficients are used.

Full source, assumptions, results and standalone
tests: docs/zee_section8_Q2c_UV_EFT_scope_audit.md.

### USER PREFERENCE: ONE large AF command

The previous integrated one-command runner is **upgraded**
to include Q2c with the original 108 tests, new 11
Q2c tests (119 expected in total when SciPy is
present), all 20 matched B2 inputs, RK4 convergence,
TypeII leptons control, both scalar mass matrices,
and the Zee gauge beta derivation.

    cd /home/aalida/zee
    git pull --ff-only
    python3 scripts/zee_section8_run_integrated_Q2_validation.py \
      --output-dir work/zee_section8_Q2_integrated_v2

Use v2 because the runner deliberately refuses to
overwrite the completed v1. Expected **software** markers:
INTEGRATED_REQUIRED_TESTS_PASS 103
MATCHED_OLD_B2_CASES_PASS 20
CONTROL_TYPEII_LEPTONS_PASS True
RK4_STABILITY_PASS True
Q2C_HEAVY_SINGLET_HIERARCHICAL_EFT_APPLICABLE False
Q2C_FULL_UV_ZEE_LEPTON_RGES_IMPLEMENTED False
FULL_ZEE_ALLOWED False

These counts/outcomes are expected, not yet AF-validated
on the new commit. The implementation fails closed if a
test, numerical invariant, or reference candidate identity
changes. Q2c applicability must be **reassessed** for
future scalar scan points rather than copied by assumption.

Physical go/no-go remains full source-matched
UV Zee RGE plus 2026 neutrino/LFV and quark
FCNC experiment. No full-allowed Zee points.


## Q2d new theoretical obstruction: lambda6/lambda7 are boundary conditions (Oct 19, 2026)

After Q2c PASS (119 tests), the literature audit identifies an
additional independent potential nonclosure: the project uses
lambda6=lambda7=0 in the scalar 2HDM subsector but allows
general complex doublet lepton Yukawas and possibly k12/lambda10.
An exact Type-II Z2 no longer protects the ENTIRE scalar/Yukawa
theory. In the general 2HDM scalar RGEs, fermion-dependent
contributions to beta_lambda6/beta_lambda7 must be included.
The boson-only lambda6=lambda7=0 fixed point does **not**
establish an all-sector fixed point. Quark alignment alone
does not fix this.

New source-based structural test:
scripts/zee_section8_Q2d_lepton_spurion_scalar_RG_audit.py
and tests/test_zee_section8_Q2d_lepton_spurion_scalar_RG_audit.py.
They compute T21, I6, I7 complex lepton box
contractions and antisymmetric f invariants
for each of the actual 20 B2 saved solutions,
without guessing complete beta_lambda6 or
beta_lambda7 coefficients. See dedicated
docs/zee_section8_Q2d_scalar_symmetry_spurion_audit.md.

The user prefers ONE large run, so the existing
single Q2 runner now incorporates 11 Q2d
regressions and the full 20-input new spurion
audit in addition to every previous test and
finite pure-2HDM RG check. The new combined
command is:

    cd /home/aalida/zee
    git pull --ff-only
    python3 scripts/zee_section8_run_integrated_Q2_validation.py \
      --output-dir work/zee_section8_Q2_integrated_v3

Expected if everything passes: 114 required unit
tests + 16 optional SciPy Barr-Zee-subset tests =
**130 total**; 20 matched Yukawa cases and 20
Q2d lepton spurion reports. NO change in physical
allowed semantics. Code committed, AF v3
execution not yet received.

**Next real theoretical job**, rather than yet
another arbitrary toy numerical scan: independently
source/generate the *complete renormalizable Zee*
one-loop coupled beta_f, beta_Pi1/Pi2,
beta_lambda6/7, with scalar singlet interactions
and mass/threshold conventions. Validate f->0
pure-2HDM and symmetry protected limits.
Use those beta equations only after an
independent second-source cross-check; then
fit modern neutrino/LFV and assess radiative
quark FCNC and scalar vacuum with the SAME Yukawas.

## Q2d AF validation completed, Q2e breakthrough from original Zee RGE source (October 2026)

User executed `work/zee_section8_Q2_integrated_v3/` with GIT_HEAD
`fe7b08fab8837596f5b6ee0390d9be9263ccb641`.
ACTUAL results: **114 required +16 optional Barr-Zee-subset tests =130 PASS**;
all 20 B2 scalar/lepton matches PASS; Type-II control and RK4
convergence PASS; Q2d ALL T21/I6/I7 nonzero TRUE across saved 20
old fixed-NO Yukawa solutions. This proves presence of the
symmetry-breaking lepton spurions, not numerical beta_lambda6/7
or experimental exclusions. Q2c heavy-singlet hierarchical
EFT remains inapplicable for both scalar candidate spectra.
Full general Zee f/Pi and quartic beta equations still unavailable.

**NEW PRIMARY RGE REFERENCE:** Kanemura et al.,
PRD64, 053007 (2001), arXiv:hep-ph/0011357v2,
[Appendix A](https://arxiv.org/pdf/hep-ph/0011357).
Their Eqs.(A1)–(A3), (A12), (A13)
provide a REDUCED one-loop Zee gauge, top-Yukawa
and **real antisymmetric charged-singlet f** running system.
They explicitly neglect all ordinary Yukawas besides top in
their source formula and neglect f numerically. For
real 3x3 antisymmetric f,
q=sum_{i<j} f_ij², f³=-q f and
D f=[-3gprime²/2-9g2²/2+12q]f, D=16pi² d/dlnmu.
THIS IS NOT A COMPLEX GENERAL-ZEE RGE and cannot
be applied to our stored B2 complex f solutions without
additional source-validated conjugation/Yukawa terms.

New code + 11 regression tests:
scripts/zee_section8_Q2e_kanemura2001_reduced_f_RGE.py
tests/test_zee_section8_Q2e_kanemura2001_reduced_f_RGE.py.
Dedicated audit:
docs/zee_section8_Q2e_Kanemura2001_reduced_f_RGE.md.
This new real-f RGE source limit is a **nontrivial independent
benchmark requirement** for a future full-model RGE generator.
An independent illustrative 700->10000 GeV numerical integration
for real f=(.001,-.002,.003), fixed-field-content gives
a norm ratio approx 0.96592, NOT a B2 physics prediction.

Single user-preferred next AF command, NO separate test commands:

    cd /home/aalida/zee
    git pull --ff-only
    python3 scripts/zee_section8_run_integrated_Q2_validation.py \
      --output-dir work/zee_section8_Q2_integrated_v4

Expect 125 required tests and 16 optional subset
Barr-Zee tests (141 total if SciPy is present), all 20
saved B2 analyses, new real-f RGE diagnostic.
NOT yet tested on user's AF. `FULL_ZEE_ALLOWED=False`
and `Q2E_GENERAL_COMPLEX_F_AND_YUKAWA_RGES_AVAILABLE=False`
must remain explicit.

Next decisive calculation is COMPLEX f and Pi1/Pi2 beta
coefficients plus lambda6/lambda7/lambda10. Require both
published Kanemura real-f and FLS pure-2HDM f=0 limits.
No further paper/physical claim before modern correlated
neutrino+complete LFV and mass-basis quark FCNC analyses.

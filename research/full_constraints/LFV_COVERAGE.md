# Zee LFV source and operator coverage — 2026-11-07

**LFV_FULL_COVERAGE_BLOCKED.** No newly complete physical observable or
exclusion is established. `physical_lfv=UNKNOWN`, `exclusion=null`,
`global_acceptance=null`. The new independent result validates parts of the
**three-body rate functional**, not the missing Zee loop coefficients.
No amplitude is added to the conditional pipeline.

The executable source locks are in [lfv/sources.json](lfv/sources.json);
numerical evidence is in [LFV_VALIDATION.json](LFV_VALIDATION.json).
`VALIDATED` below always names its limited scope. `UNVALIDATED` includes
absent calculations and unproved materiality bounds; it never means zero.

## Declared accuracy and conventions

The target remains scalar one-loop matching plus materially relevant leading
two-loop radiative terms, and coherent tree/penguin/box three-body and conversion
amplitudes. No uniform complete next-to-leading-order expansion is claimed.
Squaring tree plus selected loops retains some higher-order terms; it does
not include the virtual/radiative corrections needed for full NLO accuracy.

Frozen matching uses
`L_D=e*m_i/2 * bar(l_j) sigma^(mu nu)(C_L PL+C_R PR) l_i F_mu nu+h.c.`,
`[C]=GeV^-2`, `sigma=i[gamma,gamma]/2`, metric `(+---)`.
The public dimensionless convention is `C_X=-c_X/(8*pi^2*v^2)`.
The ordered FlavorKit bridge is `K2_X=-C_X*` only when operator and wrapper
parent masses agree; otherwise multiply by `m_operator/m_wrapper`. It is
**not** a chirality swap. A dipole bridge does not determine the relative
ordered-action sign of the generated four-fermion operators.

Frozen scalar loops set internal neutrino masses and external invariants in
loop denominators to zero, retaining external chirality flips. The seven rows
are h/H/A plus H1/H2 in the D and F sectors. Native F is antisymmetric with
`F=2*f_Chen`; `D=-sin(beta)*Ye+cos(beta)*Ye2`. Both charged eigenstates and
their signed rotations are required. No finite-neutrino or external-invariant
remainder bound has been established for a physical exclusion.

## Radiative topology × source × validation × omission

All rows contribute to the same complex dipole pair and can interfere.
Validation of one row does not bound an absent row.

| Topology / operator | Source and actual implementation | Validation | Remaining gap |
| --- | --- | --- | --- |
| Neutral h/H/A–lepton one loop, C_L/R | Module3 `core.py`; Lavoura [hep-ph/0302221](https://arxiv.org/abs/hep-ph/0302221), Eqs.26–42 | VALIDATED in frozen expansion; existing complex/limit tests replayed | finite-invariant remainder and common renormalization scheme |
| H1/H2–massless-neutrino one loop, D D† and F†F | Module3 seven-row ledger, native charged vertices | VALIDATED in frozen expansion; D15 independently derives ordered map | no mixed F-D chirality term at m_nu=0; finite-m_nu effects unbounded |
| Neutral fermion/photon two loop, nine charged species × h/H/A | Module4 27 rows; corrected public `th,ch,bh,tauh` photon projection | VALIDATED complex overlap, four original cards × three channels; maximum relative residual 3.70e-11 | already included; never append the public terms again |
| Physical charged-scalar/photon two loop, H1/H2 × h/H/A | Module4 six rows; two triangles + seagull, full trilinear rotation | VALIDATED electromagnetic subset, Ward/Bose/trace checks | already included; identity photon charge forbids a single off-diagonal trilinear insertion |
| Neutral fermion/Zγ | Corrected public heavy-species groups; pilot `neutral_fermion_z.py` also retains nine species | UNVALIDATED for integration here; prior independent radial/current evidence is source-locked | transferable neutral class, but does not complete any total observable; no duplicate photon piece |
| Non-Barr–Zee hZ kinetic group | Public `hZ` (both vector and axial lepton currents) | UNVALIDATED in this branch | native signed coefficient validation and scoped transfer absent |
| Complete remaining kinetic gauge aggregate | Public `kin`: all five f8a–e structures; pilot W/G/ghost calculations | UNVALIDATED full Zee | physical charged parents, crossed placements, BRST insertions, reducible/LSZ/counterterms and full gauge cancellation missing |
| Charged fermion–W–H± groups | Public `tHp,cHp,tauHp`; single doublet H± and retained Yukawa/CKM approximations | UNVALIDATED Zee | both H1/H2 currents and F-sector completion; no whole-group mixing rescaling proved |
| Physical charged-scalar/Zγ potential current | Pilot mixed HZ: unequal masses, Z matrix, both orientations, AZ contact | UNVALIDATED entire potential-Z sector | current tensor tests do not supply complete A-Z/G0 two-point/reducible assignment and A-G-H partners |
| Physical charged-scalar/W potential group | Public `HW`; pilot strict-2HDM normalization audit | UNVALIDATED Zee | unequal-mass currents and Goldstone mass-difference partners; public source has extra MW^-2, see below |
| Gauge dressing of F†F scalar/neutrino loop | Pilot general-R_xi W-neutrino self-energy subgraph | UNVALIDATED full dipole | nonzero gauge-dependent UV pole; emission/Goldstone/counterterm/LSZ partners missing |
| Quadratic F-D, m_nu=0 | Prior fermion-lepton-number spurion argument | Restricted selection rule, not a numerical full-model validation | does not remove F†F; Majorana insertion changes Yukawa counting |
| QED evolution, virtual/real radiation, higher Yukawa orders | neither Module4 nor public leading reference supplies a full treatment | UNVALIDATED materiality/uncertainty | cannot infer uncertainty from quadrature or the spread of partial formulas |

The public paper defines separately gauge-invariant aggregates, including a
kinetic term that depends on the charged mass. Isolating just its W/photon
pieces loses that property. See [2410.17313v4](https://arxiv.org/html/2410.17313v4),
Secs.4–6, together with the [2026 erratum](https://doi.org/10.1007/JHEP07(2026)184).
This supplies a useful 2HDM reference; its field content does not include Fzee.

## Corrected public code: actual groups and charged-mass dependence

Pinned SHA `b5035cd58d2a7e4a91e9790d045df062b97adffe`, `thdm.py` SHA-256
`9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`.
The AST inventory in the validation receipt records every source line and
attribute for both chiralities; no public total is evaluated as Zee.

| Locals in cL/cR_llpg | R / L source line | Charged H± mass enters? | Treatment |
| --- | --- | --- | --- |
| 1loop | 1256 / 1539 | L only at retained daughter-mass order | use frozen native one loop |
| th,ch,bh,tauh | 1296–1395 / 1577–1676 | no | photon part already included; Z part distinct |
| tHp,cHp,tauHp | 1429–1440 / 1710–1721 | yes | charged fermionic aggregate, unmatched Zee |
| hZ | 1450 / 1731 | no | non-Barr–Zee neutral kinetic group |
| kin | 1460 / 1741 | **yes**, through xwH in f8e | retain the whole aggregate; no W-only import |
| HA | 1492 / 1773 | yes | physical photon counterpart already in Module4 |
| HZ | 1501 / 1782 | yes | mixed Zee Z current is not a single diagonal rescaling |
| HW | 1511 / 1792 | yes | source/paper dimension mismatch, no import |

The erratum changes signs, an f8e bracket and neutral-fermion prefactors and
conjugations. The later pilot separately identified an additional **code**
normalization defect: the HW coefficient contains `vev^3/MW^2/m_i/Mh_k^2`,
although f11 and all Yukawa/potential factors are dimensionless. A dimensionless
c_X cannot have that extra inverse mass squared. The paper and captured EDM
operator identity agree after its removal in the pilot's isolated research
replacement. That evidence is **archival common-limit normalization**, not a
fresh full graph or gauge derivation here. The pinned author source and all
historical outputs remain unchanged; nothing was sent to the authors.

## Three-body and conversion operator inventory

SARAH **4.15.4**, SPheno **4.0.5** are pinned. The generated corrected source
`FlavorKit_LFV_ZeeTypeII.f90` has hash
`2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d`.
`LowEnergy_ZeeTypeII.f90` combines `B + PS + PV + TS + TV` **before** calling
the rate routines. These are box, scalar/vector penguin and scalar/vector
tree terms. A source label or a nonzero rate is not their validation.

| Process / topology | Operator and source | Validation | Omission / physical status |
| --- | --- | --- | --- |
| mu→3e, tau→3e, tau→3mu: tree h/H/A | four scalar A^S_XY; generated `CalculateTreeS4L`, lines 27795–27947 | VALIDATED rate/action normalization on four original mu3e cards; frozen tree retains masses and propagators | tree only is PARTIAL |
| Same processes: on/off-shell photon | K2L/R dipoles, K1L/R nondipoles; generated `CalculateGamma2l` at 46280, Photon_wrapper | VALIDATED pure-dipole rate normalization and K1 vector shift; scalar-loop K2 map qualified by D15 patch | full Zee two-loop K2 missing; K1 complex physical-scheme matching not validated |
| Same processes: scalar/Z penguins | PS/PV contributions to A^S_XY, A^V_XY; generated routines at 20173,25146 | UNVALIDATED model coefficients | waves, counterterms and gauge/Goldstone cancellation must be matched in a fixed scheme |
| Same processes: boxes | A^S_XY, A^V_XY, A^T_LL/RR; generated box routine at 18631 | UNVALIDATED model coefficients | neutral/charged, H1/H2/F, identical-particle orderings and loop precision untested as a complete operator set |
| Same processes: coherent rate | Lto3Lp consumes **14** coefficients: 2 K1 + 2 K2 + 4 S + 4 V + 2 T | VALIDATED 10 contact-action basis rates and 3 complex combinations by independent traces; dipole/contact relative model sign **not** validated | no complete fixed-scheme Zee input vector, no physical comparison |
| tau−→mu−e+e−, e−mu+mu− | LtoL1L2L2; same operator classes, nonidentical phase space | UNVALIDATED here | finite daughter masses, complex coefficients and interference need independent validation |
| tau−→e+mu−mu−, mu+e−e− | LtoL1L2L2 plus separately generated 4Lcross operators | UNVALIDATED here | crossed four-fermion matching; no automatic dipole contribution for same-sign daughter pair |
| mu→e conversion: dipole/vector | K1,K2 and Olluu/Olldd V_XY | UNVALIDATED full amplitude | no complete signed Zee semileptonic input or validated target calculation |
| mu→e conversion: neutral scalar / boxes | Olluu/Olldd S_XY and vector operators | UNVALIDATED full amplitude | heavy-quark/gluon matching and QCD evolution/materiality not established; source only explicitly uses u,d,s at nuclear stage |
| mu→e conversion: nuclear response | MuEconversion targets Al,Ti,Sr,Sb,Au,Pb, hard-coded GSp/GSn, Zeff,Fp,capture | **source scalar-isovector discrepancy reproduced**, six targets | scalar p/n assignment exchanged relative to published formula; no nuclear uncertainty qualification |

Source framework and rate convention: [FlavorKit, arXiv:1405.1434v3](https://arxiv.org/html/1405.1434v3),
operator definitions and App.C.1. The independent action integration checks
the scalar/vector/tensor signs without copying its analytic rate polynomial.
For pure dipoles the independent reference is [Kuno–Okada Eq.(123)](https://arxiv.org/html/hep-ph/9909265v1).
No full Zee loop-vector claim follows from either rate check.

For conversion, the direct scalar nuclear current is `Z*g_p+N*g_n`, hence
`(Z+N)g0S+(Z-N)g1S`. The pinned routine instead uses a minus before g1S;
with its own definitions this becomes `Z*g_n+N*g_p`. An isolated up-scalar
EFT insertion on Au gives source/reference rate **1.06972357425**. This is
a code/published-formula discrepancy, not a measured Zee theory error.
No local correction is integrated without qualifying the full conversion
calculation and its nuclear inputs.

## Previous Zee research is reusable evidence, not a hidden completed backend

The separate pilot checkout at `81cd376294e223c7311fba134f643db5c02bbad0`
was inspected read-only, including its later work absent from this branch.
Artifact hashes and versioned repository links are in the source manifest.

* D15 `f6676356…` derives the ordered operator bridge with Fock/spinor and
  FeynArts/PreSARAH evidence. Its scalar dipole validation requires an
  **experimental loop patch**, not pristine FlavorKit. It fixes premature
  small-r zeros and near-degenerate cancellation in C1g/C0C1C2; unsupported
  distinct-mass branches elsewhere have not thereby been validated.
  On the four original cards its separate charged-vertex residuals are at
  most 2.7e-15 and neutral scalar coefficient residuals at most 6.81e-11.
  The original full native/input differences, up to 1.97e-7 relative, remain
  distinguishable from matched-component precision. No new-card experiments
  from that branch are rerun in this task.
* D16 `dade0f9…` calculates neutral fermion Zγ and mixed physical-scalar
  currents, but explicitly leaves full W/HW, charged-fermion W, F†F and
  neutral mixing/reducible sums null. Latest `81cd376…` adds subgraphs,
  not a physical total: GWW has a nonzero `1/(4 epsilon)` subdivergence;
  the F-sector neutrino two-point pole is `-xi`, with finite part
  `4 log(2)-2` at xi=1 and p²=-MW². Dropping these as “massless-neutrino
  zeros” is not supported. A full renormalized gauge sum is still needed.
* Historical F19b combines selected W/photon and fermion kernels and calls
  itself PARTIAL. Its cross-check is not the missing general gauge sum.
  No earlier complete Wγ implementation was found in the inspected history
  or these saved research sources.

The independent [2017 Zee calculation](https://arxiv.org/html/1701.05345v2)
uses leading tree trilepton formulas and discusses omitted loop effects;
it is not an independent complete three-body operator oracle.
The [2023 Zee study](https://arxiv.org/html/2303.13383v2) also makes alignment
and quark-coupling restrictions that cannot be imposed on these Type-II cards.
Neither licenses a wholesale replacement of the present amplitudes.

## Experimental comparisons and decision

The source-specific input snapshot is [lfv/experiments.json](lfv/experiments.json).
It separates observed 90% CL limits from predictions and uses no forecast as
a bound. mu/tau decay rates divide by their **total lepton width**; conversion
divides by the **target muon capture width**, never the free muon width.
SINDRUM's published mu3e denominator is the ordinary muon decay rate; its
relation to a model-modified total width/GF must be qualified before precision
use. The supplied D12 lifetimes/alpha are an explicitly illustrative frozen
normalization, not a new precision likelihood or uncertainty estimate.

The most promising full-observable route is mu→3e: an available coherent rate
formula and existing complex tree controls. It stops at a concrete gate:
**no source-qualified independent complex K1 + four-lepton penguin/box vector
at the original physical scheme, no proved relative ordered-action bridge
to K2, and no bound permitting omission of the two-loop-enhanced dipoles**.
Tree-only leading order cannot be substituted when the omitted diagnostic
is eleven orders larger. Numerically passing a one-loop generator is
insufficient. A complete fixed-scheme operator-only calculation and an
independent nonzero full vector/reference are required before a scoped
exclusion. The radiative alternative still requires the missing full gauge
classes listed above. Stop at this source gate; do not create another
incomplete calculator or a fabricated theory sigma.

The B gate remains `B_FULL_RATE_BLOCKED` without reinvestigation. Higgs is
not evaluated here. No all-three-gates readiness or final-scan claim follows.

# D4 charged decays — 2026-10-27

**D4_TREE_DECAY_TABLE_PASS; D4_COMPLETE_TWO_BODY_BR_PASS.** These statuses apply
only to the explicitly defined LO on-shell two-body approximation below.
`PHYSICAL_LHC_CLAIM_NOT_EVALUATED`, `2026_LINEARIZED_FLAVOR_FILTER_READY=false`,
`COMPLETE_LFV=false`, `global_zee_acceptance=null` remain unchanged.
D3's historical width-only statuses and evidence are preserved verbatim.

The [channel ledger](../validation/module7/d4_decay_table.json) contains all three
selected D2 spectra, both physical charged scalars, H+ and H− partial widths,
and twelve independently authenticated NO inverse-family points. No scalar vacuum
or flavor scan was rerun. The scalar vacuum remains UNKNOWN at these points.

## Approximation and input scheme

Here “total” and “BR” mean **tree on-shell two-body**, using the native massless
**tree** neutrinos, three neutrino species and both helicities. The frozen model
has no tree Majorana mass operator or right-handed neutrino. Its nonzero
neutrino target arises at one loop. Loop-induced neutrino masses, their
helicity interference proportional to mν, off-shell three-body channels, finite
unstable daughter widths, loop-only decays, QCD/EW decay corrections, and
uncertainties are uncomputed. These are not full physical widths or collider BRs.

The explicit sourced `SM_input_card` is in the ledger. All masses are GeV:

* Kinematics: (u,c,t,d,s,b) = (0.00216,1.2730,172.4,0.00470,0.0935,4.78).
  Top is the PDG pole extraction from cross sections; bottom is the approximate
  two-loop pole value. Light/charm reference MS masses define partonic thresholds;
  no claim of observable free light-quark pole masses is made.
* Yukawa MS references: (0.00216,1.2730,162.5,0.00470,0.0935,4.183) at
  (2,1.2730,162.5,2,2,4.183). Each evolves to the **mother mass** with one-loop
  QCD, αs(91.1876)=0.1180, nf=4/5/6 and continuous matching at 4.183/172.4.
  Specifically α(Q)=α(q)/[1+α(q)(11−2nf/3)ln(Q/q)/(2π)] and
  m(Q)/m(q)=[α(Q)/α(q)]^[12/(33−2nf)] in each interval. No finite matching terms.
  At 700, mt,Y=148.0414556305571 and mb,Y=2.69162343131315.
  **163.9689 at flavor qmatch=160 is never used as a decay or pole mass.**
* CKM is exactly unitary, constructed from PDG 2024 Eqs.12.3–12.4 and
  (λ,A,ρ̄,η̄)=(0.22501,0.826,0.1591,0.3523). All nine quark pairs and color 3
  are included. Sources: [PDG quarks](https://pdg.lbl.gov/2024/download/db2024.pdf),
  [bottom schemes](https://pdg.lbl.gov/2024/listings/rpp2024-list-b-quark.pdf),
  [CKM](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf),
  [QCD](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-qcd.pdf).
* EW inputs retain the SHA-bound D2 snapshot: mW=80.379, mZ=91.1876,
  v=246.21965, cw=mW/mZ, g2=2mW/v, g1=g2 tanθW. Charged-lepton pole
  snapshot (0.00051099895,0.1056583755,1.77686) is identical to Module2.

LO scheme sensitivity is material. At 700, the nine-quark sum changes from
0.8822085463373005 to 1.3241754829841754 when reference Yukawa masses are
left unevolved with identical kinematics. At 250/300/350 the corresponding H1
sums are 0.02926449632893982/0.05712033693115363/0.08427370534213706
versus 0.03845942656974127/0.0770501184396167/0.116053876955761.
These are scheme diagnostics, not uncertainty intervals or NLO predictions.

## Source and actual native closure

[Florentino–Romão–Silva, EPJC 81 (2021) 1148](https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2),
Eqs.70–78 and Appendix B.1–B.4, already give the charged decay structures and
scalar-only cascade hierarchies/BR benchmarks. This work supplies no new decay
mechanism or partial-width formula. The web-rendered mass arguments in Eqs.74–76
contain dimensional ambiguities: comparisons use dimensionless x=m²/M² and
sqrt λ(M²,m1²,m2²), independently fixed by the amplitude and phase space.

`math -script scripts/zee_d4_vertices.m` ran successfully with Wolfram
**15.0.1** and genuine **SARAH 4.15.4**, reading immutable `ZeeTypeII`.
All SARAH output and raw numerical cases are ignored under `validation/module7/local/`.
[Native evidence](../validation/module7/d4_native_validation.json) retains source
hashes, genuine representative raw expressions, version, exact-zero proofs,
36 case residuals, and an actual complex numerical control case for falsifiers.
Model SHA256 is
`78d6b48232f9a75a21b058301d9233dba3ed067e21f534d27c0d6f415484aa4d`;
driver SHA256 is
`1449a2c4a87b22306117731f2a4653249f266c8de53a08293b22cf5387c5774d`.
The evidence also hashes parameters.m, particles.m and SARAH.m.

**100 native queries; 36 numerical cases; 6,192 signed complex coefficient
comparisons.** Cases include 24 actual family/mother-scale cards and 12 controls
with complex non-aligned lepton matrices, two β values, positive/negative γ,
zero mixing, both endpoints and reflected mixing. Maximum absolute residuals:
quarks 4.440892098500626e−16; W neutrals 0; trilinears
4.547473508864641e−13 GeV; leptons 0; gauge controls
1.4303926927627343e−15. Momentum differences and native PL/PR labels are checked.

Physical Hk+ is `conj[Hm[{k+1}]]`. The native all-incoming quark vertex is
`i(a PL+b PR)` with
`a=√2 mu,Y Vud d_k cotβ/v`, `b=√2 md,Y Vud d_k tanβ/v`,
`d_1=cosγ`, `d_2=−sinγ`. Both chiral terms have the same relative sign.
The conjugate orientation exchanges and conjugates a,b. The native color delta
is stripped once for a fixed-color amplitude; the width carries Nc=3.
The independent Clifford trace gives the interference **−4 Re(a b*) mi mj**.
Eq.74 is recovered with a common mass scheme and |Vtb|=1.

The native CP-even W coefficients are `−i g2 (ZH_j · ZP_k,doublet)/2`;
the CP-odd coefficient is real `+g2 (ZA_A · ZP_k,doublet)/2` with its distinct
momentum orientation. Crossing gives J=P+k. An independent physical-polarization
sum recovers Eq.77, including the longitudinal 1/mW² enhancement.

Scalar trilinears come from the actual native vertices, checked independently
by differentiating the full frozen potential with respect to the two charged
fields and h/H. A second implementation projects dMcharged²/dhj into the D3
charged rows. Dimensionful t yields Γ=|t|² sqrtλ/(16πM³), Eq.76.
The native A trilinear is **symbolically zero** after the physical charged and
CP-odd rotations: the physical doublet charged rows are parallel, and the Mu4
term's remaining contraction is Goldstone-orthogonal. Both orientations vanish,
independently reproduced from the potential; `FORBIDDEN_CP` is retained.

## General complex Zee leptons

In the Module2 charged-lepton mass basis, native Hk+ coefficients are
`PL=−i s_k F[j,i]`, `PR=−i d_k conj[D[i,j]]`, where
`s_1=sinγ`, `s_2=cosγ`, and D=−sinβ Ye+cosβ Ye2 has
(charged right, neutrino left) indices. Both native orientations and all 18
flavor pairs per charged scalar were queried. The Fzee/2 Lagrangian convention
produces **F**, not 2F, after antisymmetrization.

For a unitary neutrino rotation U the two matrices become A U and B U*.
Their row norms are invariant. Since native tree mν=0, opposite helicities do
not interfere. For each charged lepton i the inclusive width is therefore

`Γ_i = M/(16π) (1−mi²/M²)² [s_k² Σj|F[j,i]|² + d_k² Σj|D[i,j]|²]`.

There is no identical-particle factor: the charged lepton and neutrino differ.
Three neutrinos and both helicities are each counted once. Explicit random
complex-unitary rotations, the spin trace, charge reversal and native signed
coefficients independently check this reduction. Finite-mν interference is
explicitly outside the stated native tree approximation. Eq.78 is used only
as an aligned limit, never substituted for the actual D2 matrices.

The ignored D2 full outputs were absent. Only Module2's fast inverse was
regenerated. All twelve full Module2 output hashes, D hashes, full input hashes
and scalar hashes match committed D2 exactly; there is no borrowed benchmark.
Native cards are independently regenerated and canonical-hash compared before
any width can be emitted. Pinned byte hashes:

* seed: `6a55f774041a9d5e06bd6ea30a628bfcf5c840af0ddff30bce5f692a551c2915`
* D2: `79f4164b1bf74b21576e2711960dca3a415cc9eb03f133eb5a885ad10b607b84`
* D3: `cf9a9314197265a172305c287b9c3d306ec654e83ceeae6374e1dcf7c3346376`

## Inventory and results

The frozen physical field content permits charged-scalar + neutral
(h,H,A,Z,γ), W + neutral (h,H,A,Z,γ), nine u anti-d pairs, and three charged
leptons with all neutrinos. Both charged daughters, including same-mother
closed channels, are retained. This gives exactly **27** channels per mother
when each charged-lepton neutrino sum is one proven inclusive channel.
Color and Lorentz invariance exclude gluon + color-singlet charged states and
fermion–boson pairs; there are no doubly charged scalars, extra colored states
or right-handed neutrinos. Goldstones and ghosts add no physical final states.

Physical WZ and Wγ vertices vanish after the native Goldstone-orthogonal
projection, checked for both mothers and charges with charge-conserving queries.
The off-diagonal charged-scalar photon coupling is symbolically zero.
All open quark, Wh, WH, cascade, H1h and leptonic modes have finite validated
widths. For H2, WH is open (661.079 threshold), WA closed (714.079 threshold),
H1h open at all three spectra, H1H closed; H1A has an exact-zero CP vertex.
For H1, only quarks, Wh and leptons have nonzero open widths.

Each ledger row records daughter masses, OPEN/CLOSED/FORBIDDEN_CP status,
kinematic openness separately, positive and negative charge widths, native query
provenance, input scheme, errors and exact-zero reason. No conjugate decay is
added to a single H+ total. Missing/unknown/nonfinite/negative open widths
force `total_width_GeV=null` and `branching_fraction=null`; absent/duplicate
channels raise an error. No such blocker remains in this approximation.

Baseline family results (widths GeV; **LO tree two-body BRs only**):

| mH1 | Γ(H2→H1Z), exact D3 | Γ1,total | Γ2,total | BR2(H1Z) | BR1(tb) |
|---:|---:|---:|---:|---:|---:|
| 250 | 11.671906176399391 | 0.029301669807967994 | 14.20762411539604 | 0.8215241395463984 | 0.9952697003407711 |
| 300 | 9.411343258642537 | 0.05717261285617414 | 11.636716322693088 | 0.8087627985129457 | 0.9964794284816165 |
| 350 | 7.1240428396019855 | 0.08434643383494804 | 9.145061343633634 | 0.7790043797312975 | 0.9968224146435143 |

Additional H2 widths: quarks 0.8822085463373005, Wh 0.0012280968527578655,
WH 1.0748739308677497, and H1h =
0.5773812845483025/0.2670364088175085/0.06268184759713855 for 250/300/350.
These include the competing light-quark modes, scalar trilinear and leptons;
no tb-only normalization is used. All charge-conjugate channel widths agree
within floating-point precision.

Inclusive lepton sums for all independent families (Γℓ1, Γℓ2 in GeV):

| mH1 | family | Γℓ1 | Γℓ2 |
|---:|:---|---:|---:|
| 250 | baseline | 3.406291214876899e−5 | 2.6080390538242737e−5 |
| 250 | index0 | 3.406291978422946e−5 | 2.6080468730258103e−5 |
| 250 | index2 | 3.40629466418652e−5 | 2.6080743769353524e−5 |
| 250 | mixed13 | 3.406293948696063e−5 | 2.608067049851715e−5 |
| 300 | baseline | 4.0876177694529494e−5 | 2.608117523375355e−5 |
| 300 | index0 | 4.08761868570835e−5 | 2.6081253425770254e−5 |
| 300 | index2 | 4.087621908617079e−5 | 2.6081528464765214e−5 |
| 300 | mixed13 | 4.087621050033672e−5 | 2.608145519401169e−5 |
| 350 | baseline | 4.768945409801179e−5 | 2.6082376701817243e−5 |
| 350 | index0 | 4.768946478765874e−5 | 2.6082454893834805e−5 |
| 350 | index2 | 4.7689502388282e−5 | 2.608272993284745e−5 |
| 350 | mixed13 | 4.768949237139508e−5 | 2.6082656661978508e−5 |

The JSON retains separate e/μ/τ widths, both charge totals, and all nonzero
channel BRs for each of the twelve families. Gauge and quark widths have
**exactly zero** family spread. Here F is unchanged and dominates the lepton
widths: relative total lepton spreads are only ≈1.013e−6 (H1) and ≈1.355e−5
(H2); the largest individual spread is ≈2.721e−4 for H2→eν. Flavor-sensitive
charged final states exist algebraically, but these twelve points do **not**
demonstrate a sizeable family discriminator. No collider sensitivity follows.
D3's conditional flavor values (4.230787153913907,4.182878900268742,
4.145521835221139)×10−4 for 250/300/350, and C7/C8, remain context only.

## Validation, reproduction, and decision

The candidate generic kernels were independently audited; no formula correction
was needed. **18 D4 tests pass**, including eight generic-kernel tests.
**34 Module7 tests pass**, with **9** in the focused existing D3 file.
Separate Dirac traces, physical four-vector polarizations, full-potential
polynomial derivatives, dimension scaling, Eq.74/76/77 limits, CKM unitarity,
color, complex phases, chiral/charge orientations, generation sums, running
threshold continuity, native hashes and missing-width/BR falsifiers are covered.
The report records actual log counts and hashes. These tests accompany genuine
native execution; kernel tests alone never establish a native PASS.

```sh
python -m module7.d4_inputs
math -script scripts/zee_d4_vertices.m
python -m module7.d4_native
python -m module7.d4_decay_table
python -m unittest discover -s tests -p 'test_module7_d4_tree_kernels.py' -v
python -m unittest discover -s tests -p 'test_module7_d4_*.py' -v
python -m unittest discover -s tests -p 'test_module7_cascade_z.py' -v
python -m unittest discover -s tests -p 'test_module7_*.py' -v
git diff --check
```

Branch `feature/zee-d4-charged-decay-table` descends from verified D3
`5f70b8cddaf1092d9c97f3c2cb4e2eab5dfa8a36`; only allowed D4 paths are changed.
Native raw logs/cases are ignored; compact source hashes, residuals and results
are committed. The ledger's source manifest covers the D4 implementations and tests.

There are no remaining **conditional native tree-two-body** blockers.
Publication/discovery/exclusion prospects remain unevaluated. The 2021 paper
already supplied scalar-only decay hierarchies and BR benchmarks; the
[2017 general-Zee analysis](https://arxiv.org/abs/1701.05345) also precedes this work.
Next action: constrained general-Zee sampling that actually changes charged-lepton
final states while closing neutrino/LFV constraints, scheme/perturbative
uncertainty assessment, and justified parton-level production rates. Full LFV,
physical B→Xsγ, joint neutrino likelihoods, RG closure, population sampling and
global vacuum proof remain incomplete. No global Zee acceptance is inferred.

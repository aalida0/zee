# Mixed charged-scalar h125 Zgamma rescue: localized source-routing mismatch

**7 November 2026. `ZGAMMA_SOURCE_ROUTING_MISMATCH`; physical h/H/A Zgamma
widths remain UNKNOWN.** The bounded source comparison has executed on the
original D7/F13 cards. A literal LoopTools interpretation of the published
2021 mixed-mass expression does not equal the 2018 scalar expression. A
specific permutation of the internal masses removes the discrepancy and
passes scalar electromagnetic Ward checks. That permutation is an explicitly
identified correction candidate, not a silently corrected published result
or a released complete one-loop amplitude.

The task's Phase I.6 / Phase III amplitude-mismatch stopping condition is
exercised. No H/A extension, physical branching fraction, HiggsTools signal,
or exclusion was calculated. No new scalar point, scan, event generation,
Condor job, LFV setup, SusHi/HDECAY run or diphoton calculation was performed.
The candidate scalar kernel is independently checked within its real,
subthreshold domain; the complete leading one-loop h result is **not** validated.

## Sources actually read and citation scope

Full-text PDF hashes, retrieval URLs, versions and native library hashes are
in [ZGAMMA_SOURCE_MANIFEST.json](higgs/ZGAMMA_SOURCE_MANIFEST.json).
The relevant printed equations were also visually inspected: journal Flo21
p.21 and Thanh19 p.81. This is a focused backward/forward check, not an
exhaustive citation census or an absence claim.

| Source | Exact locator and scope | Transfer conclusion |
| --- | --- | --- |
| [Hue et al., EPJC 78 (2018) 885](https://doi.org/10.1140/epjc/s10052-018-6349-0), arXiv:1712.05234v2 | Eq.16, Table I, App.A Eqs.A1/A3; generic CP-even scalar, physical charged particles with equal charge | Explicit propagator routing and conjugate orientation; used for the independent mixed kernel. It is not a general CP-odd amplitude. |
| [Thanh/Phuong/Hong/Mai (2019), issue 37, pp.78–84](https://dthujs.vn/index.php/dthujs/article/view/477) | Eqs.1.12, 1.14, 1.17, Tables 2/4; two charged Zee states | Eq.1.17 has the same PV combination as Hue, with Aij=2 Z_ij lambda_ij for real couplings. No complete PV arguments, contact-term validation or independent code receipt is printed. Its quark Yukawa restriction is not our Type-II assignment. |
| [Florentino/Romao/Silva, EPJC 81 (2021) 1148](https://doi.org/10.1140/epjc/s10052-021-09956-2), arXiv:2106.08332 | Journal Eqs.9,12,D.19–D.21; doublets plus charged singlets, specialized Zee examples | Mixed scalar formula is published. Literal D.20 routing is the discrepancy tested here; scalar sector transfers without importing its restricted fermion assumptions. |
| [Fontes/Romao/Silva, JHEP12(2014)043](https://doi.org/10.1007/JHEP12(2014)043), arXiv:1408.2534v1 | Flo21 reference 40; C.9–C.12, E.7/E.8 | Equal-mass normalization and gauge/counterterm discussion. Equal masses cannot resolve the newly tested routing ambiguity. |
| [Boto et al., PRD109 (2024)095002](https://doi.org/10.1103/PhysRevD.109.095002), arXiv:2312.13050v2 | References 14 and 18 cite Hue18 and Flo21; Sec.II assumes equal charged masses in its illustrative amplitude | Confirms a selected forward citation to both seeds. Its equal-mass illustration does not determine the unequal-mass permutation. |

The official 2019 landing page **does provide** DOI
`10.52714/dthu.37.4.2019.686`, verified from its citation metadata. This
improves the earlier index's “no accessible DOI in PDF” entry. The 2019
bibliography explicitly cites Hue18 and Herrero-Garcia et al. 2017. Flo21
cites Fontes14; Boto24 cites both Hue18 and Flo21. No exhaustive reverse
graph, author code, erratum or authors' intended PV ordering was established.
The scoped erratum query was `"09956-2" "erratum"`; a search miss is not proof
that no clarification exists.

## Exact native coupling dictionary

Use the frozen physical-tree SARAH convention, with no SPheno pole values:

```
V contains h H_i^- G_ij H_j^+; vertex = -i G_ij,  [G] = GeV
R = ZP[physical charged rows, doublet columns]
P = R R^T
cw = MW/MZ; sw^2 = 1-cw^2; e = (2 MW/v) sw
Z = e/(sw cw) [P/2 - sw^2 I]
photon current = e I; h-independent AZ contact vertex = 2 i e Z g_munu
Flo21 Udagger U = P; g^(2ij) = G_ji/v
```

The transpose follows Eq.9's ordering S_i^+ S_j^-; for real symmetric h
couplings here it is numerically invisible. The ordered contraction is
G_ij Z_ji, **not** two independent Type-II scalar rates. The frozen native
momentum/sign convention is the one already audited in HIGGS_VALIDATION;
this work evaluates the same potential derivatives and rotations and pins
their sources. It does not claim a fresh SARAH extraction.

For the 2019 charged convention, Eq.1.4 reads
h1=sin(phi) singlet+cos(phi) doublet and
h2=cos(phi) singlet-sin(phi) doublet. Thus phi=gamma_native,
and its Eq.1.12/Table 2 generator is exactly
`e/(sw cw) [[cos(gamma)^2/2-sw^2,-sin(gamma)cos(gamma)/2],
             [-sin(gamma)cos(gamma)/2,sin(gamma)^2/2-sw^2]]`
in the common all-incoming momentum rule. Its neutral rotation maps with
alpha_2019=alpha_native-pi/2, giving
sin(beta-alpha_2019)=cos(beta-alpha_native). This maps scalar couplings;
the paper's common quark factor is still not our Type-II up/down assignment.

| Matrix entry | D7 h125 | F13 h125 |
| --- | ---: | ---: |
| G11 / GeV | 128.39325127 | -153.47296055 |
| G12=G21 / GeV | -202.57459325 | -180.13585170 |
| G22 / GeV | 1645.36270566 | 1863.66077927 |
| Z11 | -0.14175368 | -0.08565176 |
| Z12=Z21 | -0.09016183 | -0.15208516 |
| Z22 | 0.18173196 | 0.12563003 |

All full-precision masses, matrices and original scalar/Yukawa hashes are
in [ZGAMMA_SOURCE_EVIDENCE.json](higgs/ZGAMMA_SOURCE_EVIDENCE.json).
General complex leptonic Yukawas have not been replaced by the papers'
restricted textures; no full fermion amplitude is released in this audit.

## PV routing, derivation and counterexample

Let s=mh², t=MZ², a=mi², b=mj², delta=s-t. Hue A1 defines
D0=q²-a, D1=(q-pZ)²-b, D2=(q-pZ-pgamma)²-b.
For x+y+z=1 its denominator is

```
D(a,b,b) = a x + b(y+z) - t x y - s x z - i0
C0(t,0,s,a,b,c) = - integral_simplex 1/D(a,b,c)
K(a,b) = C12+C22+C2 = integral_simplex x z/D(a,b,b)
DeltaB = - integral_0^1 log[(a u+b(1-u)-s u(1-u)-i0)
                         /(a u+b(1-u)-t u(1-u)-i0)] du
```

K follows by shifting q to q-y pZ-z(pZ+pgamma): C2 contributes +z/D,
C22 contributes -z²/D and C12 contributes -yz/D. The photon is between
D1 and D2, which have the **same mass**. This matters for unequal states.

In standard LoopTools ordering the literal D.20 bracket is

```
F_literal = t/delta DeltaB + 1
          + a C0(t,0,s,a,a,b) + b C0(t,0,s,b,b,a).
```

Its second and third internal masses differ at the zero-invariant photon
vertex. The specifically tested candidate is

```
F_candidate = t/delta DeltaB + 1
            + a C0(t,0,s,b,a,a) + b C0(t,0,s,a,b,b)
            = -delta [K(a,b)+K(b,a)].
```

Equivalently, cyclically relabel masses **and external invariants together**:
C0(0,t,s,a,a,b) for the first term. Merely calling C0(t,0,s,a,a,b)
“photon adjacent” silently changes the LoopTools definition. The 2019 paper
does not supply arguments that could independently distinguish these choices.

| Original h125 mixed pair | D7 | F13 |
| --- | ---: | ---: |
| F_literal | -0.00352786919509 | -0.00116235605322 |
| F_candidate / Hue-equivalent | -0.00351971352111 | -0.00116190570418 |
| F_literal/F_Hue - 1 | 0.00231714142 | 0.000387595173 |
| Candidate reduced Ward residual | -6.66e-16 | -2.44e-15 |
| Literal reduced Ward residual | 1.63113480e-5 | 9.00698081e-7 |

These differences are **mixed-kernel** discrepancies, not relative errors
on a complete width or theoretical error bars. Equal masses pass either
routing and therefore cannot detect this problem.

An independent scalar-QED tensor/contact check uses the finite rational
term from dimensional reduction:

```
C00(a,b,b) = UV/4 - (1/2) integral_simplex log[D(a,b,b)/mu²]
B0(s,a,b) = UV - integral_0^1 log[D_B(s)/mu²]
F00_bar = 4[C00(a,b,b)+C00(b,a,a)] - 2 B0(s,a,b)
F21_bar = 4[K(a,b)+K(b,a)]
F00_bar + delta/2 F21_bar = 0.
```

The B0 term is the AZ seagull bubble; it is not an optional diagram.
The bars strip the common coupling/loop factor. Both the UV coefficient
4(1/4+1/4)-2 and the scale logarithm cancel. Substituting
F21_bar=-4 F_literal/delta fails this identity with the **physical** scalar
F00. Substituting the candidate succeeds. This is a counterexample to a
literal common-LoopTools transcription; it does **not** establish that the
authors' uninspected program violates a Ward identity or exclude a different
implicit convention in their work.

## Independent numerical evidence and its limits

Three evaluations were actually executed: tensor-product Gauss integration
(80 nodes, then 120 for the mismatch test); adaptive SciPy simplex integration
for K; and the installed Herwig 7.3.0 bundled LoopTools/FF library, whose
header identifies LoopTools 2.13. The latter uses the native C12/C22/C2 and
C00 coefficients, not another transcription of the bracket. Raw stdin,
stdout and executable hash are retained in the evidence JSON. The native
FF log reports no errors. A temporary loader symlink to the existing GSL
library was needed; no software was installed and no generator ran.

Across the sixteen native requests (original ordered/equal pairs, UV=0/7,
mu²=1/19 GeV²), maximum absolute differences from parameter integration are
2.77e-15 for DeltaB, 6.17e-20 GeV^-2 for the C0 variants,
1.18e-17 GeV^-2 for K and 2.28e-14 for C00. Native reduced Ward residuals
are below 2.40e-14. Adaptive/Gauss K relative residuals are below 2.4e-15.
These are numerical residuals, **not** model uncertainty estimates.

Passed controls include equal-mass K=I1/(4m²), ordered-species relabeling,
simultaneous field-sign rephasing of G and Z, degenerate-mass trace invariance,
zero mixed Z current at analytic mixing endpoints and fixed-coupling heavy
mass decoupling. Nonzero original mixed terms are retained. A threshold
request raises an error rather than using an unvalidated small imaginary
regulator. No absorptive-domain implementation is claimed.

The Flo21 X normalization would give the following **scalar-only source
diagnostics**, using X=2v/(e delta) sum G_ji Z_ij F_ij:

| X scalar diagnostic | D7 | F13 |
| --- | ---: | ---: |
| Literal ordered-sum scalar X | -0.141618778492 | -0.0603112148658 |
| Candidate ordered-sum scalar X | -0.141553686391 | -0.0603058235226 |
| Candidate mixed X12+X21 | -0.0280915527492 | -0.0139097274457 |

No W/fermion relative sign is inferred from these entries. Hue's F21 and
Flo21's X require a common overall tensor convention before adding sectors.

## Width/prefactor audit and release gate

Explicit transverse polarization summation gives
Gamma=M³(1-MZ²/M²)³ (|F21|²+|F5|²)/(32 pi), agreeing with Hue Eq.4.
If F21=alpha X/(2 pi v), the corresponding prefactor is
alpha² M³/(128 pi³ v²), or GF alpha² M³/(64 sqrt(2) pi³).
Thus Flo21 D.21's printed mh² must be mh³ for dimensions to work;
D.19's printed tau=4mh²/mcharged is also dimensionally inconsistent
with tau=4mcharged²/mh². D.18 additionally prints an extra MZ² DeltaB0
after its second bracket, inconsistent with a dimensionless IW. These
observations do not replace a sector-by-sector normalization check.
The 2019 printed width has a pi-squared denominator, unlike Hue's pi;
its incomplete normalization record is another reason not to use it as an
independent numerical width reference.

| Gate | Status / evidence | Consequence |
| --- | --- | --- |
| Original scalar/current convention | PASS within frozen analytic/native lineage | Matrices and source hashes retained |
| Scalar PV kernel and native tensor comparison | PASS in real subthreshold domain | Candidate independently checked |
| Literal Flo21/Hue18 mixed-source agreement | FAIL under explicit common LoopTools ordering | STOP; exact counterexample above |
| Complete SM/one-state h amplitude, relative sector signs and external width reference | UNKNOWN; not executed after source mismatch stop | No complete h width |
| 2021 numerical curve reproduction | UNKNOWN; not executed | No external mixed-amplitude reproduction claim |
| General complex fermion CP tensors; H/A thresholds | UNKNOWN; not extended | No H/A Zgamma width |
| Physical tau-tau signal | UNKNOWN | No likelihood ratio or exclusion |

The precise next decisive input is a source-verified definition of Flo21's
six-argument C0 (or corrected D.20 / original numerical code) resolving
the permutation above. A continuation must then independently fix relative
W/fermion/scalar signs and SM/one-state width normalization, reproduce a
published mixed check and only afterward handle heavy absorptive/CP sectors.
This is a bounded correction/validation request, not a claim that a Zee
formula is absent, a need for a new parameter scan, or a proof that the
candidate correction cannot be completed. No `zgamma.py` production module
is released; the diagnostic's physical-width entry point raises an error.

## Reproduction

From the repository root, using the pinned installed native libraries:

```bash
bash research/full_constraints/higgs/build_zgamma_probe.sh
python -m research.full_constraints.higgs.zgamma_source_audit \
  --probe /tmp/zee-zgamma-pv-probe \
  --out research/full_constraints/higgs/ZGAMMA_SOURCE_EVIDENCE.json \
  --replay-out research/full_constraints/higgs/TAUTAU_MATERIALITY_REPLAY.json
python -m unittest research.full_constraints.higgs.test_zgamma_source_audit -v
git diff --check
```

The tests assert the source mismatch as an expected finding; green tests
do **not** mean a green physical-amplitude gate. See
[HIGGS_TAUTAU_MATERIALITY.md](HIGGS_TAUTAU_MATERIALITY.md) for the retained
width/likelihood barriers. B and LFV statuses, old receipts, coverage matrix,
scan authorization and frozen modules are unchanged.

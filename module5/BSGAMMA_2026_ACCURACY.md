# Gate C2 — 2026 flavour accuracy audit

2026-10-27. **C2_NATIVE_NLO_MATCHING_PASS; C2_INDEPENDENT_NLO_PASS** for
real, top-only, ms=0 charged-scalar QCD matching through alpha_s.
**QUADRATIC_VALIDITY_UNKNOWN; 2026_LINEARIZED_FLAVOR_FILTER_READY=false.**
This closes two-state NLO **matching**, not an NLO Zee decay calculation.
Numerical evidence, all native API outputs, residuals, tests and actual-byte
SHA256 provenance: [accuracy_2026.json](../validation/module5/accuracy_2026.json).
Required ancestor: `429a9d6de26a072dc0290db6ca1d050a362f5ecf`.

## Source equations and basis audit

- [BMU hep-ph/9904413v1](https://arxiv.org/html/hep-ph/9904413v1),
  Sec.2 Eqs.(9)–(29), Appendix B: ordinary P4, P7, P8, positive interaction
  Lagrangian `+4 GF/sqrt(2) Vts*Vtb sum C_i P_i`, negative Hamiltonian;
  `C=C^(0)+a C^(1)`, `a=alpha_s/(4 pi)`. MSbar masses/couplings,
  dimensional regularization and fully anticommuting gamma5/NDR operator scheme.
- [Borzumati–Greub hep-ph/9802391v1](https://arxiv.org/html/hep-ph/9802391v1),
  Sec.3 Eq.(13), Appendix A Eq.(A4):
  `C7eff=C7+sum y_i C_i`, `C8eff=C8+sum z_i C_i`, with
  `y4=-4/9`, `z4=-1/6`. This finite basis definition matters at NLO.
- [Misiak et al. 2608.29863v1](https://arxiv.org/html/2608.29863v1),
  Sec.IV Eq.(4): LO NP approximation at 160 GeV, photon cut 1.6 GeV.
  LO matching is explicitly recommended for generic small NP effects;
  quadratic NP terms are dropped. Generic alpha_s matching is cited to BMU.
- [Companion 2608.29864v1](https://arxiv.org/html/2608.29864v1),
  Secs.1–3, Appendices A–C: low-scale bilinear rate, updated normalization,
  nonperturbative treatment and inputs; inspected for curvature, as below.

The first three downloaded HTML hashes exactly reproduce the C1 source hashes;
the companion's hash is also recorded. No unversioned formula is substituted.
The frozen C1 operator/sign bridge is retained.

The independent implementation is
[`zee_module5_bmu_nlo.py`](../scripts/zee_module5_bmu_nlo.py).
It evaluates the paper's generic rational functions at 70 decimal digits,
not HyperIso's G7H/G8H functions. For `x=mt(mu)^2/M^2`, `L=ln(mu^2/M^2)`,
`r1=N R1=x cot²beta/2`, `r2=N R2=x/2` (negated for the opposite-down-Yukawa
control), insert `Qpsi=2/3`, `Qphi=-1`, `kappapsi=4/3`, `kappaphi=0`, `xi=1`:

```
C7^0 = r1[(2/3)g1(x)+g1(1/x)/x] + r2[(2/3-x)g2(x)-1/2]
C8^0 = r1 g1(x) + r2 g2(x)
C4^1 = r1[-(4/3)f1(x)+f2(x)]
C7^1 = 3L[(8/3)x dC7^0/dx+(40/9)C7^0-(16/27)C8^0]
       + r1[(2/3)((4/3)h1+h3)-((4/3)h4+h6)]
       + r2[(2/3)((4/3)h7+h9)-((4/3)h10+h12)]
C8^1 = 3L[(8/3)x dC8^0/dx+(38/9)C8^0]
       + r1[(16/9)h13+(4/3)h16+h18]
       + r2[(16/9)h19+(4/3)h22+h24]
```

Crucially BMU's text after Eq.(29) holds the **entire R1 and R2 products**
fixed in the derivatives, including `S_L* B_R mpsi/mb`. One must not
differentiate the x in substituted r1/r2. The code contains explicit g/f/h
expressions transcribed from the pinned paper, including all continuation
lines of h16/h18. No new loop-convention calculation is performed.
The evaluator is restricted to positive x away from x=1; no near-degenerate
fermion/scalar numerical certification is claimed.

**Executed basis finding:** `BWilsonTHDM.cpp` returns

```
getM(C4,NLO) = EH(x,lu)
getM(C7,NLO) = G7H+Delta7H L - (4/9)EH
getM(C8,NLO) = G8H+Delta8H L - (1/6)EH
```

with `lu=cot beta`, `ld=-tan beta`. These native dipole outputs match the
**effective** coefficients in BG Appendix A4, whereas BMU Eqs.(25),(29)
are ordinary coefficients. Directly calling the API does not certify the basis.
Before constructing the witness we explicitly use
`C7^1_ordinary=getM(C7,NLO)+(4/9)getM(C4,NLO)` and
`C8^1_ordinary=getM(C8,NLO)+(1/6)getM(C4,NLO)`.
The raw API outputs remain separately recorded, unmodified. Without this
conversion the residual is precisely `-4 C4^1/9`, `-C4^1/6`.
The prewritten consumer now rejects missing/effective basis labels; synthetic
tests alone still cannot authenticate those labels or provenance hashes.

The source's BWilsonGroup running code applies effective-coefficient maps
again. This audit certifies the extracted **matching** after the explicit
published conversion only; it does not certify that running/observable path.
No upstream files, kernels or binaries are changed, and no patches are used.

## Native runtime and two-state result

Reused unmodified [HyperIso v1.0.3](https://github.com/Hyperiso/Hyperiso/tree/09d26ac6e71d1528922097a896d15693589f636b),
HEAD/tag peeled `09d26ac6e71d1528922097a896d15693589f636b`, CLI `1.0.3`.
The launcher checks tracked source integrity, CMake checkout provenance,
CLI version and actual SHA256 bytes of inputs, client binary, logs and audited
sources. Sixty-four hexadecimal characters alone are not authentication.
The upstream build/source remain external; binaries are never committed.

Reference LHA SHA256:
`984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374`.
Its SMINPUTS feed QCDHelper's threshold/running and pole-to-MSbar top
conversion. `WilsonParametersHelper.cpp` uses exactly the same calls as
our client: `msbar_mass(6,160,MassType::MSBAR)` and `alpha_s(160)`.
`THDMParametersHelper.cpp` forms x from that matching top and physical M.
Actual runtime outputs:

```
mt_MSbar(160) = 163.96892236746697 GeV
alpha_s(160) = 0.10868631788645876
a = 0.008648982369043495
```

This is reference-LHA calibration, not a fit to the 2026 SM inputs. The six-field
C1 input was reconstructed byte-for-byte and checked against its recorded
SHA256 `4955cab1809f1b89c2078af5dacaa8eda19f7de9523689e2884e30a724eedc38`.
No 163-GeV fallback, extra alpha_s multiplier or automatic scale conversion.

Unweighted ordinary matching at tanbeta=5.3 (floating representation
5.299999999999997), common mu=160 GeV:

| M [GeV] | C7^0 | C8^0 | C4^1 | C7^1 ordinary | C8^1 ordinary |
| --- | --- | --- | --- | --- | --- |
| 550 | -0.059602624672982586 | -0.0644719432489814 | 0.001644412937775417 | 1.1751998025266217 | 0.620540212489079 |
| 900 | -0.031330934470478966 | -0.03628183523815912 | 0.0009123449980750297 | 0.7677511745298502 | 0.4624364788403359 |

Literal native `getM` dipoles at NLO are respectively
`(1.1744689523320548,0.6202661436661164)` and
`(0.7673456878640391,0.4622844213406567)`.
Native `getFM` LO+NLO dipoles are respectively
`(-0.04944466341127366,-0.059107272308298556)` and
`(-0.024694175145181338,-0.03228354542850031)`.
For every C1–C8 at every executed point,
`getFM(NLO)-getFM(LO)=a getM(NLO)`; largest residual
`6.938893903907228e-18`. C1–C6 vanish at LO. At NLO C4 is nonzero;
C1,2,3,5,6 are zero for this retained sector/order. Source C3,5,6 begin
at NNLO; those higher-order numbers are outside this audit.

At gamma=1.09, weights are `(0.21389271457378156,0.7861072854262184)`.
Weighting **full ordinary matching** for the two separate masses gives:

| quantity | C4 | C7 | C8 |
| --- | --- | --- | --- |
| LO | 0 | -0.03737804303348145 | -0.042311493964722 |
| NLO coefficient, unmultiplied | 0.001068928996949981 | 0.8549014676214426 | 0.4962537156147157 |
| a times NLO coefficient | 0.000009245148048379732 | 0.007394027720727265 | 0.004292089636924 |
| LO+NLO | 0.000009245148048379732 | -0.029984015312754186 | -0.038019404327798004 |

BMU Sec.1/2 and its Fig.2 justify additive heavy scalar/fermion loops:
one colorless charged scalar and two Yukawa vertices per retained diagram;
a gluon attaches to colored lines, not to the scalar. Pure QCD neither
changes scalar species nor induces a charged-scalar mixing counterterm.
Thus each product of quark Yukawas receives a_k², and the weighted sum is
valid at this order. Electroweak/scalar-potential corrections can involve
additional scalar couplings and are not certified by this argument.

Twelve executed points include both reference masses and
`(M,tanbeta)=(300,.5),(550,2),(900,50),(2000,5.3),(100000,5.3)`, each of the
latter with physical and opposite-down-Yukawa signs. All five coefficients
agree with independent BMU; maximum absolute residual
`2.9976021664879227e-15` (acceptance tolerances 3e-10 relative / 3e-13 absolute).
These are numerical tolerances, not theory uncertainties. Both masses' LO
values agree with frozen Python; weighted C1 reproduction is at rounding
precision. Interchange, gamma=0/pi2, equal masses, heavy decoupling,
same-mass tanbeta variation, positive/negative coefficients and wrong
basis/scale/top/LO-sign/extra-alpha_s controls pass. No matching-scale
variation is performed and no 81-GeV coefficients enter Eq.(4).

## Accuracy and remaining validity limits

**NLO_MATCHING_DIPOLE_ONLY_SENSITIVITY**:

```
LO Eq.(4) NP shift x 10^4       = +0.4094799731787267
LO shift / SM central          = 0.1156723088075499
naive NLO dipole increment x10^4= -0.07219408951914487
increment / LO NP shift        = -0.17630676528259454
```

The increment is `-8.51 a DeltaC7^1 -2.16 a DeltaC8^1`. It is a measured
sensitivity of this LO-only formula to higher-order matching, **not** a
corrected 2026 BR or an error bar. C4's nonzero contribution requires
consistent evolution, effective/ordinary basis handling and matrix elements;
substitution of just the corrected dipoles omits part of the NP correction.
No physical NLO BR is reported.

**QUADRATIC_VALIDITY_UNKNOWN.** We inspected the versioned 2026 Letter's
Eq.(4) and references, its parallel companion 2608.29864v1 (rate bilinear,
normalization and nonperturbative appendices), and BG's nonlinear NLO
framework. The companion does supply a low-scale bilinear rate framework;
we did not obtain/implement and validate a numerical quadratic response
matrix for **high-scale ordinary shifts at 160 GeV with the complete 2026
normalization, cut and nonperturbative prescription**. Reconstructing it
requires the evolution, all relevant rate kernels and normalization inputs,
not just the newly calculated Q1,2–Q7 interference. BG's historical rates
and HyperIso's archived R3 use different inputs/prediction bases. No
quadratic benchmark is passed off as validated. No square of Eq.(4), old
SM rescaling, fitted R3 curvature or invented universal 10% boundary is used.
The reference 11.57% LO shift alone neither proves nor disproves accuracy.

Specific Type-II Zee operator inventory:

- Q4 is generated already at NLO QCD matching, as measured above; subsequent
  mixing/rate effects cannot be omitted from a claimed full NLO prediction.
  Q3,5,6 arise under evolution and at higher matching order. SM Q1,2 also
  interfere with NP dipoles; zero NP C1,2 here does not remove their rate role.
- Charged-Higgs exchange with active u,c can generate mass/Yukawa-suppressed
  scalar four-quark structures at tree level; internal u,c penguins carry
  small up-type masses and CKM factors. They are outside this top-only
  calculation. Their parametric suppression is not a numerical rate bound,
  especially at extreme tanbeta or in cancellation regions.
- Primed Q7',Q8' and right-handed four-quark terms require the strange/down
  Yukawa at the external vertex in this natural-flavour-conserving quark
  sector. Leading primed dipoles scale as ms/mb; wrong-helicity interference
  is additionally chirality-suppressed in the ms=0 inclusive limit. Finite-ms
  pieces, terms with two down-type Yukawas, and possible tanbeta enhancement
  need a quantitative bound; a negligible rate is not demonstrated here.
- Natural flavour conservation gives no tree-level neutral-scalar b–s
  coupling. Electroweak penguins, scalar/tensor four-quark and semileptonic
  LEFT operators are not the retained top/gluon dipole matching; their
  generation/mixing/radiative effects need order-specific assessment.
  Zee lepton Yukawas do not supply direct new charged-scalar quark vertices,
  but this is not certification of full electroweak/leptonic loop effects.

The separately published SM `(3.54 +/- .14)e-4` and experiment
`(3.49 +/- .19)e-4` are recorded without combining their errors or deriving
an exclusion. The NLO–LO difference supplies no one-sigma NP uncertainty.
No likelihood, global acceptance, collider inference, or per-scalar 670-GeV
mass cut is authorized. C0's patch failures and historical R1–R7 remain intact.

Before a scan filter: reconstruct a source-pinned 2026 coefficient-to-rate
response including quadratic terms and C4; reproduce zero-NP and independent
one-state results and falsify opposite-sign/cancellation directions; study a
controlled two-state domain in masses, mixing and tanbeta. Then calibrate
mass/scheme/scale and missing-order uncertainty, bound omitted operators and
finite-ms effects, and document correlated theory/experimental treatment.
Only those results can set an accuracy domain and statistical prescription.

## Reproduction

Download the four versioned HTML sources above to ignored
`validation/module5/local/c2/{bmu,bg,misiak,companion}.html`, then run:

```sh
python scripts/zee_module5_nlo_validate.py \
  --upstream /home/amine/zee-hyperiso-runtime-bridge/validation/module5/local/HyperIso \
  --binary /home/amine/zee-hyperiso-runtime-bridge/validation/module5/local/HyperIso/build/UserInterfaceLib/hyperiso-ui
python -m module5.hyperiso_patch_contract --input validation/module5/local/2026_reference_input.json --output validation/module5/local/c2_contract.json
python -m module5.bsgamma_matching_accuracy --contract validation/module5/local/c2_contract.json --witness validation/module5/local/c2_native_nlo_witness.json --output validation/module5/local/c2_nlo_impact.json
```

The launcher compiles the external client using existing CLI link dependencies,
executes fresh per-mass LHAs, authenticates actual local artifacts, and runs
23 focused tests (5 synthetic scaffold, 11 frozen C1, 7 frozen contract).
Synthetic tests verify validation/arithmetic only; the separately executed
12-point BMU/native comparison establishes the NLO matching evidence.

# Physical leading one-loop h125 → Zγ, original D7/F13

**`H125_ZGAMMA_LEADING_ONE_LOOP_VALIDATED`**, 7 November 2026.
The complete leading one-loop partial width passes a matched-input independent
SM code control, a signed one-charged-scalar limit, native PV tensor controls,
and the previously established mixed-scalar Ward/UV tests. This release is
one observable at the two saved NO/low_joint witnesses. It supplies neither
total widths nor a Higgs likelihood, experimental exclusion, or global PASS.
Higgs remains `HIGGS_FULL_COVERAGE_BLOCKED`; B remains
`B_FULL_RATE_BLOCKED`, LFV `LFV_FULL_COVERAGE_BLOCKED`, vacuum UNKNOWN.

| Fixed card | Γ(h125→Zγ), GeV | Γ/ΓSM |
| --- | ---: | ---: |
| SM, all nine charged fermions | 6.476096614609e−6 | 1 |
| D7 | 6.338611988312e−6 | 0.978770448547 |
| F13 | 6.408681594999e−6 | 0.989590176981 |

These are physical partial widths **at leading one loop in the declared tree
input scheme**, not precision higher-order predictions or signal strengths.
The numerical relative error allowance is 1e−10. Higher-order QCD/EW/scalar
and parametric uncertainties are not quantified; `theory_sigma=null`.
No confidence level follows from these numbers.

## Definition, inputs and complete particle content

Use the common transverse-tensor convention of
[Fontes–Romão–Silva, JHEP12(2014)043](https://arxiv.org/abs/1408.2534),
DOI 10.1007/JHEP12(2014)043, arXiv:1408.2534v1, C.1–C.4 and D.5:

```
M = c [(qγ·qZ)(εγ·εZ) − (qZ·εγ)(qγ·εZ)]
    + d ε( qγ, qZ, εγ, εZ )
c = α X/(2πv), d = α Y/(2πv)
Γ = α² mh³/(128π³v²) (1−MZ²/mh²)³ (|X|²+|Y|²).
```

The polarization test explicitly includes two photon and three Z
polarizations: both tensors have norm 2(qγ·qZ)² and their contraction
vanishes. Complex absorptive parts do not change CP-even/odd
non-interference in the unpolarized width. There is no identical-particle
factor for Zγ.

Matched inputs are mh=125 GeV, MW=80.379 GeV, MZ=91.1876 GeV,
v=246.21965 GeV; cw=MW/MZ, g2=2MW/v, e=g2 sw,
αtree=0.007565201924913188. Propagator and Yukawa masses use the same frozen
D4 values: (u,c,t,d,s,b)=(0.00216,1.2730,172.4,0.00470,0.0935,4.78) GeV;
(e,μ,τ)=(0.00051099895,0.1056583755,1.77686) GeV. Light-quark masses are
the frozen partonic prescription, not a claim of a precision hadronic error
estimate. Scalar masses, signed G and mixing matrices come from the exact
physical tree cards, not SPheno pole/loop output. Complete card-file hashes,
scalar/witness identifiers and dependency hashes are in
[ZGAMMA_H125_EVIDENCE.json](higgs/ZGAMMA_H125_EVIDENCE.json).

Included are the gauge-complete W contribution, all six quarks and three
charged leptons, and the coherent ordered sum of both charged scalars,
including off-diagonal h and Z vertices and AZ seagulls. The native Type-II
quark factors are sinα/sinβ and cosα/cosβ; kV=cos(α−β).
Leptons retain their general complex native diagonal Yukawas. A single
flavor-changing neutral Yukawa cannot close a loop with flavor-diagonal
photon and Z currents. There is no neutrino photon current. Physical
H±W∓γ and H±W∓Z tree vertices vanish for these doublets and a charged
singlet without a charged vev, so mixed physical W/charged-scalar triangles
do not add a further sector. The W function includes its gauge completion;
in a covariant gauge it incorporates the Goldstone/ghost/mixing contributions
discussed in Fontes C.4. This work does not repeat a gauge-parameter scan.

## Couplings, chiral factors and signs

Define τ=4m²/mh², λ=4m²/MZ² and I1,I2 by Fontes E.2–E.4,
with the physical absorptive continuation. The W result is

```
XW = kV cw/sw { 4(3−tw²) I2
             + [(1+2/τW)tw²−(5+2/τW)] I1 }.
gL/e = (T3−Qsw²)/(sw cw),  gR/e = −Qsw/cw
w_f = 2 Nc Q (gL+gR)/e
Xf = w_f Re(kf) (I1−I2),  Yf = w_f Im(kf) I2.
```

The two orientations retain the sum of left/right Z couplings. Axial-Z
terms cancel by charge conjugation: one photon vector current and one
axial Z current have odd charge-conjugation parity with either the scalar
or pseudoscalar insertion. Native C has right-Weyl row index:
`C PL+C* PR = Re(C)−i Im(C) γ5`; hence Fontes A.1 has a=Re(k),
b=−Im(k). C.4 then gives the Y sign written above. This overall odd-tensor
sign is specified even though flipping it alone leaves this unpolarized
width unchanged. Tests check native conjugation, the separate chiral
currents and the C.3/C.4 native-PV forms, including imaginary parts.

The scalar convention is `V ⊃ h H− G H+`, vertex −iG,
`Z=e/(sw cw)[P/2−sw² 1]`, photon e1, AZ contact 2ieZ.
With Hue18's Kij=∫simplex xz/D(mi²,mj²,mj²),

```
Xij = −2v/e Gij Zji (Kij+Kji),  Xscalar = sum_ordered_ij Xij.
Xii = −v Gii Zii/e I1/mi².
```

This reproduces Fontes C.10 with **λv=−G**, not +G. HEPfit's GeneralTHDM
convention reverses all CP-even tensor signs relative to its StandardModel
functions; its positive `vG/(2m²) A_H_Hp` therefore maps to our negative
scalar term. No sign is fitted to D7/F13 or to a width. Analytic fixed-G
heavy-mass decoupling, equal masses, zero mixing, species interchange,
field rephasing and degenerate-basis invariance retain the source-audit
controls.

| Dimensionless component | D7 | F13 |
| --- | ---: | ---: |
| XW | 12.321753356086 | 12.336003602946 |
| ΣXf | −0.636801448972 − 0.012058745044 i | −0.668671471784 − 0.011410887158 i |
| X11 | +0.027973779999 | −0.005386364864 |
| X12+X21 | −0.028091552749 | −0.013909727446 |
| X22 | −0.141435913641 | −0.041009731213 |
| Y | 3.89644925e−8 − 1.92971340e−8 i | −1.61395919e−10 + 7.99352779e−11 i |

The W/fermion, W/scalar, fermion/scalar cross terms in |X|² are respectively
(−15.6930207821, −3.48837922072, +0.180283185203) for D7 and
(−16.4974673702, −1.48786571251, +0.080649567544) for F13.
The odd fractions of the width are 1.41884e−17 and 2.40777e−22, retained
explicitly. The scalar contributions interfere destructively with W on both
cards; omitting the mixed pair is not an admissible one-state approximation.

## Independent SM and one-charged-scalar execution

The reference is the saved public
[HEPfit source at 322bd73a2dadd94ce94a6d71cb79d616e569120a](https://github.com/silvest/HEPfit/tree/322bd73a2dadd94ce94a6d71cb79d616e569120a).
`StandardModel.cpp`'s original `GammaHtoZga`, `AHZga_f`, `AHZga_W`,
`I_triangle_1/2`, `f_triangle`, `g_triangle` were extracted and compiled in
a minimal C++ input/dependency shim. Their arithmetic is unchanged:
class qualifiers are removed, gslpp complex is replaced by std::complex,
abs2 by std::norm, and the intermediate MSM is exposed for the coherent
scalar control. This is **isolated reference-function execution**, not a
full HEPfit build, fit, or default-input comparison. Full source-file,
generated-C++ and executable hashes, raw stdout and empty stderr are saved.
The harness verifies pinned source hashes before extraction.

At identical inputs and the reference's six charged fermions
(t,b,c,s,τ,μ), HEPfit yields **6.476096527951174e−6 GeV**;
our result differs by −2.44e−15 relative. Including u,d,e raises this by
1.33812e−8 relative, explaining the all-nine SM value above. The HEPfit W
component is 12.336040776842815. A distinct direct native-PV evaluation of
[Hue et al., EPJC78(2018)885](https://arxiv.org/abs/1712.05234),
DOI 10.1140/epjc/s10052-018-6349-0, Eq.20, with its opposite F21 tensor
sign mapped explicitly, agrees to 6.00e−15 relative. Thus a total-SM match
does not conceal an independently unchecked W normalization.

For the one-doublet-charged-state limit, execute HEPfit
`GeneralTHDMcache.cpp::A_H_Hp`'s expression with Z/e=(1/2−sw²)/(sw cw).
The following are analytic model-limit controls, not generated Zee points.
Both signs of G test interference, rather than the squared scalar alone.
Native LoopTools B0/C0 in published Fontes C.10 independently checks the
scalar normalization and λ sign.

| m±, GeV | G, GeV | Common-input one-scalar Γ, GeV |
| --- | ---: | ---: |
| 300 | +100 | 6.441443836204e−6 |
| 300 | −100 | 6.510842179531e−6 |
| 700 | +100 | 6.469878496947e−6 |
| 700 | −100 | 6.482317545517e−6 |

All coherent one-scalar widths agree with the executed reference to
3.34e−15 relative. These validate the public one-state amplitude limit;
no complete general-2HDM phenomenological fit or mixed-Zee external
numerical curve reproduction is claimed.

## Preserved unequal-mass finding and numerical domain

The original [source evidence](higgs/ZGAMMA_SOURCE_EVIDENCE.json),
[manifest](higgs/ZGAMMA_SOURCE_MANIFEST.json) and
[rescue report](HIGGS_ZGAMMA_2021_RESCUE.md) remain byte-for-byte unchanged.
The historical source-only calculator remains a diagnostic. Its earlier
stop is superseded **only for this h125 observable** by the independent
normalization checks here; authors' intended PV convention is still unresolved.

Literal Flo21 (DOI 10.1140/epjc/s10052-021-09956-2,
arXiv:2106.08332) D.20 in the explicitly declared LoopTools convention uses
`C0(t,0,s,a,a,b)`, where the photon-adjacent masses differ.
The validated physical ordering uses `C0(t,0,s,b,a,a)` and its reversed
orientation. The literal mixed kernel differs by **0.231714% D7** and
**0.0387595% F13**. These are mixed-kernel discrepancies, not errors on a
full physical width. The retained falsification test shows that literal
routing fails the scalar tensor Ward identity, whereas the physical
triangle-plus-seagull current is UV/scale independent and satisfies it.
This does not establish an error in the authors' uninspected program.
Printed dimensional problems in D.19/D.21 are not used for normalization.

The new ordered scalar sums reproduce the saved physical-routing sums to
2.00e−14 (D7) and 5.75e−14 (F13) absolute. Scalar integration refinement
80→120 nodes changes the full width by at most 4.45e−16 relative.
W and both charged scalar pair thresholds lie above h125. Scalar routines
reject the absorptive domain instead of inserting a small regulator.
Light fermions retain their physical cuts: fresh native LoopTools 2.13 C0
and tensor-K comparisons agree with the complex analytic functions to
4.51e−14 relative or better. Native C.3/C.4 tensor checks have maximum
absolute residual 4.11e−15. The new raw native log is retained separately.
These are numerical validation residuals, not theory-error measurements.

At fixed reduced X,Y, the separately labelled uniform αtree→α(0)
normalization comparison gives D7 5.897714946629e−6 GeV and F13
5.962910697280e−6 GeV. This keeps v, MW/MZ and the reduced couplings fixed;
it is a finite-order scheme diagnostic, not an independent consistent
electroweak fit or a guessed uncertainty. It leaves Γ/ΓSM unchanged.

## Reproduction and release decision

```
bash research/full_constraints/higgs/build_zgamma_probe.sh
python -m research.full_constraints.higgs.run_zgamma_h125 \
  --probe /tmp/zee-zgamma-pv-probe
python -m unittest research.full_constraints.higgs.test_zgamma \
  research.full_constraints.higgs.test_zgamma_source_audit -v
git diff --check
```

The reference source tree must be available at the path recorded by
`zgamma_reference.py`; its commit and exact file hashes are mandatory.
No package was installed. The fresh suite passes 20 tests, including the
unchanged scalar Ward/UV/routing falsification controls. Green tests are
supported by the numerical external-code comparison above, rather than
being used as its substitute.

| Gate | Evidence | Decision |
| --- | --- | --- |
| SM absolute normalization and W/fermion interference | Executed pinned HEPfit functions, matched inputs; native Hue20 W | PASS, h125 LO |
| Signed scalar/SM interference | Published one-state C.10, executed HEPfit scalar function, ±G | PASS, one-state limit |
| Mixed charged-scalar tensor | Preserved LoopTools/integral/Ward+UV evidence; exact sum replay | PASS, subthreshold |
| Complex fermions, CP tensors and cuts | Native C.3/C.4 and polarization/conjugation controls | PASS, h125 LO |
| D7/F13 physical partial width | All sectors coherently combined at common leading order | RELEASE for this observable only |
| Higher-order uncertainty and complete Higgs likelihood | Not established here | UNKNOWN / BLOCKED |

No heavy H/A extension, SusHi/HDECAY run, new parameter point, scan,
Condor submission or frozen module modification was performed. Full Higgs,
B, LFV and vacuum status are unchanged. The result can be used as this
declared-order partial-width input; it does not authorize a final scan.

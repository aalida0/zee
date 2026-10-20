# F4 AF result — Type-II effective-dipole inverse audit (20 Oct 2026)

**Status: Source-level basis-interface audit passed; inclusive NLO scheme/rate NOT_YET_VALIDATED.**

This note records a **user-posted AF log**, not a reconstructed or independently executed AF run. The full, uncommitted artifact remains
`work/gateF4_typeII_basis_inverse_8_v1/summary.json` on UChicago AF.

## Recorded execution

- Five `test_zee_gateF4_typeii_basis_interface` synthetic contract tests: **5/5 PASS**.
- Real F4 source-pinned pilot: `F4_STATUS NOT_YET_VALIDATED`; all 8 Type-II controls present.
- AF isolated A1M `src/wilson.c` SHA256: `a9c12d12e7879354518e2b6d5d777c4f25997b9477d0a4dc35750c3c7a61d03e`.
- `src/libsuperiso.a` SHA256: `5d688deae4effd9f5916cd8976a9ca49f8a7fb598299d0f80f014e76b5c3a986`.
- `scripts/zee_gateF3_fullNLO_rg_probe.c` SHA256: `8db5a2d339f15b2b9531deb079e40eeff091fa7eaa55714bf8ce338e99416ee0`.
- Installed EOS version: **1.1**; flavio **2.7.0**.
- All six C7eff/C8eff high-scale definitions pass source signature checks; low scale `Cb[7,8]` follows the effective-dipole evolution path and is **not** explicitly inverse-rotated in `C_calculator_base1`.
- F4 applies the **algebraic inverse** to the low-scale *NP deltas* before passing raw `c7,c8` parameters to EOS. This eliminates source-level double effective rotation, but **does not** establish the scheme/evanescent-operator correspondence with EOS at NLO.

## Numerical Type-II results

Each column is a **conditional** EOS NLO-kernel response, NOT a validated physical NLO prediction or statistical exclusion.

| tanβ | mH+ (GeV) | inverse-rotated EOS BR | inverse minus F3 direct | extra charged-Higgs NLO C3–C6 response | even/odd matching-insertion ratio |
|---:|---:|---:|---:|---:|---:|
| 5.6 | 300 | 0.000454975401913 | -1.03947436e-08 | +1.10445383e-08 | 1.005% |
| 5.6 | 580 | 0.000389258907144 | -5.02717345e-09 | +5.36437107e-09 | 0.716% |
| 5.6 | 670 | 0.000379747336412 | -4.20278486e-09 | +4.48813936e-09 | 0.648% |
| 5.6 | 1000 | 0.000360548009457 | -2.47734658e-09 | +2.65008022e-09 | 0.468% |
| 50 | 300 | 0.000454376120151 | -1.30303222e-10 | +1.38454057e-10 | 1.005% |
| 50 | 580 | 0.000389055419651 | -6.30437634e-11 | +6.72736805e-11 | 0.715% |
| 50 | 670 | 0.000379589558017 | -5.27083531e-11 | +5.62879355e-11 | 0.647% |
| 50 | 1000 | 0.000360471845246 | -3.10724108e-11 | +3.32392293e-11 | 0.468% |

Source: eight controls posted from `work/gateF4_typeII_basis_inverse_8_v1/summary.json`, October 2026.

### Perturbative warning

F4 defines `h = C_low(FULL_NLO_high_match)-C_low(LO_high_match)`, each evolved through the **same SuperIso NLO RGE**. At fixed running/matrix-element inputs it evaluates
`R(C0+h)` and `R(C0-h)`.
The even part `[R(C0+h)+R(C0-h)]/2-R(C0)` is of order `h²`, i.e. formally at least NNLO in the **NLO matching insertion**. It ranges **3.14e-08 to 1.88e-07**, larger than the isolated extra four-quark-matching effect. The odd part retains mixed NLO-kernel-times-NLO-WC terms; thus removing only the even part **does NOT create a strict NLO prediction**.

At tanβ=5.6, 300 GeV:
- LO *high-scale matching* with NLO evolution + EOS kernel: `4.7346532480875444e-4`.
- Full high-scale source NLO with inverse-basis input: `4.5497540191260957e-4`.
- Odd insertion component: `-1.8677621760352498e-5`.
- Even insertion component: `+1.876988642076239e-7`.
Do not use `R(full)-R(LO)` as a rigorously fixed-order NLO matching correction without separating the NLO matrix-element cross terms.

### EOS source provenance strengthened

The upstream **EOS v1.1 release tag** `723e674687f86d055fba56a6ffe9eb73a64c7507` contains `eos/rare-b-decays/inclusive-b-to-s-gamma.cc` with Git blob SHA
`3bbb034b920709503b767fb372f35338ae427877`, identical to the previously inspected EOS source commit `3eb16b5b7265df7023363e615179fd44a1a02d00`. This is consistent with the AF-reported `eos_version=1.1`; however, the installed compiled Python wheel/library **has not been mapped to exact build-source SHA**. It remains a blocked requirement for certified source-to-binary provenance.

Evidence from tagged source:
- lines 344–354: `c7eff` and `c8eff` recompute the effective dipoles from `wc.c3..c8`.
- lines 356–384: `D = C7eff + a_s M_i C_i` with `a_s=alpha_s/(4*pi)`.
- lines 415–443: bremsstrahlung including an exponential in `alpha_s` and quadratic Wilson products.
- lines 537–541: final rate contains `|D|² + A + |C7eff|² hqe`.
The kernel is consequently **not algebraically truncated at strict NLO when evaluated using the full NLO Wilson vector**; a strict O(alpha_s) expansion must be constructed and separately validated.

Source: https://github.com/eos/eos/blob/v1.1/eos/rare-b-decays/inclusive-b-to-s-gamma.cc .

### Independent matching context

Earlier Gate A1P independently compared SuperIso and HEPfit **LO and NLO matching coefficients** at 300, 700, 1000 and 2000 GeV with common checked `m_t(muW)=163.10709645657508` GeV and `muW=160.7384` GeV. That comparison reportedly agreed to machine precision (see `docs/gateA1p_independent_hepfit_typeii.md`). This does **not** establish matching at F4's `muW=160` GeV and tanβ=50, nor NLO EOS scheme correspondence; and A1P still has **NNLO C3..C6** discrepancies, with an independently documented HEPfit C8 convention/sign issue at NNLO.

## F4 priorities

1. **Highest priority:** a strict O(alpha_s) rate extraction with the EOS v1.1 equation and source-to-binary provenance, demonstrating explicitly which NLO-matching response terms survive, and controlled variation of muW/mub with matching/running consistently reevaluated. Require no assumption that the observed 0.5–1% even/odd ratio captures all beyond-NLO terms.
2. Independently validate the `C3...C6` operator matrix element/finite-scheme correspondence of the A1M SuperIso effective coefficient output with EOS's `WET` input, including potential NLO evanescent-operator/finite-renormalization effects.
3. Check NLO HEPfit C7/C8 and C4 at the F4 reference inputs (`muW=160`, tanβ=5.6/50) without erasing the previously identified NNLO discrepancies.
4. Only after an independent NLO Type-II branching-ratio reference and scale-variation audit can the 27 Zee spectra be propagated through a documented `B->X_s gamma` likelihood.

**NO Type-II or Zee 95% CL bound has been reproduced or inferred.** No new scan is justified at this gate.

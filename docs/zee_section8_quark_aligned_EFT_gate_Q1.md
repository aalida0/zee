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

# Zee Module 5 — native charged-quark vertices and 2026 Wilson convention (Gate A2)

## Branch / motivation
Work **only** on `feature/zee-bsgamma-native-convention` in `aalida0/zee`, branched exactly from validated Gate A commit `09e0e6788f2206e767742730a9fe4c9427f1c097`. Gate A already passed 16 tests with a validated high-precision LO kernel. **Do not repeat or redesign Gate A**. Our immediate goal is to close the **native charged-quark vertex-to-operator matching** and independently establish whether Gate A's `Delta C7,C8` have the exact sign, chirality, CKM, sigma and Hamiltonian normalization required by Misiak 2026 Eq. (4) and the pinned HyperIso source. If not fully proven, fail closed.

## Read only relevant files initially
- `scripts/zee_module5_charged_quark_vertices.m` (prewritten standalone raw SARAH driver).
- `scripts/validate_zee_module5_native.py` and `tests/test_module5_native_gate.py` (prewritten structural tests, **not** amplitude matching).
- `module5/bsgamma_lo.py`, `module5/CONVENTIONS.md`, `validation/module5/STATUS.md` and `module5/FLAVOR_2026_SOURCES.md`.
- `models/SARAH/ZeeTypeII/ZeeTypeII.m`, `module4/couplings.py`, and `scripts/zee_module4_vertices.m` as read-only examples.
- Only relevant HyperIso v1.0.3 source `Hyperiso/Hyperiso/core/src/PhysicalModel/domain/WCoef/BSM/BWilsonTHDM.cpp`, `THDMParametersHelper.cpp`, `docs/main.tex` and the official reproducibility manifest. Avoid a global repo search.

## Pinned operator source / gates
- Misiak et al. *The Inclusive Bbar -> Xs gamma Decay Rate with Higher Precision*, arXiv:2608.29863v1, Section II Eq. (2), Section IV Eq. (4): `https://arxiv.org/html/2608.29863v1`. Explicit unprimed `Q7=e*mb/(16pi²)*(sbar_L sigma b_R) F`, `Q8=gs*mb/(16pi²)*(sbar_L sigma T^a b_R) G^a`. The source uses `mu0=160 GeV`, `10^4 BR=(3.54 +/- 0.14)-8.51 DeltaC7-2.16 DeltaC8` **after exact basis/normalization closure**, linear in NP shifts. The 670 GeV exclusion is for a **single-state Type-II 2HDM**, never a per-state Zee cut.
- Frozen Zee SARAH model: two Higgs doublets with Type-II quarks, one charged singlet, Goldstone `Hm[1]`, physical `Hm[2], Hm[3]`. Complex Yukawa matrices and arbitrary quark flavor rotations must be handled without replacing CKM phases by numerical 1.
- 2021 Florentino/Romão/Silva arXiv:2106.08332v1 Eqs. (62)-(63), Appendix A.3; historical SuperIso v3.0 arXiv:0808.3144v3 Appendix C.2 LO functions; pin actual equation numbering, unlike initial candidate.
- HyperIso **v1.0.3** peeled SHA `09d26ac6e71d1528922097a896d15693589f636b`, `https://github.com/Hyperiso/Hyperiso`. Gate A source audit already established LO algebra with `lu=Y, ld=-X`, but did **not** certify Wilson operator convention; source manuscript has an editorial `Check sign` note, which is a reason to verify—not proof of a wrong sign. HyperIso's R1/R3/R6 use scale choices that differ from 2026 Eq. (4); do not substitute low-scale coefficients or treat old NNLO BR as 2026 updated result.

## Required work (sequential, stop honestly at blockers)

### A2.1 — real native SARAH vertex extraction
1. On local Ubuntu check `/usr/local/bin/math` and SARAH `/home/amine/.Mathematica/Applications/SARAH/SARAH.m`, version 4.15.4. Start the frozen `ZeeTypeII` model. Use the prewritten driver as a starting point and correct any actual syntax/query bug; do not patch SARAH model or old modules.
2. Extract and **interpret** the `bar[u_i] d_j H_k^+` and Hermitian conjugate vertices for k=1 Goldstone, 2/3 charged physical states, with `P_L/P_R` signs, conjugations, `Vu,Vd,Uu,Ud,ZP` flavor rotations; charge/color currents for `u,d` and photons/gluons. Identify correct CKM `V_{ts}^* V_{tb}` for loop `b -> s gamma`.
3. Run genuine SARAH driver `/usr/local/bin/math -script scripts/zee_module5_charged_quark_vertices.m`, then run `python scripts/validate_zee_module5_native.py validation/module5/local/charged_quark_vertices.json`. Structural `RAW_VERTICES_EXTRACTED_NOT_MATCHED` **is not a physics PASS**. Keep detailed raw output in ignored `validation/module5/local/`.
4. Independently match symbolic/native vertices against the frozen Type-II charged X,Y definitions and two physical admixtures. Use distinct nonzero quark masses, a nontrivial CKM phase, beta and gamma, nondegenerate mH1/mH2. Verify reverse-channel Hermitian conjugation, quark mass suppression and doublet/singlet decoupling. If native extraction cannot be run, state `NATIVE_SARAH_BLOCKED` rather than replacing it by historical expressions.

### A2.2 — independent dipole normalization
1. Starting from native vertices, independently derive the charged-loop `b->s gamma` and `b->s g` dipole amplitude projection into Misiak Q7/Q8, including photon attachment to top and charged scalar, gluon to top, chirality, `m_b`, CKM, electric/color charges, fermion flow and sign of the loop. Compare with the independent LO F functions; **do not assume** the correct overall sign from agreement between formula copies.
2. Identify and document Hamiltonian sign `H_eff=-4 G_F/sqrt2 Vtb Vts* sum C_i Q_i`, Lagrangian/Hamiltonian relation, dipole tensor `sigma^{mu nu}`, field strength, and whether a factor of two, gamma5 or i is hidden in different conventions. Explicitly match ordinary C7/C8 vs C7eff/C8eff at the matching scale. Compare to HyperIso implemented Hamiltonian/THDM and 2026 basis; do not infer a correction factor from its editorial source marker.
3. Validate a full set of falsifiers: overall sign flip, H1/H2 interchange, beta and gamma limits, Goldstone/SM and charged-Higgs separation, conjugate CKM channel, left/right chiral exchange, photon vs gluon charge, and matching scale. At least one genuinely independent amplitude-level check (analytic loop projection or external trusted amplitude software) must pass before marking `MATCHING_CONVENTION_PASS`. Copying SuperIso/HyperIso scalar kernels does **not** count.
4. Save a concise derivation `module5/NATIVE_OPERATOR_MATCHING.md` with exact source equations and symbolic-to-numeric tests; concise `validation/module5/native_matching.json` with hashes, actual tests/residuals and `PASS/PARTIAL/BLOCKED` per gate. Update `validation/module5/STATUS.md` only to append new scope, never rewrite Gate A's past evidence. Retain `MATCHING_CONVENTION_UNKNOWN` in production output if any material sign/normalization ambiguity remains.

### A2.3 — optional, only after proof
If and **only if** complete mapping passes, create a separate **linearized diagnostic** (not an experimental acceptance decision) for the 2026 Eq. (4) using `mu0=160 GeV`. Retain the (\mathcal O((\Delta C)^2)) truncation, uncomputed NP NLO and uncertainties as explicit caveats. Do not assert HyperIso's NNLO prediction or `BR` accuracy from this screen. If not passed, no such diagnostic.

## Tests / code / reproducibility
- Run `python -m unittest discover -s tests -p 'test_module5_native_gate.py' -v` and `python -m unittest discover -s tests -p 'test_module5_bsgamma_lo.py' -v`, plus new independent amplitude tests and SARAH numerical comparisons.
- Prewritten driver and structural tests are **only a scaffold**; audit and fix code where necessary. The physical amplitude gate must be additional and cannot be satisfied by asserting the source formula.
- The independent HyperIso **runtime** R1/R3/R6 remains Gate B and may be left for a subsequent isolated task if time/cost or environment prevents building v1.0.3. Do not say it has run when only reading raw files.
- No global Zee LFV, quark-flavor, collider allowance/exclusion or scan claims. Never apply single-Higgs 670 GeV bound independently to H1 and H2. Do not alter frozen SARAH, Modules 0–4 or existing Module5 LO physics unless a separate documented critical correction is proven; stop with CONFLICT if that occurs.
- Logs, entire HyperIso copies, generated Mathematica output and PDFs remain local and ignored. Commit only new Module5 audit/test/driver and small evidence outputs. Minimal browsing, minimal Codex chat.

## GitHub delivery — required
Run real tests, commit to `feature/zee-bsgamma-native-convention`, `git push origin feature/zee-bsgamma-native-convention`, verify local `git rev-parse HEAD` equals `git ls-remote origin refs/heads/feature/zee-bsgamma-native-convention`. Report SHA, URL, status, test counts, residuals, uncertainties and blockers; explicitly `PUSH_BLOCKED` if push fails.

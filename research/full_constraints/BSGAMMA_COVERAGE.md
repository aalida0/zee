# B→Xsγ coverage ledger — 2026-11-07

**Full-rate status: B_FULL_RATE_BLOCKED; physical decision UNKNOWN.**
The declared supported sector is real, top-only, ms=0, leading-electroweak
charged-scalar matching through NLO QCD. This ledger distinguishes that
validated sector from the additional coverage needed for a complete exclusion.
Sources/byte pins: [manifest](SOURCE_MANIFEST.json). Decision and numerical
evidence: [feasibility gate](FEASIBILITY_GATE.md).

**Execution advance, full gate unchanged:** pinned HEPfit has actually built
and run. The [execution report](bsgamma_hepfit/HEPFIT_RATE_REPORT.md) and
[37-run receipt](bsgamma_hepfit/execution/HEPFIT_EXECUTION.json) establish a
coherent eight-operator NLO bridge, exact model-limit controls, signed C4/C7/C8
response and a held-out bilinear cross term. Native Type-II versus independent
BMU matching agrees within 5.82e-17; 18 tests pass. Published NNLO table
interpolation is reproduced, but a matched same-order physical benchmark and
confidence-bound reproduction are still missing. HEPfit/D9B differences
persist with shared inputs/NP matching and are decomposed by actual source
normalization, perturbative/EM and power terms. `HEPFIT_RUNTIME_PASS` and
`INDEPENDENT_RATE_EXECUTABLE` do not promote `B_FULL_RATE_BLOCKED`.
HEPfit's approximate ms/mb-induced primed rule is retained and separately
identified; it does not certify the omitted full primed sector in this ledger.
The Type-II table's 7% nuisance and kernel's BLNPcorr*P0 are not a calibrated
two-state NLO covariance. `UNCERTAINTY_CALIBRATION_BLOCKED` remains operative.

## Model, operators and matching

Use H_eff=−4 GF/√2 Vts*Vtb Σ C_i Q_i,
Q7=e mb/(16π²) sbar_L σ b_R F and the corresponding gs Q8;
C=C^(0)+alpha_s/(4π) C^(1). Matching is ordinary BMU/NDR with
MSbar mt(mu0). Evolution converts to effective dipoles exactly once:
C7eff=C7−C3/3−4C4/9−20C5/3−80C6/9,
C8eff=C8+C3−C4/6+20C5−10C6/3.
Finite scheme changes cannot be omitted at NLO.

The vertices are √2/v a_k ubar V [mu cotβ PL+md tanβ PR] d H_k+,
a=(cosγ,−sinγ). For flavor j=u,c,t the CKM factor is Vjs*Vjb;
the validated leading-top terms factor out Vts*Vtb. Left/left products
scale as a_k² cot²β, left/right products as a_k²; finite strange/down
Yukawas restore other chiral products. The singlet has no direct quark
Yukawa. Its contribution through doublet mixing is already included.
Complex lepton Yukawas do not supply a new phase to this real pure-QCD
top matching; this does not validate general complex Wilson inputs.

| Contribution | Coverage at declared accuracy | Required before broader physical use |
| --- | --- | --- |
| ΔC7,8^(0), two charged states | Independently validated native/BMU/LO kernels; coherent a_k² sum | Reuse; no per-state mass cut |
| ΔC4^(1), ΔC7,8^(1) | Independent BMU/native QCD matching; ordinary/effective conversion checked | Reuse with one alpha_s/(4π), common scheme/scale |
| Other NP Q1–Q6 at matching | Zero in the validated real top-only scalar QCD matching at this order | Not a proof that all full-model four-quark operators vanish |
| Q3–Q6 induced by RG | Retained in D9B and native EOS bridge | Keep full vector; dipole-only evolution is insufficient |
| Internal u,c, exact CKM sum | Not certified by top-only matching | Bound their rate effects with masses/CKM at the same scheme |
| Finite-ms/right-chiral and primed Q7,8 | Not included in supported D9B domain | Compute or numerically bound; ms used as a collinear regulator does not cover NP chirality terms |
| Down-Yukawa-enhanced terms | Not quantitatively bounded over a Zee domain | Check relevant tanβ and scalar masses; top dominance alone is not an error bound |
| Charged-exchange four-quark structures outside retained basis | No complete model inventory/bound established (including possible scalar structures from light-quark Yukawas) | Match and power-count; prove negligible at claimed accuracy or include mixing/matrix elements |
| Neutral-scalar quark FCNC | Absent at tree level in the Type-II quark ansatz | Does not remove higher-EW-order diagrams |
| Extra Zee singlet/lepton, scalar-potential and electroweak loops | Outside declared leading-EW/QCD subset | Establish numerical materiality/error budget, including GF/normalization effects if relevant |
| NP NNLO QCD matching | Not independently certified in Module 5 | Not needed for a genuinely NLO claim; cannot label existing result full NNLO |
| Widely separated scalar thresholds/near numerical degeneracy | No general domain certification | Bound single-scale logs; respect BMU evaluator's uncertified near-x=1 domain |

Published bases/topology sources: [BMU hep-ph/9904413v1](https://arxiv.org/html/hep-ph/9904413v1),
Sec.2/Apps.A–B; [BG hep-ph/9802391v1](https://arxiv.org/html/hep-ph/9802391v1),
Sec.3/App.A; [Zee charged mixing 2106.08332v1](https://arxiv.org/html/2106.08332v1),
Sec.IV.C.1/App.A.3. The known literal typo in the latter's up-quark
vertex is resolved by the frozen native/source audit, not adopted anew.

## Rate, observable and uncertainty

| Requirement | Actual coverage | Gate |
| --- | --- | --- |
| Photon cut | D12/D9B and independent diagnostics use Eγ>1.6 GeV | Covered as backend input |
| CP/isospin definition | flavio explicitly CP averaged; D9B real unprimed CP-even rate; complete spectator-dependent resolved photons not certified | Full interpretation incomplete |
| SM+NP and H1/H2 interference, quadratic response | Coefficient sum before rate; archived ±C7/8, joint cross terms and held-outs executed | Kernel behavior checked, physical accuracy unvalidated |
| NLO C4 response | D9B explicit dataflow/falsifiers; EOS full-vector diagnostic | Covered in research subset |
| Rate normalization | D9B experimental semileptonic BR, CKM ratio and kinetic C; EOS width/lifetime differs; flavio legacy semileptonic | Independent matched normalization missing |
| SM baseline | Preserved per scheme, zero-NP checks passed | No 2026 intercept substitution |
| Published 2HDM limit | One-state matching/backend identities passed | Matched physical BR and confidence-bound reproduction missing |
| Parametric uncertainty | Backend priors exist; no qualified joint NP propagation/covariance here | UNKNOWN |
| Perturbative uncertainty | NLO matching validated; scale envelope alone insufficient; clipping is not a bound | UNKNOWN |
| Nonperturbative/resolved photons | Legacy central prescriptions/nuisances exist; Wilson-dependent Zee coverage uncalibrated | UNKNOWN |
| Numerical error | Prior residuals/tolerances archived; two original-card receipts verified | Implementation tolerances only |
| Experimental comparison | 2026 Letter/companion quote (3.49±0.19)e-4; cut extrapolation/correlations require explicit treatment | No adopted physical likelihood |
| Confidence interpretation | No source-consistent theory budget plus statistical coverage established | Exclusion null |

The companion's SM input covariance is not a generic NP covariance.
SuperIso's multiplicative 4% nuisance and flavio's additive legacy nuisance
are real source features; neither is assigned to the repaired two-state NLO
prediction without validation. The 2026 linear formula omits quadratic terms
and supplies no certified finite Zee remainder domain. Complete uncertainty
coverage is therefore unresolved even though nonlinear kernels are available.


Fixed-card uncertainty gate: [UNCERTAINTY_REPORT.md](bsgamma_hepfit/UNCERTAINTY_REPORT.md) records 69 new nuisance/scale executions, correlated partial errors and an unresolved Wilson-dependent theory budget. Historical table confidence root 473.1 GeV does not exactly reproduce 480 GeV. Specialist input required; B_FULL_RATE_BLOCKED, physical_bsgamma=UNKNOWN, exclusion=null, theory_sigma=null. Milestones unchanged.

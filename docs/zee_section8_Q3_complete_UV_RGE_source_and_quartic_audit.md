# Q3 — Full Zee UV RGE source gate and generic scalar BFB witness

**19 October 2026 — SOURCE AUDIT AND EXACT TREE-LEVEL QUARTIC CALCULATION ONLY.** No complete one-loop generic complex Zee beta system; no physically allowed Zee point has been certified.

## Sources and precisely limited coverage

1. Kanemura *et al.*, PRD 64 (2001) 053007, [hep-ph/0011357](https://arxiv.org/abs/hep-ph/0011357), Appendix A (A1–A3): Zee gauge coefficients (22/3,-3,-7), SM-normalized hypercharge; (A4–A11): restricted scalar beta functions; (A12): top-only Yukawa; (A13): restricted real antisymmetric f beta. The paper excludes general lepton Yukawas, lambda6/lambda7 and generic complex lambda10. Existing Q2e reproduces ONLY the restricted real-f expression and was committed after the 130/130 Q2d validation; its full AF validation remains to be reported.
2. Ferreira–Lavoura–Silva, [1001.2561](https://arxiv.org/abs/1001.2561), Eqs. (3)–(5): general *multi-doublet* Yukawa RGEs. This establishes the f=0, singlet-decoupled limit, not the general f-induced lepton terms.
3. Schmidt–Vandeleur, JHEP 06 (2026) 006, [2512.17235](https://arxiv.org/abs/2512.17235), Eq. (2.4): full general Zee scalar potential; Sec. 3 and App. B: heavy-singlet EFT hierarchy and 2HDM EFT running, **not general Zee UV beta functions**. Its EFT hierarchy is inappropriate as an uncontrolled approximation to the project's collider-favored light/sizable-mixing charged singlet.
4. Machacek–Vaughn generic framework, NPB 222 (1983), 236 (1984), 249 (1985); PyR@TE 3, CPC 261 (2021) 107819; RGBeta, EPJC 81 (2021) 408 / arXiv:2101.08265. General-purpose generator availability is not equivalent to verified model-specific coefficients.

The missing calculations are the general complex beta_f and f-corrected beta_Pi1, beta_Pi2; full beta_lambda1..lambda7, lambda_h, lambda8..lambda10; mass and trilinear betas; thresholds and consistent coupled flow. They need complete explicit Weyl-field assignments, precise charge and normalization conventions, and independent generator cross-validation. No fictitious coefficients are inserted.

## Exact quartic scalar calculation

Let x=Phi1†Phi1≥0, y=Phi2†Phi2≥0, z=Phi1†Phi2, |z|²≤xy, s=|h+|²≥0. In the convention of source Eq. (2.4),

```
V4 = lambda1*x²/2 + lambda2*y²/2 + lambda3*x*y + lambda4*|z|²
     + Re(lambda5*z² + 2*(lambda6*x+lambda7*y)*z)
     + lambda_h*s² + s*(lambda8*x+lambda9*y+2Re(lambda10*z)).
```

This has 15 real quartic parameters: seven real couplings (lambda1–4, lambda_h, lambda8, lambda9) and four complex couplings (lambda5–7, lambda10). With A=lambda8*x+lambda9*y+2Re(lambda10*z) and lambda_h>0, the exact minimization over s is

```
s_star = max(0,-A/(2*lambda_h))
min_s V4 = V_2HDM - min(0,A)²/(4*lambda_h).
```

For lambda_h<0 there is an exact singlet-only unbounded direction; for lambda_h=0 any attainable A<0 causes a runaway. Necessary BFB conditions on isolated doublet/singlet rays are lambda1,lambda2,lambda_h≥0 and lambda8≥−sqrt(2 lambda1 lambda_h), lambda9≥−sqrt(2 lambda2 lambda_h). Portal A≥0 in every doublet direction iff lambda8,lambda9≥0 and lambda8*lambda9≥|lambda10|²; that does NOT prove the 2HDM sector is BFB.

The new script `scripts/zee_section8_Q3_generic_scalar_bfb_witness.py` implements exact minimization and a deterministic 1440-point orbit-space grid. A negative physical V4 is a rigorous BFB counterexample for that parameter choice. The **absence** of a sampled negative V4 is NOT a stability proof. This is a tree-level quartic test, not an RG result, physical vacuum determination, or experimental constraint. Its diagnostics use only synthetic quartics and never label stored B2 points as allowed.

Regressions: `tests/test_zee_section8_Q3_generic_scalar_bfb_witness.py` test exact minimization, complex rephasing, Gram constraints, singlet runaway, analytic single-field necessary conditions, portal positive semidefiniteness, and explicit negative witnesses. Local equivalent 13-case implementation passed before the GitHub commit; GitHub integrated tests must be run on AF and their results reported separately.

## Scientific decision

**CURRENTLY UNTESTED; neither viable nor excluded.** Q2 numerical closure and a Q3 quartic witness are not substitutes for validated complex full UV beta functions, NuFIT 6.1 fits, coherent LFV, FCNC Wilson coefficients, matched B→X_s gamma, full global vacuum testing, and physical widths. A complete Zee-RGE generator implementation remains the next mandatory beta-equation gate. Do not turn a reduced-f or tree-level scalar calculation into a full RG claim.

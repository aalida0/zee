# Priority-1 N3: real neutral-scalar self-pair partial widths

## Original N2 result

The user's last AF N2 run completed 309/309 original Zee scalar E2/E3 spectra, source-matched neutrino/Yukawa solutions, and all additional N2 scalar-gauge and charged-pair modes. Still: 309 BLOCKED_DECAY_CHANNEL_COMPLETENESS, 0 HiggsBounds calls. For B4_0004143, H included width 1.4836812 -> 6.7584788 GeV and A -> H1 W (both charges) 10.5509907 GeV. For B4_0017640, H included width 1.599802 -> 30.4211406 GeV and A -> H1 W (both charges) 49.9275251 GeV. These are partial widths, not physical totals.

## Exact new scalar potential contribution

The source file scripts/zee_priority1_neutral_scalar_cubics.py reconstructs the neutral CP-conserving two-Higgs-doublet subsector of the original Gate6 Zee potential. Charged singlet has zero neutral VEV. Original CP-even rotations are h=(cos alpha,sin alpha) and H=(-sin alpha,cos alpha) on rho1,rho2, with CP-odd physical A=(-sin beta,cos beta) on eta1,eta2.

Compute analytic full symmetric third derivatives of V, including all lambda1...lambda5:
- g_Hhh = third derivative H,h,h
- g_HAA = third derivative H,A,A
- g_hAA = third derivative h,A,A

**Independent physics check:** the analytic tensor is compared point by point against centered finite differences of a separately evaluated gauge-invariant neutral scalar polynomial potential. Both CP-even and CP-odd reconstructed Hessian eigenvalues must match the exact original Gate6 input spectrum and neutral Goldstone must be massless.

For identical final neutral bosons, the correct width is

Gamma(S->ss) = g_Sss^2/(32 pi M_S)*sqrt(1-4 m_s^2/M_S^2),

with zero if M_S<=2m_s. These are additional exact tree-level two-body channels H->hh, H->AA and h->AA. Some may be kinematically closed for all 309 sources, but that is determined by the AF run and not assumed. All previous original N2 h/H/A/H1/H2 modes and source values are retained bitwise. Potential errors, original source mismatches, duplicate final-state labels and closed-channel nonzero rates fail closed.

**No physical widths/branching ratios or HiggsBounds exclusions**: incomplete neutral and charged decay modes, h125 WW*/ZZ*, QCD/running quarks, loop-induced, off-shell channels, independent UFO/MadWidth comparison and actual cross sections remain outstanding.

## One AF command

~~~bash
cd /home/aalida/zee
git switch feature/global-scan-priority1
git pull --ff-only
bash scripts/zee_priority1_N3_one_shot.sh
~~~

The runner first executes four numerical/source regression suites, then opens the immutable completed N2 v2 archive, checks the E2/E3 source linkage, computes all 309 actual neutral cubics with independent finite differences, and generates new partial five-state decays. The canonical Priority-1 gate must remain blocked for all 309 incomplete decay records, with zero HiggsBounds API calls and no accepted/excluded models.

New nonoverwriting destination:

work/p1_original_309_neutral_scalar_cubics_N3_20261020_v1/

Outputs: original-source-hashed combined partial five-state JSON, canonical P1 join summary and N3 summary listing eight original Pareto-priority benchmark H->hh and H->AA tree partial widths and N2->N3 included-width changes. Original E2/E3/B3/N1/N2 outputs are read only.

New unit and numerical tests:
- tests/test_zee_priority1_neutral_scalar_cubics.py: independent potential/cubic checks, threshold, identical neutral-pair factor, CP-even/odd masses.
- tests/test_zee_priority1_N3_original_N2_join.py: preserves source N2 five-state records, blocks overlaps, mandatory export provenance and no HiggsBounds false positives.

Source validation is a same-repository independent-formula audit, not external independent UFO/MadWidth or model matching. N3 is one additional incomplete but physical tree two-body module, **NOT a completed Priority 1 constraint pipeline**.

# Historical one-state confidence control

**NOT_REPRODUCED at published precision; no transfer to Zee.**
The explicit table calculation in ONE_STATE_CONFIDENCE.json gives 473.108 GeV,
versus the published 480 GeV. This 6.89 GeV discrepancy is retained, not tuned
away. HEPfit's 7% multiplicative table error, finite tanβ=100 and tabulation
are an approximation to the publication's full setup. The available table
and its nuisance do not expose the underlying component covariance.

For each mass the sampling model is Normal(B_theory(m), s(m)^2), with
s(m)^2=s_exp^2+[0.07 B_theory(m)]^2. Invert the belt
x >= B_theory(m)-1.644853627 s(m) for the observed x. This is a one-sided
95% construction under those Gaussian assumptions, rather than calling an
arbitrary pull a physical exclusion. The numerical root uses bisection on
the published reference table only; no Zee mass scan is performed.
The historical observation is (3.43 ±0.21 ±0.07)×10^-4 at 1.6 GeV;
its two errors are combined in quadrature in this reference control.
[2015 publication](https://arxiv.org/html/1503.01789v2), Eqs.(1),(11).

[2017, Sec.5/Table 3](https://arxiv.org/html/1702.04571v1) explicitly distinguishes
one-sided, central and Feldman–Cousins belts. For its preferred Rγ dataset,
the respective Type-II bounds are 692, 583 and 580 GeV. These are source
comparisons, not independently reproduced roots: the present executable
computes BR_sγ, not the publication's Rγ likelihood. Central Gaussian belts
would use z=.975 quantile; FC requires ordering by the likelihood ratio to
the best allowed parameter and cannot be replaced by that quantile.

The preserved 2026 audit records a 670 GeV result with updated perturbation
theory. Neither that result nor the 2015/2017 NNLO uncertainty determines
an NLO Zee covariance. No modern likelihood is adopted here. The historical
experimental extrapolation and its potential common hadronic inputs need
joint treatment before a present-day physical comparison.

Reproduce: `python3 research/full_constraints/bsgamma_hepfit/one_state_confidence.py`.

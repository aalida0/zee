# Priority-1 N1: actual 309 Zee neutral h/H/A tree-level included-channel widths

Previous AF user result: original P1 E3/B3 309 scalar/Yukawa-source matched charged widths succeeded 309/309, zero missing E3 Y solutions, no physical full five-state widths, no HiggsBounds. That source archive is immutable.

## What new real physics is computed

Reuse the original Gate A1D neutral Zee lepton Yukawa matrices (Chen/Florentino conventions) and Gate D5 exact two-body spin/phase-space widths. Calculate all six e,mu,tau pair modes for each original neutral state h(125), H and A: three diagonal charged-lepton modes and three flavor-off-diagonal modes, including both charge conjugates.

Separately compute four quark two-body LO modes (tt,bb,cc,ss) using the existing *Type-II-like quark Yukawa ansatz* defined in the project Gate E5. Correct CP-even and CP-odd threshold powers are used with explicitly fixed quark masses; there is NO running or QCD correction. Also compute on-shell CP-even WW and ZZ LO partial widths (A tree VV=0).

The project defines delta=beta-alpha. Neutral factors are:
- h: kV=cos(delta), ku=cos(delta)-sin(delta)/tan(beta), kd=cos(delta)+sin(delta)*tan(beta).
- H: kV=sin(delta), ku=sin(delta)+cos(delta)/tan(beta), kd=sin(delta)-cos(delta)*tan(beta).
- A: kV=0, |ku|=1/tan(beta), |kd|=tan(beta).

This generates **12 actual included partial-width channels for each h/H/A** and reuses original E3/B3 included H1/H2 channels. The three original h125 LFV rates must agree exactly with original Gate D5 for the identical optimized lepton-Y and scalar alignment.

### These are NOT physical total widths

Missing h125 WW*/ZZ*, gg, gamma gamma, Zgamma, all higher-order corrections; H/A -> Z scalar and scalar pairs; off-shell three-body modes; charged H1/H2 additional channels and QCD; independent complete heavy scalar potential trilinears. **No missing mode is assigned zero to close a total width, and no incomplete branching fraction is a model exclusion or HiggsBounds input.**

## One actual AF 309-source command

~~~bash
cd /home/aalida/zee
git switch feature/global-scan-priority1
git pull --ff-only
source .venv-flavor-f1/bin/activate
python -u scripts/zee_priority1_neutral_309_one_shot.py
~~~

This checks original prior charged stage summary/E2+E3+charged export SHA, joins the actual optimized Y with the corresponding original source scalar spectrum, computes each new neutral partial width and exports all five states *only as partial/incomplete*. The original P1 canonical CLI must report 309 times BLOCKED_DECAY_CHANNEL_COMPLETENESS, HiggsBounds API calls=0, and model allowed/excluded=NULL. It refuses overwrite of original archives.

Fresh output directory: work/p1_original_309_neutral_h_H_A_plus_charged_LO_20261020_v1/
- P1_309_h_H_A_H1_H2_partial_LO_NOT_COMPLETE.json
- joined_five_stage_report/summary.json
- summary.json listing exact source SHA and 8 original priority candidate included-width sums.

Source code:
- scripts/zee_priority1_neutral_two_body.py
- scripts/zee_priority1_neutral_309_one_shot.py
- tests/test_zee_priority1_neutral_two_body.py (seven real original physics tests)
- .github/workflows/priority1-consolidation.yml (NumPy/SciPy numerical run)

**No actual 309 neutral AF output exists before the user executes the one-shot.** The physics code passed the source-safe numerical tests in CI, not a full NLO/hadronic/QCD model calculation. Next missing physics is complete neutral bosonic/trilinear decay channels and production model validation.

# Gate C0: executable adapter blocked by pinned SM contribution semantics

2026-10-27. **`HYPERISO_PATCH_INTEGRATION_BLOCKED_SM_BSM_PATCH_DROPPED`**.
Compilation succeeds. The minimal external candidate registers exactly one
additive BSM LO B-group patch each for C7 and C8, with no alpha_s multiplier,
qmatch=160 GeV and explicit qhad=4.8 GeV. HyperIso v1.0.3 discards both in
SM mode. The adapter exits **3**, preserving this failure instead of silently
switching to a native THDM calculation. Passing rejection regressions are
not a passing integration gate.

Machine evidence: [two_state_patch.json](../validation/module5/two_state_patch.json).
Frozen physics, prior tests/audits and HyperIso remain unchanged. Branch
`feature/zee-hyperiso-two-state-patch` descends from verified Gate B
`218fe01d893730bc2699c270d10db85a22708616`.

## Runtime and source diagnosis

Reused the existing ignored Gate B cache at
`/home/amine/zee-hyperiso-runtime-bridge/validation/module5/local/HyperIso`.
Verified actual HEAD and v1.0.3 peel
`09d26ac6e71d1528922097a896d15693589f636b`, annotated tag
`5a93aca5e28011df3a348954cdc7c7c330ea2169`, clean tracked sources,
CLI version `1.0.3`, CMake source association and binary SHA256. Historical
source hashes agree. No download, upstream edit, full R1–R7 rerun or SARAH
regeneration was needed.

`WilsonManager.cpp::apply_matching_patch_to_group` accepts a patch only
when its contribution matches the group's type, or the group is TOTAL
and the patch BSM. The native SM group is SM, so BSM decoration is rejected.
`ensure_sm_model_triplet_in_matching` additionally composes BSM as zero and
TOTAL as SM+BSM. Registering after build does not supply an SM-model BSM
backend. Actual before/after matching and running outputs confirm this.

The supported existing patch path is the **THDM BSM group**. Its patch is
additive to the existing charged-Higgs contribution. At gamma=0, adding the
contract gives **twice** the intended BSM coefficient; a diagnostic proves
this. Production rejects `model=THDM`. No automatic THDM fallback, residual
subtraction or fictitious quark phases are introduced. A future production
path needs a separately audited zero-native-BSM group with compatible
composition/running, or an upstream public API fix. Neither is established
here, and upstream modification is outside authorization. Work stops at the
requested SM-model gate; diagnostics do not authorize a workaround.

The exact upstream QCDHelper call used by THDM matching gives
`mt_MSbar(160)=163.96892236746697 GeV` with the explicit reference LHA SM
parameters. The default SM LHA instead gives `163.16600571643622 GeV`;
therefore the launcher requires an explicit parameter-source LHA and checks
the actual mass, rather than assuming it from either 163 GeV or a release
number. The contract example with 163 GeV remains illustrative and fails
the runtime mass guard against the reference LHA.

## Executed checks and quantitative scope

31 scoped regressions pass: frozen LO 16, prewritten contract 7, new adapter
8. No skips, failures or errors. The adapter suite includes 19 fresh
executable invocations. Actual outputs, source hashes, provenance and each
numerical residual are recorded in the JSON. These are numerical residuals,
not theory uncertainties.

- Independent, separate native THDM LO executions at each charged mass
  reproduce the real contract's cos²gamma/sin²gamma weighted coefficients
  and individual state components. Cases include gamma=0, gamma=pi/2 with
  exchanged masses, nontrivial mixing, degeneracy, interchange, zero-doublet
  contribution and heavy-state decoupling at 100000/200000 GeV. C1–C6 BSM
  matching entries remain zero. Opposite-ld controls reverse the XY term.
- SM baseline plus the real two-state patches leaves BSM exactly zero at
  both matching and hadronic scales: the no-silent-drop condition **fails**.
  TOTAL=SM+BSM still holds; this alone cannot demonstrate injection.
- Explicitly labeled THDM diagnostics transport synthetic complex scalar_t
  shifts through matching and public `getFR(..., B_STANDARD)` at LO and
  4.8 GeV. TOTAL=SM+BSM, split .25/.75 additive patches and independent C7/C8
  patch runs agree. Native THDM BSM is retained and subtracted only when
  measuring these diagnostic increments. No such subtraction is a physical
  adapter input. No branching-ratio method is called.
- Gamma=0 THDM+contract doubles the native shifts. Production rejects that
  model, incorrect SM/TOTAL contributions, NLO, qmatch=81, nonfinite qhad,
  pole-mass labeling, inconsistent MSbar top input and altered contracts.

The fixed physical benchmark is mH1=550, mH2=900 GeV, tanbeta=5.3,
gamma=1.09, with the retrieved reference top mass. Signed requested
components and sums, observed zeros and the doubled one-state values are
reported verbatim in the machine evidence. Requested C7 components are
`-0.012748567187026497 - 0.024629475846454953 = -0.03737804303348145`;
C8 components are
`-0.013790078955371425 - 0.028521415009350584 = -0.04231149396472201`.
Observed SM-mode injected BSM sums are exactly zero at both scales.
Maximum absolute check residual is `2.7755575615628914e-17`.

## Claim hierarchy and remaining physics barriers

1. `HYPERISO_PATCH_INTEGRATION_PASS`: **not achieved**. Compile and diagnostic
   BSM-backend API checks pass, but required SM-mode injection/running fails.
2. `EXTERNAL_OPERATOR_CONVENTION_PASS`: **not achieved**;
   `MATCHING_CONVENTION_UNKNOWN` retained. No new independent pinned
   Hamiltonian/sigma/Fourier/operator insertion evidence was obtained.
   Same-source THDM matching, trend signs and complex transport cannot close it.
3. `ZEE_B_TO_XS_GAMMA_PHYSICAL_PASS`: **NOT_EVALUATED**, outside this task.
   2026 linearized BSM screen also **NOT_EVALUATED**. No BR, likelihood,
   exclusion, allowed label, per-mass cut or 670 GeV bound was applied.

LO evolution is not a complete NLO/NNLO observable. Native SARAH historical
local-only evidence is neither restored nor required for adapter checks.
Gate B R1–R7 remains historical PASS; its legacy SM BR is not compared with
the 2026 baseline. No new literature search or phenomenology scan occurred.

## Reproduce

```sh
UP=/home/amine/zee-hyperiso-runtime-bridge/validation/module5/local/HyperIso
python scripts/zee_module5_two_state_validate.py --upstream "$UP" \
  --binary "$UP/build/UserInterfaceLib/hyperiso-ui"
```

The validator returns zero when all scoped regressions (including the expected
fail-closed rejection) pass, and records integration BLOCKED separately.
For direct execution, generate a contract with the actual retrieved top
mass, then use `zee_module5_two_state_patch.py --upstream ... --binary ...
--contract ... --lha ... --qhad 4.8`; on this pin it returns 3. Detailed build
products and logs stay ignored under `validation/module5/local/`.

# Full-vector bridge continuation

Conclusion: **RATE_BRIDGE_BLOCKED** for demonstrated physical accuracy. A native
EOS full-vector prototype runs, but no matched independent physical-rate
benchmark or justified accuracy domain has been established. No exclusion use.
This supersedes the pilot's inference that the missing inverse translator was
the central obstacle. Original pilot scripts/results remain unchanged.

## Analytic JMS input (no numerical inverse)

Use the frozen ordinary operator
`Q4=(sbar_L gamma_mu T^A b_L) sum_(q=u,d,s,c,b)(qbar gamma^mu T^A q)`,
`Q7=e mb/(16 pi²) sbar_L sigma b_R F`, with the analogous gs/color Q8.
The negative Hamiltonian corresponds to positive interaction Lagrangian
`L_NP=kappa sum DeltaC_i Q_i+h.c.`, `kappa=4 GF/sqrt(2) Vtb Vts*`.
JMS coefficients are dimensionful Lagrangian coefficients, with no GF, CKM,
loop factor or mass built into the operator. Indices u,c=1,2 and d,s,b=1,2,3.
The public WCxf JMS operator definitions are the executable specification.

For physical **total NP** `c4=a0 DeltaC4^(1)`, `a0=alpha_s(mu0)/(4 pi)`,
set the following JMS coefficients; add dipoles as shown:

| JMS keys | Coefficient |
| --- | --- |
| `V8udLL_jj23`, `V8duLR_23jj`, j=1,2 | kappa c4 |
| `V8ddLR_23jj`, j=1,2,3 | kappa c4 |
| `VddLL_1123` | −kappa c4/6 |
| `VddLL_1231` | kappa* c4/2 |
| `VddLL_2223`, `VddLL_2333` | kappa c4/3 |
| `dgamma_23` | kappa e mb(mu0) DeltaC7/(16 pi²) |
| `dG_23` | kappa gs mb(mu0) DeltaC8/(16 pi²) |

Derivation: split each vector q current into L+R. The up-quark LL and all LR
color octets already are JMS operators. For down-quark LL use
`T^A_ab T^A_cd = (delta_ad delta_cb − delta_ab delta_cd/3)/2` and the
four-dimensional LL Fierz identity. The crossed d term is the hermitian
conjugate of `VddLL_1231`, hence its conjugated kappa. For identical s/b
currents the crossed and singlet contractions give `(1−1/3)/2=1/3`.
There are no primed dipoles or right-handed b→s currents here. Since NP Q4
starts at a_s, an O(a_s) evanescent correction to its tree basis conversion
would first affect its matching at O(a_s²); this is not a general NLO JMS
conversion for arbitrary LO four-quark matching.

`direct_jms()` validates the WCxf vector and reproduces the dipoles through
JMS→flavio without sign/mass/CKM changes. The installed JMS→EOS code instead
applies `np.real` to four-quark combinations **before** dividing by complex
kappa. At gamma_CKM=1.27, a pure ordinary c4=0.01 becomes
`0.00999649283751321+0.00018724135408387303i`. Its photon coefficients are
similarly split before normalization. These complex values violate the real
EOS coefficient slots. At gamma_CKM=1e-8 the correct real limit is recovered;
exact zero is avoided because ckmutil's parametrization is singular there.
The artifact is confirmed algebraically by `EOS_c4*kappa=c4*Re(kappa)`.
No projection or numerical inverse is used as a physical bridge.

## Evolution actually executed

wilson 2.5.2 `WETrunner` documents QCD/QED ADM orders 0 and 1 (LO). Its
`getUs` uses gamma0 eigenvalues only. Higher-loop alpha_s/mass running does
not supply gamma1. Passing qcd_order=2 actually fails with an uninitialized
`Us`. Also, a one-loop general JMS ADM must not be assumed to contain the
conventional higher-loop four-quark→dipole entries. Thus inserting our NLO
matching into this runner cannot establish a full conventional NLO rate.

**Small existing alternative found:** the EOS 1.0.21 wheel exports
`eos::evolve`, with gamma0, gamma1, gamma2 and the BMU evolution prescription.
The 15-component basis is `(C1..C6,CQ3..CQ6,C2b,C7tilde..C10tilde)`.
Public ordinary dipoles obey `C7tilde=a_s C7`, likewise C8. Therefore input
arrays for the retained NP sector are:

```
qcd0 = 0
qcd1[3]  = DeltaC4^(1)
qcd1[11] = DeltaC7^(0); qcd1[12] = DeltaC8^(0)
qcd2[11] = DeltaC7^(1); qcd2[12] = DeltaC8^(1)
```

All other entries vanish. No input a_s multiplier is added to these raw arrays.
The library forms its own series; public output C7/C8 is divided by a_s(mu_b)
**once**. This is also how EOS constructs its own SM top-sector matching.
The SM coefficients and matching top/alpha_s are obtained from the same native
SM model. The resulting NP ordinary coefficients are added once to that SM
vector, then the ordinary→effective map is performed by the EOS rate.

For NP qcd0=0, at fixed eta=alpha_s(mu0)/alpha_s(mu_b), native ordinary
four-quarks are `t A+t² B` and dipoles `L+t N` under simultaneous alpha_s→t
scaling. We retain `2 f(1)−f(2)/2=A` for NP four-quarks (which start at NLO),
and `f(1)=L+N` for dipoles. This removes the extra NNLO four-quark output of
EOS's higher-order interface; no ADM is reconstructed. The degree and
same-scale limits are explicitly tested. Induced Q3/Q5/Q6 are retained.
The extra CQ3..CQ6/C2b entries must remain zero or the wrapper rejects the call.

The thin C++ wrapper links the unchanged wheel libraries using the exact
release headers. An unchanged upstream evolution test is compiled and run;
its C1..C10 references pass. An empty local config.h enables no optional
**test-generation** macros; it changes no physics code. The test links the
wheel's GSL25 to avoid mixing it with system GSL27. All downloads/builds stay
ignored under local/. Wrapper code is GPL-2.0-only; no EOS routine or binary
is vendored. Full corresponding EOS sources are available at the pinned URL.

## Physical accuracy stopping condition

EOS's rate uses `|D_LO+a_s D_NLO|²`, exponential bremsstrahlung, power terms
and its own default SM matching. This is an existing NLO-labelled prescription
with additional higher-order terms. It is **not** a demonstrated uniformly
truncated NLO Zee observable. The native RG removes the wilson-order obstacle;
it does not certify the observable truncation, scheme dependence or errors.

We inspected the actual CMM hep-ph/9612313v3 paper. Its Eq.(48) gives
R_quark=3.12e-3 at delta=0.99; Eq.(49) gives 2.86e-3 at delta=z. EOS's
upstream regression labels 3.12e-3 at **delta=1/3**, and 2.88e-3 at delta=z.
Our native diagnostic calls return 3.114573327417969e-3 and
2.881598258855486e-3 for those EOS inputs. The former is not the paper's
cut, and the latter uses the EOS virtual-amplitude, mass and truncation
prescription. Neither is a matched independent physical-rate reference.
Do not promote the upstream test's numerical success to that status. The EOS
cut-fit domain also excludes delta=0.99, so its published total-rate number
cannot simply be requested from this implementation.

No independent one-charged-Higgs BR with the same cut, masses, RG and rate
prescription was established. This is the explicit unmet benchmark requirement.
The smallest next task is to retain this native EOS adapter, obtain a complete
external one-state NLO benchmark card and order prescription, and validate
against it. If strict truncation is required, obtain an existing supported
order-separated kernel from EOS/HEPfit/SuperIso authors rather than interpreting
its absence as permission to build a new flavor framework. No statistical
uncertainty or restricted accuracy domain follows from the present tests.

## Reproduction

After the original README's pinned Python setup, from repository root:

```bash
curl -fLsS https://codeload.github.com/eos/eos/tar.gz/refs/tags/v1.0.21 -o research/bsgamma_rate_validation/local/eos_v1.0.21.tar.gz
tar -xzf research/bsgamma_rate_validation/local/eos_v1.0.21.tar.gz -C research/bsgamma_rate_validation/local
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/build_eos_probe.py
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/bridge.py
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s research/bsgamma_rate_validation -p 'test_*.py' -v
git diff --check
```

To refresh the provenance report as well:

```bash
curl -fLsS https://arxiv.org/pdf/hep-ph/9612313v3 -o research/bsgamma_rate_validation/local/cmm9612313v3.pdf
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/record_bridge_evidence.py
```

Build requires g++ with C++20 and GSL headers (host GCC 11.4/GSL 2.7.1).
Archive SHA256 is checked by the builder. Source/library hashes, commands,
actual outputs and test counts are in bridge_sources.json/bridge_results.json.

References: [JMS operator definitions](https://github.com/wilson-eft/wilson/blob/v2.5.2/wilson/wcxf/bases/wet.jms.basis.json),
[JMS→EOS translation](https://github.com/wilson-eft/wilson/blob/v2.5.2/wilson/translate/wet.py),
[wilson runner](https://github.com/wilson-eft/wilson/blob/v2.5.2/wilson/run/wet/classes.py),
[EOS evolution](https://github.com/eos/eos/blob/v1.0.21/eos/models/wilson-coefficients.cc),
[EOS SM matching](https://github.com/eos/eos/blob/v1.0.21/eos/models/standard-model.cc),
[EOS evolution regression](https://github.com/eos/eos/blob/v1.0.21/eos/models/wilson-coefficients_TEST.cc),
[BMU evolution hep-ph/9910220](https://arxiv.org/abs/hep-ph/9910220v1),
[CMM reference hep-ph/9612313v3](https://arxiv.org/abs/hep-ph/9612313v3).

# Gate 6: AF reproduction — scalar sector only

Status: **SCALAR-THEORY PRE-SCREEN PASS / FULL ZEE PHYSICAL BENCHMARK NOT VALIDATED**.
All numerical figures below were supplied from an AF run on login01, 2026-10-11,
using the scripts in this repository under `/home/aalida/zee`.

## Input point (illustrative P2-like choice)

m(h125)=125, m(hheavy)=580.7, m(A)=633.7, m(H1±)=300, m(H2±)=700 GeV;
alpha=1.398, beta=1.394, gamma=1.089 rad; tanbeta=5.597170833164246.
m12²=57700 GeV²; λC=4.473; k1=1.082, k2=0.00398, k12=-0.001266.

## Theoretical scalar gates

| Check | Result |
|---|---|
| m(h125), m(hheavy) reconstruction | 125.00000000000001, 580.7 GeV |
| Charged masses reconstruction | 300.0, 700.0 GeV |
| CP-odd mass reconstruction | 633.7 GeV |
| λ1, λ2, λ3, λ4, λ5 | 2.53232660, 0.25231427, 2.64509550, -1.21054237, -1.12678185 |
| Charged trilinear μ4 | 943.40014846 GeV |
| Quartic bounded-from-below sufficient condition | PASS |
| max abs tree unitarity eigenvalue | 18.1367790857 < 8π=25.13274123 |
| Coarse beta grid that passes these particular gates | 1.3878–1.3965 rad (88/141 points) |
| Charged-breaking 82-start minimization | No deeper minimum observed |

Finite vacuum search values: V_neutral=-118445468.35925195 GeV^4,
best=-118445468.35925196 GeV^4, difference -1.49e-8 GeV^4.
**A finite local multistart search does NOT prove the global minimum.**
Also, no oblique, flavor, collider limits or full lepton-sector checks
were included. This is NOT an allowed-beta interval.

## Partial LO widths (GeV; not the complete Zee width)

| H2+ decay | Γ, GeV |
|---|---:|
| H1+ Z | 9.411343198 |
| H1+ h125 | 0.267036409 |
| t bbar | 1.558105505 |
| tau+ nu (Type-II) | 0.035684441 |
| W+ h125 | 0.001223706 |
| W+ hheavy | 1.071030743 |
| W+ A (closed) | 0 |

Sum of included H2 widths: 12.344424002 GeV.
Conditional fraction H2→H1Z/sum(included)=0.762396301.

For H1: Γ(tb)=0.0909493753 GeV; Γ(tau nu, Type-II)=0.00418126966 GeV;
Γ(W h125)=1.1359e-5 GeV; sum=0.09514200399 GeV.
Conditional H1→tb fraction=0.955932937.

**These are not physical BRs**: the independent Zee antisymmetric charged-
singlet lepton couplings (neutrino generation and LFV constraints),
loop/QCD corrections and other allowed modes are not included.

## Width stress test: impact of unspecified additional decays

Let ΔΓ_1, ΔΓ_2 denote unknown extra partial-width contributions.
Then

`BR(H1→tb) = 0.0909493753 / (0.095142004 + ΔΓ_1)`

`BR(H2→H1Z) = 9.411343198 / (12.344424002 + ΔΓ_2)`

Examples: ΔΓ1=0.1 GeV reduces the first fraction to ≈0.466;
ΔΓ2=5 GeV reduces the second fraction to ≈0.543.
The paper's published P2 scan is not a full neutrino/LFV fit.

## Mandatory next gates

1. Full 2HDM+charged-singlet Zee gauge theory/UFO, independently verified;
   never substitute the Zee–Babu model (a different field content).
2. Include independent Zee charged-singlet lepton Yukawas and neutrino mass/LFV constraints.
3. Electroweak precision S,T,U, B→X_s γ and updated Higgs/direct search constraints.
4. Full two-body/off-shell charged Higgs width closures, Ward/gauge checks.
5. Production resimulation at **tanbeta=5.59717**, not old 5.72945,
   if a physically allowed benchmark survives.
6. Detector and background modeling only after 1–5.

**Decision:** continue model development; STOP full detector simulation.

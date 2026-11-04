# D15 diagnostic: four committed D12 inputs

**Final validation status: NOT_EVALUATED.** Four reduced SPheno executions
completed, but the complex operator map is not analytically established,
the input schemes are unmatched, vertex arrays have not been checked
numerically, and individual charged/neutral contributions and null limits
have not been measured. FlavorKit is not yet a validated one-loop LFV
reference. Nothing here establishes complete Zee LFV constraints.

Run `python3 research/spheno_flavorkit/compare_dipoles.py` after generating,
building and instrumenting the reduced backend as in [README](README.md).
The script requires exactly one instrumented output per chirality, errors on
missing results, uses four central committed D12 witnesses, and records
SHA-256 for input dataset, executable, template, each card, log and spectrum.
The committed [JSON](d15_diagnostic.json) contains all complex coefficients,
residuals and provenance. Generated files remain ignored. Group 0 reproduces
the original card and instrumented log hashes; the printed spectrum may
contain run-dependent metadata. Groups 0/1 and 2/3 use NO/IO respectively,
with two scalar spectra and independently supplied complex Yukawas.

| Group | candidate relative residual L | R | SPheno BR / D12 scalar BR |
|---|---:|---:|---:|
| 0 | 2.018959e-5 | 2.453408e-5 | 1.000020983 |
| 1 | 4.153292e-5 | 2.593449e-5 | 1.000022829 |
| 2 | 2.593179e-6 | 1.362634e-5 | 1.000097054 |
| 3 | 6.949487e-6 | 1.100781e-5 | 1.000075694 |

Residual is `abs(K2+conj(C))/abs(C)` and is **only a candidate diagnostic**.
The four rates include the common scalar one-loop subset only on the D12
side, not its partial two-loop terms. No acceptance tolerance can be
scientifically justified until conventions, actual vertices and matching
uncertainties are resolved; in particular the original 2e-5 is not a
universal tolerance. Neither residuals nor rates certify the sign.

## Input and perturbative scheme audit

D12 records `v=246.21965`, `mZ=91.1876`, `mW=80.379` and an on-shell
`g2=2mW/v` scheme. Its charged-lepton masses are pole snapshots
`(0.00051099895,0.1056583755,1.77686)` GeV; see
`validation/module12/d12_benchmarks.json` `SM_decay_card`. The card exporter
sets GF from v and sets mZ and tau, but leaves SPheno electron and muon
inputs at its defaults (0.00051099893 and 0.1056583715 GeV in
`src/StandardModel.f90:684-686`). SPheno uses `mf_l_mz` in K2 normalization
and running SM Yukawas (`RunSM_ZeeTypeII.f90:134-153`), whereas the
observable uses pole `mf_l` and alpha(0). D12 uses the frozen scalar-one-loop
inputs and includes the nonzero daughter phase-space factor. The ~7e-5 rate
change from this factor helps explain the different amplitude and rate
residuals; lifetime, running and mixing differences must still be quantified.

SPheno reports `mW=80.348464`, a -0.030536 GeV difference from D12. It is
not inserted as an MW input by the exporter. Generated `RunSM_ZeeTypeII.f90`
uses a fixed `sinW2=0.22290` at MZ in constructing running SM inputs, and
SPheno performs matching/running; D12 directly fixes MW/MZ. The generated
calculation reports Q=160 GeV and tree scalar mass output (loop masses off).
These source facts establish different input paths, but do not isolate every
term producing the MW number; the exact final MW derivation is NOT_EVALUATED.
Forcing MW would not establish matched couplings. The input has alpha_s(MZ)
0.1187 versus D12 0.118; quark masses are default SPheno inputs (e.g.
mb(mb)=4.18, mt pole 172.89 GeV) versus D12's separately recorded
threshold/running choices. Quarks do not enter the compared direct scalar
lepton one-loop diagrams, but may affect matching. D12 F/Ye2 complex inputs
are written verbatim; SPheno derives Ye through its matching and rotates
fields. Eigenstate row signs were observed in the pilot. Full F, Ye, Ye2,
ZEL/ZER and scalar-mixing readback for every point remains NOT_EVALUATED.
No claim is made that selecting identical numerical mass values removes
running-versus-pole or perturbative-order differences.

## Next required work

Trace the PreSARAH tensor projector through the actual all-incoming amplitude
and photon conventions to prove the complex map; numerically export both
charged vertices including ZEL/ZER for all indices and scalar rows; instrument
charged and neutral contributions independently, quantify each input-scheme
change, and run phase, sign, null and rephasing tests. Then define a tolerance
from those measured mismatches and truncations and compare each coefficient
and rate. Treat all those gates as NOT_EVALUATED until demonstrated.

# Module 1 — PARTIAL (interface 1.0.0)

Actual validation: 23 inherited + 26 independent tests, zero failures;
four inherited CLI runs and seven complete physical JSONL benchmarks. Source hashes:
[source_manifest.json](source_manifest.json). Numerical results: [results.json](results.json).
Detailed actual logs and full per-point outputs remain ignored in `.module1_logs/`.

| Gate | Validation status |
|---|---|
| Physical → SARAH Lagrangian | PASS: independent polynomial, tadpoles, Goldstones, all Hessians and signed mixing |
| BFB | PASS for sufficient all-orientation certificates and verified negative witnesses; UNKNOWN otherwise |
| 55-channel tree unitarity | PASS: canonical normalization, Q/Y blocks, basis rotations, analytic limits |
| Neutral/charge-breaking vacuum | PARTIAL: reproducible stationary-minimum witnesses; no global proof |
| Scalar one-loop S,T,U | PASS within below-threshold scalar oblique approximation |
| Versioned one-point/JSONL interface | PASS |
| Requested Module0 tag ancestry | BLOCKED: Git object/tag absent; frozen sources match archived native validation |

Independent maxima: tadpole/v³ 4.913e-16;
mass-spectrum difference/max(m²) 9.503e-16;
Hessian difference/v² 1.229e-13;
fourth-derivative tensor 0.000e+00;
unitarity basis eigenvalues 1.066e-14;
analytic versus quadrature loop functions 2.158e-13.

P2: max unitarity eigenvalue 18.13677908573 < 8π;
S,T,U = {'S': 0.0044404330206560625, 'T': -0.0049021783175765745, 'U': 5.733708113025872e-05}; vacuum remains UNKNOWN.
The physical singlet-minimum fixture independently reproduces analytic V=-MCS2²/(4 LambdaC),
with gradient/v³ 1.208e-50 and positive transverse Hessian.
Negative doublet BFB, complex orientation/portal runaways, tree unitarity failure,
and a deeper charge-breaking vacuum are explicitly falsified by real calculations.

The inherited neutral 13x13 matrix has signed differences from physical scattering:
an explicit all-incoming basis lift reproduces them; absolute spectra and bound agree.
The disputed EWPO -1/2 coefficient shifts P2 T by 0.360288001; use Grimus -2.
Alternative covariance fits are never combined. Fixed 125 GeV SM subtraction also
works for arbitrary light-Higgs inputs.

Scientific limits: sufficient BFB is not necessary; marginal/uncertified points are UNKNOWN.
Numerical vacuum sampling never means globally stable. Only the restricted CP-conserving
scalar potential is implemented; complex lepton Yukawas do not make it the most general
scalar potential. Lambda6/7 RG closure is unproven. No global Zee acceptance, scan cohort
classification, collider/flavour acceptance, native SARAH rerun or RG result is claimed.
Frozen Module0 scripts/model and the original `~/zee` working tree are unchanged.

Reproduce: `bash scripts/run_module1_validation.sh`.
Use: `python3 -m module1.scalar_constraints --input module1/example.json`.
Contract and derivations: [../../module1/README.md](../../module1/README.md).

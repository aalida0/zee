# 14 Nov 2026: native Zee one-loop gate failed — FZEEIN/Ye2IN input propagation audit

## Evidence directly from original user's machine

Native model: original SHA-attested 4.0.5 `SPhenoZeeTypeII`, 64 repaired complex Yukawa cards, case `2264 NO 20261111`.

One-loop scalar spectrum exists and original scalar mass gate executes, but
`native_yukawa_gate` **fails on FZEE**.

| Quantity | Expected SLHA input | Output at Q=160 GeV | Implication |
|---|---:|---:|---|
| max |F| | 2.6029200757220063e-05 | 1.30716019e-04 | Mismatch factor, not numerical tolerance |
| F(2,2) | 0 + 0i | 1.30716019e-04 + 0i | Violates intended antisymmetric gauge-basis Zee F |
| max |Ye2| | 7.496887238704813e-03 | 0 | Input-to-output loss |
| F relative max delta | -- | 5.021899067098384 | 502.2% |
| F residual after fitted complex multiplicative scale | -- | 0.9986508704410658 | Simple scale running/normalization cannot account |

The original input contains exact `FZEEIN`, `IMFZEEIN`, `YEE2IN`, `IMYEE2IN`. The
generated Fortran records
- `InputOutput_ZeeTypeII.f90:155-165` recognizing and reading `FZEEIN/IMFZEEIN`;
- `SPhenoZeeTypeII.f90:218`: `fzee = fzeeIN`;
- `SPhenoZeeTypeII.f90:221`: `Ye2 = Ye2IN`.
Thus the model reads and initially assigns matrices, but this evidence does
**not** show where they are subsequently overwritten or transformed.

A controlled one-case sensitivity experiment, varying one matrix independently
and preserving all other SLHA sections, gave:
- double original `FZEEIN[1,2],[2,1]` (and its imaginary partner):
  **Δoutput F=0, Δoutput Ye2=0**;
- double `YEE2IN[3,3]` (and its imaginary partner):
  **Δoutput F/max|F_baseline|=0.7708748764755451, Δoutput Ye2=0**.
Input-output mapping is therefore **not faithfully propagated** for this
compiled model/configuration. A reader alone cannot be blamed: the driver
assigns from IN parameters at line 218/221, but subsequent spectrum/boundary
code has not yet been inspected.

`SPHENOINPUT[11]` appears twice with values 0,1; it is a decay switch and
is **not a demonstrated cause**. Do not remove it merely to pass the gate.

## Independent public documentation

SARAH's *Input parameters of SPheno* documentation says matrix inputs
`XIN` are recognized, and `LHInput[X]` in an explicit boundary condition
can enforce input values at the chosen low-scale boundary. See
https://gitlab.in2p3.fr/goodsell/sarah/-/wikis/Input_parameters_of_SPheno/diff?version_id=b18bfcdc030f32426d7d02399a938c351d9c08aa

The current `module14/physics_adapters/SPheno.m` lists scalar entries but
not `{fzee,LHInput[fzee]}` and `{Ye2,LHInput[Ye2]}` in its
`BoundaryLowScaleInput`. A separately generated
`candidate_spheno_boundary.py` now offers an **unvalidated isolated**
variant with these two assignments. It does NOT edit original SARAH sources,
run Mathematica, compile SPheno or validate spectrum/loop observables. Source
file for the actually compiled model must be matched first: branch copy can
be different from the private generated original.

## Current action gates

1. Inspect the actual generated `SPhenoZeeTypeII.f90:205-365`,
   `InputOutput_ZeeTypeII.f90:145-210` and available boundary/RGE routines
   **after initialization**, to identify exactly which assignment overrides
   `fzee` and `Ye2`.
2. If the missing low-scale Yukawa boundary condition is confirmed in
   the actual SARAH source, regenerate **an isolated modified model**
   using the candidate LHInput settings. Rebuild executable and record
   source and executable SHA-256. Do not overwrite existing validated binary.
3. Replay the two one-card input sensitivity probes, retain full complex F
   and Ye2, enforce F antisymmetry/zero diagonals and exact D zero texture,
   and recheck original scalar masses and one-loop neutrino reconstruction.
4. Only after that replay new 64 repaired source 1-loop μeγ, μ3e and
   historical corrected μAu conversion, using the actual source-generated
   interfering Wilsons. Modern LEFT/nuclear and full mixed Zee EDM/two-loop
   gaps remain separate physics scope.

**Non-negotiable current status:**
`NATIVE_YUKAWA_INPUT_INVALID`,
`REPAIRED64_NATIVE_ONELOOP=NOT_VALIDATED`,
`FULL_PHYSICAL_ZEE_LFV=UNKNOWN`,
`GLOBAL_ALLOWED_SCAN=UNKNOWN`.

No LFV rate from this failed model point is physically usable merely because
SPheno returned exit zero or scalar masses passed.
